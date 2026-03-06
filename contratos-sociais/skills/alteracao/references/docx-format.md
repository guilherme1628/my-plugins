# Formato DOCX -- Alteracao Contratual

Especificacao de formatacao para geracao de documentos Word (.docx) de alteracoes contratuais.
Baseado em analise de documentos reais do acervo.

---

## 1. Configuracao Geral do Documento

### Pagina (A4)
```javascript
// Dimensoes base (podem ser ajustadas dinamicamente)
const BASE_MARGIN_TOP = 902;
const BASE_MARGIN_BOTTOM = 851;

page: {
  size: { width: 11907, height: 16840 },  // A4 em twips
  margin: { top: MARGIN_TOP, right: 1134, bottom: MARGIN_BOTTOM, left: 1361, header: 567, footer: 907 }
}
```

### Ajuste Dinamico de Espacamento
O documento calcula automaticamente ajustes para evitar paginas com muito espaco vazio:
- Estima altura total do conteudo
- Calcula "slack" (espaco sobrando nas paginas)
- Distribui ajuste entre: **margens (30%)**, **espacamento de linha (30%)**, **espacamento de paragrafo (40%)**

```javascript
// Exemplo de ajuste calculado:
// Margins: 902/851 -> 1118/1067
// Line spacing: 324 -> 344
// Para spacing: 200 -> 255
```

### Tipografia
| Elemento | Fonte | Tamanho | Estilo |
|----------|-------|---------|--------|
| Corpo | Arial | 12pt (sz=24) | Normal |
| Nomes de socios | Arial | 12pt | **Negrito** |
| Titulos de clausulas | Arial | 12pt | **Negrito** |
| Nome da empresa | Arial | 12pt | **Negrito** |
| Cabecalho | Arial | 12pt | **Negrito**, Centralizado |

### Espacamento
```javascript
spacing: {
  line: 324,      // 1.35 linhas
  after: 200      // ~3.5mm apos paragrafo
}
```

### Alinhamento
- **Titulos e cabecalhos**: Centralizado (`AlignmentType.CENTER`)
- **Titulos de alteracoes** (I, II, III...): Esquerda (`AlignmentType.LEFT`)
- **Corpo do texto**: Justificado (`AlignmentType.BOTH`)
- **Quadro societario**: Ver tabela especifica
- **Assinaturas**: Ver tabela especifica

### Controle de Paginacao
Para evitar elementos orfaos (titulo em uma pagina, conteudo em outra):

```javascript
// Titulo de clausula - manter junto com proximo paragrafo
new Paragraph({
  keepNext: true,  // IMPORTANTE: evita titulo orfao
  children: [boldText("Cláusula Primeira")]
})

// Bloco de assinaturas - manter todas juntas na mesma pagina
// Usar keepLines na tabela e keepNext no paragrafo anterior
```

---

## 2. Cabecalho e Rodape

### Cabecalho (Header)
Contem o titulo do documento com linha inferior e margem inferior para separar do conteudo:

```javascript
new Header({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 1 } },
    spacing: { after: 400 },  // Margem inferior do header para separar do conteudo
    children: [new TextRun({
      text: "Xª ALTERAÇÃO CONTRATUAL: [NOME DA EMPRESA]",
      bold: true, font: "Arial", size: 24
    })]
  })]
})
```

**Importante**: O primeiro paragrafo do documento deve ter `spacing: { before: 200 }` para garantir separacao visual do header.

### Rodape (Footer)
Numero da pagina alinhado a direita:

```javascript
new Footer({
  children: [new Paragraph({
    alignment: AlignmentType.RIGHT,
    children: [new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 24 })]
  })]
})
```

---

## 3. Tabela -- Quadro Societario

Usada para exibir a distribuicao de quotas entre os socios.

### Estrutura
- **4 colunas**: SÓCIO | % | QUOTAS | VALOR
- **Larguras** (definidas via `columnWidths` no nivel da tabela):
  - Coluna SÓCIO: 3450 DXA (preenche espaco restante)
  - Coluna %: 1255 DXA
  - Coluna QUOTAS: 2353 DXA
  - Coluna VALOR: 2347 DXA
  - **Total: 9405 DXA** (cabe na largura disponivel da pagina)
- **Layout**: `TableLayoutType.FIXED` (obrigatorio para respeitar larguras)
- **Bordas da tabela**: Minimalista (sem bordas internas)
- **Bordas das celulas**:
  - Linha de cabecalho: bordas externas completas (top, bottom, left na 1a celula, right na ultima)
  - Linhas de dados: SEM bordas
  - Linha TOTAL: apenas borda superior

