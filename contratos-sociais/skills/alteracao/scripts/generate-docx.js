#!/usr/bin/env node
/**
 * Generate Alteração Contratual DOCX
 *
 * Usage:
 *   node generate-docx.js <input.json> <output.docx>
 *
 * Input JSON should contain:
 *   - empresa: { nome, cnpj, endereco }
 *   - socios: [{ nome, cpf, nacionalidade, estado_civil, profissao, rg, orgao_emissor, endereco, quotas, valor, percentual, isAdmin }]
 *   - alteracoes: [{ titulo, texto }]  // Numbered alteration clauses (I, II, III...)
 *   - clausulasConsolidadas: [{ titulo, texto, paragrafos, hasQuadro }]
 *   - versaoAlteracao: number (e.g., 1 for "1ª ALTERAÇÃO")
 *   - cidade: string (e.g., "São Paulo-SP")
 */

const {
  Document, Packer, Paragraph, TextRun,
  Header, Footer, AlignmentType, PageNumber, BorderStyle,
  Table, TableRow, TableCell, WidthType, TableLayoutType
} = require('docx');
const fs = require('fs');

// ============================================================================
// DATE FORMATTING
// ============================================================================

const formatDatePtBr = (date = new Date()) => {
  const months = [
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
  ];
  const day = date.getDate().toString().padStart(2, '0');
  const month = months[date.getMonth()];
  const year = date.getFullYear();
  return `${day} de ${month} de ${year}`;
};

// ============================================================================
// PAGE DIMENSIONS (A4 in twips)
// ============================================================================

const PAGE_HEIGHT = 16840;
const PAGE_WIDTH = 11907;

const BASE_MARGIN_TOP = 902;
const BASE_MARGIN_BOTTOM = 851;
const HEADER_HEIGHT = 567;
const FOOTER_HEIGHT = 907;

const FONT = "Arial";
const SIZE = 24; // 12pt in half-points

const BASE_LINE_SPACING = 324;  // 1.35 line spacing
const BASE_SPACING_AFTER = 200;

// Dynamic spacing (adjusted per document)
let MARGIN_TOP = BASE_MARGIN_TOP;
let MARGIN_BOTTOM = BASE_MARGIN_BOTTOM;
let LINE_SPACING = BASE_LINE_SPACING;
let SPACING_AFTER = BASE_SPACING_AFTER;

// ============================================================================
// SPACING CALCULATION
// ============================================================================

const getContentHeight = () => PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM - HEADER_HEIGHT - FOOTER_HEIGHT;

const CHARS_PER_LINE = 80;

const estimateTextHeight = (text, lineSpacing = BASE_LINE_SPACING, spacingAfter = BASE_SPACING_AFTER) => {
  const lines = Math.ceil(text.length / CHARS_PER_LINE);
  return (lines * lineSpacing) + spacingAfter;
};

const estimateDocumentHeight = (clausulas, socios, lineSpacing, spacingAfter) => {
  let height = 0;
  height += lineSpacing * 4 + spacingAfter * 4; // Header area
  height += socios.length * (lineSpacing * 3 + spacingAfter); // Qualifications
  height += lineSpacing * 4 + spacingAfter; // Preamble
  height += lineSpacing * 6 + spacingAfter * 3; // Alteration clauses
  height += lineSpacing * 4 + spacingAfter * 4; // Transition + title

  for (const c of clausulas) {
    height += estimateTextHeight(c.titulo, lineSpacing, spacingAfter);
    height += estimateTextHeight(c.texto, lineSpacing, spacingAfter);
    for (const p of (c.paragrafos || [])) {
      height += estimateTextHeight(p, lineSpacing, spacingAfter);
    }
    if (c.hasQuadro) {
      height += lineSpacing * (socios.length + 3) + spacingAfter * 2;
    }
    height += spacingAfter;
  }

  height += lineSpacing * 2 + spacingAfter * 2; // Closing + date
  height += socios.length * (lineSpacing * 3 + spacingAfter); // Signatures

  return height;
};

