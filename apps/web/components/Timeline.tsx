"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Clock, ShoppingBag, Info, AlertTriangle, Star, CheckCircle } from "lucide-react";

interface TimelineProps {
  history: any[];
}

export default function Timeline({ history }: TimelineProps) {
  if (!history || history.length === 0) {
    return (
      <div className="p-6 border border-white/10 rounded-2xl bg-black/40 backdrop-blur-md h-full flex items-center justify-center">
        <div className="text-white/40 flex flex-col items-center">
          <Clock size={48} className="mb-4 animate-pulse" />
          <p>Simulation started. Waiting for events...</p>
        </div>
      </div>
    );
  }

  // Reverse history to show newest at top
  const sortedHistory = [...history].reverse();

  const EventIcon = ({ type }: { type: string }) => {
    switch (type) {
      case "hunger": return <ShoppingBag size={14} className="text-cyan-400" />;
      case "exploration": return <Star size={14} className="text-purple-400" />;
      case "frustration": return <AlertTriangle size={14} className="text-amber-500" />;
      case "budget_pressure": return <AlertTriangle size={14} className="text-rose-400" />;
      default: return <Info size={14} className="text-blue-400" />;
    }
  };

  return (
    <div className="p-6 border border-white/10 rounded-2xl bg-black/40 backdrop-blur-md h-full flex flex-col">
      <div className="flex-none flex justify-between items-center mb-6">
        <h2 className="text-white font-bold text-lg flex items-center gap-2">
          <Activity size={20} className="text-cyan-400" />
          Behavioral Timeline
        </h2>
        <span className="text-white/40 text-[10px] font-mono uppercase tracking-widest">Live Feed</span>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 relative">
        <div className="border-l border-white/5 ml-3 pl-6 space-y-8 pb-8">
          <AnimatePresence initial={false}>
            {sortedHistory.map((entry, idx) => (
              <motion.div
                key={entry.timestamp + idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="relative"
              >
                <div className="absolute -left-[31px] top-1 w-2.5 h-2.5 rounded-full bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
                
                <div className="mb-1 flex justify-between items-center">
                  <span className="text-white/40 text-[10px] font-mono">{entry.timestamp.split(' ')[1].slice(0, 5)}</span>
                  <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/5 border border-white/5">
                    <EventIcon type={entry.event.type} />
                    <span className="text-[10px] text-white/60 font-mono capitalize">{entry.event.type.replace('_', ' ')}</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors">
                  <p className="text-white/90 text-sm mb-2">{entry.event.description}</p>
                  
                  {entry.outcome && entry.outcome.rating && (
                    <div className="flex flex-col gap-2">
                      <div className="flex items-center gap-2 text-[11px]">
                        <div className="flex text-amber-500">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <Star key={i} size={10} fill={i < entry.outcome.rating ? "currentColor" : "none"} />
                          ))}
                        </div>
                        <span className="text-white/40">Generated Review</span>
                      </div>
                      <p className="text-white/60 text-xs italic line-clamp-2">"{entry.outcome.text}"</p>
                    </div>
                  )}

                  {entry.outcome && entry.outcome.event_processed && (
                    <div className="flex items-center gap-2 text-[11px] text-cyan-400/80">
                      <CheckCircle size={10} />
                      <span>Cognitive state updated</span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

import { Activity } from "lucide-react";