### Formatacao das celulas
| Coluna | Alinhamento | Cabecalho | Dados | TOTAL |
|--------|-------------|-----------|-------|-------|
| SÓCIO | Esquerda | Negrito, Centro | Normal | Negrito |
| % | Centro | Negrito | Normal | Negrito |
| QUOTAS | Centro | Negrito | Normal | Negrito |
| VALOR | Direita | Negrito | Normal | Negrito |

### Codigo de referencia
```javascript
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const thinBorder = { style: BorderStyle.SINGLE, size: 2, color: "000000" };

// Larguras das colunas (definidas no nivel da tabela via columnWidths)
// Total deve caber na largura disponivel: pagina (11907) - margens (1361+1134) = ~9412 DXA
const AVAILABLE_WIDTH = 9405;
const OTHER_COLS_WIDTH = 1255 + 2353 + 2347;  // %, QUOTAS, VALOR
const colWidths = [AVAILABLE_WIDTH - OTHER_COLS_WIDTH, 1255, 2353, 2347];  // [3450, 1255, 2353, 2347]

// Criar tabela com columnWidths no nivel da tabela
new Table({
  columnWidths: colWidths,  // [3450, 1255, 2353, 2347] - define tblGrid
  layout: TableLayoutType.FIXED,  // Obrigatorio para respeitar larguras
  rows: [headerRow, ...dataRows, totalRow]
});

// Linha de cabecalho (bordas externas apenas, SEM width nas celulas)
new TableRow({
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

// Linhas de dados (SEM bordas)
new TableRow({
  children: [
    new TableCell({
      borders: noBorders,
      children: [new Paragraph({ alignment: AlignmentType.LEFT, children: [normalText(nome)] })]
    }),
    new TableCell({
      borders: noBorders,
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [normalText(percentual)] })]
    }),
    new TableCell({
      borders: noBorders,
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [normalText(quotas)] })]
    }),
    new TableCell({
      borders: noBorders,
      children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [normalText(valor)] })]
    })
  ]
});

// Linha TOTAL (apenas borda superior)
new TableRow({
  children: [
    new TableCell({
      borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder },
      children: [new Paragraph({ children: [boldText("TOTAL")] })]
    }),
    new TableCell({
      borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder },
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [boldText("100%")] })]
    }),
    new TableCell({
      borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder },
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [boldText(totalQuotas)] })]
    }),
    new TableCell({
      borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder },
      children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [boldText(totalValor)] })]
    })
  ]
});
```

---

## 4. Tabela -- Bloco de Assinaturas

Usada para organizar as assinaturas em coluna unica.

### Estrutura
- **1 coluna** (layout vertical, mais compacto)
- **Largura**: 9405 DXA (largura total disponivel)
- **Bordas**: Nenhuma (tabela invisivel)
- **Alinhamento**: Centralizado
- **Altura das linhas**: Ajustada ao conteudo

### Seguranca contra Adulteracao
Para evitar que assinaturas fiquem sozinhas em pagina em branco (risco de insercao de paginas):
1. A **ultima clausula** tem `keepNext: true` em todos os paragrafos
2. O paragrafo de encerramento tem `keepNext: true`
3. O paragrafo de local/data tem `keepNext: true`
4. A **primeira assinatura** tem `keepNext: true` (fica com a data)
5. Demais assinaturas podem fluir para proxima pagina

Isso garante que sempre haja conteudo de clausula na mesma pagina das assinaturas.

### Data do Documento
Usar a data de geracao formatada em portugues:
```javascript
const formatDatePtBr = (date = new Date()) => {
  const months = ['janeiro', 'fevereiro', 'março', ...];
  return `${day} de ${month} de ${year}`;
};

// Resultado: "São Paulo-SP, 02 de fevereiro de 2026."
```

### Estrutura de cada assinatura
Cada assinatura e um bloco compacto em uma unica celula:
1. Linha de assinatura: `________________________________`
2. Nome do socio: **NEGRITO**
3. CPF e informacoes adicionais

### Codigo de referencia
```javascript
// Helper para criar bloco de assinatura
// Primeira assinatura: keepNext em tudo (fica com data)
// Outras: apenas keepNext interno (podem fluir entre paginas)
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
    keepNext: isFirst,  // Primeira assinatura mantem com proxima
    children: [normalText(`CPF: ${s.cpf}`)]
  })
];

// Layout coluna unica: uma assinatura por linha
const buildSignatureTable = () => {
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
```

**Importante**: Cada assinatura e um bloco compacto em uma unica celula. Nao usar linhas separadas para underscore, nome e CPF -- isso cria espacamento excessivo.

### Ordem de assinaturas
1. Socios PJ (com representantes legais)
2. Socios PF administradores
3. Socios PF nao-administradores
4. Socios retirantes (com indicacao `(Sócio Retirante)`)

