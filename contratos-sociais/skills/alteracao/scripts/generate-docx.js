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
  // docx-js types
  Document, Packer, Paragraph, TextRun,
  Header, Footer, AlignmentType, PageNumber, BorderStyle,
  // Constants
  PAGE_HEIGHT, PAGE_WIDTH, HEADER_HEIGHT, FOOTER_HEIGHT, FONT, SIZE,
  // Spacing
  setSpacing, getSpacing, calculateOptimalSpacing,
  // Text helpers
  boldText, normalText, centeredPara, justifiedPara, clausulaTitulo, emptyPara,
  // Border helpers
  noBorder, thinBorder, noBorders,
  // Tables
  buildQuadroSocietario, buildSignatureTable,
  // Gender
  genero, isFeminino,
  // Qualification
  buildQualificacao,
  // Date
  formatDatePtBr
} = require('./docx-helpers');
const fs = require('fs');

// ============================================================================
// ALTERACAO-SPECIFIC: Title helper
// ============================================================================

const alteracaoTitulo = (children) => new Paragraph({
  alignment: AlignmentType.LEFT,
  spacing: { line: getSpacing().lineSpacing, after: getSpacing().spacingAfter },
  keepNext: true,
  children: Array.isArray(children) ? children : [children]
});

// ============================================================================
// ALTERACAO-SPECIFIC: Preamble (singular/plural aware)
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
// ALTERACAO-SPECIFIC: Closing (singular/plural aware)
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

  // Calculate optimal spacing and apply to shared state
  const optimalSpacing = calculateOptimalSpacing(clausulasConsolidadas, socios);
  setSpacing(optimalSpacing);
  const sp = getSpacing();

  const ordinal = versaoAlteracao === 1 ? '1ª' : `${versaoAlteracao}ª`;

  // Build company header (omit CNPJ line if empty)
  const companyHeader = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, line: sp.lineSpacing, after: sp.spacingAfter },
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
          spacing: { before: 200, line: sp.lineSpacing, after: sp.spacingAfter },
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
