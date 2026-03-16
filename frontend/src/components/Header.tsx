import { useState } from "react";
import { motion } from "framer-motion";
import { Gavel, BarChart3, Info, Menu, X } from "lucide-react";

const navItems = [
  { label: "Início", href: "#", icon: Gavel },
  { label: "Estatísticas", href: "#stats", icon: BarChart3 },
  { label: "Sobre", href: "#about", icon: Info },
];

export function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 glass">
      <div className="container mx-auto flex items-center justify-between h-16 px-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-gold flex items-center justify-center">
            <Gavel className="w-5 h-5 text-primary-foreground" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-display text-lg font-bold text-foreground">Monitor de Leilões</span>
            <span className="text-[10px] font-semibold tracking-wider bg-primary/15 text-primary px-2 py-0.5 rounded-full border border-primary/20">
              MG & SP
            </span>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </a>
          ))}
        </nav>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {mobileOpen && (
        <motion.nav
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden border-t border-border px-4 py-3 space-y-1"
        >
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </a>
          ))}
        </motion.nav>
      )}
    </header>
  );
}