---

## 5. Elementos de Texto

### Funcoes auxiliares padrao
```javascript
const FONT = "Arial";
const SIZE = 24;  // 12pt em half-points
const LINE_SPACING = 324;
const SPACING_AFTER = 200;

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
  keepNext: opts.keepNext || false,  // Para manter com proximo paragrafo
  keepLines: opts.keepLines || false,
  children: Array.isArray(children) ? children : [children]
});

// Titulo de clausula - SEMPRE manter com proximo paragrafo
const clausulaTitulo = (children) => new Paragraph({
  alignment: AlignmentType.LEFT,  // Alinhado a esquerda
  spacing: { line: LINE_SPACING, after: SPACING_AFTER },
  keepNext: true,  // IMPORTANTE: evita titulo orfao
  children: Array.isArray(children) ? children : [children]
});

// Titulo de alteracao (I, II, III...) - alinhado a esquerda
const alteracaoTitulo = (children) => new Paragraph({
  alignment: AlignmentType.LEFT,  // NAO centralizado
  spacing: { line: LINE_SPACING, after: SPACING_AFTER },
  keepNext: true,  // Manter com conteudo
  children: Array.isArray(children) ? children : [children]
});

const emptyPara = () => new Paragraph({ spacing: { after: SPACING_AFTER }, children: [] });
```

### Formatacao de nomes
Nomes de socios e empresas devem ser destacados em negrito dentro do texto corrido:

```javascript
justifiedPara([
  boldText("NOME DO SÓCIO"),
  normalText(", brasileiro, empresário, casado, portador da carteira de identidade nº ..."),
])
```

---

## 6. Dependencias (docx-js)

```javascript
const {
  Document, Packer, Paragraph, TextRun,
  Header, Footer, AlignmentType, PageNumber, BorderStyle,
  Table, TableRow, TableCell, WidthType, VerticalAlign
} = require('docx');
```

Instalacao: `npm install docx`

---

## 7. Secao de Consolidacao

A secao de consolidacao do contrato segue este formato:

### Texto de transicao (ANTES do titulo)
```
Diante das alterações acima, o Contrato Social passa a ter a seguinte redação:
```

### Titulo da consolidacao
```
CONTRATO SOCIAL CONSOLIDADO
```
**IMPORTANTE**: Usar "CONTRATO SOCIAL CONSOLIDADO" (nao "Consolidacao do Contrato Social").

### Exemplo completo
```javascript
// Texto de transicao
justifiedPara([
  normalText("Diante das alterações acima, o Contrato Social passa a ter a seguinte redação:")
]),
emptyPara(),

// Titulo da consolidacao
centeredPara(boldText("CONTRATO SOCIAL CONSOLIDADO"), true),
emptyPara(),

// Clausulas consolidadas...
```

---

## 8. Geracao do Documento

```javascript
const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: SIZE } } } },
  sections: [{
    properties: { page: { margin: {...}, size: {...} } },
    headers: { default: new Header({...}) },
    footers: { default: new Footer({...}) },
    children: [
      // Cabecalho da empresa (com spacing.before para separar do header)
      // Titulo (Xª ALTERAÇÃO CONTRATUAL)
      // Qualificacao dos socios
      // Preambulo

      // Clausulas de alteracao (I, II, III...) - usar alteracaoTitulo() para titulos
      alteracaoTitulo([boldText("I – Da Alteração da Administração")]),
      justifiedPara([...]),

      // Clausula "Ficam inalteradas..."
      // Texto de transicao ("Diante das alterações acima...")
      // Titulo "CONTRATO SOCIAL CONSOLIDADO"

      // Clausulas consolidadas - usar clausulaTitulo() para titulos
      clausulaTitulo([boldText("Cláusula Primeira")]),  // keepNext: true automatico
      justifiedPara([...]),

      // Quadro societario (TABELA - largura dinamica na 1a coluna)

      // Encerramento - MANTER COM ASSINATURAS
      justifiedPara([normalText("E, por estarem assim justos...")], { keepNext: true }),
      emptyPara(),
      centeredParaKeepNext(normalText("São Paulo-SP, ___ de ___")),  // keepNext: true
      emptyPara(),

      // Assinaturas (TABELA - com keepLines/keepNext em cada paragrafo)
      buildSignatureTable()
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("documento.docx", buffer);
});
```

### Helpers adicionais para paginacao
```javascript
// Paragrafo centralizado que mantem com proximo (para local/data antes de assinaturas)
const centeredParaKeepNext = (children) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { line: LINE_SPACING, after: SPACING_AFTER },
  keepNext: true,
  children: Array.isArray(children) ? children : [children]
});
```
