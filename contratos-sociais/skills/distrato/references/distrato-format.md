# Formato do Distrato Social

Reference document format for distrato social (company dissolution).
Based on analysis of reference: DISTRATO BACO.pdf.

All output documents are in **Brazilian Portuguese**.

---

## 1. Document Structure (Assembly Order)

1. Page header (repeated on every page)
2. Company block (centered)
3. Partner qualification block(s) + preamble paragraph
4. Clausula Primeira — Settlement of haveres
5. Clausula Segunda — Quitacao and dissolution
6. Clausula Terceira — Liquidation responsibility
7. Closing paragraph
8. Date (centered)
9. Signature block

---

## 2. Page Header

Repeated on every page via document header. Bold, centered, with bottom border line.

```
DISTRATO SOCIAL DA EMPRESA: "[COMPANY NAME]"
```

Example:
```
DISTRATO SOCIAL DA EMPRESA: "BACO DIVINO COMÉRCIO DE BEBIDAS LTDA"
```

Note: Company name in quotes, ALL CAPS in the header text.

---

## 3. Company Block

Centered, bold. Three lines:

```
"[COMPANY NAME]"
CNPJ: XX.XXX.XXX/XXXX-XX
NIRE: XX.XXX.XXX.XXX
```

- Company name in quotes and bold+caps
- CNPJ with standard formatting
- NIRE if available (omit line if not available)

---

## 4. Qualification Block + Preamble

The qualification block and preamble form a SINGLE continuous paragraph (unlike alteracao which separates them). The partner qualification flows directly into the company description and dissolution declaration.

### Single Partner — Masculine

```
[NOME], [nacionalidade], [estado_civil], [profissao], natural da cidade de [naturalidade], nascido em [data_nascimento], [doc_identidade]: [numero], [orgao_emissor], e CPF: [cpf], residente e domiciliado na [endereco], único sócio da empresa "[EMPRESA]", sociedade empresária limitada com sede na [sede], com contrato social arquivado na Junta Comercial do Estado de [estado] – [junta] sob nº [nire], em sessão de [data_sessao], e devidamente inscrita no CNPJ: [cnpj], resolve de comum acordo e na melhor forma de direito proceder o encerramento das atividades da sociedade empresária limitada, de acordo com as cláusulas e condições seguintes:
```

### Single Partner — Feminine

```
[NOME], [nacionalidade], [estado_civil], [profissao], natural da cidade de [naturalidade], nascida em [data_nascimento], [doc_identidade]: [numero], [orgao_emissor], e CPF: [cpf], residente e domiciliada na [endereco], única sócia da empresa "[EMPRESA]", sociedade empresária limitada com sede na [sede], com contrato social arquivado na Junta Comercial do Estado de [estado] – [junta] sob nº [nire], em sessão de [data_sessao], e devidamente inscrita no CNPJ: [cnpj], resolve de comum acordo e na melhor forma de direito proceder o encerramento das atividades da sociedade empresária limitada, de acordo com as cláusulas e condições seguintes:
```

### Multiple Partners

Each partner qualification separated by semicolon, then shared preamble:

```
[NOME 1], [qualificacao completa 1], residente e domiciliado(a) na [endereco1];

[NOME 2], [qualificacao completa 2], residente e domiciliado(a) na [endereco2].

Os sócios acima qualificados, únicos sócios da empresa "[EMPRESA]", sociedade empresária limitada com sede na [sede], com contrato social arquivado na Junta Comercial do Estado de [estado] – [junta] sob nº [nire], em sessão de [data_sessao], e devidamente inscrita no CNPJ: [cnpj], resolvem de comum acordo e na melhor forma de direito proceder o encerramento das atividades da sociedade empresária limitada, de acordo com as cláusulas e condições seguintes:
```

### Key Differences from Alteracao Preamble

- Distrato single-partner: qualification + preamble in ONE paragraph (not separate)
- Distrato includes: naturalidade, data_nascimento, NIRE, session date, company sede
- Distrato text: "proceder o encerramento das atividades" (not "proceder à seguinte alteração")
- Distrato multi-partner: separate qualification blocks THEN shared preamble paragraph

