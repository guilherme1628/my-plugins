#!/usr/bin/env node
/**
 * Generate Distrato Social DOCX (company dissolution document)
 *
 * Usage:
 *   node generate-distrato.js <input.json> <output.docx>
 *
 * Input JSON should contain:
 *   - empresa: { nome, cnpj, endereco }
 *   - socios: [{ nome, cpf, nacionalidade, estado_civil, profissao, naturalidade,
 *               data_nascimento, doc_identidade: { tipo, numero, orgao_emissor },
 *               endereco, quotas, valor, valor_extenso, percentual }]
 *   - nire: string | null
 *   - juntaComercial: string | null
 *   - dataSessao: string | null
 *   - capitalSocial: { valor, extenso }
 *   - objetoSocial: string
 *   - dataInicioAtividades: string
 *   - dataEncerramentoAtividades: string
 *   - liquidante: string (nome of the liquidation partner)
 *   - cidade: string
 */

const {
  // docx-js types
  Document, Packer, Paragraph, TextRun,
  Header, Footer, AlignmentType, PageNumber, BorderStyle,
  // Constants
  PAGE_HEIGHT, PAGE_WIDTH, HEADER_HEIGHT, FOOTER_HEIGHT, FONT, SIZE,
  BASE_LINE_SPACING, BASE_SPACING_AFTER, BASE_MARGIN_TOP, BASE_MARGIN_BOTTOM,
  // Spacing
  setSpacing, getSpacing, getContentHeight,
  estimateTextHeight,
  // Text helpers
  boldText, normalText, centeredPara, justifiedPara, clausulaTitulo, emptyPara,
  // Border helpers
  noBorder, thinBorder, noBorders,
  // Tables
  buildSignatureTable,
  // Gender
  genero, isFeminino
} = require('../../alteracao/scripts/docx-helpers');
const fs = require('fs');

// ============================================================================
// DISTRATO-SPECIFIC: Qualification builder (includes naturalidade, data_nascimento)
// ============================================================================

const buildDistratoQualificacao = (socio) => {
  const g = (m, f) => genero(socio, m, f);
  const docId = socio.doc_identidade;
  return [
    boldText(socio.nome.toUpperCase()),
    normalText(`, ${socio.nacionalidade}, ${socio.estado_civil}, ${socio.profissao}, natural da cidade de ${socio.naturalidade}, ${g('nascido', 'nascida')} em ${socio.data_nascimento}, ${docId.tipo}: ${docId.numero}, ${docId.orgao_emissor}, e CPF: ${socio.cpf}, ${g('residente e domiciliado', 'residente e domiciliada')} na ${socio.endereco}`)
  ];
};

// ============================================================================
// DISTRATO-SPECIFIC: Preamble
// ============================================================================

const buildDistratoPreamble = (socios, empresa, nire, juntaComercial, dataSessao) => {
  const isSingle = socios.length === 1;

  // Build the shared company/dissolution portion
  const companyPart = (unicoText, resolveText) => {
    const parts = [];
    parts.push(normalText(`, ${unicoText} da empresa `));
    parts.push(boldText(`"${empresa.nome}"`));
    parts.push(normalText(`, sociedade empresária limitada com sede na ${empresa.endereco}`));
    if (nire && juntaComercial && dataSessao) {
      parts.push(normalText(`, com contrato social arquivado na ${juntaComercial} sob nº ${nire}, em sessão de ${dataSessao}`));
    }
    parts.push(normalText(`, e devidamente inscrita no CNPJ: ${empresa.cnpj}, ${resolveText} de comum acordo e na melhor forma de direito proceder o encerramento das atividades da sociedade empresária limitada, de acordo com as cláusulas e condições seguintes:`));
    return parts;
  };

  if (isSingle) {
    const s = socios[0];
    const fem = isFeminino(s);
    const unicoText = fem ? 'única sócia' : 'único sócio';
    const resolveText = 'resolve';
    // Single partner: ONE paragraph combining qualification + preamble
    const children = [
      ...buildDistratoQualificacao(s),
      ...companyPart(unicoText, resolveText)
    ];
    return [justifiedPara(children)];
  } else {
    // Multi-partner: separate qualification blocks, then shared preamble paragraph
    const qualParas = socios.map((s, idx) => {
      const isLast = idx === socios.length - 1;
      const ending = isLast ? '.' : ';';
      const qualChildren = buildDistratoQualificacao(s);
      qualChildren.push(normalText(ending));
      return justifiedPara(qualChildren);
    });
    const preambleChildren = [
      normalText('Os sócios acima qualificados, únicos sócios da empresa '),
      boldText(`"${empresa.nome}"`),
      normalText(`, sociedade empresária limitada com sede na ${empresa.endereco}`)
    ];
    if (nire && juntaComercial && dataSessao) {
      preambleChildren.push(normalText(`, com contrato social arquivado na ${juntaComercial} sob nº ${nire}, em sessão de ${dataSessao}`));
    }
    preambleChildren.push(normalText(`, e devidamente inscrita no CNPJ: ${empresa.cnpj}, resolvem de comum acordo e na melhor forma de direito proceder o encerramento das atividades da sociedade empresária limitada, de acordo com as cláusulas e condições seguintes:`));
    return [
      ...qualParas,
      emptyPara(),
      justifiedPara(preambleChildren)
    ];
  }
};

