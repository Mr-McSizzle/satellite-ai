import { useState, useEffect, useRef } from 'react';
import { Play, Pause, Square } from 'lucide-react';

export function DemoAutopilot() {
  const [playing, setPlaying] = useState(false);
  const [step, setStep] = useState(0);
  const timerRef = useRef<any>(null);

  const actions = [
    { type: 'wait', ms: 2000, desc: 'Intro...' },
    { type: 'click', selector: '#demo-mode-offline', desc: 'Switch to Offline Archive' },
    { type: 'wait', ms: 1000, desc: 'View offline' },
    { type: 'click', selector: '[data-demo-nav="SEARCH"]', desc: 'Go to Search' },
    { type: 'wait', ms: 1000, desc: 'Prepare search' },
    { type: 'type', selector: '#demo-search-input', text: 'newly built structures near water', desc: 'Typing search' },
    { type: 'wait', ms: 500, desc: 'Pause' },
    { type: 'click', selector: '#demo-search-btn', desc: 'Search' },
    { type: 'wait', ms: 4000, desc: 'Wait for results' },
    { type: 'click', selector: '[data-demo-similar]', index: 0, desc: 'Find similar' },
    { type: 'wait', ms: 4000, desc: 'Clustering results' },
    { type: 'click', selector: '[data-demo-nav="CHANGE SCAN"]', desc: 'Go to Change Scan' },
    { type: 'wait', ms: 1000, desc: 'Prepare scan' },
    { type: 'click', selector: '#demo-scan-btn', desc: 'Run scan' },
    { type: 'wait', ms: 4000, desc: 'Wait for scan' },
    { type: 'click', selector: '[data-demo-nav="REVIEW"]', desc: 'Go to Review Queue' },
    { type: 'wait', ms: 1000, desc: 'Prepare review' },
    { type: 'click', selector: '[data-demo-confirm]', index: 0, desc: 'Confirm first' },
    { type: 'wait', ms: 1000, desc: 'Pause' },
    { type: 'click', selector: '[data-demo-reject]', index: 0, desc: 'Reject second (now first)' },
    { type: 'wait', ms: 2000, desc: 'Pause' },
    { type: 'click', selector: '#demo-mode-interactive', desc: 'Switch to Interactive' },
    { type: 'wait', ms: 5000, desc: 'End of automated demo (User uploads file manually)' },
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
      const el = document.querySelector(action.selector) as HTMLInputElement;
      if (el) {
        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
        // Type character by character
        for (let i = 1; i <= action.text.length; i++) {
          const partial = action.text.substring(0, i);
          nativeSetter?.call(el, partial);
          el.dispatchEvent(new Event('input', { bubbles: true }));
          await new Promise(r => setTimeout(r, 50));
        }
      }
      return new Promise(r => { timerRef.current = setTimeout(r, 500); });
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

  return (
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
        <div className="truncate text-white">{actions[step]?.desc || 'Ready'}</div>
        <div className="w-full bg-slate-800 h-1 mt-1 rounded-full overflow-hidden">
           <div className="bg-cyan-400 h-full transition-all duration-300" style={{ width: `${(step / Math.max(1, actions.length-1)) * 100}%` }}></div>
        </div>
      </div>
    </div>
  );
}
