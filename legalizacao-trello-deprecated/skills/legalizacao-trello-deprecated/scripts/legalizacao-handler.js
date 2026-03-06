#!/usr/bin/env node

const TrelloAPI = require('./trello-api');
const { LEGALIZACAO_CONFIG } = require('./config');
const fs = require('fs');
const path = require('path');
const os = require('os');

class LegalizacaoHandler extends TrelloAPI {
  constructor() {
    super();
    this.dataDir = path.join(os.homedir(), '.legalizacao-data');
    this.dataPath = path.join(this.dataDir, 'drafts.json');
    this.ensureDataDir();
  }

  ensureDataDir() {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
  }

  // Save draft data
  saveDraft(type, data) {
    let drafts = {};
    if (fs.existsSync(this.dataPath)) {
      drafts = JSON.parse(fs.readFileSync(this.dataPath, 'utf8'));
    }

    drafts[type] = {
      ...drafts[type],
      ...data,
      lastUpdated: new Date().toISOString()
    };

    fs.writeFileSync(this.dataPath, JSON.stringify(drafts, null, 2));
  }

  // Load draft data
  loadDraft(type) {
    if (!fs.existsSync(this.dataPath)) return null;

    const drafts = JSON.parse(fs.readFileSync(this.dataPath, 'utf8'));
    return drafts[type] || null;
  }

  // List all drafts
  listDrafts() {
    if (!fs.existsSync(this.dataPath)) return [];

    const drafts = JSON.parse(fs.readFileSync(this.dataPath, 'utf8'));
    return Object.entries(drafts).map(([type, data]) => ({
      type,
      lastUpdated: data.lastUpdated,
      company: data.basic?.companyName || '-'
    }));
  }

  // Interactive collection for ABERTURA
  async collectAbertura() {
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const question = (prompt) => new Promise(resolve => rl.question(prompt, resolve));

    console.log('\n=== COLETA DE DADOS - ABERTURA DE EMPRESA ===\n');

    const data = {
      type: 'ABERTURA',
      basic: {},
      company: {},
      partners: []
    };

    // Basic info
    data.basic.companyName = await question('Nome da empresa (ou opções): ');
    data.basic.priority = await question('Prioridade (Urgente/Importante/Normal): ');
    data.basic.deadline = await question('Prazo desejado (DD/MM/YYYY): ');

    // Company data
    console.log('\n--- Dados da Empresa ---');
    data.company.activities = await question('Atividades a serem exercidas: ');
    data.company.iptu = await question('IPTU do imóvel sede: ');
    data.company.socialCapital = await question('Capital social (R$): ');

    // Partners
    console.log('\n--- Sócios ---');
    const numPartners = parseInt(await question('Número de sócios: '));

    for (let i = 0; i < numPartners; i++) {
      console.log(`\nSócio ${i + 1}:`);
      const partner = {
        name: await question('  Nome completo: '),
        birthCity: await question('  Cidade de nascimento: '),
        birthState: await question('  Estado de nascimento: '),
        maritalStatus: await question('  Estado civil: '),
        marriageRegime: await question('  Regime de bens (se casado): '),
        profession: await question('  Profissão: '),
        participation: await question('  Participação no capital (%): '),
        documents: {
          rg: await question('  RG: '),
          cpf: await question('  CPF: '),
          residenceProof: await question('  Comprovante de residência: ')
        }
      };
      data.partners.push(partner);
    }

    rl.close();
    return data;
  }

