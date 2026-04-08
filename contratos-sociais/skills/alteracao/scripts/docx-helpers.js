#!/usr/bin/env node
/**
 * Shared DOCX helpers for contratos-sociais document generation.
 * Used by both generate-docx.js (alteracao) and generate-distrato.js (distrato).
 */

const {
  Document, Packer, Paragraph, TextRun,
  Header, Footer, AlignmentType, PageNumber, BorderStyle,
  Table, TableRow, TableCell, WidthType, TableLayoutType
} = require('docx');

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

// Mutable spacing state — set by setSpacing(), read by text helpers.
// Each generator calls setSpacing() before building paragraphs.
let MARGIN_TOP = BASE_MARGIN_TOP;
let MARGIN_BOTTOM = BASE_MARGIN_BOTTOM;
let LINE_SPACING = BASE_LINE_SPACING;
let SPACING_AFTER = BASE_SPACING_AFTER;

const setSpacing = (opts) => {
  MARGIN_TOP = opts.marginTop;
  MARGIN_BOTTOM = opts.marginBottom;
  LINE_SPACING = opts.lineSpacing;
  SPACING_AFTER = opts.spacingAfter;
};

const getSpacing = () => ({
  marginTop: MARGIN_TOP,
  marginBottom: MARGIN_BOTTOM,
  lineSpacing: LINE_SPACING,
  spacingAfter: SPACING_AFTER
});

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
// EXPORTS
// ============================================================================

module.exports = {
  // docx-js re-exports (so generators don't need to require('docx') directly)
  Document, Packer, Paragraph, TextRun,
  Header, Footer, AlignmentType, PageNumber, BorderStyle,
  Table, TableRow, TableCell, WidthType, TableLayoutType,

  // Constants
  PAGE_HEIGHT, PAGE_WIDTH, BASE_MARGIN_TOP, BASE_MARGIN_BOTTOM,
  HEADER_HEIGHT, FOOTER_HEIGHT, FONT, SIZE,
  BASE_LINE_SPACING, BASE_SPACING_AFTER, AVAILABLE_WIDTH,

  // Spacing state management
  setSpacing, getSpacing,

  // Functions
  formatDatePtBr,
  getContentHeight, estimateTextHeight, estimateDocumentHeight,
  calculateOptimalSpacing,
  boldText, normalText, centeredPara, justifiedPara, clausulaTitulo, emptyPara,
  noBorder, thinBorder, noBorders,
  buildQuadroSocietario, createSignatureBlock, buildSignatureTable,
  genero, isFeminino, buildQualificacao
};
