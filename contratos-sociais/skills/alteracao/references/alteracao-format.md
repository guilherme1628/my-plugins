# Formato Padrao -- Alteracao Contratual

Documento de referencia para geracao de alteracoes contratuais de sociedades limitadas brasileiras.
Padroes extraidos de documentos reais do acervo.

---

## 1. Estrutura Geral do Documento

Uma alteracao contratual segue a seguinte ordem fixa:

1. Cabecalho (nome da empresa, CNPJ, NIRE)
2. Titulo do documento (Xª Alteracao Contratual)
3. Bloco de qualificacao dos socios
4. Preambulo (deliberacao dos socios)
5. Clausulas de alteracao (numeradas com algarismos romanos)
6. Clausula de consolidacao (contrato consolidado)
7. Bloco de assinatura

---

## 2. Cabecalho

O cabecalho identifica a empresa. Formato centralizado, em caixa alta:

```
[NOME EMPRESARIAL COMPLETO]
CNPJ: XX.XXX.XXX/XXXX-XX
NIRE: XXXXXXXXXXX
```

O NIRE (Numero de Identificacao do Registro de Empresas) e obrigatorio quando disponivel. Se nao constar no JSON, omitir a linha.

---

## 3. Titulo do Documento

Centralizado, em negrito ou caixa alta:

```
Xª ALTERACAO CONTRATUAL
```

Exemplos reais: `1ª ALTERAÇÃO CONTRATUAL`, `12ª ALTERAÇÃO CONTRATUAL`, `21ª ALTERAÇÃO CONTRATUAL`.

---

## 4. Bloco de Qualificacao dos Socios

Cada socio e qualificado individualmente, seguindo o template padrao. O bloco aparece antes do preambulo.

### Template para pessoa fisica:

```
{{nomeCompleto}}, {{nacionalidade}}, {{profissao}}, {{estadoCivil}}, nascido(a) em {{dataNascimento}}, portador(a) da carteira de identidade nº {{rg}}, expedida pela {{orgaoEmissor}}, inscrito(a) no CPF sob o nº {{cpf}}, residente e domiciliado(a) na {{endereco}}.
```

Exemplo real:

```
WAGNER TANNÚS, brasileiro, engenheiro civil, casado sob regime de comunhão parcial de bens, nascido em 06/06/1969, portador da carteira de identidade nº M-3.948.675, expedida pela SSP/MG, inscrito no CPF sob o nº 581.924.766-34, residente e domiciliado na Rua dos Colibris, 12, bairro Area I (CBMM), CEP: 38.182-192, Araxá-MG.
```

### Template para pessoa juridica (socio PJ):

```
{{razaoSocial}}, inscrita no CNPJ sob o nº {{cnpj}}, com sede na {{endereco}}, neste ato representada na forma de seu contrato/estatuto social.
```

### Regras do bloco de qualificacao:

- Se houver mais de um socio, separar por ponto e virgula ou por paragrafo
- Quando a data de nascimento nao estiver disponivel no JSON, omitir o trecho `nascido(a) em...`
- Usar genero correto: `brasileiro/brasileira`, `portador/portadora`, `inscrito/inscrita`, `domiciliado/domiciliada`
- O endereco segue o formato: `{{logradouro}}, {{numero}}, bairro {{bairro}}, CEP: {{cep}}, {{cidade}}-{{estado}}`

---

## 5. Preambulo

O preambulo conecta a qualificacao dos socios ao corpo das alteracoes. Padrao observado:

### Para sociedade limitada com multiplos socios:

```
Os sócios acima qualificados, únicos sócios da empresa [NOME EMPRESARIAL], inscrita no CNPJ sob o nº [CNPJ], com sede na [endereço], neste ato e na melhor forma de direito, resolvem, de comum acordo, proceder à(s) seguinte(s) alteração(ões) no contrato social da empresa:
```

### Para socio unico (masculino):

```
Acima qualificado, único sócio da empresa [NOME EMPRESARIAL], inscrita no CNPJ sob o nº [CNPJ], com sede na [endereço], neste ato e na melhor forma de direito, resolve proceder à seguinte alteração no contrato social da empresa:
```

### Para socia unica (feminino):

```
Acima qualificada, única sócia da empresa [NOME EMPRESARIAL], inscrita no CNPJ sob o nº [CNPJ], com sede na [endereço], neste ato e na melhor forma de direito, resolve proceder à seguinte alteração no contrato social da empresa:
```

### Variantes encontradas nos documentos reais:

- `"...únicos sócios e representantes legais da empresa..."` (mais formal)
- `"...neste ato e pela melhor forma de direito, resolvem alterar o contrato social..."` (variacao)

