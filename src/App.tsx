import { useState } from 'react';
import { Activity, AlertTriangle, Cloud, Eye, Gauge, Layers3, Map, Menu, Play, Radio, RefreshCw, Satellite, Search, ShieldCheck, Sparkles, Wind, X } from 'lucide-react';

type Forecast = { h: number; lat: number; lon: number; wind: number };

const forecast: Forecast[] = [
  { h: 6, lat: 15.8, lon: 83.1, wind: 84 },
  { h: 12, lat: 16.4, lon: 83.9, wind: 86 },
  { h: 24, lat: 17.2, lon: 85.1, wind: 88 },
  { h: 36, lat: 18.0, lon: 86.2, wind: 82 },
  { h: 48, lat: 18.8, lon: 87.1, wind: 74 },
];

function App() {
  const [sources, setSources] = useState(['IR', 'WV', 'VIS', 'MW']);
  const [running, setRunning] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const toggleSource = (source: string) => setSources((current) => current.includes(source) ? current.filter((s) => s !== source) : [...current, source]);
  const runAnalysis = () => { setRunning(true); window.setTimeout(() => setRunning(false), 1400); };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark"><Wind size={20}/></div><div><strong>Cyclone<span>AI</span></strong><small>Multi-source cyclone intelligence</small></div></div>
        <nav className={mobileOpen ? 'nav open' : 'nav'}>
          <a className="active">Dashboard</a><a>Historical Replay</a><a>Model Metrics</a><a>Data Sources</a>
        </nav>
        <div className="top-actions"><span className="live-dot"><i/> Prototype</span><button className="icon-btn" onClick={() => setMobileOpen(!mobileOpen)}>{mobileOpen ? <X/> : <Menu/>}</button></div>
      </header>

      <main>
        <section className="hero-row">
          <div><p className="eyebrow"><Radio size={14}/> AI-ASSISTED TROPICAL CYCLONE ANALYSIS</p><h1>See the storm.<br/><em>Understand what comes next.</em></h1><p className="hero-copy">Fuse satellite observations and historical tracks to identify, classify and predict tropical cyclone evolution — with explainable AI.</p></div>
          <div className="hero-status"><div className="status-icon"><Activity/></div><div><span>System status</span><strong>Analysis ready</strong><small>Last model sync · 12:00 UTC</small></div></div>
        </section>

        <section className="dashboard-grid">
          <div className="map-card panel">
            <div className="panel-head"><div><span className="section-label">LIVE ANALYSIS</span><h2>Bay of Bengal</h2></div><div className="head-actions"><button className="ghost-btn"><Layers3 size={15}/> Layers</button><button className="ghost-btn"><RefreshCw size={15}/> Refresh</button></div></div>
            <div className="map-stage">
              <div className="grid-lines"/><div className="ocean-glow"/>
              <div className="landmass india"><span>INDIA</span></div><div className="landmass sri"><span>SRI LANKA</span></div><div className="landmass myanmar"><span>MYANMAR</span></div>
              <div className="map-label label-andaman">ANDAMAN SEA</div><div className="map-label label-bay">BAY OF BENGAL</div>
              <div className="track actual"><span className="track-title">Observed</span><b className="dot d1"/><b className="dot d2"/><b className="dot d3"/><b className="dot d4"/></div>
              <div className="track predicted"><span className="track-title">AI forecast</span><b className="p-dot p1"/><b className="p-dot p2"/><b className="p-dot p3"/><b className="p-dot p4"/></div>
              <div className="storm-core"><div className="rings"><i/><i/><i/></div><strong>CYCLONE</strong><span>Current center</span></div>
              <div className="forecast-card"><span>48H FORECAST</span><strong>18.8°N · 87.1°E</strong><small>74 kt predicted wind</small></div>
              <div className="map-legend"><span><i className="legend-observed"/> Observed</span><span><i className="legend-ai"/> AI forecast</span></div>
            </div>
          </div>

          <aside className="side-stack">
            <div className="panel intensity-card"><div className="section-label">CURRENT SYSTEM</div><div className="storm-name"><div><h2>Severe Cyclonic Storm</h2><span>Bay of Bengal · 02 Sep 2026</span></div><AlertTriangle size={22}/></div><div className="metric-main"><div><small>MAX SUSTAINED WIND</small><strong>82 <sup>kt</sup></strong></div><div className="confidence"><span>AI confidence</span><strong>91%</strong><div><i style={{width:'91%'}}/></div></div></div><div className="mini-metrics"><div><span>Pressure</span><strong>970 hPa</strong></div><div><span>Movement</span><strong>NW · 12 kt</strong></div><div><span>Position</span><strong>15.2°N 82.4°E</strong></div></div></div>
            <div className="panel source-card"><div className="panel-head compact"><div><div className="section-label">INPUT SOURCES</div><h3>Multi-source fusion</h3></div><span className="source-count">{sources.length}/4 active</span></div><div className="source-list">{['IR','WV','VIS','MW'].map((s, i) => <button key={s} className={sources.includes(s) ? 'source active' : 'source'} onClick={() => toggleSource(s)}><span className="source-icon">{i === 0 ? <Cloud/> : i === 1 ? <Satellite/> : i === 2 ? <Eye/> : <Activity/>}</span><span><strong>{s === 'IR' ? 'Infrared' : s === 'WV' ? 'Water Vapor' : s === 'VIS' ? 'Visible' : 'Microwave'}</strong><small>{s === 'IR' ? 'Cloud-top temperature' : s === 'WV' ? 'Moisture structure' : s === 'VIS' ? 'Cloud morphology' : 'Precipitation structure'}</small></span><i className="toggle"/></button>)}</div></div>
          </aside>
        </section>

        <section className="lower-grid">
          <div className="panel forecast-panel"><div className="panel-head compact"><div><div className="section-label">PREDICTION</div><h3>Track & intensity forecast</h3></div><span className="pill"><Sparkles size={13}/> Multi-task model</span></div><div className="forecast-table"><div className="table-head"><span>HORIZON</span><span>POSITION</span><span>WIND</span><span>CLASS</span></div>{forecast.map((row) => <div className="table-row" key={row.h}><strong>+{row.h}h</strong><span>{row.lat.toFixed(1)}°N · {row.lon.toFixed(1)}°E</span><b>{row.wind} kt</b><span className={row.wind >= 83 ? 'class severe' : 'class'}>{row.wind >= 83 ? 'Very Severe' : 'Severe'}</span></div>)}</div></div>
          <div className="panel explain-panel"><div className="section-label">EXPLAINABILITY</div><h3>Why the model is confident</h3><div className="heatmap"><div className="heat-core"/><div className="heat-band one"/><div className="heat-band two"/><span>Grad-CAM attention</span></div><div className="explain-tags"><span>✓ Deep convection</span><span>✓ Curved banding</span><span>✓ Eye structure</span></div></div>
        </section>

        <section className="cta-panel"><div><div className="section-label">READY FOR MODEL INTEGRATION</div><h2>Run a new cyclone analysis</h2><p>The dashboard is wired to a clean model API contract, so your ML model can plug in without changing the UI.</p></div><button className="primary-btn" onClick={runAnalysis}>{running ? <><RefreshCw className="spin"/> Running model…</> : <><Play/> Run analysis</>}</button></section>
      </main>
      <footer><span><Wind size={15}/> CycloneAI</span><span>AI-assisted decision support · Prototype</span><span>Model v0.1 · Data pipeline ready</span></footer>
    </div>
  );
}
export default App;
