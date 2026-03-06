# Contratos Sociais

Plugin para Claude Code que automatiza o processamento de contratos sociais e alteracoes contratuais de empresas brasileiras.

## Funcionalidades

- **Conversao de Contratos**: Converte PDFs e DOCXs de contratos sociais em JSON estruturado com parsing clausula-por-clausula
- **Geracao de Alteracoes**: Gera alteracoes contratuais modificando clausulas especificas enquanto preserva o texto inalterado caractere-por-caractere
- **Busca de Empresas**: Localiza contratos no banco de dados JSON por nome da empresa
- **Processamento em Lote**: Converte diretorios inteiros de contratos de uma vez

## Instalacao

### Uso Local (por sessao)

```bash
claude --plugin-dir /caminho/para/contratos-sociais
```

### Uso em Projeto

Copie o plugin para o diretorio `.claude-plugin/` do seu projeto:

```bash
cp -r contratos-sociais /seu/projeto/.claude-plugin/
```

## Pre-requisitos

- Python 3.8+ (para os scripts de busca e processamento em lote)
- Diretorio com arquivos JSON de contratos (banco de dados)

## Uso

### Comandos

#### `/converter`

Converte contratos de PDF/DOCX para JSON estruturado.

```
/converter arquivo.pdf --jsons-dir ./contratos/jsons/
/converter ./pasta-de-contratos/ --jsons-dir ./contratos/jsons/
```

**Argumentos:**
- `<arquivo-ou-pasta>`: Caminho para um arquivo PDF/DOCX ou diretorio
- `--jsons-dir <caminho>`: Diretorio onde salvar os JSONs (sera solicitado se nao informado)

#### `/alterar`

Gera uma alteracao contratual para uma empresa.

```
/alterar "Empresa Exemplo Ltda" --jsons-dir ./contratos/jsons/
```

**Argumentos:**
- `<nome-empresa>`: Nome (ou parte do nome) da empresa
- `--jsons-dir <caminho>`: Diretorio contendo os JSONs de contratos (sera solicitado se nao informado)

### Skills

Os skills sao ativados automaticamente quando voce menciona tarefas relacionadas:

- **convert-contrato**: "converter contrato", "extrair dados do PDF", "converter PDF para JSON"
- **alteracao**: "criar alteracao contratual", "remover socio", "adicionar socio", "transferir cotas", "mudar endereco"

## Estrutura do Banco de Dados

Os arquivos JSON seguem o padrao de nomenclatura:

```
{nome_empresa}|{cnpj}|{tipo_documento}|{versao_alteracao}.json
```

Exemplo:
```
Empresa Exemplo Ltda|12.345.678_0001-90|Alteracao Contratual|2a Alteracao.json
```

## Schema JSON

O schema completo esta documentado em `references/schema.md`. Campos principais:

- `resumo`: Contagens e indicadores de extracao
- `tipo_documento`: "Contrato Social" ou "Alteracao Contratual"
- `versao_alteracao`: "1a Alteracao", "2a Alteracao", etc.
- `empresa`: Nome, CNPJ, endereco
- `socios`: Array com dados completos de cada socio
- `contrato_consolidado`: Todas as clausulas com texto integral
- `assinatura`: Local e data

## Regras Criticas

O plugin segue regras estritas para garantir validade juridica:

1. **Preservacao Verbatim**: Clausulas inalteradas sao copiadas caractere-por-caractere
2. **Valores por Extenso**: `R$ 10.000,00 (dez mil reais)`
3. **Quantidades por Extenso**: `10.000 (dez mil) cotas`
4. **Retroqualificacao**: Apos primeira mencao completa, usar `retroqualificado(a)`
5. **Concordancia de Genero**: `brasileiro/brasileira`, `portador/portadora`
6. **Formato CPF/CNPJ**: Sempre com pontuacao padrao

## Estrutura do Plugin

```
contratos-sociais/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── converter.md
│   └── alterar.md
├── references/
│   └── schema.md
├── skills/
│   ├── convert-contrato/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── batch_convert.py
│   └── alteracao/
│       ├── SKILL.md
│       ├── references/
│       │   ├── alteracao-format.md
│       │   └── clause-categories.md
│       └── scripts/
│           └── find_company.py
└── README.md
```

## Licenca

Uso interno.
