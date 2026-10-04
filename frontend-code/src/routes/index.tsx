import React, { useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Cloud, Database } from 'lucide-react';

// We import the two isolated components
import { OnlineDashboard } from '@/components/OnlineDashboard';
import { OfflineDashboard } from '@/components/OfflineDashboard';

export const Route = createFileRoute('/')({
  component: SuperProjectWrapper
});

function SuperProjectWrapper() {
  const [mode, setMode] = useState<'CLOUD' | 'OFFLINE'>('CLOUD');

  return (
    <div className="h-screen w-screen relative overflow-hidden bg-[#02050a]">
      {/* Global Mode Switcher - Highest Z-Index */}
      <div className="absolute top-16 left-1/2 -translate-x-1/2 z-[100] flex bg-[#060b13]/90 backdrop-blur-md border border-[#1e293b] rounded-full p-1 shadow-[0_0_20px_rgba(34,211,238,0.1)]">
        <button
          onClick={() => setMode('CLOUD')}
          className={`flex items-center gap-2 px-6 py-1.5 rounded-full font-mono text-[10px] transition-all duration-300 ${
            mode === 'CLOUD' 
              ? 'bg-cyan-500/20 text-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.2)]' 
              : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
          }`}
        >
          <Cloud className="size-3" /> SATQUERY CLOUD (VLM)
        </button>
        <button
          onClick={() => setMode('OFFLINE')}
          className={`flex items-center gap-2 px-6 py-1.5 rounded-full font-mono text-[10px] transition-all duration-300 ${
            mode === 'OFFLINE' 
              ? 'bg-amber-500/20 text-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.2)]' 
              : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
          }`}
        >
          <Database className="size-3" /> OFFLINE ARCHIVE (INDEX)
        </button>
      </div>

      {/* Render the selected dashboard */}
      <div className="w-full h-full animate-in fade-in zoom-in-95 duration-500 ease-out" key={mode}>
        {mode === 'CLOUD' ? <OnlineDashboard /> : <OfflineDashboard />}
      </div>
    </div>
  );
}
