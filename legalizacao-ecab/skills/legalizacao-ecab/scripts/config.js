// ECAB Legalizacao Configuration

const ECAB_CONFIG = {
  SUPABASE_URL: process.env.ECAB_SUPABASE_URL,
  API_KEY: process.env.LEGALIZACAO_API_KEY,
};

function validateConfig() {
  if (!ECAB_CONFIG.SUPABASE_URL || !ECAB_CONFIG.API_KEY) {
    throw new Error(
      "ECAB_SUPABASE_URL and LEGALIZACAO_API_KEY must be set in environment variables"
    );
  }
}

module.exports = {
  ECAB_CONFIG,
  validateConfig,
};