const calculateOptimalSpacing = (clausulas, socios) => {
  const CONTENT_HEIGHT = getContentHeight();
  const baseHeight = estimateDocumentHeight(clausulas, socios, BASE_LINE_SPACING, BASE_SPACING_AFTER);
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
    let numParagraphs = 10 + socios.length;
    let numLines = 0;
    for (const c of clausulas) {
      numParagraphs += 2 + (c.paragrafos || []).length;
      numLines += Math.ceil(c.texto.length / CHARS_PER_LINE);
      for (const p of (c.paragrafos || [])) {
        numLines += Math.ceil(p.length / CHARS_PER_LINE);
      }
    }
    numParagraphs += socios.length;
    numLines += socios.length * 3 + 20;

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

    console.log(`Document: ${baseHeight} twips, ${numPages} pages, slack: ${slack} twips`);
    console.log(`Adjustments: margins ${BASE_MARGIN_TOP}/${BASE_MARGIN_BOTTOM} -> ${result.marginTop}/${result.marginBottom}`);
    console.log(`             line spacing ${BASE_LINE_SPACING} -> ${result.lineSpacing}`);
    console.log(`             para spacing ${BASE_SPACING_AFTER} -> ${result.spacingAfter}`);
  } else {
    console.log(`Document: ${baseHeight} twips, ${numPages} pages, no adjustment needed`);
  }

  return result;
};

// ============================================================================
// TEXT HELPERS
// ============================================================================

const boldText = (text) => new TextRun({ text, bold: true, font: FONT, size: SIZE });
const normalText = (text) => new TextRun({ text, font: FONT, size: SIZE });

const centeredPara = (children, extraSpacing = false) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { line: LINE_SPACING, after: extraSpacing ? 400 : SPACING_AFTER },
  children: Array.isArray(children) ? children : [children]
});

const justifiedPara = (children, opts = {}) => new Paragraph({
  alignment: AlignmentType.BOTH,
  spacing: { line: LINE_SPACING, after: SPACING_AFTER },
  keepNext: opts.keepNext || false,
  keepLines: opts.keepLines || false,
  children: Array.isArray(children) ? children : [children]
});

const clausulaTitulo = (children) => new Paragraph({
  alignment: AlignmentType.LEFT,
  spacing: { line: LINE_SPACING, after: SPACING_AFTER },
  keepNext: true,
  children: Array.isArray(children) ? children : [children]
});

const alteracaoTitulo = (children) => new Paragraph({
  alignment: AlignmentType.LEFT,
  spacing: { line: LINE_SPACING, after: SPACING_AFTER },
  keepNext: true,
  children: Array.isArray(children) ? children : [children]
});

const emptyPara = () => new Paragraph({ spacing: { after: SPACING_AFTER }, children: [] });

// ============================================================================
// BORDER HELPERS
// ============================================================================

const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const thinBorder = { style: BorderStyle.SINGLE, size: 2, color: "000000" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// ============================================================================
// TABLE BUILDERS
// ============================================================================

const AVAILABLE_WIDTH = 9405;
const OTHER_COLS_WIDTH = 1255 + 2353 + 2347;

const buildQuadroSocietario = (socios) => {
  const nameColumnWidth = AVAILABLE_WIDTH - OTHER_COLS_WIDTH;
  const colWidths = [nameColumnWidth, 1255, 2353, 2347];

  const headerRow = new TableRow({
    children: [
      new TableCell({
        borders: { top: thinBorder, bottom: thinBorder, left: thinBorder, right: noBorder },
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [boldText("SÓCIO")] })]
      }),
      new TableCell({
        borders: { top: thinBorder, bottom: thinBorder, left: noBorder, right: noBorder },
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [boldText("%")] })]
      }),
      new TableCell({
        borders: { top: thinBorder, bottom: thinBorder, left: noBorder, right: noBorder },
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [boldText("QUOTAS")] })]
      }),
      new TableCell({
        borders: { top: thinBorder, bottom: thinBorder, left: noBorder, right: thinBorder },
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [boldText("VALOR")] })]
      })
    ]
  });

  const dataRows = socios.map(s => new TableRow({
    children: [
      new TableCell({ borders: noBorders, children: [new Paragraph({ alignment: AlignmentType.LEFT, children: [normalText(s.nome)] })] }),
      new TableCell({ borders: noBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [normalText(s.percentual)] })] }),
      new TableCell({ borders: noBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [normalText(s.quotas.toLocaleString('pt-BR'))] })] }),
      new TableCell({ borders: noBorders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [normalText(s.valor)] })] })
    ]
  }));

  const totalQuotas = socios.reduce((sum, s) => sum + s.quotas, 0);
  const totalValor = socios.reduce((sum, s) => sum + parseFloat(s.valor.replace(/[^\d,]/g, '').replace(',', '.')), 0);

  const totalRow = new TableRow({
    children: [
      new TableCell({ borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder }, children: [new Paragraph({ alignment: AlignmentType.LEFT, children: [boldText("TOTAL")] })] }),
      new TableCell({ borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [boldText("100%")] })] }),
      new TableCell({ borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [boldText(totalQuotas.toLocaleString('pt-BR'))] })] }),
      new TableCell({ borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [boldText(`R$ ${totalValor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`)] })] })
    ]
  });

  return new Table({
    columnWidths: colWidths,
    layout: TableLayoutType.FIXED,
    rows: [headerRow, ...dataRows, totalRow]
  });
};

