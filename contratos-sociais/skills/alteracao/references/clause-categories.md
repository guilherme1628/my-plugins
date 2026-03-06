# Categorias de Clausulas e Mapeamento de Instrucoes

Referencia para mapear instrucoes do usuario as clausulas afetadas em uma alteracao contratual.

---

## 1. Categorias Padrao de Clausulas

As clausulas de um contrato social tipico se enquadram nas seguintes categorias:

| Categoria             | Clausula Tipica                                  | Conteudo                                                             |
|-----------------------|--------------------------------------------------|----------------------------------------------------------------------|
| Nome Empresarial      | Clausula Primeira                                | Razao social, nome fantasia                                          |
| Objeto Social         | Clausula Segunda                                 | Atividades economicas da empresa                                     |
| Sede / Endereco       | Clausula Terceira                                | Endereco da sede, filiais                                            |
| Prazo de Duracao      | Clausula Quarta (varia)                          | Data de inicio, prazo determinado/indeterminado                      |
| Capital Social        | Clausula Quinta (varia)                          | Valor total, quotas, distribuicao entre socios                       |
| Cessao de Quotas      | Varia                                            | Regras de transferencia de quotas a terceiros                        |
| Responsabilidade      | Varia                                            | Responsabilidade limitada ao valor das quotas                        |
| Administracao         | Varia                                            | Quem administra, poderes, representacao                              |
| Prestacao de Contas   | Varia                                            | Exercicio social, balanco, lucros e perdas                           |
| Pro-labore            | Varia                                            | Retirada mensal dos administradores                                  |
| Falecimento/Sucessao  | Varia                                            | Continuidade da empresa em caso de morte                             |
| Impedimentos          | Varia                                            | Declaracao de nao impedimento dos administradores                    |
| Foro                  | Ultima clausula (tipicamente)                    | Foro eleito para resolucao de disputas                               |
| Conselho Fiscal       | Varia                                            | Existencia ou dispensa do conselho fiscal                            |
| Deliberacoes          | Varia                                            | Regras de quorum e forma de deliberacao                              |

---

## 2. Mapeamento: Instrucao do Usuario -> Clausulas Afetadas

### Alteracoes Simples (1 clausula afetada)

#### "Alterar endereco" / "Mudar sede"

- **Clausula afetada**: Sede / Endereco
- **Categoria da alteracao**: `Endereço`
- **Padrao**: `"À partir desta data o endereço da empresa passa a ser: [novo endereço]."`
- **Consolidacao**: Atualizar a clausula de sede com novo endereco. Se a clausula de Nome Empresarial contiver o endereco (formato consolidado), atualizar tambem.
- **Atencao**: Verificar se o endereco tambem aparece na clausula Primeira (alguns contratos agrupam nome, sede e foro na mesma clausula).

#### "Alterar objeto social" / "Mudar atividade"

- **Clausula afetada**: Objeto Social
- **Categoria da alteracao**: `Objeto Social`
- **Padrao**: `"À partir desta data os objetivos sociais passam a ser: [novos objetivos]."`
- **Consolidacao**: Substituir o texto da clausula de objeto social.

#### "Alterar nome empresarial" / "Mudar razao social"

- **Clausula afetada**: Nome Empresarial
- **Categoria da alteracao**: `Nome Empresarial`
- **Padrao**: `"A sociedade passará a adotar a denominação social de [NOVO NOME]."`
- **Consolidacao**: Atualizar a clausula de nome empresarial. Verificar se o nome aparece em outras clausulas (administracao, preambulo).

#### "Alterar distribuicao de lucros"

- **Clausula afetada**: Prestacao de Contas / Exercicio Social
- **Categoria da alteracao**: `Outra`
- **Padrao**: Reescrever a clausula de lucros/perdas com nova regra de distribuicao.
- **Consolidacao**: Substituir a clausula correspondente.

---

### Alteracoes de Capital (1-2 clausulas afetadas)

#### "Aumentar capital" / "Aumentar capital social"