### Gender-Aware Terms in Preamble

| Masculine | Feminine |
|-----------|----------|
| nascido | nascida |
| único sócio | única sócia |
| residente e domiciliado | residente e domiciliada |

### Singular/Plural Terms in Preamble

| Singular | Plural |
|----------|--------|
| resolve | resolvem |
| único sócio / única sócia | únicos sócios |

---

## 5. Clausula Primeira — Settlement of Haveres

Template for each partner's settlement. Single clause, listing all partners.

### Single Partner — Masculine

```
CLÁUSULA PRIMEIRA: O sócio [NOME], recebe por saldo de seus haveres na sociedade a importância de R$ [valor] ([extenso]), correspondente ao valor de seu capital de R$ [capital] ([extenso]),
```

### Single Partner — Feminine

```
CLÁUSULA PRIMEIRA: A sócia [NOME], recebe por saldo de seus haveres na sociedade a importância de R$ [valor] ([extenso]), correspondente ao valor de seu capital de R$ [capital] ([extenso]),
```

### Multiple Partners (single clause, all partners listed)

```
CLÁUSULA PRIMEIRA: Os sócios recebem por saldo de seus haveres na sociedade as seguintes importâncias: o sócio [NOME 1], recebe a importância de R$ [valor1] ([extenso1]), correspondente ao valor de seu capital de R$ [capital1] ([extenso1]); a sócia [NOME 2], recebe a importância de R$ [valor2] ([extenso2]), correspondente ao valor de seu capital de R$ [capital2] ([extenso2]),
```

### Gender-Aware Terms

| Masculine | Feminine |
|-----------|----------|
| O sócio | A sócia |
| o sócio | a sócia |

---

## 6. Clausula Segunda — Quitacao and Dissolution

### Single Partner — Masculine

```
CLÁUSULA SEGUNDA: O sócio dá entre si e a sociedade empresária limitada, da qual também recebe, geral, ampla e irrevogável quitação, para nada mais reclamar com fundamento no contrato social de constituição e no presente instrumento, declarando dissolvida para todos os efeitos, a empresa acima, a qual efetivamente encerrou suas atividades que consistia [objeto_social], tendo iniciado suas atividades em [data_inicio_atividades].
```

### Single Partner — Feminine

```
CLÁUSULA SEGUNDA: A sócia dá entre si e a sociedade empresária limitada, da qual também recebe, geral, ampla e irrevogável quitação, para nada mais reclamar com fundamento no contrato social de constituição e no presente instrumento, declarando dissolvida para todos os efeitos, a empresa acima, a qual efetivamente encerrou suas atividades que consistia [objeto_social], tendo iniciado suas atividades em [data_inicio_atividades].
```

### Multiple Partners

```
CLÁUSULA SEGUNDA: Os sócios dão entre si e a sociedade empresária limitada, da qual também recebem, geral, ampla e irrevogável quitação, para nada mais reclamar com fundamento no contrato social de constituição e no presente instrumento, declarando dissolvida para todos os efeitos, a empresa acima, a qual efetivamente encerrou suas atividades que consistia [objeto_social], tendo iniciado suas atividades em [data_inicio_atividades].
```

### Gender/Plural Terms

| Singular Masc | Singular Fem | Plural |
|---------------|--------------|--------|
| O sócio dá | A sócia dá | Os sócios dão |
| recebe | recebe | recebem |

---

## 7. Clausula Terceira — Liquidation Responsibility

### Single Partner — Masculine

```
CLÁUSULA TERCEIRA: A responsabilidade pela liquidação do Ativo e Passivo da sociedade, com sede [sede], que se dissolve pelo fato de não mais interessar ao sócio a exploração objeto do contrato social de constituição, tendo inicio de sua atividade em [data_inicio_atividades] e exercido suas atividades até [data_encerramento], ficará a cargo do sócio [NOME], a qual se compromete a manter em ao guarda os livros e documentos da sociedade, cujo capital social era de R$ [capital] ([extenso]).
```

