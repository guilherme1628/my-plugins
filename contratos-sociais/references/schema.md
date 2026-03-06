# Schema JSON -- Contrato Social / Alteracao Contratual

Schema padronizado para extracao estruturada de contratos sociais e alteracoes contratuais.

---

## Regras de Extracao

1. **Texto integral** -- Extrair todas as clausulas e paragrafos na integra. Nunca resumir, truncar ou usar `[...]`.
2. **Versao da alteracao** -- Identificar se e 1a, 2a, 3a alteracao etc.
3. **Redacao original** -- Na secao `alteracoes`, copiar o texto exatamente como consta no documento. Nao interpretar nem reformular.
4. **Quadro societario**:
   - Se for texto, extrair dados dos socios normalmente.
   - Se for imagem, tentar OCR. Se nao for possivel: `"quadro_societario": { "tipo": "imagem", "extraido": false }`.
5. **Resumo** -- Sempre incluir o objeto `resumo` com contagens e status de extracao.
6. **Formato** -- A saida DEVE ser JSON valido. Nenhum texto fora do JSON.

---

## Estrutura Completa

```json
{
  "resumo": { ... },
  "tipo_documento": "...",
  "versao_alteracao": "...",
  "contexto": "...",
  "empresa": { ... },
  "socios": [ ... ],
  "quadro_societario": { ... },
  "alteracoes": [ ... ],
  "contrato_consolidado": [ ... ],
  "assinatura": { ... }
}
```

---

## Campos -- Definicao Detalhada

### `resumo`

Contagens e indicadores de extracao. Sempre presente.

| Campo                        | Tipo    | Descricao                                      |
|------------------------------|---------|-------------------------------------------------|
| `qtd_clausulas`              | number  | Total de clausulas no contrato                  |
| `qtd_alteracoes`             | number  | Total de alteracoes feitas (0 se contrato novo) |
| `qtd_socios`                 | number  | Quantidade de socios identificados              |
| `quadro_societario_extraido` | boolean | `true` se extraido, `false` se nao              |

```json
"resumo": {
  "qtd_clausulas": 15,
  "qtd_alteracoes": 2,
  "qtd_socios": 3,
  "quadro_societario_extraido": true
}
```

---

### `tipo_documento`

| Valor                      | Quando usar                         |
|----------------------------|-------------------------------------|
| `"Contrato Social"`       | Documento original de constituicao  |
| `"Alteracao Contratual"`  | Qualquer alteracao ao contrato      |

---

### `versao_alteracao`

Identifica a ordem da alteracao. `null` se for contrato social original.

Valores validos: `"1a Alteracao"`, `"2a Alteracao"`, `"3a Alteracao"`, ..., ou `null`.

---

### `contexto`

Tipo: `string`

Descricao textual do motivo da alteracao contratual. Se nao aplicavel (contrato social original), usar string vazia `""`.

---

### `empresa`

| Campo      | Tipo   | Formato / Descricao                     |
|------------|--------|-----------------------------------------|
| `nome`     | string | Razao social completa                   |
| `cnpj`     | string | Formato: `XX.XXX.XXX/XXXX-XX`          |
| `endereco` | string | Endereco completo em texto livre        |

```json
"empresa": {
  "nome": "Empresa Exemplo Ltda",
  "cnpj": "12.345.678/0001-90",
  "endereco": "Rua Exemplo, 100, Centro, Cidade - UF, CEP 00000-000"
}
```

---

### `socios`

Array de objetos. Um objeto por socio identificado.

| Campo                   | Tipo   | Formato / Descricao                                                |
|-------------------------|--------|--------------------------------------------------------------------|
| `nome`                  | string | Nome completo do socio                                             |
| `cpf`                   | string | Formato: `XXX.XXX.XXX-XX`                                         |
| `nacionalidade`         | string | Ex: `"Brasileiro"`, `"Brasileira"`, `"Portugues"`                  |
| `estado_civil`          | string | Ex: `"Solteiro"`, `"Casado sob regime de comunhao parcial"`        |
| `profissao`             | string | Profissao declarada                                                |
| `data_nascimento`       | string | Formato: `DD/MM/AAAA`                                              |
| `documento_identidade`  | object | Ver sub-objeto abaixo                                              |
| `endereco`              | object | Ver sub-objeto abaixo                                              |
| `participacao`          | string | Ex: `"50%"`, `"1/3"`, valor em fracao ou percentual                |
| `cotas`                 | object | Ver sub-objeto abaixo                                              |

#### `socios[].documento_identidade`

| Campo           | Tipo   | Descricao                    |
|-----------------|--------|------------------------------|
| `rg`            | string | Numero do RG                 |
| `orgao_emissor` | string | Orgao emissor. Ex: `SSP/SP`  |

#### `socios[].endereco`

| Campo        | Tipo   | Descricao                          |
|--------------|--------|------------------------------------|
| `logradouro` | string | Rua, Avenida etc.                  |
| `numero`     | string | Numero do imovel                   |
| `bairro`     | string | Bairro                             |
| `cidade`     | string | Cidade                             |
| `estado`     | string | UF (2 letras). Ex: `SP`, `RJ`     |
| `cep`        | string | Formato: `XXXXX-XXX`              |

#### `socios[].cotas`

| Campo            | Tipo   | Descricao                             |
|------------------|--------|---------------------------------------|
| `quantidade`     | number | Numero inteiro de cotas               |
| `valor_unitario` | string | Valor com cifrao. Ex: `"R$1,00"`      |