- **Clausulas afetadas**: Capital Social + Quadro Societario (se houver clausula separada)
- **Categoria da alteracao**: `Capital Social`
- **Padrao**: Descrever valor anterior, novo valor, diferenca, forma de integralizacao por socio
- **Consolidacao**: Atualizar clausula de capital com novo valor total, nova quantidade de quotas, nova distribuicao.
- **Atencao**: Atualizar tabela/quadro de distribuicao de quotas entre socios.

#### "Reduzir capital"

- **Clausulas afetadas**: Capital Social
- **Categoria da alteracao**: `Capital Social`
- **Padrao**: Descrever valor anterior, novo valor, motivo da reducao
- **Consolidacao**: Atualizar clausula de capital. Verificar se a reducao afeta a proporcao entre socios.

---

### Alteracoes Societarias (multiplas clausulas afetadas)

#### "Remover socio" / "Saida de socio" / "Retirada de socio"

- **Clausulas afetadas**:
  1. **Quadro Societario** -- Registrar a saida e a destinacao das quotas
  2. **Capital Social** -- Atualizar distribuicao de quotas (e valor, se houver reducao)
  3. **Administracao** -- Se o socio retirante era administrador, designar novo ou ajustar texto
- **Categoria da alteracao**: `Quadro Societário`
- **Padrao**: `"Decide sair da sociedade o sócio [NOME], retroqualificado, transferindo [...] quotas para [CESSIONÁRIO]."`
- **Consolidacao**: Remover socio da distribuicao de quotas. Atualizar clausula de administracao se necessario.
- **Atencao**: As quotas do retirante devem ter destino: transferidas para outro socio existente, para novo socio, ou canceladas (reducao de capital).

#### "Incluir socio" / "Entrada de socio" / "Admitir socio"

- **Clausulas afetadas**:
  1. **Quadro Societario** -- Registrar a entrada e a qualificacao do novo socio
  2. **Capital Social** -- Atualizar distribuicao de quotas (e valor, se houver aumento)
  3. **Administracao** -- Se o novo socio sera administrador, ajustar clausula
- **Categoria da alteracao**: `Entrada de Sócio` ou `Quadro Societário`
- **Padrao**: `"Fica incluído no quadro societário o sócio ora admitido: [qualificação completa]."`
- **Consolidacao**: Adicionar socio na distribuicao de quotas. Atualizar clausula de administracao se aplicavel.
- **Atencao**: Qualificacao completa do novo socio e obrigatoria (nome, nacionalidade, profissao, estado civil, data nascimento, RG, CPF, endereco).

#### "Transferir quotas" / "Cessao de quotas"

- **Clausulas afetadas**:
  1. **Quadro Societario** -- Registrar a transferencia
  2. **Capital Social** -- Atualizar distribuicao de quotas
- **Categoria da alteracao**: `Quadro Societário`
- **Padrao**: `"O sócio [CEDENTE] transfere [quantidade] quotas para o sócio [CESSIONÁRIO], com a anuência dos demais sócios."`
- **Consolidacao**: Ajustar quantidade de quotas de cedente e cessionario.
- **Atencao**: Se o cedente transfere TODAS as quotas, trata-se de saida de socio. Se o cessionario nao era socio, trata-se tambem de entrada de socio.

#### "Substituir socio" / "Trocar socio"

- **Clausulas afetadas**:
  1. **Quadro Societario** -- Saida do antigo + entrada do novo
  2. **Capital Social** -- Atualizar distribuicao
  3. **Administracao** -- Se aplicavel
- **Categoria da alteracao**: `Entrada de Sócio` ou `Quadro Societário`
- **Padrao**: Combinar saida e entrada em uma unica clausula de alteracao.
- **Consolidacao**: Substituir socio na distribuicao e demais clausulas onde apareca.

---

### Alteracoes de Administracao

#### "Alterar administrador" / "Trocar administrador"

- **Clausula afetada**: Administracao
- **Categoria da alteracao**: `Outra`
- **Padrao**: Designar novo administrador com qualificacao completa.
- **Consolidacao**: Reescrever clausula de administracao com novo(s) nome(s).

#### "Alterar poderes do administrador"

- **Clausula afetada**: Administracao
- **Categoria da alteracao**: `Outra`
- **Padrao**: Especificar novos poderes/restricoes.
- **Consolidacao**: Reescrever clausula de administracao.

