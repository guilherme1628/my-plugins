#!/usr/bin/env node

require("dotenv").config({ path: require("path").join(__dirname, ".env") });
const EcabAPI = require("./ecab-api");
const fs = require("fs");
const path = require("path");
const os = require("os");
const readline = require("readline");

const DATA_DIR = path.join(os.homedir(), ".legalizacao-data");
const DRAFTS_PATH = path.join(DATA_DIR, "drafts.json");

// --- Draft management ---

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function saveDraft(type, data) {
  ensureDataDir();
  let drafts = {};
  if (fs.existsSync(DRAFTS_PATH)) {
    drafts = JSON.parse(fs.readFileSync(DRAFTS_PATH, "utf8"));
  }
  drafts[type] = { ...drafts[type], ...data, lastUpdated: new Date().toISOString() };
  fs.writeFileSync(DRAFTS_PATH, JSON.stringify(drafts, null, 2));
}

function loadDraft(type) {
  if (!fs.existsSync(DRAFTS_PATH)) return null;
  const drafts = JSON.parse(fs.readFileSync(DRAFTS_PATH, "utf8"));
  return drafts[type] || null;
}

function listDrafts() {
  if (!fs.existsSync(DRAFTS_PATH)) return [];
  const drafts = JSON.parse(fs.readFileSync(DRAFTS_PATH, "utf8"));
  return Object.entries(drafts).map(([type, data]) => ({
    type,
    lastUpdated: data.lastUpdated,
    company: data.basic?.companyName || "-",
  }));
}

function cleanDrafts() {
  if (fs.existsSync(DRAFTS_PATH)) {
    fs.unlinkSync(DRAFTS_PATH);
    console.log("\n✅ All drafts cleaned");
  } else {
    console.log("\nNo drafts to clean");
  }
}

function cleanSingleDraft(type) {
  if (fs.existsSync(DRAFTS_PATH)) {
    const drafts = JSON.parse(fs.readFileSync(DRAFTS_PATH, "utf8"));
    delete drafts[type];
    if (Object.keys(drafts).length === 0) {
      fs.unlinkSync(DRAFTS_PATH);
    } else {
      fs.writeFileSync(DRAFTS_PATH, JSON.stringify(drafts, null, 2));
    }
  }
}

// --- Interactive collection (human use) ---

function createPrompt() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  return { rl, question };
}

async function collectAbertura() {
  const { rl, question } = createPrompt();

  console.log("\n=== COLETA DE DADOS - ABERTURA DE EMPRESA ===\n");

  const data = { type: "ABERTURA", basic: {}, company: {}, partners: [] };

  data.basic.companyName = await question("Nome da empresa (ou opções): ");
  data.basic.priority = await question("Prioridade (urgente/importante/normal): ");
  data.basic.deadline = await question("Prazo desejado (DD/MM/YYYY ou vazio): ");

  console.log("\n--- Dados da Empresa ---");
  data.company.activities = await question("Atividades a serem exercidas: ");
  data.company.iptu = await question("IPTU do imóvel sede: ");
  data.company.socialCapital = await question("Capital social (R$): ");

  console.log("\n--- Sócios ---");
  const numPartners = parseInt(await question("Número de sócios: "));

  for (let i = 0; i < numPartners; i++) {
    console.log(`\nSócio ${i + 1}:`);
    const partner = {
      name: await question("  Nome completo: "),
      birthCity: await question("  Cidade de nascimento: "),
      birthState: await question("  Estado de nascimento: "),
      maritalStatus: await question("  Estado civil: "),
      marriageRegime: await question("  Regime de bens (se casado): "),
      profession: await question("  Profissão: "),
      participation: await question("  Participação no capital (%): "),
      documents: {
        rg: await question("  RG: "),
        cpf: await question("  CPF: "),
        residenceProof: await question("  Comprovante de residência: "),
      },
    };
    data.partners.push(partner);
  }

  rl.close();
  return data;
}

