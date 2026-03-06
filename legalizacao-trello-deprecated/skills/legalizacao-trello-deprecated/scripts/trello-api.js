const axios = require('axios');
const { LEGALIZACAO_CONFIG, getAuthParams } = require('./config');

class TrelloAPI {
  constructor() {
    this.baseURL = LEGALIZACAO_CONFIG.BASE_URL;
    this.auth = getAuthParams();
  }

  // Generic request method
  async request(method, endpoint, params = {}) {
    try {
      const response = await axios({
        method,
        url: `${this.baseURL}${endpoint}`,
        params: { ...this.auth, ...params }
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(`Trello API Error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      }
      throw error;
    }
  }

  // Board operations
  async getBoard(boardId) {
    const [lists, cards] = await Promise.all([
      this.request('GET', `/boards/${boardId}/lists`, { fields: 'id,name,closed' }),
      this.request('GET', `/boards/${boardId}/cards`, {
        fields: 'id,name,desc,labels,due,idList,idChecklists',
        checklists: 'all',
        checklist_fields: 'id,name,nameCheckItems'
      })
    ]);

    // Organize cards by list
    const listsWithCards = lists
      .filter(list => !list.closed)
      .map(list => ({
        ...list,
        cards: cards.filter(card => card.idList === list.id)
      }));

    return listsWithCards;
  }

  // List operations
  async findList(boardId, listName) {
    const lists = await this.request('GET', `/boards/${boardId}/lists`, {
      fields: 'id,name,closed'
    });
    return lists.find(list => list.name === listName && !list.closed);
  }

  // Card operations
  async createCard(listId, title, description = '') {
    return this.request('POST', '/cards', {
      idList: listId,
      name: title,
      desc: description,
      pos: 'bottom'
    });
  }

  async moveCard(cardId, listId) {
    return this.request('PUT', `/cards/${cardId}`, {
      idList: listId
    });
  }

  async addLabel(cardId, labelId) {
    return this.request('POST', `/cards/${cardId}/idLabels`, {
      value: labelId
    });
  }

  async setDueDate(cardId, dueDate) {
    return this.request('PUT', `/cards/${cardId}`, {
      due: dueDate
    });
  }

  // Checklist operations
  async createChecklist(cardId, name) {
    return this.request('POST', `/cards/${cardId}/checklists`, {
      name: name,
      pos: 'bottom'
    });
  }

  async addCheckItem(checklistId, name, position = 'bottom') {
    return this.request('POST', `/checklists/${checklistId}/checkItems`, {
      name: name,
      pos: position
    });
  }

  // Search operations
  async findCard(boardId, cardName) {
    const cards = await this.request('GET', `/boards/${boardId}/cards/search`, {
      query: cardName,
      card_fields: 'id,name,idList,labels,due'
    });
    return cards.find(card => card.name.toLowerCase().includes(cardName.toLowerCase()));
  }

  // Utility methods
  formatDateForTrello(dateString) {
    // Convert DD/MM/YYYY to ISO 8601
    if (dateString === '-' || !dateString) return null;

    if (dateString.includes('/')) {
      const [day, month, year] = dateString.split('/');
      return `${year}-${month}-${day}T23:59:59.000Z`;
    }

    return dateString; // Assume already ISO format
  }

  parseDateFromTrello(isoString) {
    if (!isoString) return null;
    return new Date(isoString).toLocaleDateString('pt-BR');
  }
}

module.exports = TrelloAPI;