// ============================================================================
// CLAUSULA PRIMEIRA — Settlement of Haveres
// ============================================================================

const buildClausulaPrimeira = (socios) => {
  const isSingle = socios.length === 1;
  const title = clausulaTitulo([boldText('CLÁUSULA PRIMEIRA:')]);

  if (isSingle) {
    const s = socios[0];
    const fem = isFeminino(s);
    const artigo = fem ? 'A sócia' : 'O sócio';
    const body = justifiedPara([
      normalText(`${artigo} ${s.nome.toUpperCase()}, recebe por saldo de seus haveres na sociedade a importância de ${s.valor} (${s.valor_extenso}), correspondente ao valor de seu capital de ${s.valor} (${s.valor_extenso}),`)
    ]);
    return [title, body];
  } else {
    // Multi-partner: single clause listing all
    const children = [
      normalText('Os sócios recebem por saldo de seus haveres na sociedade as seguintes importâncias: ')
    ];
    socios.forEach((s, idx) => {
      const fem = isFeminino(s);
      const artigo = fem ? 'a sócia' : 'o sócio';
      const isLast = idx === socios.length - 1;
      const separator = isLast ? ',' : '; ';
      children.push(normalText(`${artigo} ${s.nome.toUpperCase()}, recebe a importância de ${s.valor} (${s.valor_extenso}), correspondente ao valor de seu capital de ${s.valor} (${s.valor_extenso})${separator}`));
    });
    const body = justifiedPara(children);
    return [title, body];
  }
};

// ============================================================================
// CLAUSULA SEGUNDA — Quitacao and Dissolution
// ============================================================================

const buildClausulaSegunda = (socios, objetoSocial, dataInicioAtividades) => {
  const isSingle = socios.length === 1;
  const title = clausulaTitulo([boldText('CLÁUSULA SEGUNDA:')]);

  let prefix;
  let recebeText;
  if (isSingle) {
    const fem = isFeminino(socios[0]);
    prefix = fem ? 'A sócia dá' : 'O sócio dá';
    recebeText = 'recebe';
  } else {
    prefix = 'Os sócios dão';
    recebeText = 'recebem';
  }

  const body = justifiedPara([
    normalText(`${prefix} entre si e a sociedade empresária limitada, da qual também ${recebeText}, geral, ampla e irrevogável quitação, para nada mais reclamar com fundamento no contrato social de constituição e no presente instrumento, declarando dissolvida para todos os efeitos, a empresa acima, a qual efetivamente encerrou suas atividades que consistia ${objetoSocial}, tendo iniciado suas atividades em ${dataInicioAtividades}.`)
  ]);
  return [title, body];
};

// ============================================================================
// CLAUSULA TERCEIRA — Liquidation Responsibility
// ============================================================================

const buildClausulaTerceira = (socios, empresa, capitalSocial, dataInicioAtividades, dataEncerramentoAtividades, liquidante) => {
  const isSingle = socios.length === 1;
  const title = clausulaTitulo([boldText('CLÁUSULA TERCEIRA:')]);

  // Determine the interest phrase based on singular/plural/gender
  let interesseText;
  if (isSingle) {
    const fem = isFeminino(socios[0]);
    interesseText = fem ? 'à sócia' : 'ao sócio';
  } else {
    interesseText = 'aos sócios';
  }

  // Find the liquidante socio to determine gender
  const liquidanteSocio = socios.find(s => s.nome === liquidante) || socios[0];
  const liquidanteFem = isFeminino(liquidanteSocio);
  const cargoText = liquidanteFem ? 'da sócia' : 'do sócio';
  const qualText = liquidanteFem ? 'a qual' : 'o qual';

  const body = justifiedPara([
    normalText(`A responsabilidade pela liquidação do Ativo e Passivo da sociedade, com sede ${empresa.endereco}, que se dissolve pelo fato de não mais interessar ${interesseText} a exploração objeto do contrato social de constituição, tendo inicio de sua atividade em ${dataInicioAtividades} e exercido suas atividades até ${dataEncerramentoAtividades}, ficará a cargo ${cargoText} ${liquidante.toUpperCase()}, ${qualText} se compromete a manter em sua guarda os livros e documentos da sociedade, cujo capital social era de ${capitalSocial.valor} (${capitalSocial.extenso}).`)
  ], { keepNext: true });
  return [title, body];
};