async function collectAlteracao() {
  const { rl, question } = createPrompt();

  console.log("\n=== COLETA DE DADOS - ALTERAÇÃO CONTRATUAL ===\n");

  const data = { type: "ALTERACAO", basic: {}, alteration: {} };

  data.basic.companyName = await question("Nome da empresa: ");
  data.basic.clienteId = await question("ID do cliente no sistema (obrigatório): ");
  data.basic.priority = await question("Prioridade (urgente/importante/normal): ");
  data.basic.deadline = await question("Prazo desejado (DD/MM/YYYY ou vazio): ");

  console.log("\n--- Tipo de Alteração ---");
  console.log("  1. Alteração de endereço");
  console.log("  2. Alteração de objeto social");
  console.log("  3. Alteração de capital social");
  console.log("  4. Inclusão de sócio");
  console.log("  5. Exclusão de sócio");
  console.log("  6. Transferência de cotas");
  console.log("  7. Alteração de nome empresarial");
  console.log("  8. Outro");
  data.alteration.type = await question("\nTipo(s) de alteração (ex: 1,3,6): ");
  data.alteration.details = await question("Detalhes da alteração: ");

  console.log("\n--- Documentação ---");
  data.alteration.hasContratoSocial = await question("Possui contrato social atual? (s/n): ");
  data.alteration.hasDocsSocios = await question("Documentos dos sócios atualizados? (s/n): ");
  data.alteration.observations = await question("Observações adicionais: ");

  rl.close();
  return data;
}

async function collectBaixa() {
  const { rl, question } = createPrompt();

  console.log("\n=== COLETA DE DADOS - BAIXA DE EMPRESA ===\n");

  const data = { type: "BAIXA", basic: {}, closure: {} };

  data.basic.companyName = await question("Nome da empresa: ");
  data.basic.clienteId = await question("ID do cliente no sistema (obrigatório): ");
  data.basic.priority = await question("Prioridade (urgente/importante/normal): ");
  data.basic.deadline = await question("Prazo desejado (DD/MM/YYYY ou vazio): ");

  console.log("\n--- Dados da Baixa ---");
  data.closure.reason = await question("Motivo do encerramento: ");
  data.closure.hasDebts = await question("Possui débitos pendentes? (s/n): ");
  data.closure.hasCertidoes = await question("Possui certidões negativas? (s/n): ");
  data.closure.hasContratoSocial = await question("Possui contrato social? (s/n): ");
  data.closure.lastBalanceDate = await question("Data do último balanço (DD/MM/YYYY ou vazio): ");
  data.closure.observations = await question("Observações adicionais: ");

  rl.close();
  return data;
}

// --- Build notes from collected data ---

const ALTERATION_TYPE_MAP = {
  "1": "Alteração de endereço",
  "2": "Alteração de objeto social",
  "3": "Alteração de capital social",
  "4": "Inclusão de sócio",
  "5": "Exclusão de sócio",
  "6": "Transferência de cotas",
  "7": "Alteração de nome empresarial",
  "8": "Outro",
};

