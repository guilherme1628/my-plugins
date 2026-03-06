#!/usr/bin/env node

require('dotenv').config();
const LegalizacaoHandler = require('./legalizacao-handler');

/**
 * Legalização Workflow Skill
 *
 * Installation:
 * npm install legalizacao-workflow
 *
 * Environment Variables:
 * TRELLO_API_KEY=your-api-key
 * TRELLO_TOKEN=your-token
 */

class LegalizacaoSkill {
  constructor() {
    this.handler = new LegalizacaoHandler();
  }

  async run() {
    const command = process.argv[2];
    const type = process.argv[3];

    try {
      switch (command) {
        case 'collect':
          await this.collect(type);
          break;
        case 'create':
          await this.create(type);
          break;
        case 'list':
          this.listDrafts();
          break;
        case 'report':
          await this.report();
          break;
        case 'requirements':
          this.showRequirements(type);
          break;
        case 'clean':
          this.cleanDrafts();
          break;
        default:
          this.showUsage();
      }
    } catch (error) {
      console.error('\n❌ Error:', error.message);
      console.log('\nTroubleshooting:');
      console.log('1. Check if TRELLO_API_KEY and TRELLO_TOKEN are set');
      console.log('2. Verify access to LEGALIZACAO board');
      console.log('3. Check network connection');
    }
  }

  async collect(type = 'ABERTURA') {
    if (!['ABERTURA', 'ALTERAÇÃO', 'BAIXA'].includes(type)) {
      console.log('\n❌ Invalid type. Use: ABERTURA, ALTERAÇÃO, or BAIXA');
      return;
    }

    console.log(`\n📋 Collecting data for ${type}\n`);

    let data;
    if (type === 'ABERTURA') {
      data = await this.handler.collectAbertura();
    } else {
      console.log(`\n⚠️  Collection for ${type} not implemented in CLI mode`);
      console.log('Please use a more sophisticated interface for complex types');
      return;
    }

    this.handler.saveDraft(type, data);
    console.log('\n✅ Data collected and saved!');
    console.log('Run "legalizacao create" to create the task');
  }

  async create(type = 'ABERTURA') {
    const draft = this.handler.loadDraft(type);

    if (!draft) {
      console.log(`\n❌ No draft data found for ${type}`);
      console.log('Run "legalizacao collect" first');
      return;
    }

    console.log(`\n📋 Creating ${type} task...\n`);

    const result = await this.handler.createLegalizacaoTask(draft);

    console.log('\n✅ Legalização task created successfully!');
    console.log(`📋 Title: ${result.title}`);
    console.log(`📁 Board: LEGALIZACAO`);
    console.log(`📌 List: RECEBIDAS`);
    console.log(`🏷️  Category: ECAB`);
    console.log(`⭐ Priority: ${result.priority}`);
    console.log(`📅 Deadline: ${result.deadline}`);
    console.log(`🔗 URL: ${result.url}`);

    // Clean draft after successful creation
    this.cleanSingleDraft(type);
  }

  listDrafts() {
    const drafts = this.handler.listDrafts();

    if (drafts.length === 0) {
      console.log('\nNo drafts found');
      return;
    }

    console.log('\n📝 Saved Drafts:\n');
    drafts.forEach((draft, i) => {
      const date = new Date(draft.lastUpdated).toLocaleString('pt-BR');
      console.log(`${i + 1}. ${draft.type} - ${draft.company}`);
      console.log(`   Last updated: ${date}\n`);
    });
  }

  async report() {
    console.log('\n📊 Legalização Report\n');

    const report = await this.handler.generateReport();

    console.log(`Total Tasks: ${report.total}`);
    console.log('\nBy List:');
    Object.entries(report.byList).forEach(([list, count]) => {
      console.log(`  ${list}: ${count}`);
    });

    console.log('\nBy Type:');
    Object.entries(report.byType).forEach(([type, count]) => {
      console.log(`  ${type}: ${count}`);
    });

    console.log('\nBy Priority:');
    Object.entries(report.byPriority).forEach(([priority, count]) => {
      console.log(`  ${priority}: ${count}`);
    });

    if (report.recent.length > 0) {
      console.log('\nRecent Tasks (last 7 days):');
      report.recent.forEach(task => {
        console.log(`  • ${task.title} (${task.list}) - ${task.created}`);
      });
    }

    if (report.overdue.length > 0) {
      console.log('\n⚠️  Overdue Tasks:');
      report.overdue.forEach(task => {
        console.log(`  • ${task.title} (${task.due} in ${task.list})`);
      });
    }
  }

