import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, SlidersHorizontal, RotateCcw, MapPin, Building2, Map } from "lucide-react";

const estados = ["Todos", "Minas Gerais", "São Paulo"];
const fontes = ["Todas", "Detran MG", "Detran SP", "Superbid"];

export function FilterSection() {
  const [estado, setEstado] = useState("Todos");
  const [fonte, setFonte] = useState("Todas");
  const [cidade, setCidade] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <section className="container mx-auto px-4 -mt-8 relative z-10">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
        className="bg-card border border-border rounded-2xl p-6 shadow-card"
      >
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-primary" />
            <h2 className="font-display text-lg font-semibold text-foreground">Filtrar Leilões</h2>
          </div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <SlidersHorizontal className="w-4 h-4" />
            Filtros Avançados
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="space-y-1.5">
            <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <MapPin className="w-3.5 h-3.5" /> Estado
            </label>
            <select
              value={estado}
              onChange={(e) => setEstado(e.target.value)}
              className="w-full h-10 rounded-lg bg-input border border-border px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow"
            >
              {estados.map((e) => (
                <option key={e} value={e}>{e}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Building2 className="w-3.5 h-3.5" /> Fonte
            </label>
            <select
              value={fonte}
              onChange={(e) => setFonte(e.target.value)}
              className="w-full h-10 rounded-lg bg-input border border-border px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow"
            >
              {fontes.map((f) => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Map className="w-3.5 h-3.5" /> Cidade
            </label>
            <input
              type="text"
              placeholder="Buscar cidade..."
              value={cidade}
              onChange={(e) => setCidade(e.target.value)}
              className="w-full h-10 rounded-lg bg-input border border-border px-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow"
            />
          </div>

          <div className="flex items-end gap-2">
            <button className="flex-1 h-10 bg-gradient-gold rounded-lg text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity flex items-center justify-center gap-1.5">
              <Search className="w-4 h-4" />
              Filtrar
            </button>
            <button
              onClick={() => { setEstado("Todos"); setFonte("Todas"); setCidade(""); }}
              className="h-10 w-10 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-secondary flex items-center justify-center transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>

        <AnimatePresence>
          {showAdvanced && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="pt-4 mt-4 border-t border-border text-sm text-muted-foreground">
                Mais filtros em breve: faixa de preço, tipo de veículo, ano...
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </section>
  );
}
