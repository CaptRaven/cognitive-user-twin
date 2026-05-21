"use client";

import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import TwinState from "@/components/TwinState";
import Timeline from "@/components/Timeline";
import CognitionPanel from "@/components/CognitionPanel";
import { Play, SkipForward, RefreshCw, Brain, Activity, Database } from "lucide-react";
import { motion } from "framer-motion";

const API_BASE = "https://cognitive-user-twin-api-production.up.railway.app";

export default function Home() {
  const [state, setState] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [autoPlay, setAutoPlay] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [stateRes, historyRes] = await Promise.all([
        axios.get(`${API_BASE}/simulate/state`),
        axios.get(`${API_BASE}/timeline/`),
      ]);
      setState(stateRes.data);
      setHistory(historyRes.data);
    } catch (err) {
      console.error("Failed to fetch data", err);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    let interval: any;
    if (autoPlay) {
      interval = setInterval(async () => {
        await handleStep();
      }, 5000); // Step every 5 seconds
    }
    return () => clearInterval(interval);
  }, [autoPlay]);

  const handleStart = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/simulate/start`, { user_id: "demo_twin_01" });
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStep = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/simulate/step`);
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#050505] text-white p-6 font-sans selection:bg-cyan-500/30">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyan-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 blur-[120px] rounded-full" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150" />
      </div>

      <div className="relative max-w-[1600px] mx-auto h-[calc(100vh-3rem)] flex flex-col overflow-hidden">
        {/* Header */}
        <header className="flex-none flex justify-between items-center mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Brain size={24} className="text-black" />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tighter uppercase italic">
                Cognitive <span className="text-cyan-500">Twin</span>
              </h1>
              <div className="flex items-center gap-2 text-[10px] font-mono text-white/40 uppercase tracking-widest">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                System Live: Production Mode
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setAutoPlay(!autoPlay)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all ${
                autoPlay 
                ? "bg-cyan-500 border-cyan-400 text-black shadow-lg shadow-cyan-500/40" 
                : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10"
              }`}
            >
              {autoPlay ? <RefreshCw size={18} className="animate-spin" /> : <Play size={18} />}
              <span className="text-sm font-bold uppercase tracking-wide">
                {autoPlay ? "Live Simulation" : "Auto Mode"}
              </span>
            </button>
            
            <button
              onClick={handleStep}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white/60 hover:bg-white/10 transition-all disabled:opacity-50"
            >
              <SkipForward size={18} />
              <span className="text-sm font-bold uppercase tracking-wide">Step</span>
            </button>

            <button
              onClick={handleStart}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white/60 hover:bg-white/10 transition-all"
            >
              <RefreshCw size={18} />
              <span className="text-sm font-bold uppercase tracking-wide">Reset</span>
            </button>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="flex-1 grid grid-cols-12 gap-6 min-h-0 mb-6">
          {/* Left Panel - State */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="col-span-3 h-full overflow-hidden"
          >
            <TwinState state={state} />
          </motion.div>

          {/* Center Panel - Timeline */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="col-span-5 h-full overflow-hidden"
          >
            <Timeline history={history} />
          </motion.div>

          {/* Right Panel - Cognition */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-4 h-full overflow-hidden"
          >
            <CognitionPanel lastEvent={history[history.length - 1]} />
          </motion.div>
        </div>

        {/* Footer Info */}
        <footer className="flex-none flex justify-between items-center text-[10px] font-mono text-white/20 uppercase tracking-[0.2em]">
          <div className="flex gap-8">
            <div className="flex items-center gap-2">
              <Activity size={12} />
              Neural Architecture: v4.2.0-Alpha
            </div>
            <div className="flex items-center gap-2">
              <Database size={12} />
              Vector Store: ChromaDB (140 Nodes)
            </div>
          </div>
          <div>
            Mistral-AI Integration: Active
          </div>
        </footer>
      </div>
    </main>
  );
}
