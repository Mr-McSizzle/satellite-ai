import { useState, useEffect, useRef } from 'react';

export function DemoAutopilot() {
  const [playing, setPlaying] = useState(false);
  const [step, setStep] = useState(0);
  const timerRef = useRef<any>(null);

  const actions = [
    { type: 'wait', ms: 7000, subtitle: 'Hello. Welcome to the demonstration of GAIA, our Geospatial Artificial Intelligence Assistant.' },
    { type: 'wait', ms: 7000, subtitle: 'To adhere strictly to PS 26227, this core platform operates entirely on-premises on an air-gapped machine.' },
    { type: 'click', selector: '#demo-mode-offline', subtitle: 'Let\'s begin in the Offline Archive, the heart of our local intelligence database.' },
    { type: 'wait', ms: 2000, subtitle: 'Let\'s begin in the Offline Archive, the heart of our local intelligence database.' },
    { type: 'click', selector: '[data-demo-nav="SEARCH"]', subtitle: 'Because we use a localized Vision Transformer, analysts can query historical tiles using natural language.' },
    { type: 'wait', ms: 4000, subtitle: 'Because we use a localized Vision Transformer, analysts can query historical tiles using natural language.' },
    { type: 'type', selector: '#demo-search-input', text: 'newly built structures near water', subtitle: 'When we search for "newly built structures near water"...' },
    { type: 'wait', ms: 1000, subtitle: '...the local model instantly retrieves matching tiles based on semantic vector similarity.' },
    { type: 'click', selector: '#demo-search-btn', subtitle: '...the local model instantly retrieves matching tiles based on semantic vector similarity.' },
    { type: 'wait', ms: 7000, subtitle: '...the local model instantly retrieves matching tiles based on semantic vector similarity.' },
    { type: 'click', selector: '[data-demo-similar]', index: 0, subtitle: 'Furthermore, we support unsupervised clustering. By selecting a tile and clicking "Find Similar"...' },
    { type: 'wait', ms: 7000, subtitle: '...the system clusters comparable sites. Crucially, CRS and Geotransform are preserved for every tile.' },
    { type: 'click', selector: '[data-demo-nav="CHANGE SCAN"]', subtitle: 'Next, let\'s look at the Temporal Change Scanner.' },
    { type: 'wait', ms: 3000, subtitle: 'Rather than requiring human oversight, it autonomously scans the history of every spatial cell.' },
    { type: 'click', selector: '#demo-scan-btn', subtitle: 'Rather than requiring human oversight, it autonomously scans the history of every spatial cell.' },
    { type: 'wait', ms: 7000, subtitle: 'The outputs are structured. It categorizes specific phenomenologies like "Construction" or "Clearance"...' },
    { type: 'wait', ms: 8000, subtitle: '...and suppresses false alarms by anchoring detections against seasonal baselines and tracking NDVI shifts.' },
    { type: 'click', selector: '[data-demo-nav="REVIEW"]', subtitle: 'All automated detections are routed to the Analyst Review Queue.' },
    { type: 'wait', ms: 4000, subtitle: 'By confirming or rejecting candidates, the analyst establishes an auditable track record.' },
    { type: 'click', selector: '[data-demo-confirm]', index: 0, subtitle: 'By confirming or rejecting candidates, the analyst establishes an auditable track record.' },
    { type: 'wait', ms: 3000, subtitle: 'This human-in-the-loop feedback dynamically reranks future queues.' },
    { type: 'click', selector: '[data-demo-reject]', index: 0, subtitle: 'This human-in-the-loop feedback dynamically reranks future queues.' },
    { type: 'wait', ms: 4000, subtitle: 'Finally, let\'s look at the Interactive Mode to demonstrate the future of geospatial UX.' },
    { type: 'click', selector: '#demo-mode-interactive', subtitle: 'Finally, let\'s look at the Interactive Mode to demonstrate the future of geospatial UX.' },
    { type: 'wait', ms: 2000, subtitle: 'I will now upload a local file to demonstrate.' },
    { type: 'wait', ms: 1000, subtitle: '' } // Clear subtitle at the end
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
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPlaying((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

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
        <div className="fixed bottom-12 left-1/2 -translate-x-1/2 z-[9998] w-3/4 max-w-4xl pointer-events-none">
          <div className="bg-black/60 backdrop-blur-sm text-white font-sans text-2xl md:text-3xl font-medium text-center p-6 rounded-xl shadow-[0_0_30px_rgba(0,0,0,0.5)] border border-white/10 mx-auto leading-relaxed">
            {activeSubtitle}
          </div>
        </div>
      )}
    </>
  );
}
