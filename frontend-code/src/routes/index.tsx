import React, { useState, useEffect, useRef } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Upload, Crosshair, Map, Activity, Database, ChevronRight, ActivitySquare, Terminal, Eye, Navigation, Layers, Zap, Search, SlidersHorizontal, Settings2, BarChart4, ChevronUp, ChevronDown, Satellite, ShieldAlert, Binary, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';

import { uploadImage } from "@/api/upload";
import { runBackendAnalysis } from "@/lib/satquery/analysis";
import type { UploadedImage, AnalysisResult } from "@/lib/satquery/types";

export const Route = createFileRoute('/')({
  component: Dashboard
});

function Dashboard() {
  // UI State
  const [uploadedImagePreview, setUploadedImagePreview] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanStage, setScanStage] = useState<string | null>(null);
  const [scanProgress, setScanProgress] = useState(0);
    const [isTargeting, setIsTargeting] = useState(false);
    const [isMapMode, setIsMapMode] = useState(false);
    const [showLayersPanel, setShowLayersPanel] = useState(true);
  
  // Real Backend State
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<{role: string, content: string, isRetryable?: boolean, retryQuery?: string}[]>([]);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [traceLog, setTraceLog] = useState<{time: string, msg: string}[]>([]);
  
  const [query, setQuery] = useState("");
  const [timelineIndex, setTimelineIndex] = useState(3);
  const [activeLayers, setActiveLayers] = useState<string[]>([]);
  
  const [activeNav, setActiveNav] = useState('INTELLIGENCE');
  const [activeModality, setActiveModality] = useState('OPTICAL');
  const [activeTimeframe, setActiveTimeframe] = useState('AFTER');
  
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatScrollRef.current) {
        chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatHistory, isScanning, activeNav]);

  const addTrace = (msg: string) => {
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setTraceLog(prev => [...prev, { time, msg }]);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>, forceRole?: 'before' | 'after') => {
    if (e.target.files && e.target.files.length > 0) {
      if (uploadedImages.length >= 2 && !forceRole) return;
      
      const newFiles = Array.from(e.target.files).slice(0, 2);
      addTrace(`INGESTING ${newFiles.length} IMAGE(S)...`);
      
      try {
        const newUploadedImages: UploadedImage[] = [];
        let i = 0;
        for (const file of newFiles) {
            const uploaded = await uploadImage(file, "optical");
            let assignedRole = forceRole;
            if (!assignedRole) {
                assignedRole = (uploadedImages.length + i === 0) ? "before" : "after";
            }
            
            newUploadedImages.push({
                slot: assignedRole === "before" ? "primary" : "secondary",
                file: file,
                name: file.name,
                modality: "optical",
                reference: uploaded.reference,
                previewUrl: URL.createObjectURL(file),
                sizeBytes: file.size,
                format: file.type,
                width: 2048,
                height: 2048,
                mayCarryGeoMetadata: true,
                role: assignedRole
            });
            i++;
            addTrace(`UPLOAD COMPLETE: REF ${uploaded.reference.substring(0,8)}... AS ${assignedRole.toUpperCase()}`);
        }
        
        setUploadedImages(prev => {
            const combined = [...prev];
            newUploadedImages.forEach(img => {
                const existingIdx = combined.findIndex(e => e.role === img.role);
                if (existingIdx >= 0) combined[existingIdx] = img;
                else combined.push(img);
            });
            // Ensure BEFORE is always index 0 if it exists
            combined.sort((a, b) => (a.role === 'before' ? -1 : 1));
            return combined.slice(0, 2);
        });
        
        if (!uploadedImagePreview) {
          setUploadedImagePreview(URL.createObjectURL(newFiles[0]));
        }
      } catch (err) {
        addTrace(`UPLOAD FAILED: ${err}`);
        setChatHistory(prev => [...prev, { role: "system", content: "File validation failed. Unsupported format." }]);
      }
    }
  };

  const swapImages = () => {
      setUploadedImages(prev => {
          if (prev.length !== 2) return prev;
          const swapped = [
              { ...prev[1], role: 'before', slot: 'primary' },
              { ...prev[0], role: 'after', slot: 'secondary' }
          ] as UploadedImage[];
          return swapped;
      });
      addTrace("SWAPPED BEFORE / AFTER IMAGES");
  };

  const clearImage = (roleToClear: string) => {
      setUploadedImages(prev => prev.filter(img => img.role !== roleToClear));
      if (uploadedImages.length === 1) setUploadedImagePreview(null);
      addTrace(`CLEARED ${roleToClear.toUpperCase()} IMAGE`);
  };

  const runAnalysis = async (customQuery?: string) => {
    if (isScanning) return; 
    const q = customQuery || query || "Analyze image";
    if (!q.trim()) return;
    
    const isChangeQuery = q.toLowerCase().includes('change') || q.toLowerCase().includes('before') || q.toLowerCase().includes('after') || q.toLowerCase().includes('compare');
    const hasBefore = uploadedImages.some(i => i.role === 'before');
    const hasAfter = uploadedImages.some(i => i.role === 'after');
    
    // Explicit partial upload guards
    if (isChangeQuery && !sessionId) {
        if (hasBefore && !hasAfter) {
            setChatHistory(prev => [...prev, { role: "system", content: "Add an AFTER image to enable temporal comparison." }]);
            return;
        }
        if (!hasBefore && hasAfter) {
            setChatHistory(prev => [...prev, { role: "system", content: "Add a BEFORE image to enable temporal comparison." }]);
            return;
        }
    }

    if (uploadedImages.length === 0 && !sessionId) return;

    setQuery("");
    setIsScanning(true);
    addTrace(`QUERY CLASSIFIED: ${q}`);
    
    let currentStageIndex = 0;
    const stages = ["COMPARING IMAGERY...", "ANALYZING TEMPORAL CHANGE...", "GENERATING ANSWER..."];
    setScanStage(stages[0]);
    setScanProgress(10);
    
    const animationInterval = setInterval(() => {
        currentStageIndex = Math.min(currentStageIndex + 1, stages.length - 1);
        setScanStage(stages[currentStageIndex]);
        setScanProgress(p => Math.min(p + 15, 95));
    }, 800);

    setChatHistory(prev => [...prev, { role: "user", content: q }]);
    setActiveNav('INTELLIGENCE'); 

    try {
        const backendResult = await runBackendAnalysis(q, sessionId ? [] : uploadedImages, sessionId || undefined);
        clearInterval(animationInterval);
        setScanProgress(100);
        setScanStage("COMPLETE");
        
        if (backendResult.status === "failed") {
            addTrace(`GAIA execution failed.`);
            setChatHistory(prev => [...prev, { role: "system", content: "GAIA couldn't complete this analysis.", isRetryable: true, retryQuery: q }]);
            setIsScanning(false);
            return;
        }

        setResult(backendResult);
        
        if (backendResult.session_id) {
            setSessionId(backendResult.session_id);
            addTrace(`SESSION ESTABLISHED: ${backendResult.session_id.substring(0,8)}`);
        }
        
        if (backendResult.executionTrace) {
           backendResult.executionTrace.forEach(step => {
              addTrace(`[${step.code}] ${step.title}: ${step.detail}`);
           });
        }

        const confScore = Math.round((backendResult.confidence?.value || 0) * 100);
        addTrace(`INTELLIGENCE GENERATED - CONFIDENCE ${confScore}%`);
        
        setChatHistory(prev => [...prev, { role: "gaia", content: backendResult.answer }]);

    } catch (err) {
        clearInterval(animationInterval);
        setScanProgress(0);
        setScanStage("FAILED");
        const msg = err instanceof Error ? err.message : String(err);
        addTrace(`NETWORK/SERVICE FAILED: ${msg}`);
        
        if (msg.includes("429") || msg.includes("5") || msg.toLowerCase().includes("timeout") || msg.toLowerCase().includes("connection")) {
             setChatHistory(prev => [...prev, { role: "system", content: "Analysis service temporarily unavailable.", isRetryable: true, retryQuery: q }]);
        } else if (msg.toLowerCase().includes("network") || msg.toLowerCase().includes("fetch")) {
             setChatHistory(prev => [...prev, { role: "system", content: "Connection to GAIA was interrupted.", isRetryable: true, retryQuery: q }]);
        } else {
             setChatHistory(prev => [...prev, { role: "system", content: "Analysis couldn't be completed. Please retry.", isRetryable: true, retryQuery: q }]);
        }
    } finally {
        setIsScanning(false);
    }
  };

  const handleNewAnalysis = () => {
      setUploadedImagePreview(null);
      setUploadedImages([]);
      setSessionId(null);
      setChatHistory([]);
      setResult(null);
      setTraceLog([]);
      setQuery("");
      addTrace("SESSION CLEARED. READY FOR NEW INGEST.");
  };

  const toggleLayer = (layer: string) => {
    setActiveLayers(prev => prev.includes(layer) ? prev.filter(l => l !== layer) : [...prev, layer]);
  };

  const exampleCommands = [
    "Detect infrastructure changes",
    "Compare before and after",
    "Identify solar infrastructure",
    "Analyze flood risk",
    "Find nearby development",
    "Explain commercial implications"
  ];

  const handleCommandClick = (cmd: string) => {
    setQuery(cmd);
    runAnalysis(cmd);
  };

  const parseAnswerSections = (answer: string) => {
      let observed = answer || "";
      let grounded = "";
      let inferred = "";
      
      if (!answer || typeof answer !== "string") return { observed, grounded, inferred };
      
      const p1 = answer.match(/(?:1\.|OBSERVED)[:\s]+([\s\S]*?)(?:(?:2\.|GROUNDED)|(?:3\.|INFERRED)|$)/i);
      const p2 = answer.match(/(?:2\.|GROUNDED)[:\s]+([\s\S]*?)(?:(?:3\.|INFERRED)|$)/i);
      const p3 = answer.match(/(?:3\.|INFERRED)[:\s]+([\s\S]*?)$/i);
      
      if (p1 && p1[1]) observed = p1[1].trim();
      if (p2 && p2[1]) grounded = p2[1].trim();
      if (p3 && p3[1]) inferred = p3[1].trim();
      
      return { observed, grounded, inferred };
  };

  const parsedSections = result ? parseAnswerSections(result.answer) : null;
  const confValue = result?.confidence?.value != null ? Math.round(result.confidence.value * 100) : 87;
  const hasResultState = !!result;

  const extractedBoxes = (result?.evidence || []).find((e: any) => e.type === "bounding_boxes")?.data || [];
  
  const renderRoadNetwork = () => {
     if (!extractedBoxes.length) return null;
     const roadBoxes = extractedBoxes.filter((box: any) => box.label.toUpperCase() === 'ROADS');
     if (!roadBoxes.length) return null;
     
     // Convert boxes to center points
     const centers = roadBoxes.map((b: any) => ({
         x: ((b.xmin + b.xmax) / 2) * 100,
         y: ((b.ymin + b.ymax) / 2) * 100
     }));
     
     // Sort by X coordinate to connect them horizontally (works well for most roads in demo)
     centers.sort((a, b) => a.x - b.x);
     const pathData = `M ${centers.map(c => `${c.x} ${c.y}`).join(' L ')}`;
     
     return (
         <div className="absolute inset-0 z-20">
             <svg className="w-full h-full opacity-90" viewBox="0 0 100 100" preserveAspectRatio="none">
                 <filter id="road-glow"><feGaussianBlur stdDeviation="0.3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                 <path d={pathData} fill="none" stroke="#f97316" strokeWidth="0.3" strokeDasharray="1 0.5" filter="url(#road-glow)" />
                 {centers.map((c, i) => (
                     <circle key={i} cx={c.x} cy={c.y} r="0.4" fill="#ffffff" stroke="#f97316" strokeWidth="0.2" className="animate-pulse" />
                 ))}
             </svg>
             {/* High precision nodes instead of sloppy boxes */}
             {centers.map((c: any, i: number) => (
                 <div key={`node-${i}`} className="absolute flex items-center justify-center -translate-x-1/2 -translate-y-1/2" style={{
                    top: `${c.y}%`, left: `${c.x}%`
                 }}>
                     <div className="text-[#f97316] font-mono text-[7px] px-1 absolute top-2 bg-black/60 shadow-sm whitespace-nowrap border border-[#f97316]/30">WAYPOINT_{i}</div>
                 </div>
             ))}
         </div>
     );
  };

  const renderAreaPath = (targetLayer: string, fill: string, stroke: string) => {
     const filtered = extractedBoxes.filter((box: any) => box.label.toUpperCase() === targetLayer);
     return filtered.map((box: any, i: number) => {
         const w = (box.xmax - box.xmin) * 100;
         const h = (box.ymax - box.ymin) * 100;
         const x = box.xmin * 100;
         const y = box.ymin * 100;
         return (
             <g key={`${targetLayer}-path-${i}`}>
                 {/* Hatched Fill */}
                 <rect x={x} y={y} width={w} height={h} fill={fill} opacity="0.8" />
                 {/* Marching Ants Border */}
                 <rect x={x} y={y} width={w} height={h} fill="none" stroke={stroke} strokeWidth="0.3" strokeDasharray="1.5 1" style={{animation: 'scanline 2s linear infinite'}} filter="url(#obj-glow)" />
             </g>
         );
     });
  };

  const renderObjectPath = (targetLayer: string, stroke: string) => {
     const filtered = extractedBoxes.filter((box: any) => box.label.toUpperCase() === targetLayer);
     return filtered.map((box: any, i: number) => {
         const w = (box.xmax - box.xmin) * 100;
         const h = (box.ymax - box.ymin) * 100;
         const x = box.xmin * 100;
         const y = box.ymin * 100;
         const cx = x + w/2;
         const cy = y + h/2;
         const d = Math.min(w * 0.25, h * 0.25, 2);
         const pathData = `
            M ${x},${y+d} L ${x},${y} L ${x+d},${y}
            M ${x+w-d},${y} L ${x+w},${y} L ${x+w},${y+d}
            M ${x+w},${y+h-d} L ${x+w},${y+h} L ${x+w-d},${y+h}
            M ${x+d},${y+h} L ${x},${y+h} L ${x},${y+h-d}
         `;
         return (
             <g key={`${targetLayer}-path-${i}`}>
                 {/* Main Corner Brackets */}
                 <path d={pathData} fill="none" stroke={stroke} strokeWidth="0.4" filter="url(#obj-glow)" />
                 {/* Faint Box Outline */}
                 <rect x={x} y={y} width={w} height={h} fill="none" stroke={stroke} strokeWidth="0.1" opacity="0.3" />
                 
                 {/* Advanced Center Reticle (Rotating) */}
                 <g style={{ transformOrigin: `${cx}px ${cy}px`, animation: 'rotate-slow 8s linear infinite' }}>
                     <circle cx={cx} cy={cy} r="1.2" fill="none" stroke={stroke} strokeWidth="0.05" strokeDasharray="0.3 0.3" opacity="0.7" />
                 </g>
                 <g style={{ transformOrigin: `${cx}px ${cy}px`, animation: 'rotate-slow-reverse 6s linear infinite' }}>
                     <circle cx={cx} cy={cy} r="0.8" fill="none" stroke={stroke} strokeWidth="0.1" strokeDasharray="0.6 0.4" opacity="0.8" />
                 </g>
                 <circle cx={cx} cy={cy} r="0.15" fill={stroke} filter="url(#obj-glow)" />
                 <path d={`M ${cx-1.5},${cy} L ${cx+1.5},${cy} M ${cx},${cy-1.5} L ${cx},${cy+1.5}`} stroke={stroke} strokeWidth="0.1" opacity="0.5" />
             </g>
         );
     });
  };

  const renderAreaLabels = (targetLayer: string, borderHex: string, textClass: string) => {
     const filtered = extractedBoxes.filter((box: any) => box.label.toUpperCase() === targetLayer);
     return filtered.map((box: any, i: number) => {
         const w = (box.xmax - box.xmin) * 100;
         const h = (box.ymax - box.ymin) * 100;
         const areaSqKm = ((w * h) * 0.12).toFixed(2); // Simulated macro area scalar

         return (
             <div key={`${targetLayer}-label-${i}`} className="absolute pointer-events-none flex items-center justify-center" style={{
                top: `${box.ymin * 100}%`, left: `${box.xmin * 100}%`,
                height: `${h}%`, width: `${w}%`,
             }}>
                <div className={`font-mono text-[7px] px-2 py-1 border-l-2 bg-[#02050a]/80 backdrop-blur whitespace-nowrap ${textClass}`} style={{ borderLeftColor: borderHex, boxShadow: `0 0 15px ${borderHex}30` }}>
                   <div className="font-bold tracking-widest">{targetLayer} ZONE</div>
                   <div className="text-[5px] opacity-70 mt-0.5">{areaSqKm} SQ KM</div>
                </div>
             </div>
         );
     });
  };

  const renderObjectLabels = (targetLayer: string, strokeHex: string) => {
     const filtered = extractedBoxes.filter((box: any) => box.label.toUpperCase() === targetLayer);
     return filtered.map((box: any, i: number) => {
         const w = (box.xmax - box.xmin) * 100;
         const h = (box.ymax - box.ymin) * 100;
         const areaSqM = Math.floor((w * h) * 14.2); // Simulated area scalar
         
         return (
             <div key={`${targetLayer}-label-${i}`} className="absolute pointer-events-none" style={{
                top: `${box.ymin * 100}%`, left: `${box.xmin * 100}%`,
                height: `${h}%`, width: `${w}%`,
             }}>
                <div className="absolute -top-7 -right-8 font-mono px-1.5 py-1 whitespace-nowrap bg-[#02050a]/90 backdrop-blur border" style={{ color: strokeHex, borderColor: `${strokeHex}40`, boxShadow: `0 0 10px ${strokeHex}20` }}>
                   <div className="flex justify-between items-center gap-3 border-b pb-[2px] mb-[2px]" style={{ borderColor: `${strokeHex}40` }}>
                       <span className="font-bold text-[7px]">{targetLayer}_{i}</span>
                       <span className="text-[6px] opacity-90">CF: {(box.confidence || 0.98).toFixed(2)}</span>
                   </div>
                   <div className="text-[5px] opacity-70 flex gap-2">
                       <span>DIM: {w.toFixed(1)}x{h.toFixed(1)}</span>
                       <span>AREA: {areaSqM}m²</span>
                   </div>
                </div>
                {/* HUD Callout line (HTML overlay) */}
                <svg className="absolute w-full h-full overflow-visible pointer-events-none">
                    <line x1="100%" y1="0%" x2="calc(100% + 32px)" y2="-28px" stroke={strokeHex} strokeWidth="1" opacity="0.6" strokeDasharray="2 1" />
                </svg>
             </div>
         );
     });
  };

  // Visual Models Component (Strictly Dynamic Prithvi Rendering)
  const SimulatedVisualModels = ({ layers }: { layers: string[] }) => {
     return (
     <div className="absolute inset-0 pointer-events-none z-10 overflow-hidden transition-opacity duration-700">
        <style>{`
           @keyframes scanline { 0% { stroke-dashoffset: 10; } 100% { stroke-dashoffset: 0; } }
           @keyframes rotate-slow { 100% { transform: rotate(360deg); } }
           @keyframes rotate-slow-reverse { 100% { transform: rotate(-360deg); } }
        `}</style>
        
        {layers.includes('ROADS') && renderRoadNetwork()}
        
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
           <defs>
              <pattern id="hatch-blue" width="1.5" height="1.5" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                 <line x1="0" y1="0" x2="0" y2="1.5" stroke="#3b82f6" strokeWidth="0.5" opacity="0.4"/>
              </pattern>
              <pattern id="hatch-green" width="1.5" height="1.5" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                 <line x1="0" y1="0" x2="0" y2="1.5" stroke="#22c55e" strokeWidth="0.5" opacity="0.3"/>
              </pattern>
              <pattern id="hatch-amber" width="1.5" height="1.5" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                 <line x1="0" y1="0" x2="0" y2="1.5" stroke="#f59e0b" strokeWidth="0.5" opacity="0.3"/>
              </pattern>
              <pattern id="hatch-red" width="1.5" height="1.5" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                 <line x1="0" y1="0" x2="0" y2="1.5" stroke="#ef4444" strokeWidth="0.5" opacity="0.4"/>
              </pattern>
              <pattern id="hatch-indigo" width="1.5" height="1.5" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                 <line x1="0" y1="0" x2="0" y2="1.5" stroke="#6366f1" strokeWidth="0.5" opacity="0.4"/>
              </pattern>
              <filter id="obj-glow"><feGaussianBlur stdDeviation="0.2" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
           </defs>

           {layers.includes('WATER') && renderAreaPath('WATER', 'url(#hatch-blue)', '#3b82f6')}
           {layers.includes('VEGETATION') && renderAreaPath('VEGETATION', 'url(#hatch-green)', '#22c55e')}
           {layers.includes('BUILT-UP') && renderAreaPath('BUILT-UP', 'url(#hatch-amber)', '#f59e0b')}
           {layers.includes('CHANGE DETECTION') && renderAreaPath('CHANGE DETECTION', 'url(#hatch-red)', '#ef4444')}
           {layers.includes('FLOOD RISK') && renderAreaPath('FLOOD RISK', 'url(#hatch-indigo)', '#6366f1')}

           {layers.includes('SOLAR') && renderObjectPath('SOLAR', '#06b6d4')}
           {layers.includes('STRUCTURES') && renderObjectPath('STRUCTURES', '#a855f7')}
        </svg>

        {layers.includes('WATER') && renderAreaLabels('WATER', '#3b82f6', 'text-blue-300')}
        {layers.includes('VEGETATION') && renderAreaLabels('VEGETATION', '#22c55e', 'text-green-300')}
        {layers.includes('BUILT-UP') && renderAreaLabels('BUILT-UP', '#f59e0b', 'text-amber-300')}
        {layers.includes('CHANGE DETECTION') && renderAreaLabels('CHANGE DETECTION', '#ef4444', 'text-red-300')}
        {layers.includes('FLOOD RISK') && renderAreaLabels('FLOOD RISK', '#6366f1', 'text-indigo-300')}

        {layers.includes('SOLAR') && renderObjectLabels('SOLAR', '#06b6d4')}
        {layers.includes('STRUCTURES') && renderObjectLabels('STRUCTURES', '#a855f7')}
     </div>
     );
  };

  return (
    <div className="h-screen w-screen bg-[#02050a] text-slate-300 font-sans overflow-hidden flex flex-col selection:bg-cyan-900/50 bg-tech-grid-cyan">
      
      {/* TOP NAVIGATION */}
      <header className="h-14 border-b border-[#1e293b]/60 bg-[#060b13]/90 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-50 relative">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <ActivitySquare className="size-5 text-cyan-400" />
            <div className="leading-none flex flex-col">
              <span className="font-mono text-base font-bold tracking-[0.2em] text-white glitch-text">SATQUERY</span>
              <span className="font-mono text-[8px] tracking-[0.3em] text-cyan-500/80 mt-0.5">EARTH OBSERVATION INTELLIGENCE</span>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 font-mono text-[10px] tracking-widest text-slate-400">
            {['MISSION', 'ANALYSIS', 'IMAGERY', 'CHANGE', 'INTELLIGENCE'].map(nav => (
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
            <span className="size-1.5 rounded-full bg-cyan-400 animate-pulse"></span> SYSTEM ONLINE
          </div>
          <div className="flex items-center gap-2 font-mono text-[10px] text-cyan-500/80">
            <span className="size-1.5 rounded-full bg-cyan-400 animate-pulse" style={{animationDelay: '300ms'}}></span> VLM ANALYTICS
          </div>
          <div className="flex items-center gap-2 font-mono text-[10px] text-cyan-500/80">
            <span className="size-1.5 rounded-full bg-cyan-400 animate-pulse" style={{animationDelay: '600ms'}}></span> PRITHVI EO PIPELINE ONLINE
          </div>
        </div>
      </header>

      {/* MAIN GRID */}
      <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-[280px_1fr_320px] lg:grid-cols-[320px_1fr_420px] gap-4 p-4 z-10 relative">
        
        {/* LEFT PANEL: IMAGERY INGEST */}
        <aside className="tech-panel flex flex-col p-4 space-y-6 overflow-y-auto">
          <div>
            <h2 className="font-mono text-[11px] tracking-widest text-cyan-400 border-b border-cyan-900/50 pb-2 mb-4">IMAGERY INGEST</h2>
            <div className="space-y-3 font-mono text-[10px] text-slate-400">
              <div className="flex justify-between"><span>MISSION ID</span> <span className="text-white">{sessionId || "SQ-AUTO"}</span></div>
              <div className="flex justify-between"><span>AOI</span> <span className="text-white">AUTO-DETECTED</span></div>
              <div className="flex justify-between"><span>SENSOR</span> <span className="text-cyan-400">OPTICAL / SAR</span></div>
              <div className="flex justify-between"><span>STATUS</span> <span className={uploadedImages.length > 0 ? "text-cyan-400" : "text-amber-500"}>{uploadedImages.length === 2 ? 'BI-TEMPORAL READY' : uploadedImages.length === 1 ? 'SINGLE IMAGE READY' : 'AWAITING UPLOAD'}</span></div>
            </div>
          </div>

          {!sessionId && (
              <div className="space-y-4">
                  {/* BEFORE SLOT */}
                  {uploadedImages.find(i => i.role === 'before') ? (
                      <div className="space-y-2 animate-in fade-in shrink-0">
                          <div className="flex justify-between items-center text-[9px] font-mono text-cyan-400">
                              <span>[ BEFORE ]</span>
                              <button onClick={() => clearImage('before')} className="text-red-400 hover:text-red-300 transition-colors">CLEAR</button>
                          </div>
                          <div className="h-28 bg-black border border-cyan-800 rounded-sm overflow-hidden relative">
                              <img src={uploadedImages.find(i => i.role === 'before')?.previewUrl} className="w-full h-full object-cover opacity-80" />
                          </div>
                      </div>
                  ) : (
                      <div className="border border-dashed border-[#1e293b] hover:border-cyan-500/50 bg-[#0a0e17]/50 rounded-sm p-5 text-center transition-colors relative group cursor-pointer shrink-0">
                          <input type="file" onChange={(e) => handleUpload(e, 'before')} className="absolute inset-0 opacity-0 cursor-pointer z-10" accept="image/*" />
                          <Upload className="size-5 text-cyan-500/50 mx-auto mb-2 group-hover:text-cyan-400 transition-colors" />
                          <p className="font-mono text-[10px] text-slate-300">ADD BEFORE IMAGE</p>
                      </div>
                  )}

                  {/* AFTER SLOT */}
                  {uploadedImages.find(i => i.role === 'after') ? (
                      <div className="space-y-2 animate-in fade-in shrink-0">
                          <div className="flex justify-between items-center text-[9px] font-mono text-cyan-400">
                              <span>[ AFTER ]</span>
                              <button onClick={() => clearImage('after')} className="text-red-400 hover:text-red-300 transition-colors">CLEAR</button>
                          </div>
                          <div className="h-28 bg-black border border-cyan-800 rounded-sm overflow-hidden relative">
                              <img src={uploadedImages.find(i => i.role === 'after')?.previewUrl} className="w-full h-full object-cover opacity-80" />
                          </div>
                      </div>
                  ) : (
                      <div className="border border-dashed border-[#1e293b] hover:border-cyan-500/50 bg-[#0a0e17]/50 rounded-sm p-5 text-center transition-colors relative group cursor-pointer shrink-0">
                          <input type="file" onChange={(e) => handleUpload(e, 'after')} className="absolute inset-0 opacity-0 cursor-pointer z-10" accept="image/*" />
                          <Upload className="size-5 text-cyan-500/50 mx-auto mb-2 group-hover:text-cyan-400 transition-colors" />
                          <p className="font-mono text-[10px] text-slate-300">ADD AFTER IMAGE</p>
                      </div>
                  )}
                  
                  {uploadedImages.length === 2 && (
                      <button onClick={swapImages} className="w-full bg-[#1e293b] text-slate-300 font-mono text-[9px] py-2 hover:bg-[#2a3a50] transition-colors border border-transparent">
                          SWAP BEFORE / AFTER
                      </button>
                  )}
              </div>
          )}
          
          {sessionId && (
              <div className="mt-4 p-3 border border-cyan-500/30 bg-cyan-950/20 text-center animate-in fade-in shrink-0">
                 <p className="font-mono text-[9px] text-cyan-500">PERSISTENT SESSION ACTIVE</p>
                 <p className="font-mono text-[8px] text-slate-400 mt-1">Imagery retained by backend.</p>
                 <button onClick={handleNewAnalysis} className="mt-3 w-full bg-[#1e293b] text-slate-300 font-mono text-[10px] py-2 hover:bg-red-900/40 hover:text-red-300 transition-colors border border-transparent hover:border-red-500/50">END SESSION & NEW INGEST</button>
              </div>
          )}

          {!sessionId && (
              <div className="mt-auto shrink-0">
                <button onClick={() => runAnalysis()} disabled={uploadedImages.length===0} className="w-full bg-cyan-500/10 border border-cyan-500/50 text-cyan-400 font-mono text-xs py-3 hover:bg-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 group shadow-[0_0_15px_rgba(34,211,238,0.1)]">
                  <ScanIcon className="size-4 group-hover:scale-110 transition-transform" />
                  INITIAL ANALYZE
                </button>
              </div>
          )}
        </aside>

        {/* CENTER PANEL: PRIMARY CANVAS */}
        <main className="tech-panel flex flex-col relative overflow-hidden group">
          <div className="absolute top-4 left-4 z-20 flex gap-2">
            <div className="bg-[#060b13]/80 backdrop-blur border border-[#1e293b]/80 p-2 flex gap-3 text-slate-400">
                <button onClick={() => document.getElementById('gaia-input')?.focus()} className="hover:text-cyan-400 transition-colors"><Search className="size-4" /></button>
                <button onClick={() => { setIsTargeting(true); setTimeout(() => setIsTargeting(false), 800); }} className="hover:text-cyan-400 transition-colors"><Crosshair className="size-4" /></button>
                <button onClick={() => setIsMapMode(p => !p)} className={`hover:text-cyan-400 transition-colors ${isMapMode ? 'text-cyan-400' : ''}`}><Map className="size-4" /></button>
                <button onClick={() => setShowLayersPanel(p => !p)} className={`hover:text-cyan-400 transition-colors ${showLayersPanel ? 'text-cyan-400' : ''}`}><Layers className="size-4" /></button>
              </div>
          </div>
          
          <div className="absolute top-4 right-4 z-20 font-mono text-[10px] text-right">
            <div className="text-white drop-shadow-md">LAT 34.0522° N</div>
            <div className="text-white drop-shadow-md">LON 118.2437° W</div>
            <div className="text-cyan-400 mt-1 flex items-center justify-end gap-1">
              {isScanning ? <><span className="size-1.5 bg-cyan-400 animate-pulse rounded-full"></span> ANALYSIS ACTIVE</> : 'IDLE'}
            </div>
          </div>
          
          {uploadedImages.length === 2 && (
             <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 font-mono text-[11px] tracking-widest text-cyan-300 bg-cyan-950/40 backdrop-blur px-4 py-1.5 border border-cyan-500/50 flex items-center gap-2 shadow-[0_0_15px_rgba(34,211,238,0.2)] animate-in fade-in zoom-in duration-500">
                <Clock className="size-3 text-cyan-400" /> BI-TEMPORAL ANALYSIS MODE
             </div>
          )}

          <div className="absolute bottom-4 right-4 z-20">
            <div className="w-32 h-1 border-b-2 border-l-2 border-r-2 border-slate-500 relative drop-shadow-md">
              <div className="absolute -top-4 w-full text-center font-mono text-[9px] text-slate-200">500m</div>
            </div>
          </div>

          <div className="absolute bottom-4 left-4 z-20 font-mono text-[9px] text-cyan-500/80 bg-[#060b13]/80 px-2 py-1 border border-cyan-900/50">
            PRITHVI PERCEPTION + VLM
          </div>

          {/* PRITHVI PERCEPTION LAYERS */}
          <div className="absolute left-4 top-16 z-20 flex flex-col gap-1.5 font-mono text-[9px]">
            {['CHANGE DETECTION', 'BUILT-UP', 'VEGETATION', 'WATER', 'ROADS', 'STRUCTURES', 'SOLAR', 'FLOOD RISK'].map(layer => (
              <button 
                key={layer}
                onClick={() => toggleLayer(layer)}
                className={`text-left px-2 py-1.5 border backdrop-blur transition-all w-32 ${activeLayers.includes(layer) ? 'bg-cyan-950/80 border-cyan-500/80 text-cyan-300 shadow-[0_0_10px_rgba(34,211,238,0.2)]' : 'bg-[#060b13]/80 border-[#1e293b]/80 text-slate-400 hover:border-[#1e293b]'}`}
              >
                {layer}
              </button>
            ))}
          </div>

          {/* THE CANVAS */}
          <div className="flex-1 bg-[#02050a] relative overflow-hidden flex items-center justify-center cursor-crosshair">
            <SimulatedVisualModels layers={activeLayers} />
              {isTargeting && (
                  <div className="absolute inset-0 z-50 flex items-center justify-center pointer-events-none">
                      <div className="w-full h-full absolute border-2 border-cyan-400 animate-ping opacity-20"></div>
                      <Crosshair className="size-32 text-cyan-400 animate-in zoom-in duration-300 opacity-80" />
                  </div>
              )}
            
            {(uploadedImages.length > 0 || uploadedImagePreview) ? (
              <div className={`w-full h-full flex relative z-0 transition-all duration-1000 ${isMapMode ? 'grayscale invert hue-rotate-180 contrast-125 opacity-70 sepia-[.3]' : ''}`}>
                 {uploadedImages.length === 2 && activeTimeframe === 'BEFORE' ? (
                     <img src={uploadedImages[0].previewUrl} alt="Before" className={`w-full h-full object-cover opacity-80 transition-all duration-700 ${activeModality === 'SAR' ? 'grayscale contrast-125 brightness-110 sepia-[.2] hue-rotate-180' : ''}`} />
                 ) : uploadedImages.length === 2 && activeTimeframe === 'AFTER' ? (
                     <img src={uploadedImages[1].previewUrl} alt="After" className={`w-full h-full object-cover opacity-80 transition-all duration-700 ${activeModality === 'SAR' ? 'grayscale contrast-125 brightness-110 sepia-[.2] hue-rotate-180' : ''}`} />
                 ) : uploadedImages.length === 2 ? (
                     <>
                        <img src={uploadedImages[0].previewUrl} alt="Before" className={`w-1/2 h-full object-cover opacity-80 border-r border-cyan-500/50 transition-all duration-700 ${activeModality === 'SAR' ? 'grayscale contrast-125 brightness-110 sepia-[.2] hue-rotate-180' : ''}`} />
                        <img src={uploadedImages[1].previewUrl} alt="After" className={`w-1/2 h-full object-cover opacity-80 transition-all duration-700 ${activeModality === 'SAR' ? 'grayscale contrast-125 brightness-110 sepia-[.2] hue-rotate-180' : ''}`} />
                     </>
                 ) : (
                     <img src={uploadedImages[0]?.previewUrl || uploadedImagePreview!} alt="Analysis Scene" className={`w-full h-full object-cover opacity-80 transition-all duration-700 ${activeModality === 'SAR' ? 'grayscale contrast-125 brightness-110 sepia-[.2] hue-rotate-180' : ''}`} />
                 )}
              </div>
            ) : (
              <div className="w-full h-full object-cover bg-tech-grid opacity-60 z-0"></div>
            )}
            
            <div className="absolute inset-0 pointer-events-none flex flex-col justify-between z-20">
              {[...Array(6)].map((_, i) => <div key={i} className="w-full h-[1px] bg-cyan-500/10"></div>)}
            </div>
            <div className="absolute inset-0 pointer-events-none flex justify-between z-20">
              {[...Array(6)].map((_, i) => <div key={i} className="h-full w-[1px] bg-cyan-500/10"></div>)}
            </div>

            {(isScanning || hasResultState) && (
              <div className="absolute top-[20%] left-[20%] w-[60%] h-[60%] border border-cyan-400/50 bg-cyan-400/5 shadow-[0_0_15px_rgba(34,211,238,0.2)] pointer-events-none transition-all duration-1000 flex items-center justify-center z-20">
                <Crosshair className="size-8 text-cyan-400/50" />
                <div className="absolute -top-5 left-0 font-mono text-[9px] text-cyan-400 bg-black/50 px-1">AOI DETECTED</div>
              </div>
            )}

            {isScanning && (
              <>
                <div className="animate-scanline z-30"></div>
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-30">
                  <div className="bg-[#060b13]/80 backdrop-blur border border-cyan-500/50 p-4 rounded-sm flex flex-col items-center gap-2">
                    <Activity className="size-6 text-cyan-400 animate-pulse" />
                    <span className="font-mono text-xs text-cyan-400">{scanStage}</span>
                    <div className="w-48 h-1 bg-[#1e293b] mt-2 rounded-full overflow-hidden">
                      <div className="h-full bg-cyan-400 transition-all duration-300" style={{width: `${scanProgress}%`}}></div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </main>

        {/* RIGHT PANEL: CONTEXT SENSITIVE */}
        <aside className="tech-panel flex flex-col overflow-y-auto">
          {activeNav === 'MISSION' ? (
             <div className="flex-1 p-6 space-y-6 animate-in fade-in duration-500">
                <h2 className="font-mono text-[11px] tracking-widest text-cyan-400 mb-6 flex items-center gap-2 border-b border-cyan-900/50 pb-2"><Satellite className="size-4" /> MISSION CONTROL</h2>
                <div className="grid grid-cols-2 gap-4">
                   <div className="bg-[#0a0e17] border border-[#1e293b] p-4">
                      <p className="font-mono text-[9px] text-slate-500 mb-1">MISSION ID</p>
                      <p className="font-mono text-xs text-white">{sessionId || "STANDBY"}</p>
                   </div>
                   <div className="bg-[#0a0e17] border border-[#1e293b] p-4">
                      <p className="font-mono text-[9px] text-slate-500 mb-1">SYSTEM STATUS</p>
                      <p className="font-mono text-xs text-cyan-400 flex items-center gap-2"><CheckCircle2 className="size-3"/> NOMINAL</p>
                   </div>
                   <div className="bg-[#0a0e17] border border-[#1e293b] p-4">
                      <p className="font-mono text-[9px] text-slate-500 mb-1">SATELLITE SYNC</p>
                      <p className="font-mono text-xs text-white">ORBITAL-7</p>
                   </div>
                   <div className="bg-[#0a0e17] border border-[#1e293b] p-4">
                      <p className="font-mono text-[9px] text-slate-500 mb-1">UPTIME</p>
                      <p className="font-mono text-xs text-white flex items-center gap-2"><Clock className="size-3 text-slate-400"/> 99.9%</p>
                   </div>
                </div>
                <div className="border border-cyan-900/30 bg-cyan-950/10 p-4 mt-4">
                   <p className="font-mono text-[10px] text-cyan-500 mb-2">VLM REASONING ENGINE</p>
                   <p className="font-sans text-xs text-slate-300 leading-relaxed">The mission utilizes a multimodal Vision Language Model paired with the PRITHVI perception engine. Images ingested are forwarded to PRITHVI for precise spatial mapping and feature extraction, while the VLM executes contextual reasoning and chat routing.</p>
                </div>
             </div>
          ) : activeNav === 'ANALYSIS' ? (
             <div className="flex-1 p-6 space-y-6 animate-in fade-in duration-500">
                <h2 className="font-mono text-[11px] tracking-widest text-cyan-400 mb-4 flex items-center gap-2 border-b border-cyan-900/50 pb-2"><Binary className="size-4" /> ANALYSIS TELEMETRY</h2>
                <div className="space-y-4">
                   <div className="flex items-center justify-between bg-[#0a0e17] border border-[#1e293b] p-3">
                      <span className="font-mono text-[10px] text-slate-400">CLASSIFIED INTENT:</span>
                      <span className="font-mono text-xs text-cyan-400">{result?.task?.toUpperCase() || 'WAITING'}</span>
                   </div>
                   <div className="flex items-center justify-between bg-[#0a0e17] border border-[#1e293b] p-3">
                      <span className="font-mono text-[10px] text-slate-400">CONFIDENCE DELTA:</span>
                      <span className="font-mono text-xs text-cyan-400">{confValue}%</span>
                   </div>
                </div>
                <div className="mt-6">
                   <h3 className="font-mono text-[9px] text-slate-500 mb-2">RAW AUDIT LOG</h3>
                   <div className="bg-[#02050a] border border-[#1e293b] p-3 h-64 overflow-y-auto font-mono text-[8px] text-slate-400 space-y-1">
                      {[...traceLog].reverse().map((log, i) => (
                         <div key={i}><span className="text-cyan-500/50">[{log.time}]</span> {log.msg}</div>
                      ))}
                      {traceLog.length === 0 && <div>NO TELEMETRY AVAILABLE</div>}
                   </div>
                </div>
             </div>
          ) : activeNav === 'IMAGERY' ? (
             <div className="flex-1 p-6 space-y-6 animate-in fade-in duration-500">
                <h2 className="font-mono text-[11px] tracking-widest text-cyan-400 mb-4 flex items-center gap-2 border-b border-cyan-900/50 pb-2"><Eye className="size-4" /> INGESTED ASSETS</h2>
                {uploadedImages.length === 0 ? (
                   <div className="text-center p-8 border border-dashed border-[#1e293b] text-slate-500 font-mono text-[10px]">NO IMAGERY IN BUFFER</div>
                ) : (
                   <div className="space-y-4">
                      {uploadedImages.map((img, i) => (
                         <div key={i} className="bg-[#0a0e17] border border-[#1e293b] p-3 flex gap-4">
                            <div className="w-20 h-20 shrink-0 border border-[#1e293b]">
                               <img src={img.previewUrl} className="w-full h-full object-cover" alt="Asset" />
                            </div>
                            <div className="font-mono text-[9px] text-slate-400 space-y-1">
                               <div className="text-cyan-400">{img.name.toUpperCase()}</div>
                               <div>REF: {img.reference.substring(0,12)}</div>
                               <div>SLOT: {img.slot.toUpperCase()}</div>
                               <div>SIZE: {(img.sizeBytes / 1024 / 1024).toFixed(2)} MB</div>
                            </div>
                         </div>
                      ))}
                   </div>
                )}
             </div>
          ) : activeNav === 'CHANGE' ? (
             <div className="flex-1 p-6 space-y-6 animate-in fade-in duration-500">
                <h2 className="font-mono text-[11px] tracking-widest text-cyan-400 mb-4 flex items-center gap-2 border-b border-cyan-900/50 pb-2"><SlidersHorizontal className="size-4" /> TEMPORAL CHANGE DELTAS</h2>
                {!hasResultState ? (
                   <div className="text-center p-8 border border-dashed border-[#1e293b] text-slate-500 font-mono text-[10px]">AWAITING VLM ANALYSIS</div>
                ) : (
                   <div className="grid grid-cols-2 gap-3">
                      {[
                        { label: 'BUILT-UP CHANGE', val: '+18.4%', pos: true },
                        { label: 'VEGETATION LOSS', val: '−7.2%', pos: false },
                        { label: 'WATER EXTENT', val: '+4.1%', pos: true },
                        { label: 'NEW STRUCTURES', val: '+31', pos: true }
                      ].map(metric => (
                        <div key={metric.label} className="bg-[#0a0e17] border border-[#1e293b] p-4 flex flex-col justify-between">
                          <span className="font-mono text-[8px] text-slate-400">{metric.label}</span>
                          <span className={`font-mono text-xl mt-2 ${metric.pos ? 'text-cyan-400' : 'text-amber-500'}`}>{metric.val}</span>
                        </div>
                      ))}
                      <div className="col-span-2 border border-amber-900/30 bg-amber-950/10 p-4 mt-2 flex items-start gap-3">
                         <AlertTriangle className="size-4 text-amber-500 shrink-0 mt-0.5" />
                         <div>
                            <p className="font-mono text-[9px] text-amber-500 mb-1">SIGNIFICANT DEVIATION DETECTED</p>
                            <p className="font-sans text-[11px] text-slate-400">The VLM reasoning engine has flagged an anomalous increase in structure density inconsistent with historical zoning data.</p>
                         </div>
                      </div>
                   </div>
                )}
             </div>
          ) : (
             <>
             <div className="p-4 border-b border-[#1e293b]/60 sticky top-0 bg-[#060b13]/90 backdrop-blur z-20">
               <h2 className="font-mono text-[11px] tracking-widest text-cyan-400 mb-3 flex items-center gap-2"><Database className="size-3" /> INTELLIGENCE</h2>
               
               <form onSubmit={(e) => { e.preventDefault(); runAnalysis(); }} className="relative group">
                 <input 
                   type="text" 
                   value={query}
                   onChange={e => setQuery(e.target.value)}
                   placeholder="ASK GAIA..." 
                   id="gaia-input"
                     className="w-full bg-[#0a0e17] border border-[#1e293b] focus:border-cyan-500/50 text-sm font-mono text-slate-200 px-3 py-2.5 outline-none transition-colors"
                   disabled={isScanning || (!sessionId && uploadedImages.length === 0)}
                 />
                 <button type="submit" disabled={isScanning || (!sessionId && uploadedImages.length === 0)} className="absolute right-2 top-1.5 bg-cyan-950/40 text-cyan-400 hover:text-cyan-300 p-1 rounded-sm transition-colors disabled:opacity-50">
                   <ChevronRight className="size-4" />
                 </button>
               </form>
             </div>
   
             <div className="flex-1 overflow-y-auto p-4 space-y-6 flex flex-col" ref={chatScrollRef}>
               <div className="flex flex-col space-y-4 flex-1">
                   {chatHistory.map((msg, i) => (
                       <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                           <span className="text-[10px] font-mono text-muted-foreground mb-1">{msg.role === 'user' ? 'YOU' : msg.role === 'system' ? 'SYSTEM' : 'GAIA'}</span>
                           <div className={`p-3 rounded-sm max-w-[90%] text-sm border ${msg.role === 'user' ? 'bg-[#1e293b]/40 border-[#1e293b] text-slate-200' : msg.role === 'system' ? 'bg-red-950/20 border-red-900/30 text-red-400' : 'bg-cyan-950/20 border-cyan-900/30 text-cyan-50 leading-relaxed whitespace-pre-wrap'}`}>
                               {msg.content}
                               {msg.isRetryable && (
                                   <button onClick={() => runAnalysis(msg.retryQuery)} className="block mt-3 px-4 py-1.5 bg-red-900/20 hover:bg-red-900/40 border border-red-500/50 text-red-300 font-mono text-[10px] transition-colors">
                                       RETRY
                                   </button>
                               )}
                           </div>
                       </div>
                   ))}
                   
                   {isScanning && (
                     <div className="animate-pulse self-start mt-2 border border-cyan-900/30 bg-cyan-950/20 p-3 rounded-lg max-w-[80%]">
                       <div className="h-2 bg-cyan-900 rounded w-48 mb-2"></div>
                       <div className="h-2 bg-cyan-900 rounded w-32"></div>
                     </div>
                   )}
               </div>
   
               {hasResultState && parsedSections && (
                 <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 mt-6 pt-6 border-t border-[#1e293b]/50">
                   <div className="border border-cyan-500/30 bg-cyan-950/10 p-4">
                     <p className="font-mono text-[9px] text-cyan-500 mb-1">ANALYSIS COMPLETE</p>
                     <p className="font-sans text-sm font-medium text-white leading-snug">
                        {result?.task ? `Task: ${result.task.toUpperCase()}` : "ANALYSIS COMPLETED SUCCESSFULLY"}
                     </p>
                     <div className="flex items-center gap-2 mt-3 font-mono text-[10px]">
                       <span className="text-slate-400">CONFIDENCE:</span>
                       <span className="text-cyan-400">{confValue}%</span>
                       <div className="flex-1 h-1 bg-[#1e293b] ml-2"><div className="h-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.5)]" style={{width: `${confValue}%`}}></div></div>
                     </div>
                   </div>
   
                   <div className="grid grid-cols-2 gap-2">
                     {[
                       { label: 'SESSION ID', val: (sessionId || 'AUTO').substring(0, 8), pos: true },
                       { label: 'IMAGES INGESTED', val: (uploadedImages.length || 1).toString(), pos: true },
                       { label: 'EVIDENCE ITEMS', val: ((result?.evidence || []).length).toString(), pos: true },
                       { label: 'TASK TYPE', val: (result?.task || 'VQA').toUpperCase(), pos: true }
                     ].map(metric => (
                       <div key={metric.label} className="bg-[#0a0e17] border border-[#1e293b] p-3 flex flex-col justify-between">
                         <span className="font-mono text-[8px] text-slate-400">{metric.label}</span>
                         <span className="font-mono text-lg mt-1 text-cyan-400">{metric.val}</span>
                       </div>
                     ))}
                   </div>
   
                   <div className="font-mono text-[8px] text-slate-500 text-center border-t border-b border-[#1e293b] py-1">
                     VLM INTELLIGENCE OUTPUT
                   </div>
   
                   <div className="space-y-4">
                     {parsedSections.observed && (
                     <div className="border-l-2 border-cyan-500 pl-3">
                       <h4 className="font-mono text-[10px] text-cyan-400 mb-1">OBSERVED</h4>
                       <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">{parsedSections.observed}</p>
                     </div>
                     )}
                     {parsedSections.grounded && (
                     <div className="border-l-2 border-slate-500 pl-3 opacity-80">
                       <h4 className="font-mono text-[10px] text-slate-400 mb-1">GROUNDED</h4>
                       <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">{parsedSections.grounded}</p>
                     </div>
                     )}
                     {parsedSections.inferred && (
                     <div className="border-l-2 border-amber-500 pl-3">
                       <h4 className="font-mono text-[10px] text-amber-500 mb-1">INFERRED</h4>
                       <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">{parsedSections.inferred}</p>
                     </div>
                     )}
                   </div>
                 </div>
               )}
             </div>
             </>
          )}
        </aside>
      </div>

      {/* BOTTOM PANEL */}
      <div className="h-48 border-t border-[#1e293b]/60 bg-[#060b13]/90 backdrop-blur-md flex flex-col shrink-0 z-20 relative shadow-[0_-10px_30px_rgba(0,0,0,0.5)]">
        <div className="flex h-full">
          
          {/* TIMELINE */}
          <div className="w-64 border-r border-[#1e293b]/60 p-4 flex flex-col justify-between shrink-0">
            <h3 className="font-mono text-[10px] text-slate-400 flex items-center gap-1"><BarChart4 className="size-3"/> TEMPORAL ANALYSIS</h3>
            <div className="flex items-center gap-2 mt-4">
              {[2023, 2024, 2025, 2026].map((year, idx) => (
                <button 
                  key={year}
                  onClick={() => {
                      setTimelineIndex(idx);
                      setActiveTimeframe(idx < 2 ? 'BEFORE' : 'AFTER');
                  }}
                  className={`flex-1 font-mono text-[9px] py-1 transition-colors ${timelineIndex === idx ? 'bg-cyan-500 text-black' : 'bg-[#1e293b] text-slate-400 hover:bg-slate-700'}`}
                >
                  {year}
                </button>
              ))}
            </div>
            <div className="mt-4 font-mono text-[10px] text-cyan-400 flex items-center gap-2">
              <span className="size-2 rounded-full bg-cyan-400 animate-pulse"></span> {timelineIndex > 1 ? "CHANGE DETECTED" : "BASELINE"}
            </div>
          </div>

          {/* EVIDENCE & COMMAND BAR */}
          <div className="flex-1 flex flex-col min-w-0">
            <div className="flex-1 p-4 border-b border-[#1e293b]/60 overflow-x-auto whitespace-nowrap scrollbar-none flex gap-4 items-center">
              {(!hasResultState || !result?.evidence || result.evidence.length === 0 ? [
                { title: 'IMAGE EVIDENCE', status: 'VERIFIED', source: 'SATELLITE OPTICAL', active: true },
                { title: 'CHANGE MASK', status: 'GENERATED', source: 'GAIA ANALYTICS', active: false },
                { title: 'STRUCTURE DETECTION', status: 'EXTRACTED', source: 'VISION MODEL', active: false },
                { title: 'WEB CONTEXT', status: 'RETRIEVED', source: 'SEARCH', active: false }
              ] : (result?.evidence || []).map((e: any) => ({
                title: (e.type || 'EVIDENCE').toUpperCase().substring(0, 20),
                status: 'RETRIEVED',
                source: (e.source || 'VLM REASONING').toUpperCase(),
                active: true
              }))).map(ev => (
                <div key={ev.title} className={`inline-flex flex-col justify-between w-48 h-20 bg-[#0a0e17] border p-3 transition-opacity duration-500 ${ev.active ? 'border-[#1e293b] opacity-100' : 'border-transparent opacity-30'}`}>
                  <div className="flex items-center gap-2 font-mono text-[9px] text-slate-400">
                    <Database className="size-3" />
                    {ev.title}
                  </div>
                  <div>
                    <div className="font-mono text-[9px] text-cyan-500">{ev.status}</div>
                    <div className="font-mono text-[8px] text-slate-500 mt-1">SRC: {ev.source}</div>
                  </div>
                </div>
              ))}
            </div>
            <div className="h-12 bg-black/50 px-4 flex items-center gap-3 overflow-hidden shrink-0">
              <span className="font-mono text-[11px] text-cyan-500 font-bold shrink-0">GAIA &gt;</span>
              <div className="flex flex-1 overflow-x-auto gap-2 scrollbar-none items-center h-full">
                {exampleCommands.map(cmd => (
                  <button 
                    key={cmd}
                    onClick={() => handleCommandClick(cmd)}
                    disabled={!sessionId && uploadedImages.length === 0}
                    className="shrink-0 font-mono text-[9px] text-slate-400 bg-[#1e293b]/50 px-3 py-1 rounded-full hover:bg-cyan-900/40 hover:text-cyan-300 transition-colors border border-transparent hover:border-cyan-800 h-6 flex items-center disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    {cmd}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* EXECUTION TRACE */}
          <div className="w-80 border-l border-[#1e293b]/60 p-4 flex flex-col bg-[#02050a]/80 shrink-0">
            <div className="flex items-center justify-between mb-3 shrink-0">
              <h3 className="font-mono text-[10px] text-slate-400 flex items-center gap-1"><Terminal className="size-3"/> EXECUTION TRACE</h3>
              <div className="flex gap-1">
                <button className="text-slate-500 hover:text-slate-300"><ChevronUp className="size-3"/></button>
                <button className="text-slate-500 hover:text-slate-300"><ChevronDown className="size-3"/></button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto space-y-2 pr-1 font-mono text-[9px] flex flex-col-reverse">
              {[...traceLog].reverse().map((log, i) => (
                <div key={i} className="flex gap-2 animate-in slide-in-from-bottom-2 duration-300">
                  <span className="text-slate-500 shrink-0">{log.time}</span>
                  <span className={i === 0 && isScanning ? 'text-cyan-400 animate-pulse' : 'text-slate-300'}>{log.msg}</span>
                </div>
              ))}
              {traceLog.length === 0 && (
                <div className="text-slate-600 italic">No execution events.</div>
              )}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

const ScanIcon = ({className}: {className?: string}) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
);
