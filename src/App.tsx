import { useState } from 'react';
import {
  Activity, AlertTriangle, Cloud, Eye, Layers3, Menu, Play, Radio,
  RefreshCw, Satellite, Sparkles, Wind, X,
} from 'lucide-react';
import { CycloneMap } from './components/CycloneMap';
import { runAnalysis } from './services/modelApi';
import type { CycloneAnalysis, SatelliteSource } from './types/analysis';

const SOURCE_META: Record<SatelliteSource, { name: string; detail: string }> = {
  IR: { name: 'Infrared', detail: 'Cloud-top temperature' },
  WV: { name: 'Water Vapor', detail: 'Moisture structure' },
  VIS: { name: 'Visible', detail: 'Cloud morphology' },
  MW: { name: 'Microwave', detail: 'Precipitation structure' },
};

const INITIAL: CycloneAnalysis = {
  cyclone_detected: true,
  classification: { label: 'Very Severe Cyclonic Storm', confidence: 0.91 },
  intensity: { wind_knots: 82, pressure_hpa: 970 },
  center: { latitude: 15.2, longitude: 82.4 },
  movement: { direction: 'NW', speed_knots: 12 },
  observed_track: [
    { hours: -18, latitude: 14.1, longitude: 79.7, wind_knots: 74 },
    { hours: -12, latitude: 14.5, longitude: 80.6, wind_knots: 77 },
    { hours: -6, latitude: 14.9, longitude: 81.5, wind_knots: 80 },
  ],
  track: [
    { hours: 6, latitude: 15.8, longitude: 83.1, wind_knots: 84, uncertainty_km: 45 },
    { hours: 12, latitude: 16.4, longitude: 83.9, wind_knots: 86, uncertainty_km: 70 },
    { hours: 24, latitude: 17.2, longitude: 85.1, wind_knots: 88, uncertainty_km: 105 },
    { hours: 36, latitude: 18.0, longitude: 86.2, wind_knots: 82, uncertainty_km: 145 },
    { hours: 48, latitude: 18.8, longitude: 87.1, wind_knots: 74, uncertainty_km: 190 },
  ],
  explainability: { labels: ['Deep convection', 'Curved banding', 'Eye structure'] },
  model: { version: 'mock-v0.1', generated_at: '2026-09-02T12:00:00Z' },
};

