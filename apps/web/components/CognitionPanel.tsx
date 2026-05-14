"use client";

import { motion } from "framer-motion";
import { Brain, Search, MessageSquare, ShieldCheck, Database, GitBranch } from "lucide-react";

interface CognitionPanelProps {
  lastEvent: any;
}

export default function CognitionPanel({ lastEvent }: CognitionPanelProps) {
  if (!lastEvent || !lastEvent.outcome || !lastEvent.outcome.reasoning) {
    return (
      <div className="p-6 border border-white/10 rounded-2xl bg-black/40 backdrop-blur-md h-full flex items-center justify-center">
        <div className="text-white/40 flex flex-col items-center text-center">
          <Brain size={48} className="mb-4" />
          <p className="max-w-[200px]">Neural traces will appear during decision events.</p>
        </div>
      </div>
    );
  }

  const { outcome } = lastEvent;

  return (
    <div className="p-6 border border-white/10 rounded-2xl bg-black/40 backdrop-blur-md h-full flex flex-col">
      <h2 className="text-white font-bold text-lg mb-6 flex-none flex items-center gap-2">
        <GitBranch size={20} className="text-purple-400" />
        Cognition Trace
      </h2>

      <div className="flex-1 overflow-y-auto pr-2 space-y-6">
        {/* Reasoning Steps */}
        <div className="space-y-4">
          <h3 className="text-white/40 text-[10px] font-mono uppercase tracking-widest flex items-center gap-2">
            <Search size={12} />
            Reasoning Chain
          </h3>
          <div className="space-y-3">
            {outcome.reasoning.map((step: string, i: number) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex gap-3"
              >
                <div className="text-purple-500 font-mono text-[10px] pt-1">{i + 1}.</div>
                <div className="p-3 rounded-xl bg-purple-500/5 border border-purple-500/10 text-white/80 text-xs leading-relaxed flex-1">
                  {step}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Cognitive Factors */}
        {outcome.factors && (
          <div className="space-y-4">
            <h3 className="text-white/40 text-[10px] font-mono uppercase tracking-widest flex items-center gap-2">
              <Database size={12} />
              Influence Vectors
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(outcome.factors).map(([factor, score]: [string, any]) => (
                <div key={factor} className="p-2 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] text-white/60 capitalize">{factor.replace('_', ' ')}</span>
                    <span className="text-[10px] text-purple-400 font-mono">{Math.abs(score as number).toFixed(2)}</span>
                  </div>
                  <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-purple-500" 
                      style={{ width: `${Math.min(100, (score as number) * 100)}%` }} 
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Memory Influence */}
        <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/10">
          <div className="flex items-center gap-2 mb-3">
            <ShieldCheck size={14} className="text-blue-400" />
            <span className="text-white text-xs font-semibold">Memory Integration</span>
          </div>
          <p className="text-white/60 text-[11px] leading-relaxed">
            Retrieval query weighted by current emotional valence and temporal decay. 
            Cross-referenced 140 candidates from ChromaDB.
          </p>
        </div>
      </div>
    </div>
  );
}
