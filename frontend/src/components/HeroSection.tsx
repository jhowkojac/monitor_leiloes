import { motion } from "framer-motion";
import { Flame, TrendingUp, Car } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-hero py-16 md:py-24">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-primary/5 blur-3xl" />
        {/* Grid pattern */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: 'linear-gradient(hsl(38 92% 55%) 1px, transparent 1px), linear-gradient(90deg, hsl(38 92% 55%) 1px, transparent 1px)',
          backgroundSize: '60px 60px'
        }} />
      </div>

      <div className="container mx-auto px-4 relative">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-3xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-1.5 mb-6">
            <Flame className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">Leilões em Andamento</span>
          </div>

          <h1 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold mb-5 leading-tight">
            Encontre as melhores{" "}
            <span className="text-gradient-gold">oportunidades</span>{" "}
            em veículos
          </h1>

          <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-10">
            Monitore leilões do Detran MG e SP em tempo real. Filtros inteligentes para achar o veículo ideal pelo menor preço.
          </p>

          <div className="flex flex-wrap justify-center gap-6 mt-8">
            {[
              { icon: Car, label: "Veículos", value: "2.500+" },
              { icon: TrendingUp, label: "Economia média", value: "40%" },
              { icon: Flame, label: "Leilões ativos", value: "31" },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + i * 0.1, duration: 0.5 }}
                className="flex items-center gap-3 bg-card/50 border border-border rounded-xl px-5 py-3"
              >
                <stat.icon className="w-5 h-5 text-primary" />
                <div className="text-left">
                  <div className="text-xl font-bold font-display text-foreground">{stat.value}</div>
                  <div className="text-xs text-muted-foreground">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