---

## 6. Clausulas de Alteracao

Cada alteracao e numerada com algarismos romanos. O titulo descreve o tipo de alteracao.

### Formato padrao:

```
I – Da Alteração do [TIPO]

[Texto da alteração]
```

### Padroes reais por tipo de alteracao:

#### Alteracao de Endereco:

```
I – Da Alteração do Endereço

À partir desta data o endereço da empresa passa a ser: [novo endereço completo].
```

#### Alteracao de Objeto Social:

```
I – Da Alteração dos Objetivos Sociais

À partir desta data os objetivos sociais passam a ser: [novo objeto social].
```

#### Aumento de Capital Social:

```
II – Do Aumento do Capital Social

O Capital Social da empresa no valor de R$ [valor anterior] ([extenso]), dividido em [quantidade] ([extenso]) quotas no valor unitário de R$ 1,00 (um real), já inteiramente subscrito e integralizado em [forma], é aumentado para R$ [novo valor] ([extenso]), sendo o aumento de R$ [diferença] ([extenso]) integralizados pelos sócios da seguinte forma:

I – Pelo sócio [Nome]: R$ [valor] ([extenso]) [forma de integralizacao];
II – Pela sócia [Nome]: R$ [valor] ([extenso]) [forma de integralizacao].
```

#### Alteracao do Quadro Societario (saida de socio):

```
I – Da Alteração do Quadro Societário

Decide sair da sociedade o sócio [NOME COMPLETO], retroqualificado, transferindo com a anuência dos demais sócios o total de suas [quantidade] ([extenso]) quotas no valor unitário de R$ 1,00 (um real) para o sócio [NOME DO CESSIONÁRIO], retroqualificado.
```

#### Entrada e Saida de Socio:

```
1ª – DA ENTRADA E SAÍDA DE SÓCIO

Retira-se da Sociedade nesta data o sócio [NOME]. Fica incluído no quadro societário o sócio ora admitido: [qualificação completa do novo sócio].
```

#### Alteracao de Denominacao Social:

```
I – Da Nova Denominação Social

A sociedade ora constituída girará sob a denominação social de "[NOVO NOME]".
```

#### Alteracao da Distribuicao de Lucros:

```
I – Da Alteração da Distribuição dos Lucros ou Prejuízos

À partir desta data, ao término de cada exercício social, em 31 de dezembro, [texto completo da nova regra].
```

---

## 7. Clausula de Consolidacao

Apos as clausulas de alteracao, o contrato consolidado e reproduzido integralmente. Este e o ponto mais critico: **todas as clausulas nao alteradas devem ser copiadas ipsis litteris do contrato vigente**.

### Formato:

**Texto de transicao** (antes do titulo):
```
Diante das alterações acima, o Contrato Social passa a ter a seguinte redação:
```

**Titulo** (centralizado, negrito):
```
CONTRATO SOCIAL CONSOLIDADO
```

**Clausulas** (na sequencia):

Cláusula Primeira – [titulo]
[texto integral]

Parágrafo único. [texto do paragrafo, se houver]

Cláusula Segunda – [titulo]
[texto integral]

[... todas as clausulas na sequencia ...]
```

### Regras da consolidacao:

1. **Clausulas nao alteradas**: copiar o texto EXATAMENTE como consta no `contrato_consolidado` do JSON vigente. Nenhuma virgula, acento ou palavra pode ser diferente.
2. **Clausulas alteradas**: substituir pelo novo texto definido na alteracao.
3. **Ordem das clausulas**: manter a numeracao original. Se uma clausula foi adicionada, inserir na posicao correta e renumerar as subsequentes.
4. **Paragrafos**: preservar todos os paragrafos de cada clausula (`Parágrafo único`, `§ 1º`, `§ 2º` etc.).
5. **Quadro societario**: se a clausula de capital social contiver tabela de distribuicao de quotas, atualizar com os novos valores.

### Padroes de titulo de clausulas observados:

**Estilo numeral ordinal (mais comum):**
- `Cláusula Primeira`, `Cláusula Segunda`, ..., `Cláusula Décima Sexta`

**Estilo ordinal descritivo:**
- `PRIMEIRA: Da Natureza Jurídica, Prazo de Duração, Denominação, Sede e Foro`
- `SEGUNDA: Dos Objetivos Sociais`
- `TERCEIRA: Do Capital Social, sua Subscrição e Integralização`

**Estilo romano:**
- `I – DO TIPO DE SOCIEDADE`
- `II – DA DENOMINAÇÃO SOCIAL`
- `V – DO CAPITAL SOCIAL`

O estilo DEVE seguir o mesmo padrao do contrato original.

---

## 8. Bloco de Assinatura

Encerra o documento com local, data e espaco para assinaturas.

### Formato padrao (plural -- multiplos socios):

```
E, por estarem assim justos e contratados, assinam o presente instrumento.

