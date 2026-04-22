const { ECAB_CONFIG, validateConfig } = require("./config");

class EcabAPI {
  constructor() {
    validateConfig();
    this.baseURL = ECAB_CONFIG.SUPABASE_URL;
    this.apiKey = ECAB_CONFIG.API_KEY;
    this.anonKey = ECAB_CONFIG.SUPABASE_ANON_KEY;
  }

  async createLegalizacao({
    tipo,
    nome_empresa,
    responsavel_id,
    prioridade,
    data_vencimento,
    cliente_id,
    notas,
  }) {
    const url = `${this.baseURL}/functions/v1/create-legalizacao`;

    const body = {
      tipo,
      nome_empresa,
      prioridade: prioridade || "normal",
    };

    if (responsavel_id) body.responsavel_id = responsavel_id;
    if (data_vencimento) body.data_vencimento = data_vencimento;
    if (cliente_id) body.cliente_id = cliente_id;
    if (notas) body.notas = notas;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": this.apiKey,
        Authorization: `Bearer ${this.anonKey}`,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        `ECAB API Error: ${response.status} - ${data.error || JSON.stringify(data)}`
      );
    }

    return data.legalizacao;
  }

  async searchClients(query) {
    const url = `${this.baseURL}/functions/v1/create-legalizacao?q=${encodeURIComponent(query)}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        "X-API-Key": this.apiKey,
        Authorization: `Bearer ${this.anonKey}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        `ECAB API Error: ${response.status} - ${data.error || JSON.stringify(data)}`
      );
    }

    return data.clients;
  }
}

module.exports = EcabAPI;