const createSignatureBlock = (s, isFirst) => [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: isFirst ? 400 : 300, after: 0 },
    keepNext: true,
    children: [normalText("________________________________")]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 0 },
    keepNext: true,
    children: [boldText(s.nome.toUpperCase())]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    keepNext: isFirst,
    children: [normalText(`CPF: ${s.cpf}`)]
  })
];

const buildSignatureTable = (socios) => {
  const rows = socios.map((s, idx) => new TableRow({
    children: [
      new TableCell({
        width: { size: 9405, type: WidthType.DXA },
        borders: noBorders,
        children: createSignatureBlock(s, idx === 0)
      })
    ]
  }));

  return new Table({
    columnWidths: [9405],
    layout: TableLayoutType.FIXED,
    rows
  });
};

// ============================================================================
// GENDER & SINGULAR/PLURAL HELPERS
// ============================================================================

const genero = (socio, masc, fem) => {
  const feminino = socio.nacionalidade.endsWith('a');
  return feminino ? fem : masc;
};

const isFeminino = (socio) => socio.nacionalidade.endsWith('a');

// ============================================================================
// QUALIFICATION BUILDER
// ============================================================================

const buildQualificacao = (socio, isLast) => {
  const g = (m, f) => genero(socio, m, f);
  const ending = isLast ? '.' : ';';
  return [
    boldText(socio.nome.toUpperCase()),
    normalText(`, ${socio.nacionalidade}, ${socio.profissao}, ${socio.estado_civil}, ${g('portador', 'portadora')} da carteira de identidade nº ${socio.rg}, expedida pela ${socio.orgao_emissor}, ${g('inscrito', 'inscrita')} no CPF sob o nº ${socio.cpf}, ${g('residente e domiciliado', 'residente e domiciliada')} na ${socio.endereco}${ending}`)
  ];
};

// ============================================================================
// PREAMBLE BUILDER (singular/plural aware)
// ============================================================================

const buildPreamble = (socios, empresa) => {
  const isSingle = socios.length === 1;
  const fem = isFeminino(socios[0]);

  if (isSingle) {
    const qualificador = fem ? 'qualificada' : 'qualificado';
    const unico = fem ? 'única sócia' : 'único sócio';
    return justifiedPara([
      normalText(`Acima ${qualificador}, ${unico} da empresa `),
      boldText(empresa.nome),
      normalText(`, inscrita no CNPJ sob o nº ${empresa.cnpj}, com sede na ${empresa.endereco}, neste ato e na melhor forma de direito, resolve proceder à seguinte alteração no contrato social da empresa:`)
    ]);
  } else {
    return justifiedPara([
      normalText(`Os sócios acima qualificados, únicos sócios da empresa `),
      boldText(empresa.nome),
      normalText(`, inscrita no CNPJ sob o nº ${empresa.cnpj}, com sede na ${empresa.endereco}, neste ato e na melhor forma de direito, resolvem, de comum acordo, proceder à seguinte alteração no contrato social da empresa:`)
    ]);
  }
};

// ============================================================================
// CLOSING BUILDER (singular/plural aware)
// ============================================================================

const buildClosing = (socios) => {
  const isSingle = socios.length === 1;
  if (isSingle) {
    return justifiedPara([
      normalText(`E, por estar assim justo e contratado, assina o presente instrumento.`)
    ], { keepNext: true });
  } else {
    return justifiedPara([
      normalText(`E, por estarem assim justos e contratados, assinam o presente instrumento.`)
    ], { keepNext: true });
  }
};

// ============================================================================
// DOCUMENT GENERATOR
// ============================================================================