function buildNotas(data) {
  let notas = `Tipo: ${data.type}\n`;
  notas += `Empresa: ${data.basic.companyName}\n`;
  notas += `Prioridade: ${data.basic.priority}\n`;

  if (data.basic.deadline) {
    notas += `Prazo: ${data.basic.deadline}\n`;
  }

  if (data.company) {
    notas += `\nCAPITAL SOCIAL: ${data.company.socialCapital || "-"}`;
    if (data.company.iptu) notas += `\nIPTU: ${data.company.iptu}`;
    if (data.company.activities) {
      notas += `\n\nATIVIDADES EXERCIDAS:`;
      data.company.activities.split("\n").forEach((act) => {
        if (act.trim()) notas += `\n- ${act.trim()}`;
      });
    }
  }

  if (data.partners && data.partners.length > 0) {
    const tipoSociedade = data.partners.length === 1 ? "Unipessoal" : `${data.partners.length} socios`;
    notas += `\n\nDADOS DO SOCIO (${tipoSociedade}):`;

    data.partners.forEach((partner, i) => {
      if (data.partners.length > 1) notas += `\n\nSocio ${i + 1}:`;
      notas += `\n- ${partner.name}`;
      notas += `\n- ${partner.birthCity || "-"}/${partner.birthState || "-"}`;
      notas += `\n- ${partner.maritalStatus || "-"}`;
      if (partner.marriageRegime && partner.marriageRegime !== "-") {
        notas += ` - ${partner.marriageRegime}`;
      }
      notas += `\n- Profissao: ${partner.profession || "-"}`;
      notas += `\n- Participacao: ${partner.participation}%`;
    });
  }

  if (data.alteration) {
    const types = data.alteration.type
      .split(",")
      .map((t) => ALTERATION_TYPE_MAP[t.trim()] || t.trim())
      .join(", ");
    notas += `\n\nTIPO DE ALTERACAO: ${types}`;
    if (data.alteration.details) notas += `\nDetalhes: ${data.alteration.details}`;
    if (data.alteration.hasContratoSocial) {
      notas += `\nContrato social atual: ${data.alteration.hasContratoSocial === "s" ? "Sim" : "Nao"}`;
    }
    if (data.alteration.hasDocsSocios) {
      notas += `\nDocs socios atualizados: ${data.alteration.hasDocsSocios === "s" ? "Sim" : "Nao"}`;
    }
    if (data.alteration.observations) notas += `\nObservacoes: ${data.alteration.observations}`;
  }

  if (data.closure) {
    notas += `\n\nMOTIVO DO ENCERRAMENTO: ${data.closure.reason}`;
    notas += `\nDebitos pendentes: ${data.closure.hasDebts === "s" ? "Sim" : "Nao"}`;
    notas += `\nCertidoes negativas: ${data.closure.hasCertidoes === "s" ? "Sim" : "Nao"}`;
    notas += `\nContrato social: ${data.closure.hasContratoSocial === "s" ? "Sim" : "Nao"}`;
    if (data.closure.lastBalanceDate) notas += `\nUltimo balanco: ${data.closure.lastBalanceDate}`;
    if (data.closure.observations) notas += `\nObservacoes: ${data.closure.observations}`;
  }

  return notas;
}

// --- Format date DD/MM/YYYY to ISO ---

function formatDateToISO(dateString) {
  if (!dateString || dateString === "-") return null;
  if (dateString.includes("/")) {
    const [day, month, year] = dateString.split("/");
    return `${year}-${month}-${day}`;
  }
  return dateString;
}

// --- Commands ---

async function collect(type = "ABERTURA") {
  if (!["ABERTURA", "ALTERACAO", "BAIXA"].includes(type)) {
    console.log("\n❌ Invalid type. Use: ABERTURA, ALTERACAO, or BAIXA");
    return;
  }

  console.log(`\n📋 Collecting data for ${type}\n`);

  let data;
  if (type === "ABERTURA") {
    data = await collectAbertura();
  } else if (type === "ALTERACAO") {
    data = await collectAlteracao();
  } else if (type === "BAIXA") {
    data = await collectBaixa();
  }

  saveDraft(type, data);
  console.log("\n✅ Data collected and saved!");
  console.log(`Run "node index.js create ${type}" to create in ECAB`);
}

async function create(type, jsonArg) {
  let draft;

  if (jsonArg) {
    draft = JSON.parse(jsonArg);
    draft.type = type;
    if (!draft.basic) {
      console.log("\n❌ JSON must have a 'basic' object with at least 'companyName'");
      return;
    }
  } else {
    draft = loadDraft(type);
    if (!draft) {
      console.log(`\n❌ No draft data found for ${type}`);
      console.log('Run "node index.js collect" first, or pass JSON directly');
      return;
    }
  }

  console.log(`\n📋 Creating ${type} in ECAB...\n`);

  const api = new EcabAPI();
  const companyName = draft.basic.companyName.split("(")[0].trim();

  const params = {
    tipo: draft.type.toLowerCase(),
    nome_empresa: companyName,
    prioridade: (draft.basic.priority || "normal").toLowerCase(),
    data_vencimento: formatDateToISO(draft.basic.deadline),
    notas: buildNotas(draft),
  };

  if (draft.basic.clienteId) {
    params.cliente_id = parseInt(draft.basic.clienteId);
  }

  const result = await api.createLegalizacao(params);

  console.log("✅ Legalizacao created in ECAB!");
  console.log(JSON.stringify({
    id: result.id,
    nome_empresa: result.nome_empresa,
    prioridade: result.prioridade,
    data_vencimento: result.data_vencimento || null,
    checklist_items: result.legalizacao_checklist_items?.length || 0,
  }, null, 2));

  if (!jsonArg) {
    cleanSingleDraft(type);
  }
}