```json
"socios": [
  {
    "nome": "Joao da Silva",
    "cpf": "123.456.789-00",
    "nacionalidade": "Brasileiro",
    "estado_civil": "Casado sob regime de comunhao parcial de bens",
    "profissao": "Empresario",
    "data_nascimento": "01/01/1980",
    "documento_identidade": {
      "rg": "12.345.678-9",
      "orgao_emissor": "SSP/SP"
    },
    "endereco": {
      "logradouro": "Rua das Flores",
      "numero": "100",
      "bairro": "Centro",
      "cidade": "Sao Paulo",
      "estado": "SP",
      "cep": "01000-000"
    },
    "participacao": "50%",
    "cotas": {
      "quantidade": 10000,
      "valor_unitario": "R$1,00"
    }
  }
]
```

---

### `quadro_societario`

Indica como o quadro societario foi obtido.

| Campo     | Tipo    | Valores                       | Descricao                                  |
|-----------|---------|-------------------------------|--------------------------------------------|
| `tipo`    | string  | `"texto"` ou `"imagem"`       | Formato do quadro no documento original    |
| `extraido`| boolean | `true` ou `false`             | Se os dados foram extraidos com sucesso    |

Combinacoes esperadas:

| Cenario                              | `tipo`     | `extraido` |
|--------------------------------------|------------|------------|
| Texto legivel, extracao ok           | `"texto"`  | `true`     |
| Imagem com OCR bem-sucedido         | `"imagem"` | `true`     |
| Imagem sem possibilidade de OCR     | `"imagem"` | `false`    |

---

### `alteracoes`

Array de objetos. Cada objeto representa uma alteracao feita ao contrato. Array vazio `[]` se for contrato social original.

| Campo              | Tipo   | Descricao                                                    |
|--------------------|--------|--------------------------------------------------------------|
| `ordem`            | number | Sequencia numerica (1, 2, 3...)                              |
| `categoria`        | string | Categoria da alteracao (ver valores validos abaixo)          |
| `clausula_alterada`| string | Titulo da clausula original que foi alterada                 |
| `texto_original`   | string | Texto INTEGRAL da alteracao, copiado ipsis litteris          |

**Categorias validas para `alteracoes[].categoria`:**

- `"Nome Empresarial"`
- `"Endereco"`
- `"Objeto Social"`
- `"Capital Social"`
- `"Quadro Societario"`
- `"Entrada de Socio"`
- `"Incorporacao"`
- `"Outra"`

```json
"alteracoes": [
  {
    "ordem": 1,
    "categoria": "Nome Empresarial",
    "clausula_alterada": "Clausula Primeira - Do Nome Empresarial",
    "texto_original": "A sociedade passara a adotar a denominacao social..."
  }
]
```

---

### `contrato_consolidado`

Array de objetos. Representa o contrato consolidado clausula por clausula.

| Campo            | Tipo   | Descricao                                              |
|------------------|--------|---------------------------------------------------------|
| `ordem`          | number | Sequencia numerica da clausula (1, 2, 3...)            |
| `titulo`         | string | Titulo da clausula                                     |
| `categoria`      | string | Categoria da clausula (ver valores validos abaixo)     |
| `texto_original` | string | Texto INTEGRAL da clausula                             |
| `paragrafos`     | array  | Lista de paragrafos da clausula                        |

**Categorias validas para `contrato_consolidado[].categoria`:**

- `"Nome Empresarial"`
- `"Objeto Social"`
- `"Capital Social"`
- `"Endereço"` / `"Sede"`
- `"Administração"`
- `"Outra"`

#### `contrato_consolidado[].paragrafos[]`

| Campo            | Tipo   | Descricao                                                        |
|------------------|--------|------------------------------------------------------------------|
| `ordem`          | string | `"unico"` se ha apenas um, senao `"1"`, `"2"`, `"3"` etc.      |
| `texto_original` | string | Texto integral do paragrafo                                      |

```json
"contrato_consolidado": [
  {
    "ordem": 1,
    "titulo": "Clausula Primeira - Do Nome Empresarial",
    "categoria": "Nome Empresarial",
    "texto_original": "A sociedade sera denominada Empresa Exemplo Ltda.",
    "paragrafos": [
      {
        "ordem": "unico",
        "texto_original": "Paragrafo unico. A sociedade podera utilizar o nome fantasia..."
      }
    ]
  }
]
```

---

### `assinatura`

| Campo    | Tipo   | Formato / Descricao              |
|----------|--------|----------------------------------|
| `cidade` | string | Cidade onde foi assinado         |
| `data`   | string | Formato: `DD/MM/AAAA`           |

```json
"assinatura": {
  "cidade": "Sao Paulo",
  "data": "15/03/2024"
}
```

---

## Checklist de Validacao

Antes de retornar o JSON, verificar:

- [ ] Todas as clausulas foram extraidas na integra (sem `[...]` ou resumos)
- [ ] Todos os paragrafos de cada clausula estao presentes
- [ ] O campo `resumo` reflete as contagens corretas
- [ ] Campos de CPF e CNPJ estao no formato com pontuacao
- [ ] Datas estao no formato `DD/MM/AAAA`
- [ ] CEP esta no formato `XXXXX-XXX`
- [ ] `versao_alteracao` esta preenchido corretamente ou `null`
- [ ] `quadro_societario` reflete o metodo real de extracao
- [ ] O JSON e valido (sem virgulas extras, sem campos faltantes)
