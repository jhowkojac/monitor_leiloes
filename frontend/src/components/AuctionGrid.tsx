import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { LayoutGrid, List, Flame, DollarSign } from "lucide-react";
import { AuctionCard } from "./AuctionCard";
import { apiService, Leilao, FiltrosLeilao } from "../services/api";

export function AuctionGrid() {
  const [view, setView] = useState<"grid" | "list">("grid");
  const [leiloes, setLeiloes] = useState<Leilao[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtros, setFiltros] = useState<FiltrosLeilao>({});

  useEffect(() => {
    carregarLeiloes();
  }, [filtros]);

  const carregarLeiloes = async () => {
    setLoading(true);
    try {
      const dados = Object.keys(filtros).length > 0 
        ? await apiService.filterLeiloes(filtros)
        : await apiService.getLeiloes();
      setLeiloes(dados);
    } catch (error) {
      console.error('Erro ao carregar leilões:', error);
    } finally {
      setLoading(false);
    }
  };

  const atualizarLeiloes = async () => {
    try {
      await apiService.atualizarLeiloes();
      await carregarLeiloes();
    } catch (error) {
      console.error('Erro ao atualizar leilões:', error);
    }
  };

  const formatarData = (dataString?: string) => {
    if (!dataString) return '';
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const transformarParaCard = (leilao: Leilao) => ({
    title: leilao.titulo,
    city: leilao.cidade,
    state: leilao.estado,
    source: leilao.fonte,
    images: leilao.imagens.length > 0 ? leilao.imagens : (leilao.imagem_url ? [leilao.imagem_url] : []),
    date: formatarData(leilao.data_leilao),
    vehicleCount: 0, // Seria calculado baseado nos veículos do leilão
  });

  return (
    <section className="container mx-auto px-4 py-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground mb-1">
            Leilões Disponíveis
          </h2>
          <p className="text-sm text-muted-foreground">Oportunidades exclusivas em veículos</p>
        </div>

        <div className="flex items-center gap-4">
          {/* Stats pills */}
          <div className="flex gap-2">
            <div className="flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-lg px-3 py-2">
              <Flame className="w-4 h-4 text-primary" />
              <div>
                <div className="text-lg font-bold font-display text-foreground leading-none">{leiloes.length}</div>
                <div className="text-[10px] text-muted-foreground">Ativos</div>
              </div>
            </div>
            <div className="flex items-center gap-2 bg-secondary border border-border rounded-lg px-3 py-2">
              <DollarSign className="w-4 h-4 text-muted-foreground" />
              <div>
                <div className="text-lg font-bold font-display text-foreground leading-none">
                  {leiloes.filter(l => l.valor_inicial).length}
                </div>
                <div className="text-[10px] text-muted-foreground">Com Valores</div>
              </div>
            </div>
          </div>

          {/* View toggle */}
          <div className="flex bg-secondary rounded-lg p-0.5 border border-border">
            <button
              onClick={() => setView("grid")}
              className={`p-2 rounded-md transition-colors ${view === "grid" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"}`}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setView("list")}
              className={`p-2 rounded-md transition-colors ${view === "list" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      )}

      {/* Grid */}
      {!loading && (
        <motion.div
          layout
          className={
            view === "grid"
              ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5"
              : "flex flex-col gap-4"
          }
        >
          {leiloes.map((leilao, i) => (
            <AuctionCard 
              key={leilao.id} 
              {...transformarParaCard(leilao)} 
              index={i} 
            />
          ))}
        </motion.div>
      )}

      {/* Empty state */}
      {!loading && leiloes.length === 0 && (
        <div className="text-center py-12">
          <div className="text-muted-foreground mb-4">Nenhum leilão encontrado</div>
          <button
            onClick={atualizarLeiloes}
            className="bg-gradient-gold text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 transition-opacity"
          >
            Atualizar Leilões
          </button>
        </div>
      )}
    </section>
  );
}