// ============================================================================
// CLOSING
// ============================================================================

const buildDistratoClosing = (socios) => {
  const isSingle = socios.length === 1;

  if (isSingle) {
    const fem = isFeminino(socios[0]);
    const acordo = fem ? 'justa e contratada' : 'justo e contratado';
    return justifiedPara([
      normalText(`E por estar assim ${acordo}, assina o presente ato em 1 (uma via) de igual teor e forma para que gere os efeitos de direito.`)
    ], { keepNext: true });
  } else {
    return justifiedPara([
      normalText('E por estarem assim justos e contratados, assinam o presente ato em 1 (uma via) de igual teor e forma para que gere os efeitos de direito.')
    ], { keepNext: true });
  }
};

// ============================================================================
// DATE FORMATTING
// ============================================================================

const formatDistratoDate = (cidade, date = new Date()) => {
  const months = [
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
  ];
  const day = date.getDate();
  const dayStr = day === 1 ? '1º' : day.toString().padStart(2, '0');
  const month = months[date.getMonth()];
  const year = date.getFullYear();
  return `${cidade}, ${dayStr} de ${month} de ${year}.`;
};

// ============================================================================
// SPACING ESTIMATION & CALCULATION
// ============================================================================

const estimateDistratoHeight = (socios, lineSpacing, spacingAfter) => {
  let height = 0;

  // Company block (nome, CNPJ, NIRE, empty line)
  height += lineSpacing * 3 + spacingAfter * 3;

  // Qualifications + preamble
  height += socios.length * (lineSpacing * 4 + spacingAfter);
  height += lineSpacing * 4 + spacingAfter; // Preamble text

  // 3 clauses (title + body each)
  height += (lineSpacing * 2 + spacingAfter * 2) * 3; // titles
  height += estimateTextHeight('X'.repeat(300), lineSpacing, spacingAfter) * 3; // bodies (est ~300 chars each)

  // Closing + date
  height += lineSpacing * 2 + spacingAfter * 2;

  // Signatures
  height += socios.length * (lineSpacing * 3 + spacingAfter);

  // Empty paragraphs between sections
  height += spacingAfter * 6;

  return height;
};

const calculateDistratoSpacing = (socios) => {
  const CONTENT_HEIGHT = getContentHeight();
  const baseHeight = estimateDistratoHeight(socios, BASE_LINE_SPACING, BASE_SPACING_AFTER);
  const numPages = Math.ceil(baseHeight / CONTENT_HEIGHT);
  const targetHeight = numPages * CONTENT_HEIGHT;
  const slack = targetHeight - baseHeight;

  let result = {
    marginTop: BASE_MARGIN_TOP,
    marginBottom: BASE_MARGIN_BOTTOM,
    lineSpacing: BASE_LINE_SPACING,
    spacingAfter: BASE_SPACING_AFTER
  };

  if (slack > CONTENT_HEIGHT * 0.15) {
    // Estimate paragraph and line counts for distribution
    const numParagraphs = 10 + socios.length * 2; // quals + clauses + closing + date + sigs
    const numLines = socios.length * 4 + 30; // rough line estimate

    const marginSlack = slack * 0.30;
    const lineSlack = slack * 0.30;
    const paraSlack = slack * 0.40;

    const extraMargin = Math.floor(marginSlack / (numPages * 2));
    result.marginTop = Math.min(BASE_MARGIN_TOP + extraMargin, 1200);
    result.marginBottom = Math.min(BASE_MARGIN_BOTTOM + extraMargin, 1100);

    const extraLineSpacing = Math.floor(lineSlack / numLines);
    result.lineSpacing = Math.min(BASE_LINE_SPACING + extraLineSpacing, 400);

    const extraParaSpacing = Math.floor(paraSlack / numParagraphs);
    result.spacingAfter = Math.min(BASE_SPACING_AFTER + extraParaSpacing, 350);

    console.log(`Distrato: ${baseHeight} twips, ${numPages} pages, slack: ${slack} twips`);
    console.log(`Adjustments: margins ${BASE_MARGIN_TOP}/${BASE_MARGIN_BOTTOM} -> ${result.marginTop}/${result.marginBottom}`);
    console.log(`             line spacing ${BASE_LINE_SPACING} -> ${result.lineSpacing}`);
    console.log(`             para spacing ${BASE_SPACING_AFTER} -> ${result.spacingAfter}`);
  } else {
    console.log(`Distrato: ${baseHeight} twips, ${numPages} pages, no adjustment needed`);
  }

  return result;
};