---

### Alteracoes Compostas (instrucoes que afetam varias clausulas)

#### "Transformar EIRELI em LTDA" / "Transformar tipo societario"

- **Clausulas afetadas**:
  1. **Nome Empresarial** -- Atualizar tipo societario no nome
  2. **Quadro Societario** -- Incluir novo(s) socio(s)
  3. **Capital Social** -- Redistribuir quotas
  4. **Administracao** -- Ajustar conforme novo quadro
  5. **Varias outras** -- Adaptar texto de "titular" para "socios"
- **Categoria da alteracao**: `Nome Empresarial` + outras conforme necessidade

#### "Incorporacao" / "Fusao"

- **Clausulas afetadas**: Todas (documento especial)
- **Categoria da alteracao**: `Incorporação`
- **Padrao**: Aprovacao do protocolo de incorporacao, laudo contabil, extincao da incorporada.
- **Atencao**: Este tipo de alteracao tem formato proprio, com anexos obrigatorios.

---

## 3. Matriz de Dependencia entre Clausulas

Ao alterar uma clausula, verificar dependencias:

| Clausula Alterada     | Verificar Impacto em                                           |
|-----------------------|----------------------------------------------------------------|
| Nome Empresarial      | Clausula Primeira, preambulo, fecho                            |
| Endereco / Sede       | Clausula de sede, Clausula Primeira (se unificada), fecho      |
| Capital Social        | Quadro de distribuicao, clausula de responsabilidade           |
| Quadro Societario     | Capital Social, Administracao, Deliberacoes                    |
| Administracao         | Validade de documentos, pro-labore, impedimentos               |
| Objeto Social         | Clausula de objeto (geralmente isolada)                        |

---

## 4. Categorias Validas no JSON

Para o campo `alteracoes[].categoria`:

| Categoria            | Uso                                                         |
|----------------------|-------------------------------------------------------------|
| `Nome Empresarial`   | Alteracao da razao social ou nome fantasia                  |
| `Endereço`           | Alteracao de sede ou endereco                               |
| `Objeto Social`      | Alteracao das atividades da empresa                         |
| `Capital Social`     | Aumento, reducao ou redistribuicao de capital               |
| `Quadro Societário`  | Entrada, saida ou transferencia entre socios                |
| `Entrada de Sócio`   | Especificamente entrada de novo socio                       |
| `Incorporação`       | Incorporacao por outra empresa                              |
| `Outra`              | Qualquer outra alteracao nao enquadrada acima               |

---

## 5. Checklist por Tipo de Instrucao

### Saida de socio
- [ ] Identificar socio retirante no JSON
- [ ] Definir cessionario das quotas (socio existente ou novo)
- [ ] Calcular nova distribuicao percentual
- [ ] Verificar se retirante era administrador
- [ ] Gerar clausula de alteracao do quadro societario
- [ ] Atualizar clausula de capital social na consolidacao
- [ ] Atualizar clausula de administracao se necessario

### Entrada de socio
- [ ] Obter qualificacao completa do novo socio
- [ ] Definir origem das quotas (aumento de capital ou transferencia)
- [ ] Calcular nova distribuicao percentual
- [ ] Definir se novo socio sera administrador
- [ ] Gerar clausula de alteracao do quadro societario
- [ ] Atualizar clausula de capital social na consolidacao
- [ ] Atualizar clausula de administracao se necessario

### Alteracao de endereco
- [ ] Obter novo endereco completo (logradouro, numero, bairro, CEP, cidade, UF)
- [ ] Gerar clausula de alteracao do endereco
- [ ] Verificar se endereco aparece em outras clausulas (Primeira unificada)
- [ ] Atualizar todas as ocorrencias na consolidacao

### Aumento de capital
- [ ] Obter novo valor total do capital
- [ ] Calcular diferenca (aumento)
- [ ] Definir forma de integralizacao por socio
- [ ] Definir nova distribuicao de quotas
- [ ] Gerar clausula de alteracao do capital
- [ ] Atualizar clausula de capital na consolidacao com nova tabela