  showRequirements(type) {
    const requirements = {
      ABERTURA: {
        title: 'ABERTURA (Opening New Company)',
        needed: [
          '3 name options for the company',
          'Activities to be performed',
          'IPTU of the headquarters property',
          'Social capital amount',
          'Partner documents (RG, CPF)',
          'Proof of residence for partners',
          'Complete partner qualification',
          'Participation percentage in capital'
        ]
      },
      ALTERAÇÃO: {
        title: 'ALTERAÇÃO (Company Modification)',
        needed: [
          'Specific alteration type',
          'Updated partner documents',
          'Current company documents',
          'Social contract'
        ]
      },
      BAIXA: {
        title: 'BAIXA (Company Closure)',
        needed: [
          'Reason for closure',
          'All company documents',
          'List of pending issues',
          'Tax clearance certificates'
        ]
      }
    };

    const req = requirements[type];
    if (!req) {
      console.log('\n❌ Invalid type. Use: ABERTURA, ALTERAÇÃO, or BAIXA');
      return;
    }

    console.log(`\n${req.title}\n`);
    console.log('Required Documents:\n');

    req.needed.forEach((item, i) => {
      console.log(`${i + 1}. ${item}`);
    });

    console.log('\nProcess:');
    console.log('1. All tasks created in LEGALIZACAO board');
    console.log('2. Initial list: RECEBIDAS');
    console.log('3. Workflow: RECEBIDAS → ANÁLISE → EM ANDAMENTO → CONCLUÍDO');
  }

  cleanDrafts() {
    const fs = require('fs');
    const path = require('path');
    const os = require('os');
    const dataPath = path.join(os.homedir(), '.legalizacao-data', 'drafts.json');

    if (fs.existsSync(dataPath)) {
      fs.unlinkSync(dataPath);
      console.log('\n✅ All drafts cleaned');
    } else {
      console.log('\nNo drafts to clean');
    }
  }

  cleanSingleDraft(type) {
    const fs = require('fs');
    const path = require('path');
    const os = require('os');
    const dataPath = path.join(os.homedir(), '.legalizacao-data', 'drafts.json');

    if (fs.existsSync(dataPath)) {
      const drafts = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
      delete drafts[type];

      if (Object.keys(drafts).length === 0) {
        fs.unlinkSync(dataPath);
      } else {
        fs.writeFileSync(dataPath, JSON.stringify(drafts, null, 2));
      }
    }
  }

  showUsage() {
    console.log('\nLegalização Workflow - Company Legalization Management\n');
    console.log('Usage: legalizacao [command] [type]\n');
    console.log('Commands:');
    console.log('  collect [type]    - Collect data for legalizacao');
    console.log('  create [type]     - Create task from collected data');
    console.log('  list              - List saved drafts');
    console.log('  report            - Generate status report');
    console.log('  requirements      - Show requirements for type');
    console.log('  clean             - Clean all drafts\n');
    console.log('Types:');
    console.log('  ABERTURA          - Opening new company');
    console.log('  ALTERAÇÃO         - Modifying existing company');
    console.log('  BAIXA             - Closing company\n');
    console.log('Examples:');
    console.log('  legalizacao collect ABERTURA');
    console.log('  legalizacao create ABERTURA');
    console.log('  legalizacao report');
    console.log('  legalizacao requirements ABERTURA\n');
    console.log('Environment Variables:');
    console.log('  TRELLO_API_KEY    - Your Trello API key');
    console.log('  TRELLO_TOKEN      - Your Trello token');
  }
}

// Execute if called directly
if (require.main === module) {
  const skill = new LegalizacaoSkill();
  skill.run();
}

module.exports = LegalizacaoSkill;