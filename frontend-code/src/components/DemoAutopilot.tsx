import { useState, useEffect, useRef } from 'react';
import { Play, Pause, Square } from 'lucide-react';

export function DemoAutopilot() {
  const [playing, setPlaying] = useState(false);
  const [step, setStep] = useState(0);
  const timerRef = useRef<any>(null);

  const actions = [
    { type: 'wait', ms: 5000, subtitle: 'Hello. Welcome to the demonstration of GAIA, our Geospatial Artificial Intelligence Assistant.' },
    { type: 'wait', ms: 5000, subtitle: 'To adhere strictly to PS 26227, this core platform operates entirely on-premises on an air-gapped machine.' },
    { type: 'click', selector: '#demo-mode-offline', subtitle: 'Let\'s begin in the Offline Archive, the heart of our local intelligence database.' },
    { type: 'wait', ms: 1000, subtitle: 'Let\'s begin in the Offline Archive, the heart of our local intelligence database.' },
    { type: 'click', selector: '[data-demo-nav="SEARCH"]', subtitle: 'Because we use a localized Vision Transformer, analysts can query historical tiles using natural language.' },
    { type: 'wait', ms: 1000, subtitle: 'Because we use a localized Vision Transformer, analysts can query historical tiles using natural language.' },
    { type: 'type', selector: '#demo-search-input', text: 'newly built structures near water', subtitle: 'When we search for "newly built structures near water"...' },
    { type: 'wait', ms: 500, subtitle: '...the local model instantly retrieves matching tiles based on semantic vector similarity.' },
    { type: 'click', selector: '#demo-search-btn', subtitle: '...the local model instantly retrieves matching tiles based on semantic vector similarity.' },
    { type: 'wait', ms: 4000, subtitle: '...the local model instantly retrieves matching tiles based on semantic vector similarity.' },
    { type: 'click', selector: '[data-demo-similar]', index: 0, subtitle: 'Furthermore, we support unsupervised clustering. By selecting a tile and clicking "Find Similar"...' },
    { type: 'wait', ms: 4000, subtitle: '...the system clusters comparable sites. Crucially, CRS and Geotransform are preserved for every tile.' },
    { type: 'click', selector: '[data-demo-nav="CHANGE SCAN"]', subtitle: 'Next, let\'s look at the Temporal Change Scanner.' },
    { type: 'wait', ms: 1000, subtitle: 'Rather than requiring human oversight, it autonomously scans the history of every spatial cell.' },
    { type: 'click', selector: '#demo-scan-btn', subtitle: 'Rather than requiring human oversight, it autonomously scans the history of every spatial cell.' },
    { type: 'wait', ms: 4000, subtitle: 'The outputs are structured. It categorizes specific phenomenologies like "Construction" or "Clearance"...' },
    { type: 'wait', ms: 4000, subtitle: '...and suppresses false alarms by anchoring detections against seasonal baselines and tracking NDVI shifts.' },
    { type: 'click', selector: '[data-demo-nav="REVIEW"]', subtitle: 'All automated detections are routed to the Analyst Review Queue.' },
    { type: 'wait', ms: 1000, subtitle: 'By confirming or rejecting candidates, the analyst establishes an auditable track record.' },
    { type: 'click', selector: '[data-demo-confirm]', index: 0, subtitle: 'By confirming or rejecting candidates, the analyst establishes an auditable track record.' },
    { type: 'wait', ms: 1000, subtitle: 'This human-in-the-loop feedback dynamically reranks future queues.' },
    { type: 'click', selector: '[data-demo-reject]', index: 0, subtitle: 'This human-in-the-loop feedback dynamically reranks future queues.' },
    { type: 'wait', ms: 2000, subtitle: 'Finally, let\'s look at the Interactive Mode to demonstrate the future of geospatial UX.' },
    { type: 'click', selector: '#demo-mode-interactive', subtitle: 'Finally, let\'s look at the Interactive Mode to demonstrate the future of geospatial UX.' },
    { type: 'wait', ms: 2000, subtitle: 'When an analyst uploads a raw 16-bit GeoTIFF, the backend dynamically normalizes the data...' },
    { type: 'upload', selector: 'input[type="file"]', fileUrl: '', fileName: 'recent_download_sentinel2.png', fileType: 'image/png', subtitle: '...so the VLM can read it natively.' },
    { type: 'wait', ms: 2000, subtitle: 'But more importantly, an intelligent auto-ingestion pipeline runs in the background...' },
    { type: 'type', selector: 'textarea', text: 'Describe the structures in this image.', subtitle: '...silently indexing this new imagery directly into the Offline FAISS Archive.' },
    { type: 'wait', ms: 500, subtitle: 'The database is entirely self-building.' },
    { type: 'click', selector: 'button[type="submit"]', subtitle: 'The database is entirely self-building.' },
    { type: 'wait', ms: 5000, subtitle: 'Thank you for your time. We believe GAIA represents the next generation of Earth observation intelligence.' },
    { type: 'wait', ms: 3000, subtitle: 'Demo Complete.' }
  ];

  const executeAction = async (action: any) => {
    if (action.type === 'wait') {
      return new Promise(r => { timerRef.current = setTimeout(r, action.ms); });
    }
    if (action.type === 'click') {
      const els = document.querySelectorAll(action.selector);
      const el = els[action.index || 0] as HTMLElement;
      if (el) el.click();
      return new Promise(r => { timerRef.current = setTimeout(r, 500); });
    }
    if (action.type === 'type') {
      const el = document.querySelector(action.selector) as HTMLInputElement | HTMLTextAreaElement;
      if (el) {
        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set 
          || Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
        for (let i = 1; i <= action.text.length; i++) {
          const partial = action.text.substring(0, i);
          nativeSetter?.call(el, partial);
          el.dispatchEvent(new Event('input', { bubbles: true }));
          await new Promise(r => setTimeout(r, 40));
        }
      }
      return new Promise(r => { timerRef.current = setTimeout(r, 500); });
    }
    if (action.type === 'upload') {
      const el = document.querySelector(action.selector) as HTMLInputElement;
      if (el) {
        try {
          const canvas = document.createElement('canvas');
          canvas.width = 256; canvas.height = 256;
          const ctx = canvas.getContext('2d');
          if (ctx) {
             ctx.fillStyle = '#1e293b'; ctx.fillRect(0,0,256,256);
             ctx.fillStyle = '#06b6d4'; ctx.fillRect(50,50,100,100);
          }
          canvas.toBlob((blob) => {
             if (blob) {
                const file = new File([blob], action.fileName, { type: action.fileType });
                const dt = new DataTransfer();
                dt.items.add(file);
                el.files = dt.files;
                el.dispatchEvent(new Event('change', { bubbles: true }));
             }
          }, 'image/png');
        } catch (e) {
          console.error('Upload simulation failed', e);
        }
      }
      return new Promise(r => { timerRef.current = setTimeout(r, 1000); });
    }
  };

  const runLoop = async () => {
    let currentStep = step;
    while (currentStep < actions.length) {
      setStep(currentStep);
      await executeAction(actions[currentStep]);
      currentStep++;
    }
    setPlaying(false);
    setStep(0);
  };

  useEffect(() => {
    if (playing) {
      runLoop();
    } else {
      if (timerRef.current) clearTimeout(timerRef.current);
    }
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [playing]);

  const activeSubtitle = actions[step]?.subtitle || '';

  return (
    <>
      {/* Subtitles Overlay */}
      {playing && activeSubtitle && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-[9998] w-3/4 max-w-4xl pointer-events-none">
          <div className="bg-black/60 backdrop-blur-sm text-white font-sans text-xl md:text-2xl font-medium text-center p-4 rounded-xl shadow-[0_0_30px_rgba(0,0,0,0.5)] border border-white/10 mx-auto">
            {activeSubtitle}
          </div>
        </div>
      )}

      {/* Autopilot Controls */}
      <div className="fixed bottom-4 right-4 z-[9999] bg-[#060b13]/90 backdrop-blur-md border border-[#1e293b] p-3 rounded-xl shadow-2xl flex items-center gap-4 text-xs font-mono text-slate-300">
        <div className="flex items-center gap-2">
          <button onClick={() => setPlaying(!playing)} className="p-2 bg-cyan-900/30 text-cyan-400 rounded-lg hover:bg-cyan-900/50">
            {playing ? <Pause className="size-4" /> : <Play className="size-4" />}
          </button>
          <button onClick={() => { setPlaying(false); setStep(0); }} className="p-2 bg-slate-800 text-slate-400 rounded-lg hover:bg-slate-700">
            <Square className="size-4" />
          </button>
        </div>
        <div className="w-48">
          <div className="text-[10px] text-cyan-500 mb-1">AUTOPILOT DEMO</div>
          <div className="truncate text-white">Step {step + 1} / {actions.length}</div>
          <div className="w-full bg-slate-800 h-1 mt-1 rounded-full overflow-hidden">
             <div className="bg-cyan-400 h-full transition-all duration-300" style={{ width: `${(step / Math.max(1, actions.length-1)) * 100}%` }}></div>
          </div>
        </div>
      </div>
    </>
  );
}
