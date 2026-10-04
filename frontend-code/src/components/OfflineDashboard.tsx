import React, { useState, useEffect } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Search, History, CheckSquare, Download, Crosshair, Map, ActivitySquare, AlertTriangle, Layers, Zap } from 'lucide-react';
import { HudFrame } from '@/components/gaia/HudFrame';

export function OfflineDashboard() {
  const [activeNav, setActiveNav] = useState('SEARCH');
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [changeResults, setChangeResults] = useState<any[]>([]);
  const [reviewQueue, setReviewQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query) return;
    setLoading(true);
    try {
      const res = await fetch('/offline/api/v1/search/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 12 })
      });
      const data = await res.json();
      setSearchResults(data.results);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSearch = async (tileId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/offline/api/v1/search/image?tile_id=${tileId}`);
      const data = await res.json();
      setSearchResults(data.results);
      setActiveNav('SEARCH');
      setQuery(`Similar to ${tileId}`);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleScanChange = async () => {
    setLoading(true);
    try {
      const res = await fetch('/offline/api/v1/change/scan', { method: 'POST' });
      const data = await res.json();
      setChangeResults(data.changes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchReviewQueue = async () => {
    try {
      const res = await fetch('/offline/api/v1/review/queue');
      const data = await res.json();
      setReviewQueue(data.queue);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (activeNav === 'REVIEW') {
      fetchReviewQueue();
    }
  }, [activeNav]);

  const handleDecision = async (candidateId: string, status: string) => {
    try {
      await fetch('/offline/api/v1/review/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: candidateId, status })
      });
      fetchReviewQueue();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="h-full w-full bg-[#02050a] text-slate-300 font-sans overflow-hidden flex flex-col selection:bg-cyan-900/50 bg-tech-grid-cyan">
      <header className="h-14 border-b border-[#1e293b]/60 bg-[#060b13]/90 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-50 relative">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <ActivitySquare className="size-5 text-cyan-400" />
            <div className="leading-none flex flex-col">
              <span className="font-mono text-base font-bold tracking-[0.2em] text-white glitch-text">GAIA OFFLINE</span>
              <span className="font-mono text-[8px] tracking-[0.3em] text-cyan-500/80 mt-0.5">ARCHIVE RETRIEVAL & CHANGE</span>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 font-mono text-[10px] tracking-widest text-slate-400">
            {['SEARCH', 'CHANGE SCAN', 'REVIEW'].map(nav => (
                <button 
                  key={nav} 
                  onClick={() => setActiveNav(nav)}
                  className={`transition-colors pb-1 ${activeNav === nav ? 'text-cyan-400 border-b border-cyan-400' : 'hover:text-cyan-300 border-b border-transparent'}`}
                >
                  {nav}
                </button>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-5">
           <div className="flex items-center gap-2 font-mono text-[10px] text-cyan-500/80">
             <span className="size-1.5 rounded-full bg-cyan-400 animate-pulse"></span> LOCAL NETWORK ISOLATION
           </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-6 relative">
        {activeNav === 'SEARCH' && (
          <div className="max-w-6xl mx-auto space-y-6">
            <HudFrame>
              <form onSubmit={handleSearch} className="bg-[#060b13]/80 border border-[#1e293b] p-4 flex gap-4 items-center">
                <Search className="size-5 text-cyan-500/50" />
                <input 
                  type="text" 
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="e.g. 'newly built structures near water' or 'solar panels'" 
                  className="flex-1 bg-transparent border-none outline-none font-mono text-sm text-white placeholder-slate-600"
                />
                <button type="submit" disabled={loading} className="px-6 py-2 bg-cyan-900/30 text-cyan-400 font-mono text-xs border border-cyan-500/50 hover:bg-cyan-900/50 transition-colors disabled:opacity-50">
                  {loading ? 'SEARCHING...' : 'SEARCH'}
                </button>
              </form>
            </HudFrame>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {searchResults.map((res, i) => (
                <HudFrame key={i} className="bg-[#0a0e17] border border-[#1e293b] overflow-hidden group">
                  <div className="aspect-square relative border-b border-[#1e293b]">
                    <img src={res.chip_url} className="w-full h-full object-cover" alt="Tile" />
                    <button 
                        onClick={() => handleImageSearch(res.tile_id)}
                        className="absolute inset-0 bg-cyan-900/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center font-mono text-xs text-white backdrop-blur-sm">
                        FIND SIMILAR
                    </button>
                  </div>
                  <div className="p-3 font-mono text-[10px] space-y-1">
                    <div className="flex justify-between text-cyan-400">
                      <span>{new Date(res.datetime).toISOString().split('T')[0]}</span>
                      <span>CF: {res.score.toFixed(2)}</span>
                    </div>
                    <div className="text-slate-500 truncate" title={res.tile_id}>{res.tile_id}</div>
                    <div className="grid grid-cols-2 gap-x-2 mt-2 pt-2 border-t border-[#1e293b] text-slate-400">
                       <div>VEG: {(res.frac_veg*100).toFixed(0)}%</div>
                       <div>BLT: {(res.frac_built*100).toFixed(0)}%</div>
                    </div>
                  </div>
                </HudFrame>
              ))}
            </div>
          </div>
        )}

        {activeNav === 'CHANGE SCAN' && (
          <div className="max-w-6xl mx-auto space-y-6">
             <div className="flex justify-between items-center">
                <div>
                   <h2 className="font-mono text-lg text-white mb-1">Temporal Change Scanner</h2>
                   <p className="font-mono text-xs text-slate-400">Scans all indexed tiles across time to find persistent thematic changes (PS 2.2.2)</p>
                </div>
                <button onClick={handleScanChange} disabled={loading} className="px-6 py-2 bg-amber-900/30 text-amber-400 font-mono text-xs border border-amber-500/50 hover:bg-amber-900/50 transition-colors">
                  {loading ? 'SCANNING ARCHIVE...' : 'RUN FULL ARCHIVE SCAN'}
                </button>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {changeResults.map((c, i) => (
                <HudFrame key={i} className="bg-[#0a0e17] border border-[#1e293b] flex gap-4 p-4">
                  <div className="flex-1 space-y-4">
                    <div className="flex gap-2">
                      <div className="flex-1 space-y-1">
                        <p className="font-mono text-[9px] text-slate-500">BASELINE</p>
                        <img src={`/offline/api/v1/tiles/chip/${c.evidence.before_tile}.png`} className="w-full aspect-square object-cover border border-[#1e293b]" />
                        <p className="font-mono text-[9px] text-center text-slate-400">{new Date(c.baseline_date).toISOString().split('T')[0]}</p>
                      </div>
                      <div className="flex-1 space-y-1">
                        <p className="font-mono text-[9px] text-slate-500">EARLIEST OBSERVATION</p>
                        <img src={`/offline/api/v1/tiles/chip/${c.evidence.after_tile}.png`} className="w-full aspect-square object-cover border border-amber-500/50" />
                        <p className="font-mono text-[9px] text-center text-amber-400">{new Date(c.earliest_date).toISOString().split('T')[0]}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex-1 font-mono text-[10px] space-y-3">
                    <div>
                      <span className="text-amber-400 text-sm">{c.type.toUpperCase().replace('_', ' ')}</span>
                      <p className="text-slate-500 mt-1">CONFIDENCE: {(c.confidence*100).toFixed(0)}%</p>
                    </div>
                    <div className="space-y-1 pt-3 border-t border-[#1e293b] text-slate-400">
                      <p>Δ NDVI: <span className={c.evidence.delta_ndvi < 0 ? 'text-red-400' : 'text-green-400'}>{c.evidence.delta_ndvi > 0 ? '+' : ''}{c.evidence.delta_ndvi.toFixed(2)}</span></p>
                      <p>Δ NDBI: <span className={c.evidence.delta_ndbi > 0 ? 'text-amber-400' : 'text-slate-400'}>{c.evidence.delta_ndbi > 0 ? '+' : ''}{c.evidence.delta_ndbi.toFixed(2)}</span></p>
                      <p>Δ NDWI: <span className={c.evidence.delta_ndwi > 0 ? 'text-blue-400' : 'text-slate-400'}>{c.evidence.delta_ndwi > 0 ? '+' : ''}{c.evidence.delta_ndwi.toFixed(2)}</span></p>
                    </div>
                  </div>
                </HudFrame>
              ))}
            </div>
          </div>
        )}

        {activeNav === 'REVIEW' && (
          <div className="max-w-4xl mx-auto space-y-6">
             <div className="flex justify-between items-center">
                <div>
                   <h2 className="font-mono text-lg text-white mb-1">Analyst Review Queue</h2>
                   <p className="font-mono text-xs text-slate-400">Confirm or reject candidates to build an audit trail (PS 2.2.5)</p>
                </div>
                <button className="px-4 py-2 bg-slate-800 text-slate-300 font-mono text-xs hover:bg-slate-700 transition-colors flex items-center gap-2">
                  <Download className="size-4" /> EXPORT DECISIONS
                </button>
             </div>

             <div className="space-y-4">
              {reviewQueue.length === 0 && (
                <div className="text-center p-12 border border-dashed border-[#1e293b] text-slate-500 font-mono text-xs">QUEUE IS EMPTY</div>
              )}
              {reviewQueue.map((item, i) => (
                <HudFrame key={i} className="bg-[#0a0e17] border border-[#1e293b] flex gap-6 p-4 items-center">
                   <div className="w-24 h-24 shrink-0">
                      <img src={`/offline/api/v1/tiles/chip/${item.tile_id}.png`} className="w-full h-full object-cover border border-[#1e293b]" />
                   </div>
                   <div className="flex-1 font-mono text-xs space-y-1">
                      <div className="text-cyan-400">TYPE: {item.type.toUpperCase()}</div>
                      <div className="text-slate-400">ID: {item.candidate_id}</div>
                      <div className="text-slate-500">SCORE: {item.score.toFixed(3)}</div>
                   </div>
                   <div className="flex gap-2 shrink-0">
                      <button onClick={() => handleDecision(item.candidate_id, 'confirmed')} className="px-6 py-3 bg-green-900/30 text-green-400 hover:bg-green-900/60 border border-green-500/50 font-mono text-xs transition-colors">
                        CONFIRM
                      </button>
                      <button onClick={() => handleDecision(item.candidate_id, 'rejected')} className="px-6 py-3 bg-red-900/30 text-red-400 hover:bg-red-900/60 border border-red-500/50 font-mono text-xs transition-colors">
                        REJECT
                      </button>
                   </div>
                </HudFrame>
              ))}
             </div>
          </div>
        )}
      </main>
    </div>
  );
}