### Single Partner — Feminine

```
CLÁUSULA TERCEIRA: A responsabilidade pela liquidação do Ativo e Passivo da sociedade, com sede [sede], que se dissolve pelo fato de não mais interessar à sócia a exploração objeto do contrato social de constituição, tendo inicio de sua atividade em [data_inicio_atividades] e exercido suas atividades até [data_encerramento], ficará a cargo da sócia [NOME], a qual se compromete a manter em ao guarda os livros e documentos da sociedade, cujo capital social era de R$ [capital] ([extenso]).
```

### Multiple Partners

```
CLÁUSULA TERCEIRA: A responsabilidade pela liquidação do Ativo e Passivo da sociedade, com sede [sede], que se dissolve pelo fato de não mais interessar aos sócios a exploração objeto do contrato social de constituição, tendo inicio de sua atividade em [data_inicio_atividades] e exercido suas atividades até [data_encerramento], ficará a cargo do sócio [NOME DO LIQUIDANTE], o qual se compromete a manter em sua guarda os livros e documentos da sociedade, cujo capital social era de R$ [capital] ([extenso]).
```

### Data Required (Ask User)

- `data_encerramento`: The date when activities ceased (e.g., "31/03/2026")
- `liquidante`: Which partner is responsible for liquidation (default: first partner, or ask user to choose)

### Gender/Plural Terms

| Singular Masc | Singular Fem | Plural |
|---------------|--------------|--------|
| ao sócio | à sócia | aos sócios |
| do sócio [NOME] | da sócia [NOME] | do sócio [NOME] (liquidante) |
| a qual (refers to responsibility) | a qual | o qual / a qual (depends on liquidante gender) |

---

## 8. Closing

### Single Partner — Masculine

```
E por estar assim justo e contratado, assina o presente ato em 1 (uma via) de igual teor e forma para que gere os efeitos de direito.
```

### Single Partner — Feminine

```
E por estar assim justa e contratada, assina o presente ato em 1 (uma via) de igual teor e forma para que gere os efeitos de direito.
```

### Multiple Partners

```
E por estarem assim justos e contratados, assinam o presente ato em 1 (uma via) de igual teor e forma para que gere os efeitos de direito.
```

### Key Differences from Alteracao Closing

- Distrato: "assina o presente **ato** em 1 (uma via) de igual teor e forma para que gere os efeitos de direito."
- Alteracao: "assina o presente **instrumento**."
- Distrato includes "1 (uma via)" (always 1 copy)
- Distrato adds "de igual teor e forma para que gere os efeitos de direito"

### Singular/Plural/Gender

| Singular Masc | Singular Fem | Plural |
|---------------|--------------|--------|
| justo e contratado | justa e contratada | justos e contratados |
| assina | assina | assinam |

---

## 9. Date

Centered, format: `[Cidade], [dia]º de [mes] de [ano].`

If day is 1, use ordinal: `1º`. Otherwise use cardinal: `02`, `15`, etc.

Example:
```
São Paulo, 1º de abril de 2026.
```

---

## 10. Signature Block

Same format as alteracao: single-column table, one signature per row.

```
________________________________
[NOME DO SÓCIO]
```

NOTE: Include CPF below the name for legal best practice.

---

## 11. Critical Rules (Same as Alteracao)

1. **VALUES BY EXTENSO**: Every monetary value must be followed by written form: `R$ 10.000,00 (dez mil reais)`
2. **GENDER AGREEMENT**: All gendered terms must match the partner
3. **SINGULAR/PLURAL**: Correct forms for single vs. multiple partners
4. **CPF/CNPJ FORMAT**: Standard punctuation: `XXX.XXX.XXX-XX` / `XX.XXX.XXX/XXXX-XX`
5. **ADDRESS NORMALIZATION**: Standard format: `Logradouro, número, complemento, Bairro, Cidade-UF, CEP: XX.XXX-XXX`
6. **DOCUMENT LANGUAGE**: Entire output in Brazilian Portuguese
7. **VERBATIM DATA**: Use exact data from contrato social JSON — no paraphrasing