[Cidade]-[UF], [dia] de [mês por extenso] de [ano].


_________________________________
[NOME DO SÓCIO 1]
CPF: XXX.XXX.XXX-XX


_________________________________
[NOME DO SÓCIO 2]
CPF: XXX.XXX.XXX-XX
```

### Formato para socio unico (singular):

```
E, por estar assim justo e contratado, assina o presente instrumento.

[Cidade]-[UF], [dia] de [mês por extenso] de [ano].


_________________________________
[NOME DO SÓCIO]
CPF: XXX.XXX.XXX-XX
```

### Variantes de fechamento:

- `"E, por estarem assim justos e contratados, firmam as partes o presente instrumento..."`
- `"E, por estarem justos e acordados, assinam o presente em..."`
- Quando ha testemunhas: adicionar bloco separado com nome e CPF de cada testemunha.

---

## 9. Formato Padrao de Enderecos

Todos os enderecos no documento (qualificacao, preambulo, clausulas de sede, clausulas de alteracao) DEVEM seguir o mesmo formato padronizado:

```
Logradouro, número, complemento, Bairro, Cidade-UF, CEP: XX.XXX-XXX
```

### Regras:

- **Sem prefixo "bairro:"** -- usar o nome do bairro diretamente, sem rotulo
- **Cidade-UF** com hifen, sem espacos (ex: `São Paulo-SP`, `Araxá-MG`)
- **CEP** sempre com prefixo `CEP:`, ponto separador e hifen (ex: `CEP: 05.442-000`)
- **Caixa mista** (title case) -- nunca ALL CAPS nos enderecos
- **Abreviacoes padrao**: `Conj.`, `Cj.`, `Apto.`, `Sala`, `Av.`
- **Complementos** separados por virgula (ex: `Conj. 13-D, Sala 53`)
- **CEP sempre no final**, apos cidade-UF

### Exemplos:

```
Rua Líbero Badaró, 293, Conj. 13-D, Sala 53, Centro, São Paulo-SP, CEP: 01.009-907
Avenida Prefeito Aracely de Paula, 1250-A, Centro, Araxá-MG, CEP: 38.184-022
Rua Pereira Leite, 323, Conjunto 2, Sala A, Sumarezinho, São Paulo-SP, CEP: 05.442-000
Rua Leopoldo Couto Magalhães Junior, 695, Itaim Bibi, São Paulo-SP, CEP: 04.542-011
```

---

## 10. Regras de Singular/Plural

Quando a empresa tem um unico socio, o documento deve usar formas no singular:

### Bloco de qualificacao:
- **Ultimo socio** (ou socio unico) termina com ponto (`.`), demais com ponto e virgula (`;`)

### Preambulo:
- **Plural**: `"Os sócios acima qualificados, únicos sócios da empresa... resolvem, de comum acordo, proceder à..."`
- **Singular masc.**: `"Acima qualificado, único sócio da empresa... resolve proceder à..."`
- **Singular fem.**: `"Acima qualificada, única sócia da empresa... resolve proceder à..."`

### Fecho:
- **Plural**: `"E, por estarem assim justos e contratados, assinam o presente instrumento."`
- **Singular**: `"E, por estar assim justo e contratado, assina o presente instrumento."`

### Cabecalho CNPJ:
- Se o CNPJ estiver vazio (empresa sem CNPJ no registro), omitir a linha `CNPJ: ...`

---

## 11. Regras Criticas

1. **Preservacao literal**: clausulas nao alteradas DEVEM ser copiadas caractere por caractere. Uma virgula trocada pode invalidar o documento na Junta Comercial.
2. **Valores por extenso**: todo valor monetario deve ser seguido do valor por extenso entre parenteses.
3. **Quantidade por extenso**: toda quantidade de quotas deve ser seguida do extenso entre parenteses.
4. **Retroqualificacao**: apos a primeira mencao completa de um socio no bloco de qualificacao, nas clausulas subsequentes usa-se `retroqualificado(a)`.
5. **Concordancia de genero**: ajustar para masculino/feminino conforme o socio.
6. **CNPJ e CPF com pontuacao**: sempre no formato padrao com pontos, barras e hifens.
7. **Enderecos padronizados**: todos os enderecos devem seguir o formato da Secao 9 -- sem prefixo "bairro:", CEP com ponto, cidade-UF com hifen.
8. **Singular/plural**: respeitar numero de socios no preambulo, fecho e qualificacao conforme Secao 10.