// ============================================================================
// MAIN DOCUMENT GENERATOR
// ============================================================================

const generateDistratoDocx = (data) => {
  const {
    empresa, socios, nire, juntaComercial, dataSessao,
    capitalSocial, objetoSocial,
    dataInicioAtividades, dataEncerramentoAtividades,
    liquidante, cidade
  } = data;

  // Calculate optimal spacing and apply to shared state
  const optimalSpacing = calculateDistratoSpacing(socios);
  setSpacing(optimalSpacing);
  const sp = getSpacing();

  // Company block
  const companyBlock = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, line: sp.lineSpacing, after: sp.spacingAfter },
      children: [boldText(`"${empresa.nome}"`)]
    }),
    centeredPara(normalText(`CNPJ: ${empresa.cnpj}`))
  ];
  if (nire) {
    companyBlock.push(centeredPara(normalText(`NIRE: ${nire}`)));
  }
  companyBlock.push(emptyPara());

  // Qualification + preamble
  const preambleParas = buildDistratoPreamble(socios, empresa, nire, juntaComercial, dataSessao);

  // Clauses
  const clausulaPrimeira = buildClausulaPrimeira(socios);
  const clausulaSegunda = buildClausulaSegunda(socios, objetoSocial, dataInicioAtividades);
  const clausulaTerceira = buildClausulaTerceira(socios, empresa, capitalSocial, dataInicioAtividades, dataEncerramentoAtividades, liquidante);

  // Closing
  const closing = buildDistratoClosing(socios);

  // Date
  const dateText = formatDistratoDate(cidade);
  const datePara = new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, line: sp.lineSpacing, after: sp.spacingAfter },
    keepNext: true,
    children: [normalText(dateText)]
  });

  // Signatures
  const signatureTable = buildSignatureTable(socios);

  // Assemble document
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: FONT, size: SIZE }
        }
      }
    },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
          margin: { top: sp.marginTop, right: 1134, bottom: sp.marginBottom, left: 1361, header: HEADER_HEIGHT, footer: FOOTER_HEIGHT }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 1 } },
            spacing: { after: 400 },
            children: [new TextRun({
              text: `DISTRATO SOCIAL DA EMPRESA: "${empresa.nome}"`,
              bold: true, font: FONT, size: SIZE
            })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SIZE })]
          })]
        })
      },
      children: [
        // Company block
        ...companyBlock,

        // Qualification + preamble
        ...preambleParas,
        emptyPara(),

        // Clausula Primeira
        ...clausulaPrimeira,
        emptyPara(),

        // Clausula Segunda
        ...clausulaSegunda,
        emptyPara(),

        // Clausula Terceira
        ...clausulaTerceira,
        emptyPara(),

        // Closing
        closing,

        // Date
        datePara,

        // Signatures
        signatureTable
      ]
    }]
  });

  return doc;
};

// ============================================================================
// CLI INTERFACE
// ============================================================================

const main = async () => {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.log('Usage: node generate-distrato.js <input.json> <output.docx>');
    console.log('');
    console.log('Input JSON should contain: empresa, socios, nire, juntaComercial, dataSessao,');
    console.log('  capitalSocial, objetoSocial, dataInicioAtividades, dataEncerramentoAtividades,');
    console.log('  liquidante, cidade');
    process.exit(1);
  }

  const [inputPath, outputPath] = args;

  try {
    const data = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
    const doc = generateDistratoDocx(data);
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(outputPath, buffer);
    console.log(`Distrato generated: ${outputPath}`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
};

// Run if called directly
if (require.main === module) {
  main();
}

// Export for use as module
module.exports = {
  generateDistratoDocx,
  buildDistratoPreamble,
  buildClausulaPrimeira,
  buildClausulaSegunda,
  buildClausulaTerceira,
  buildDistratoClosing,
  formatDistratoDate,
  estimateDistratoHeight,
  calculateDistratoSpacing
};
