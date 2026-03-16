// API Service para integração com FastAPI

export interface Leilao {
  id: string;
  titulo: string;
  cidade: string;
  estado: string;
  fonte: string;
  imagens: string[];
  imagem_url?: string;
  data_leilao?: string;
  valor_inicial?: number;
  url?: string;
  created_at: string;
  updated_at: string;
}

export interface FiltrosLeilao {
  estado?: string;
  fonte?: string;
  cidade?: string;
}

class ApiService {
  private baseURL = process.env.NODE_ENV === 'production' 
    ? 'https://monitor-leiloes.onrender.com/api'
    : 'http://localhost:8000/api';

  async getLeiloes(): Promise<Leilao[]> {
    try {
      const response = await fetch(`${this.baseURL}/leiloes`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar leilões:', error);
      // Fallback para dados mock durante desenvolvimento
      return this.getMockLeiloes();
    }
  }

  async getLeilaoById(id: string): Promise<Leilao | null> {
    try {
      const response = await fetch(`${this.baseURL}/leiloes/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar leilão:', error);
      return null;
    }
  }

  async filterLeiloes(filtros: FiltrosLeilao): Promise<Leilao[]> {
    try {
      const params = new URLSearchParams();
      if (filtros.estado) params.append('estado', filtros.estado);
      if (filtros.fonte) params.append('fonte', filtros.fonte);
      if (filtros.cidade) params.append('cidade', filtros.cidade);

      const response = await fetch(`${this.baseURL}/leiloes?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erro ao filtrar leilões:', error);
      return this.getMockLeiloes();
    }
  }

  async atualizarLeiloes(): Promise<{ total: number; mensagem: string }> {
    try {
      const response = await fetch(`${this.baseURL}/leiloes/atualizar`, {
        method: 'GET',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erro ao atualizar leilões:', error);
      return { total: 0, mensagem: 'Erro ao atualizar' };
    }
  }

  // Dados mock para desenvolvimento
  private getMockLeiloes(): Leilao[] {
    return [
      {
        id: "1",
        titulo: "Edital 3194/2026 - Belo Horizonte",
        cidade: "Belo Horizonte",
        estado: "MG",
        fonte: "detran_mg",
        imagens: ["https://leilao.detran.mg.gov.br/Imagens/visualizar/leiloes/leilao_3194/img_293711_1.jpg"],
        imagem_url: "https://leilao.detran.mg.gov.br/Imagens/visualizar/leiloes/leilao_3194/img_293711_1.jpg",
        data_leilao: "2026-03-25",
        valor_inicial: 5000,
        url: "https://leilao.detran.mg.gov.br/lotes/lista-lotes/3194/2026",
        created_at: "2026-03-16T10:00:00Z",
        updated_at: "2026-03-16T10:00:00Z",
      },
      {
        id: "2", 
        titulo: "Edital 3150/2026 - Belo Horizonte",
        cidade: "Belo Horizonte",
        estado: "MG",
        fonte: "detran_mg",
        imagens: ["https://leilao.detran.mg.gov.br/Imagens/visualizar/leiloes/leilao_3150/img_288703_1.jpg"],
        imagem_url: "https://leilao.detran.mg.gov.br/Imagens/visualizar/leiloes/leilao_3150/img_288703_1.jpg",
        data_leilao: "2026-03-22",
        valor_inicial: 7500,
        url: "https://leilao.detran.mg.gov.br/lotes/lista-lotes/3150/2026",
        created_at: "2026-03-16T10:00:00Z",
        updated_at: "2026-03-16T10:00:00Z",
      },
      {
        id: "3",
        titulo: "Edital 2980/2026 - Uberlândia",
        cidade: "Uberlândia",
        estado: "MG",
        fonte: "detran_mg",
        imagens: [],
        data_leilao: "2026-03-20",
        valor_inicial: 3000,
        url: "https://leilao.detran.mg.gov.br/lotes/lista-lotes/2980/2026",
        created_at: "2026-03-16T10:00:00Z",
        updated_at: "2026-03-16T10:00:00Z",
      },
      {
        id: "4",
        titulo: "Leilão Detran SP - Capital Zona Sul",
        cidade: "São Paulo",
        estado: "SP",
        fonte: "detran_sp",
        imagens: [],
        data_leilao: "2026-03-28",
        valor_inicial: 10000,
        url: "https://www.detran.sp.gov.br/",
        created_at: "2026-03-16T10:00:00Z",
        updated_at: "2026-03-16T10:00:00Z",
      },
      {
        id: "5",
        titulo: "Leilão Detran SP - Campinas",
        cidade: "Campinas",
        estado: "SP",
        fonte: "detran_sp",
        imagens: [],
        data_leilao: "2026-03-27",
        valor_inicial: 8000,
        url: "https://www.detran.sp.gov.br/",
        created_at: "2026-03-16T10:00:00Z",
        updated_at: "2026-03-16T10:00:00Z",
      },
      {
        id: "6",
        titulo: "Superbid - Frota Renovável MG",
        cidade: "Contagem",
        estado: "MG",
        fonte: "superbid",
        imagens: [],
        data_leilao: "2026-03-30",
        valor_inicial: 6000,
        url: "https://www.superbid.net/",
        created_at: "2026-03-16T10:00:00Z",
        updated_at: "2026-03-16T10:00:00Z",
      },
    ];
  }
}

export const apiService = new ApiService();