function showList() {
  const drafts = listDrafts();
  if (drafts.length === 0) {
    console.log("\nNo drafts found");
    return;
  }
  console.log("\n📝 Saved Drafts:\n");
  drafts.forEach((draft, i) => {
    const date = new Date(draft.lastUpdated).toLocaleString("pt-BR");
    console.log(`${i + 1}. ${draft.type} - ${draft.company}`);
    console.log(`   Last updated: ${date}\n`);
  });
}

function showRequirements(type) {
  const requirements = {
    ABERTURA: {
      title: "ABERTURA (Opening New Company)",
      needed: [
        "3 name options for the company",
        "Activities to be performed",
        "IPTU of the headquarters property",
        "Social capital amount",
        "Partner documents (RG, CPF)",
        "Proof of residence for partners",
        "Complete partner qualification",
        "Participation percentage in capital",
      ],
    },
    ALTERACAO: {
      title: "ALTERACAO (Company Modification)",
      needed: [
        "Client ID (from search)",
        "Alteration type (1-8)",
        "Alteration details",
        "Updated partner documents",
        "Current social contract",
      ],
    },
    BAIXA: {
      title: "BAIXA (Company Closure)",
      needed: [
        "Client ID (from search)",
        "Reason for closure",
        "Debt status",
        "Tax clearance certificates",
        "Current social contract",
      ],
    },
  };

  const req = requirements[type];
  if (!req) {
    console.log("\n❌ Invalid type. Use: ABERTURA, ALTERACAO, or BAIXA");
    return;
  }

  console.log(`\n${req.title}\n`);
  console.log("Required:\n");
  req.needed.forEach((item, i) => {
    console.log(`${i + 1}. ${item}`);
  });

  if (type === "ALTERACAO") {
    console.log("\nAlteration types:");
    Object.entries(ALTERATION_TYPE_MAP).forEach(([k, v]) => {
      console.log(`  ${k}. ${v}`);
    });
  }
}

async function searchClients(query) {
  if (!query || query.length < 2) {
    console.log("\n❌ Search query must be at least 2 characters");
    console.log('Usage: node index.js search "company name"');
    return;
  }

  const api = new EcabAPI();
  const clients = await api.searchClients(query);

  if (!clients || clients.length === 0) {
    console.log("No clients found.");
    return;
  }

  console.log(JSON.stringify(clients, null, 2));
}

function showUsage() {
  console.log(`
Legalizacao ECAB - Company Legalization Management

Usage: node index.js <command> [type] [json]

Commands:
  search <query>              Search clients by name (returns JSON)
  collect <type>              Collect data interactively (human use)
  create <type> [json]        Create legalizacao (from draft or JSON)
  list                        List saved drafts
  requirements <type>         Show requirements for type
  clean                       Clean all drafts

Types: ABERTURA, ALTERACAO, BAIXA

Non-interactive (agent-friendly):
  node index.js search "MerchX"
  node index.js create ALTERACAO '{"basic":{"companyName":"MerchX","clienteId":"504","priority":"normal"},"alteration":{"type":"1","details":"Change address to Rua X, 123"}}'
  node index.js create BAIXA '{"basic":{"companyName":"Company","clienteId":"80","priority":"normal"},"closure":{"reason":"Encerramento de atividades"}}'

Interactive (human use):
  node index.js collect ABERTURA
  node index.js create ABERTURA
`);
}

// --- Main ---

async function main() {
  const command = process.argv[2];
  const arg1 = process.argv[3];
  const arg2 = process.argv[4];

  try {
    switch (command) {
      case "collect":
        await collect(arg1);
        break;
      case "create":
        await create(arg1, arg2);
        break;
      case "list":
        showList();
        break;
      case "requirements":
        showRequirements(arg1);
        break;
      case "search":
        await searchClients(arg1);
        break;
      case "clean":
        cleanDrafts();
        break;
      default:
        showUsage();
    }
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
}

main();
