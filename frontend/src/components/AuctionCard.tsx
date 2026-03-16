import { useState } from "react";
import { motion } from "framer-motion";
import { MapPin, ExternalLink, ChevronLeft, ChevronRight, Calendar, Tag } from "lucide-react";

interface AuctionCardProps {
  title: string;
  city: string;
  state: string;
  source: string;
  images: string[];
  date?: string;
  vehicleCount?: number;
  index: number;
}

export function AuctionCard({ title, city, state, source, images, date, vehicleCount, index }: AuctionCardProps) {
  const [imgIndex, setImgIndex] = useState(0);
  const [imgError, setImgError] = useState(false);

  const nextImg = () => setImgIndex((i) => (i + 1) % images.length);
  const prevImg = () => setImgIndex((i) => (i - 1 + images.length) % images.length);

  const sourceLabel = source === "detran_mg" ? "Detran MG" : source === "detran_sp" ? "Detran SP" : "Superbid";
  const sourceColor = source === "detran_mg" ? "bg-primary/15 text-primary border-primary/20" : source === "detran_sp" ? "bg-blue-500/15 text-blue-400 border-blue-500/20" : "bg-emerald-500/15 text-emerald-400 border-emerald-500/20";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.4 }}
      className="group bg-card border border-border rounded-xl overflow-hidden hover:border-primary/30 hover:shadow-gold transition-all duration-300"
    >
      {/* Image carousel */}
      <div className="relative aspect-[16/10] bg-secondary overflow-hidden">
        {!imgError ? (
          <img
            src={images[imgIndex]}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground">
            <Tag className="w-10 h-10 opacity-30" />
          </div>
        )}

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-card/80 via-transparent to-transparent" />

        {/* Source badge */}
        <div className={`absolute top-3 left-3 text-[11px] font-semibold px-2.5 py-1 rounded-full border ${sourceColor}`}>
          {sourceLabel}
        </div>

        {/* Carousel controls */}
        {images.length > 1 && (
          <>
            <button
              onClick={(e) => { e.preventDefault(); prevImg(); }}
              className="absolute left-2 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-card/70 text-foreground flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-card"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={(e) => { e.preventDefault(); nextImg(); }}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-card/70 text-foreground flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-card"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
              {images.map((_, i) => (
                <div
                  key={i}
                  className={`w-1.5 h-1.5 rounded-full transition-colors ${i === imgIndex ? "bg-primary" : "bg-foreground/30"}`}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-display font-semibold text-sm text-foreground mb-2 line-clamp-2 group-hover:text-primary transition-colors">
          {title}
        </h3>

        <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-3">
          <MapPin className="w-3.5 h-3.5 text-primary/60" />
          <span>{city}</span>
          <span className="text-border">·</span>
          <span className="font-semibold text-primary/80">{state}</span>
        </div>

        {date && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-3">
            <Calendar className="w-3.5 h-3.5" />
            <span>{date}</span>
          </div>
        )}

        <a
          href="#"
          className="flex items-center justify-center gap-1.5 w-full h-9 rounded-lg bg-secondary text-sm font-medium text-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
        >
          Ver detalhes
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </motion.div>
  );
}