const generateAlteracaoDocx = (data) => {
  const { empresa, socios, alteracoes, clausulasConsolidadas, versaoAlteracao, cidade } = data;

  // Calculate optimal spacing
  const optimalSpacing = calculateOptimalSpacing(clausulasConsolidadas, socios);
  MARGIN_TOP = optimalSpacing.marginTop;
  MARGIN_BOTTOM = optimalSpacing.marginBottom;
  LINE_SPACING = optimalSpacing.lineSpacing;
  SPACING_AFTER = optimalSpacing.spacingAfter;

  const ordinal = versaoAlteracao === 1 ? '1ª' : `${versaoAlteracao}ª`;

  // Build company header (omit CNPJ line if empty)
  const companyHeader = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, line: LINE_SPACING, after: SPACING_AFTER },
      children: [boldText(empresa.nome)]
    })
  ];
  if (empresa.cnpj) {
    companyHeader.push(centeredPara(normalText(`CNPJ: ${empresa.cnpj}`)));
  }
  companyHeader.push(emptyPara());

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
          margin: { top: MARGIN_TOP, right: 1134, bottom: MARGIN_BOTTOM, left: 1361, header: HEADER_HEIGHT, footer: FOOTER_HEIGHT }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 1 } },
            spacing: { after: 400 },
            children: [new TextRun({
              text: `${ordinal} ALTERAÇÃO CONTRATUAL: ${empresa.nome}`,
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
        // Company header
        ...companyHeader,

        // Document title
        centeredPara(boldText(`${ordinal} ALTERAÇÃO CONTRATUAL`), true),
        emptyPara(),

        // Partner qualifications (last one ends with period, others with semicolon)
        ...socios.map((s, idx) => justifiedPara(buildQualificacao(s, idx === socios.length - 1))),
        emptyPara(),

        // Preamble (singular/plural aware)
        buildPreamble(socios, empresa),
        emptyPara(),

        // Alteration clauses
        ...alteracoes.flatMap(a => [
          alteracaoTitulo([boldText(a.titulo)]),
          justifiedPara([normalText(a.texto)]),
          emptyPara()
        ]),

        // Unchanged clauses statement
        justifiedPara([normalText("Ficam inalteradas as demais cláusulas e condições do contrato social.")]),
        emptyPara(),

        // Transition text
        justifiedPara([normalText("Diante das alterações acima, o Contrato Social passa a ter a seguinte redação:")]),
        emptyPara(),

        // Consolidated title
        centeredPara(boldText("CONTRATO SOCIAL CONSOLIDADO"), true),
        emptyPara(),

        // All consolidated clauses (last clause has keepNext for security)
        ...clausulasConsolidadas.flatMap((c, idx) => {
          const isLastClause = idx === clausulasConsolidadas.length - 1;
          const items = [
            clausulaTitulo([boldText(c.titulo)]),
            justifiedPara([normalText(c.texto)], { keepNext: isLastClause })
          ];
          if (c.hasQuadro) {
            items.push(emptyPara());
            items.push(buildQuadroSocietario(socios));
            items.push(emptyPara());
          }
          const paragrafos = c.paragrafos || [];
          for (let i = 0; i < paragrafos.length; i++) {
            const isLastPara = isLastClause && i === paragrafos.length - 1;
            items.push(justifiedPara([normalText(paragrafos[i])], { keepNext: isLastPara }));
          }
          if (!isLastClause) {
            items.push(emptyPara());
          }
          return items;
        }),

        // Closing (singular/plural aware, keepNext chain for security)
        buildClosing(socios),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 200, line: LINE_SPACING, after: SPACING_AFTER },
          keepNext: true,
          children: [normalText(`${cidade}, ${formatDatePtBr()}.`)]
        }),

        // Signatures
        buildSignatureTable(socios)
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
    console.log('Usage: node generate-docx.js <input.json> <output.docx>');
    console.log('');
    console.log('Input JSON should contain: empresa, socios, alteracoes, clausulasConsolidadas, versaoAlteracao, cidade');
    process.exit(1);
  }

  const [inputPath, outputPath] = args;

  try {
    const data = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
    const doc = generateAlteracaoDocx(data);
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(outputPath, buffer);
    console.log(`Document generated: ${outputPath}`);
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
module.exports = { generateAlteracaoDocx, formatDatePtBr };