function App() {
  const [sources, setSources] = useState<SatelliteSource[]>(['IR', 'WV', 'VIS', 'MW']);
  const [analysis, setAnalysis] = useState(INITIAL);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);

  const toggleSource = (source: SatelliteSource) =>
    setSources((current) => current.includes(source) ? current.filter((s) => s !== source) : [...current, source]);

  const runNewAnalysis = async () => {
    setRunning(true);
    setError('');
    try {
      const result = await runAnalysis({
        timestamp: new Date().toISOString(),
        latitude: analysis.center.latitude,
        longitude: analysis.center.longitude,
        sources,
      });
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to run analysis');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark"><Wind size={20}/></div><div><strong>Cyclone<span>AI</span></strong><small>Multi-source cyclone intelligence</small></div></div>
        <nav className={mobileOpen ? 'nav open' : 'nav'}>
          <a className="active">Dashboard</a><a>Historical Replay</a><a>Model Metrics</a><a>Data Sources</a>
        </nav>
        <div className="top-actions"><span className="live-dot"><i/> Prototype</span><button className="icon-btn" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle menu">{mobileOpen ? <X/> : <Menu/>}</button></div>
      </header>

      <main>
        <section className="hero-row">
          <div><p className="eyebrow"><Radio size={14}/> AI-ASSISTED TROPICAL CYCLONE ANALYSIS</p><h1>See the storm.<br/><em>Understand what comes next.</em></h1><p className="hero-copy">Fuse satellite observations and historical tracks to identify, classify and predict tropical cyclone evolution — with explainable AI.</p></div>
          <div className="hero-status"><div className="status-icon"><Activity/></div><div><span>System status</span><strong>{running ? 'Running analysis…' : 'Analysis ready'}</strong><small>Model {analysis.model.version}</small></div></div>
        </section>

        <section className="dashboard-grid">
          <div className="map-card panel">
            <div className="panel-head"><div><span className="section-label">LIVE ANALYSIS</span><h2>Bay of Bengal</h2></div><div className="head-actions"><button className="ghost-btn"><Layers3 size={15}/> Layers</button><button className="ghost-btn" onClick={runNewAnalysis}><RefreshCw size={15}/> Refresh</button></div></div>
            <div className="map-stage"><CycloneMap analysis={analysis}/><div className="map-overlay-title"><span>INTERACTIVE TRACK MAP</span><small>Observed vs AI forecast</small></div><div className="forecast-card"><span>48H FORECAST</span><strong>{analysis.track.at(-1)?.latitude.toFixed(1)}°N · {analysis.track.at(-1)?.longitude.toFixed(1)}°E</strong><small>{analysis.track.at(-1)?.wind_knots} kt predicted wind</small></div><div className="map-legend"><span><i className="legend-observed"/> Observed</span><span><i className="legend-ai"/> AI forecast</span><span><i className="legend-uncertainty"/> Uncertainty</span></div></div>
          </div>

          <aside className="side-stack">
            <div className="panel intensity-card"><div className="section-label">CURRENT SYSTEM</div><div className="storm-name"><div><h2>{analysis.classification.label}</h2><span>Bay of Bengal · 02 Sep 2026</span></div><AlertTriangle size={22}/></div><div className="metric-main"><div><small>MAX SUSTAINED WIND</small><strong>{analysis.intensity.wind_knots} <sup>kt</sup></strong></div><div className="confidence"><span>AI confidence</span><strong>{Math.round(analysis.classification.confidence * 100)}%</strong><div><i style={{width:`${analysis.classification.confidence * 100}%`}}/></div></div></div><div className="mini-metrics"><div><span>Pressure</span><strong>{analysis.intensity.pressure_hpa} hPa</strong></div><div><span>Movement</span><strong>{analysis.movement.direction} · {analysis.movement.speed_knots} kt</strong></div><div><span>Position</span><strong>{analysis.center.latitude.toFixed(1)}°N {analysis.center.longitude.toFixed(1)}°E</strong></div></div></div>
            <div className="panel source-card"><div className="panel-head compact"><div><div className="section-label">INPUT SOURCES</div><h3>Multi-source fusion</h3></div><span className="source-count">{sources.length}/4 active</span></div><div className="source-list">{(['IR','WV','VIS','MW'] as SatelliteSource[]).map((s, i) => <button key={s} className={sources.includes(s) ? 'source active' : 'source'} onClick={() => toggleSource(s)}><span className="source-icon">{i === 0 ? <Cloud/> : i === 1 ? <Satellite/> : i === 2 ? <Eye/> : <Activity/>}</span><span><strong>{SOURCE_META[s].name}</strong><small>{SOURCE_META[s].detail}</small></span><i className="toggle"/></button>)}</div></div>
          </aside>
        </section>

        <section className="lower-grid">
          <div className="panel forecast-panel"><div className="panel-head compact"><div><div className="section-label">PREDICTION</div><h3>Track & intensity forecast</h3></div><span className="pill"><Sparkles size={13}/> Multi-task model</span></div><div className="forecast-table"><div className="table-head"><span>HORIZON</span><span>POSITION</span><span>WIND</span><span>CLASS</span></div>{analysis.track.map((row) => <div className="table-row" key={row.hours}><strong>+{row.hours}h</strong><span>{row.latitude.toFixed(1)}°N · {row.longitude.toFixed(1)}°E</span><b>{row.wind_knots} kt</b><span className={row.wind_knots >= 83 ? 'class severe' : 'class'}>{row.wind_knots >= 83 ? 'Very Severe' : 'Severe'}</span></div>)}</div></div>
          <div className="panel explain-panel"><div className="section-label">EXPLAINABILITY</div><h3>Why the model is confident</h3><div className="heatmap"><div className="heat-core"/><div className="heat-band one"/><div className="heat-band two"/><span>Grad-CAM attention · {analysis.model.version}</span></div><div className="explain-tags">{analysis.explainability.labels.map((label) => <span key={label}>✓ {label}</span>)}</div></div>
        </section>

        <section className="cta-panel"><div><div className="section-label">MODEL INTEGRATION</div><h2>Run a new cyclone analysis</h2><p>{error || 'The frontend uses a typed model adapter. Set VITE_API_BASE_URL when the FastAPI service is ready.'}</p></div><button className="primary-btn" onClick={runNewAnalysis} disabled={running}>{running ? <><RefreshCw className="spin"/> Running model…</> : <><Play/> Run analysis</>}</button></section>
      </main>
      <footer><span><Wind size={15}/> CycloneAI</span><span>AI-assisted decision support · Prototype</span><span>Model {analysis.model.version} · API ready</span></footer>
    </div>
  );
}
export default App;
