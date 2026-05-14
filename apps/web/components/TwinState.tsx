"use client";

import { motion } from "framer-motion";
import { User, Heart, Zap, Brain, Shield, DollarSign, Activity } from "lucide-react";

interface TwinStateProps {
  state: any;
}

const Metric = ({ icon: Icon, label, value, color }: any) => (
  <div className="mb-6">
    <div className="flex justify-between items-center mb-2">
      <div className="flex items-center gap-2 text-white/60 text-sm">
        <Icon size={16} className={color} />
        <span>{label}</span>
      </div>
      <span className="text-white font-mono text-xs">{(value * 100).toFixed(0)}%</span>
    </div>
    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${value * 100}%` }}
        className={`h-full ${color.replace('text-', 'bg-')}`}
        transition={{ duration: 1, ease: "easeOut" }}
      />
    </div>
  </div>
);

export default function TwinState({ state }: TwinStateProps) {
  if (!state || state.status === "not_initialized") {
    return (
      <div className="p-6 border border-white/10 rounded-2xl bg-black/40 backdrop-blur-md h-full flex items-center justify-center">
        <div className="text-white/40 animate-pulse flex flex-col items-center">
          <Brain size={48} className="mb-4" />
          <p>Awaiting Initialization...</p>
        </div>
      </div>
    );
  }

  const { features, metadata, environment } = state;

  return (
    <div className="p-6 border border-white/10 rounded-2xl bg-black/40 backdrop-blur-md h-full overflow-y-auto">
      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <User className="text-white" />
        </div>
        <div>
          <h2 className="text-white font-bold text-lg">{metadata?.name || "Anonymous Twin"}</h2>
          <p className="text-cyan-400 text-xs font-mono uppercase tracking-wider">{metadata?.archetype || "Simulated Agent"}</p>
        </div>
      </div>

      <div className="space-y-2 mb-8">
        <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex justify-between items-center">
          <span className="text-white/40 text-xs">Environment</span>
          <span className="text-white text-xs font-mono">{environment?.time.split(' ')[1].slice(0, 5)} | {environment?.weather}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-1">
        <Metric icon={Heart} label="Loyalty" value={features.loyalty_score} color="text-rose-500" />
        <Metric icon={Zap} label="Emotionality" value={features.emotionality} color="text-amber-500" />
        <Metric icon={Brain} label="Exploration" value={features.exploration_tendency} color="text-purple-500" />
        <Metric icon={Shield} label="Consistency" value={features.temporal_consistency} color="text-emerald-500" />
        <Metric icon={DollarSign} label="Budget Sensitivity" value={features.price_sensitivity} color="text-cyan-500" />
        <Metric icon={Activity} label="Cognitive Load" value={1 - features.temporal_consistency} color="text-blue-500" />
      </div>

      <div className="mt-8 p-4 rounded-xl bg-cyan-500/5 border border-cyan-500/10">
        <h3 className="text-cyan-400 text-[10px] font-mono uppercase mb-2 tracking-widest">Active Neural State</h3>
        <p className="text-white/80 text-sm leading-relaxed">
          {features.emotionality > 0.7 ? "Twin is currently in a highly reactive emotional state. " : ""}
          {features.temporal_consistency < 0.4 ? "High cognitive fatigue detected. Preference for convenience is elevated. " : "Neural consistency is stable."}
        </p>
      </div>
    </div>
  );
}
