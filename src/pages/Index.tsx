import { useRef, useState } from "react";
import { Aperture, ArrowUpRight, Box, ChevronRight, CircleDotDashed, Cpu, FileUp, Gauge, Layers3, Play, ScanLine, SlidersHorizontal, Sparkles, TableProperties, Upload, Video } from "lucide-react";

const pipeline = [
  { n: "01", title: "Monocular prior", note: "Depth Anything V2", tone: "cyan" },
  { n: "02", title: "Stereo geometry", note: "SGBM disparity", tone: "amber" },
  { n: "03", title: "Confidence fusion", note: "Aligned depth field", tone: "blue" },
  { n: "04", title: "3D scene map", note: "Objects + point cloud", tone: "mint" },
];

const readings = [
  ["person", "0.94", "~3.7 m", "cyan"],
  ["chair", "0.89", "~1.8 m", "amber"],
  ["table", "0.84", "~3.2 m", "blue"],
];

export default function Index() {
  const [mode, setMode] = useState<"single" | "stereo">("stereo");
  const [active, setActive] = useState("overview");
  const [fileName, setFileName] = useState<string | null>(null);
  const [showCloud, setShowCloud] = useState(true);
  const fileInput = useRef<HTMLInputElement>(null);
  const label = mode === "stereo" ? "Stereo pair" : "Single image";
  return <main className="min-h-screen bg-[#071525] text-[#eaf5ff] selection:bg-cyan-300 selection:text-[#071525]">
    <div className="depth-grid fixed inset-0 pointer-events-none opacity-50" />
    <div className="relative mx-auto max-w-[1500px] px-5 pb-12 pt-5 lg:px-8">
      <header className="flex items-center justify-between border-b border-white/10 pb-5">
        <button className="flex items-center gap-3" onClick={() => setActive("overview")}>
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-[#1269e8] shadow-[0_0_30px_rgba(18,105,232,.35)]"><Aperture size={21}/></span>
          <span className="text-left"><span className="block text-sm font-black tracking-[.2em]">DEPTHFORGE</span><span className="block text-[10px] tracking-[.18em] text-[#8eacc8]">SPATIAL AI LAB</span></span>
        </button>
        <nav className="hidden items-center gap-7 text-sm text-[#8eacc8] md:flex">{["overview", "pipeline", "calibration", "evaluation"].map(item => <button key={item} onClick={() => setActive(item)} className={active === item ? "text-white" : "hover:text-white"}>{item[0].toUpperCase() + item.slice(1)}</button>)}</nav>
        <div className="flex items-center gap-3"><span className="hidden rounded-full border border-cyan-300/25 bg-cyan-300/10 px-3 py-1 text-[11px] font-semibold text-cyan-200 sm:block"><i className="mr-2 inline-block h-1.5 w-1.5 rounded-full bg-cyan-300"/>SYSTEM READY</span><button onClick={() => fileInput.current?.click()} className="rounded-xl bg-white px-4 py-2 text-xs font-bold text-[#09203a] hover:bg-cyan-100"><Upload className="mr-2 inline" size={14}/>New scene</button></div>
      </header>

      <section className="grid gap-8 py-10 lg:grid-cols-[1.1fr_.9fr] lg:py-14">
        <div className="animate-rise"><div className="mb-5 flex items-center gap-2 text-xs font-bold tracking-[.15em] text-cyan-300"><Sparkles size={14}/> CAMERA-BASED 3D RESEARCH</div>
          <h1 className="max-w-3xl text-4xl font-black leading-[.98] tracking-[-.055em] sm:text-6xl">Understand the space<br/><span className="text-[#4fa2ff]">behind every pixel.</span></h1>
          <p className="mt-6 max-w-xl text-base leading-7 text-[#9cb4cc]">DepthForge combines learned monocular cues with geometric stereo evidence to make spatial perception inspectable, measurable, and technically honest.</p>
          <div className="mt-8 flex flex-wrap gap-3"><button onClick={() => fileInput.current?.click()} className="rounded-xl bg-[#1269e8] px-5 py-3 text-sm font-bold shadow-[0_12px_35px_rgba(18,105,232,.3)] hover:bg-[#2c7bf0]"><FileUp className="mr-2 inline" size={16}/>Analyze a scene</button><button onClick={() => setActive("pipeline")} className="rounded-xl border border-white/15 px-5 py-3 text-sm font-bold text-[#d8ebff] hover:border-cyan-300/60">Explore methodology <ChevronRight className="inline" size={16}/></button></div>
          <p className="mt-5 text-xs text-[#7291af]">{fileName ? `Loaded: ${fileName}` : "No imagery leaves your local Streamlit workflow."}</p>
        </div>
        <div className="relative overflow-hidden rounded-[28px] border border-cyan-200/15 bg-[#0c223a] p-5 shadow-2xl shadow-black/20">
          <div className="absolute inset-0 opacity-35 depth-orb"/><div className="relative flex items-center justify-between"><span className="font-mono text-xs text-cyan-200">LIVE FUSION PREVIEW</span><span className="rounded-full bg-[#153858] px-2.5 py-1 font-mono text-[10px] text-[#a9c9e6]">FRAME 00218</span></div>
          <div className="relative mt-5 grid h-[250px] place-items-center overflow-hidden rounded-2xl border border-white/10 bg-[#061321]">
            <div className="scene-room"><div className="scene-wall"/><div className="scene-floor"/><div className="scene-person"/><div className="scene-box b1"/><div className="scene-box b2"/></div>
            <div className="scan-line"/><span className="absolute left-[36%] top-[27%] rounded border border-cyan-300 bg-cyan-300/15 px-2 py-1 text-[10px] font-bold">PERSON · ~3.7m</span>
          </div>
          <div className="relative mt-4 grid grid-cols-3 gap-2"><div><p className="text-[10px] text-[#86a5c3]">MONO DEPTH</p><p className="font-mono text-sm">42 ms</p></div><div><p className="text-[10px] text-[#86a5c3]">STEREO VALID</p><p className="font-mono text-sm">81.6%</p></div><div><p className="text-[10px] text-[#86a5c3]">FUSION MODE</p><p className="font-mono text-sm text-cyan-200">CONFIDENT</p></div></div>
        </div>
      </section>

      <section className="rounded-[28px] border border-white/10 bg-[#0b1e33]/90 p-4 sm:p-6">
        <div className="flex flex-col justify-between gap-5 border-b border-white/10 pb-5 md:flex-row md:items-center"><div><p className="text-xs font-bold tracking-[.15em] text-cyan-300">WORKSPACE</p><h2 className="mt-1 text-2xl font-bold">Scene analysis console</h2></div><div className="flex rounded-xl bg-[#061525] p-1">{(["single", "stereo"] as const).map(k => <button onClick={() => setMode(k)} key={k} className={`rounded-lg px-4 py-2 text-xs font-bold ${mode === k ? "bg-[#1b4166] text-white" : "text-[#7896b4]"}`}>{k === "single" ? "Single image" : "Stereo pair"}</button>)}</div></div>
        <div className="grid gap-6 pt-6 lg:grid-cols-[250px_1fr]">
          <aside className="space-y-5"><div><p className="section-label">INPUT</p><button onClick={() => fileInput.current?.click()} className="mt-2 grid w-full place-items-center rounded-2xl border border-dashed border-[#376688] bg-[#0a1a2c] px-4 py-7 text-center hover:border-cyan-300"><Upload size={19} className="mb-2 text-cyan-300"/><span className="text-xs font-bold">Upload {label}</span><span className="mt-1 text-[10px] text-[#7896b4]">PNG, JPG · local processing</span></button><input ref={fileInput} className="hidden" type="file" accept="image/*" onChange={e => setFileName(e.target.files?.[0]?.name ?? null)}/></div>
          <div><p className="section-label">FUSION SETTINGS</p><div className="mt-3 space-y-3 text-xs"><Setting label="Focal length" value="700 px"/><Setting label="Baseline" value="0.12 m"/><Setting label="SGBM blocks" value="5 × 5"/></div></div>
          <div className="rounded-xl border border-amber-300/20 bg-amber-300/5 p-3 text-[11px] leading-4 text-amber-100"><Gauge size={14} className="mb-1 text-amber-300"/>Uncalibrated stereo outputs are approximate. DepthForge never labels them as ground truth.</div></aside>
          <div className="grid gap-4 xl:grid-cols-2"><DepthPanel title="MONOCULAR DEPTH" chip="RELATIVE" art="mono"/><DepthPanel title={mode === "stereo" ? "FUSED DEPTH" : "OBJECT DISTANCE"} chip={mode === "stereo" ? "APPROXIMATE" : "MEDIAN ROI"} art={mode === "stereo" ? "fused" : "detect"}/></div>
        </div>
      </section>

      <section className="grid gap-5 py-8 lg:grid-cols-[1.1fr_.9fr]"><div className="rounded-[24px] border border-white/10 bg-[#0b1e33] p-5"><div className="flex items-center justify-between"><div><p className="section-label">PIPELINE</p><h2 className="mt-1 text-xl font-bold">Evidence, not a black box</h2></div><button onClick={() => setActive("pipeline")} className="text-xs font-bold text-cyan-300">Inspect flow <ArrowUpRight className="inline" size={14}/></button></div><div className="mt-6 grid gap-3 sm:grid-cols-2">{pipeline.map(p => <div key={p.n} className="rounded-2xl border border-white/10 bg-[#092038] p-4"><span className={`text-[10px] font-bold text-${p.tone === "amber" ? "amber" : "cyan"}-300`}>{p.n}</span><h3 className="mt-5 font-bold">{p.title}</h3><p className="mt-1 text-xs text-[#82a1bd]">{p.note}</p></div>)}</div></div>
      <div className="rounded-[24px] border border-white/10 bg-[#0b1e33] p-5"><div className="flex items-center justify-between"><div><p className="section-label">SPATIAL READINGS</p><h2 className="mt-1 text-xl font-bold">Detected objects</h2></div><ScanLine className="text-cyan-300" size={20}/></div><div className="mt-5 space-y-1">{readings.map(([name, confidence, distance, tone]) => <div key={name} className="flex items-center justify-between rounded-xl px-3 py-3 hover:bg-white/5"><span className="flex items-center gap-3 text-sm"><i className={`h-2 w-2 rounded-full bg-${tone === "amber" ? "amber" : tone === "blue" ? "blue" : "cyan"}-300`}/>{name}</span><span className="font-mono text-xs text-[#9db7d0]">{confidence}</span><span className="font-mono text-sm text-white">{distance}</span></div>)}</div><p className="mt-3 text-[10px] text-[#708fac]">Median depth within each detection region · metric only with a valid calibration.</p></div></section>
      <section className="overflow-hidden rounded-[28px] border border-white/10 bg-[#0b1e33] p-5"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p className="section-label">3D RECONSTRUCTION</p><h2 className="mt-1 text-xl font-bold">Point-cloud inspector</h2></div><button onClick={() => setShowCloud(!showCloud)} className="rounded-xl border border-white/15 px-3 py-2 text-xs font-bold"><Box className="mr-2 inline" size={15}/>{showCloud ? "Hide cloud" : "Show cloud"}</button></div>{showCloud && <div className="cloud-view mt-5 h-52 rounded-2xl border border-white/10"><div className="cloud-points"/><div className="absolute bottom-4 left-4 rounded-lg bg-[#061525]/85 px-3 py-2 font-mono text-[10px] text-cyan-100">RGB-D PROJECTED · 18,422 POINTS</div></div>}</section>
      <footer className="flex flex-col gap-2 pt-7 text-xs text-[#6d8ca8] sm:flex-row sm:justify-between"><span>DEPTHFORGE / Spatial perception research prototype</span><span>Relative · Approximate metric · Calibrated metric</span></footer>
    </div>
  </main>
}
function Setting({label,value}:{label:string,value:string}) { return <div className="flex justify-between border-b border-white/10 pb-2"><span className="text-[#86a4bf]">{label}</span><span className="font-mono text-white">{value}</span></div> }
function DepthPanel({title,chip,art}:{title:string;chip:string;art:string}) { return <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#07192b]"><div className="flex items-center justify-between p-4"><span className="text-xs font-bold">{title}</span><span className="rounded-full bg-cyan-300/10 px-2 py-1 text-[9px] font-bold text-cyan-200">{chip}</span></div><div className={`depth-art ${art}`}><div className="depth-island a"/><div className="depth-island b"/><div className="depth-island c"/>{art === "detect" && <div className="detect-card">person<br/><b>~3.7 m</b></div>}</div></div> }
