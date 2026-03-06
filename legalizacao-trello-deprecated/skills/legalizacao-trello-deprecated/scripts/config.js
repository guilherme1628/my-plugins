// Legalizacao Configuration

const LEGALIZACAO_CONFIG = {
  // Board Information
  BOARD_ID: "64136717a7f4757485088703",
  BOARD_NAME: "LEGALIZACAO",

  // Lists
  LISTS: {
    RECEBIDAS: "RECEBIDAS",
    ANALISE: "ANÁLISE",
    EM_ANDAMENTO: "EM ANDAMENTO",
    CONCLUIDO: "CONCLUÍDO"
  },

  // Blue label for legalizacao tasks
  CATEGORY: {
    name: "",
    id: "64136718d88ffb994ecf2015",
    color: "blue"
  },

  // API Configuration
  API_KEY: process.env.TRELLO_API_KEY,
  TOKEN: process.env.TRELLO_TOKEN,
  BASE_URL: "https://api.trello.com/1"
};

// Helper function to get auth params
function getAuthParams() {
  return {
    key: LEGALIZACAO_CONFIG.API_KEY,
    token: LEGALIZACAO_CONFIG.TOKEN
  };
}

// Validate configuration
function validateConfig() {
  if (!LEGALIZACAO_CONFIG.API_KEY || !LEGALIZACAO_CONFIG.TOKEN) {
    throw new Error("TRELLO_API_KEY and TRELLO_TOKEN must be set in environment variables");
  }
}

module.exports = {
  LEGALIZACAO_CONFIG,
  getAuthParams,
  validateConfig
};