  // Create legalizacao task
  async createLegalizacaoTask(data) {
    try {
      // Find RECEBIDAS list
      const listId = await this.findList(LEGALIZACAO_CONFIG.BOARD_ID, 'RECEBIDAS');
      if (!listId) {
        throw new Error('RECEBIDAS list not found in LEGALIZACAO board');
      }

      // Build title (shorter, just first name option)
      const companyName = data.basic.companyName.split('(')[0].trim();
      const title = `[${data.type}] - ${companyName}`;

      // Build description matching existing card format
      let description = `**Categoria:** ECAB
**Prioridade:** ${data.basic.priority}
**Tipo:** Normal
**Prazo:** ${data.basic.deadline}

**DADOS DA LEGALIZAÇÃO:**
**Contexto:** ${data.type}
**Empresa:** ${companyName}`;

      // Company names section
      if (data.basic.companyName.includes('(') || data.basic.companyName.includes(',')) {
        description += `\n\n**OPÇÕES DE NOMES:**`;
        const names = data.basic.companyName.replace(/[()]/g, '').split(/,|opções:/i).map(n => n.trim()).filter(n => n);
        names.forEach((name, i) => {
          description += `\n${i + 1}. ${name}`;
        });
      }

      // Company data section
      if (data.company) {
        description += `\n\n**CAPITAL SOCIAL:** ${data.company.socialCapital || '-'}`;
        description += `\n**PORTE:** ${data.company.porte || '-'}`;

        if (data.company.endereco) {
          description += `\n\n**ENDEREÇO DA EMPRESA:**\n${data.company.endereco}`;
        }

        description += `\n\n**IPTU:** ${data.company.iptu || '-'}`;

        if (data.company.activities) {
          description += `\n\n**ATIVIDADES EXERCIDAS:**`;
          const activities = data.company.activities.split('\n');
          activities.forEach(act => {
            if (act.trim()) description += `\n• ${act.trim()}`;
          });
        }
      }

      // Partners section with full details
      if (data.partners && data.partners.length > 0) {
        const tipoSociedade = data.partners.length === 1 ? 'Unipessoal' : `${data.partners.length} sócios`;
        description += `\n\n**DADOS DO SÓCIO (${tipoSociedade}):**`;

        data.partners.forEach((partner, i) => {
          if (data.partners.length > 1) {
            description += `\n\n**Sócio ${i + 1}:**`;
          }
          description += `\n• ${partner.name}`;
          description += `\n• ${partner.birthCity || '-'}/${partner.birthState || '-'}`;
          description += `\n• ${partner.maritalStatus || '-'}`;
          if (partner.marriageRegime && partner.marriageRegime !== '-') {
            description += ` - ${partner.marriageRegime}`;
          }
          description += `\n• Profissão: ${partner.profession || '-'}`;
          description += `\n• Participação: ${partner.participation}%`;
          description += `\n• Documentos: ${partner.documents?.rg === 'Anexo' ? 'Anexados no Trello' : 'Serão anexados no Trello'}`;
        });
      }

      // Create card
      const card = await this.createCard(listId.id, title, description);

      // Add ECAB label
      await this.addLabel(card.id, LEGALIZACAO_CONFIG.CATEGORY.id);

      // Set due date
      if (data.basic.deadline && data.basic.deadline !== '-') {
        const isoDate = this.formatDateForTrello(data.basic.deadline);
        if (isoDate) {
          await this.setDueDate(card.id, isoDate);
        }
      }

      // Create checklist based on type
      const checklist = await this.createChecklist(card.id, 'Documentos Necessários');

      if (data.type === 'ABERTURA') {
        const aberturaItems = [
          '3 opções de nomes da empresa',
          'Lista de atividades exercidas',
          'Documentos dos sócios (RG, CPF)',
          'Comprovante de residência dos sócios',
          'IPTU do imóvel sede',
          'Qualificação completa dos sócios',
          'Definição de participação no capital',
          'Valor do capital social'
        ];

        for (const item of aberturaItems) {
          await this.addCheckItem(checklist.id, item);
        }
      } else if (data.type === 'ALTERAÇÃO') {
        const alteracaoItems = [
          'Tipo específico da alteração',
          'Documentos dos sócios',
          'Documentos da empresa atual',
          'ANEXAR DOCUMENTO ALTERACAO'
        ];

        for (const item of alteracaoItems) {
          await this.addCheckItem(checklist.id, item);
        }
      } else if (data.type === 'BAIXA') {
        const baixaItems = [
          'Motivo da baixa',
          'Documentos da empresa',
          'Verificar pendências',
          'ANEXAR DOCUMENTO ALTERACAO'
        ];

        for (const item of baixaItems) {
          await this.addCheckItem(checklist.id, item);
        }
      }

      return {
        id: card.id,
        url: card.url,
        title: card.name,
        type: data.type,
        company: data.basic.companyName,
        priority: data.basic.priority,
        deadline: data.basic.deadline
      };

    } catch (error) {
      console.error('Error creating legalização task:', error.message);
      throw error;
    }
  }

  // Generate report of tasks in LEGALIZACAO board
  async generateReport() {
    try {
      const board = await this.getBoard(LEGALIZACAO_CONFIG.BOARD_ID);

      const report = {
        total: 0,
        byList: {},
        byType: { ABERTURA: 0, ALTERAÇÃO: 0, BAIXA: 0 },
        byPriority: { Urgente: 0, Importante: 0, Normal: 0 },
        overdue: [],
        recent: []
      };

      const now = new Date();

      for (const list of board) {
        report.byList[list.name] = list.cards.length;
        report.total += list.cards.length;

        for (const card of list.cards) {
          // Count by type
          if (card.name.includes('[ABERTURA]')) report.byType.ABERTURA++;
          else if (card.name.includes('[ALTERAÇÃO]')) report.byType.ALTERAÇÃO++;
          else if (card.name.includes('[BAIXA]')) report.byType.BAIXA++;

          // Count by priority
          if (card.desc) {
            if (card.desc.includes('Prioridade: Urgente')) report.byPriority.Urgente++;
            else if (card.desc.includes('Prioridade: Importante')) report.byPriority.Importante++;
            else report.byPriority.Normal++;
          }

          // Check overdue
          if (card.due && new Date(card.due) < now) {
            report.overdue.push({
              title: card.name,
              due: this.parseDateFromTrello(card.due),
              list: list.name
            });
          }

          // Recent tasks (last 7 days)
          const createdDate = new Date(card.dateLastActivity || card.id);
          const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          if (createdDate > sevenDaysAgo) {
            report.recent.push({
              title: card.name,
              list: list.name,
              created: createdDate.toLocaleDateString('pt-BR')
            });
          }
        }
      }

      return report;
    } catch (error) {
      console.error('Error generating report:', error.message);
      throw error;
    }
  }
}

module.exports = LegalizacaoHandler;