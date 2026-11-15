import {
  Component,
  Suspense,
  lazy,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  Activity,
  ArrowUpRight,
  Check,
  FileUp,
  FlaskConical,
  Map,
  Menu,
  Orbit,
  Play,
  X,
} from "lucide-react";
import { Button } from "./components/ui/button";
import { demoStudy } from "./data/demo";
import { parseStudyPackage } from "./lib/validate-package";
import { installTilt } from "./lib/tilt";
import { loadSites, loadScientificSite, type SiteOption } from "./lib/science";
import type { StudyPackage } from "./types/frontend";

const Landing = lazy(() => import("./pages/Landing"));
const Explorer = lazy(() => import("./pages/Explorer"));
const ScienceLab = lazy(() => import("./pages/ScienceLab"));
const Story = lazy(() => import("./pages/Story"));
const routes = ["home", "explore", "science", "story"] as const;
type Route = (typeof routes)[number];
const getRoute = (): Route =>
  routes.includes(location.hash.slice(1) as Route)
    ? (location.hash.slice(1) as Route)
    : "home";
const nav = [
  { route: "home", label: "Overview", icon: Orbit },
  { route: "explore", label: "Explore", icon: Map },
  { route: "science", label: "Science Lab", icon: FlaskConical },
  { route: "story", label: "Guided story", icon: Play },
] as const;

export default function App() {
  const [route, setRoute] = useState<Route>(getRoute);
  const [study, setStudy] = useState<StudyPackage>(demoStudy);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sites,setSites] = useState<SiteOption[]>([]), [siteId,setSiteId] = useState("");
  const [loading,setLoading] = useState(false);
  const apiSource = import.meta.env.VITE_SARPULSE_API_URL as string | undefined;
  const dataSource = new URL(apiSource ?? import.meta.env.VITE_SARPULSE_DATA_URL ?? `${import.meta.env.BASE_URL}data/`, location.origin).href;
  const fileInput = useRef<HTMLInputElement>(null);
  const main = useRef<HTMLElement>(null);
  useEffect(() => installTilt(document.body), []);
  useEffect(() => {
    const controller = new AbortController();
    void loadSites(dataSource,Boolean(apiSource),controller.signal).then(options => {
      if (controller.signal.aborted) return;
      setSites(options); if(options.length) setSiteId(options[0].id);
    }).catch(e=>{if(!controller.signal.aborted && apiSource) setError(`Configured data source is unavailable: ${e.message}. The labelled demo remains open.`);});
    return ()=>controller.abort();
  },[dataSource,apiSource]);
  useEffect(() => {
    if(!siteId) return;
    const controller=new AbortController(); setLoading(true);
    void loadScientificSite(dataSource,siteId,Boolean(apiSource),controller.signal).then(s=>{
      if(!controller.signal.aborted){setStudy(s);setError("");setNotice(`Opened ${s.title}. ${s.science?.analysis.data_status}.`);}
    }).catch(e=>{if(!controller.signal.aborted) setError(`Investigation could not load: ${e.message}`);})
      .finally(()=>{if(!controller.signal.aborted)setLoading(false);});
    return ()=>controller.abort();
  },[siteId,dataSource,apiSource]);
  useEffect(() => {
    const onHash = () => {
      setRoute(getRoute());
      setMobileOpen(false);
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  useEffect(() => {
    document.title = `${nav.find((n) => n.route === route)?.label} · SARPulse`;
    main.current?.focus({ preventScroll: true });
  }, [route]);
  async function loadFile(file?: File) {
    if (!file) return;
    setError("");
    setNotice("");
    try {
      if (file.size > 5 * 1024 * 1024)
        throw new Error("Choose a JSON package smaller than 5 MB.");
      const parsed = parseStudyPackage(JSON.parse(await file.text()));
      setStudy(parsed);
      setNotice(
        `Opened ${parsed.title}. ${parsed.status === "synthetic" ? "Synthetic demonstration only." : "Supplied data; review source evidence in Science Lab."}`,
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "The package could not be opened.",
      );
    }
    if (fileInput.current) fileInput.current.value = "";
  }
  return (
    <div className={route === "home" ? "app-shell orbital-shell" : "app-shell"}>
      <a
        className="skip-link"
        href="#main-content"
        onClick={(e) => {
          e.preventDefault();
          main.current?.focus();
        }}
      >
        Skip to content
      </a>
      <header className="app-header">
        <a href="#home" className="brand" aria-label="SARPulse home">
          <span className="brand-symbol">
            <Activity size={25} />
          </span>
          <span>
            SAR<span className="brand-light">Pulse</span>
            <small>by Team StarFire</small>
          </span>
        </a>
        <nav
          className={mobileOpen ? "main-nav is-open" : "main-nav"}
          aria-label="Main navigation"
        >
          {nav.map(({ route: r, label, icon: Icon }) => (
            <a
              key={r}
              href={`#${r}`}
              aria-current={route === r ? "page" : undefined}
            >
              <Icon size={15} />
              {label}
            </a>
          ))}
        </nav>
        <div className="header-actions">
          {sites.length>0 && <label className="investigation-picker">Investigation<select aria-label="Scientific investigation" value={siteId} disabled={loading}
            onChange={e=>setSiteId(e.target.value)}>{sites.map(s=><option value={s.id} key={s.id}>{s.name}</option>)}</select></label>}
          <Button
            variant="outline"
            size="sm"
            aria-label="Open data package"
            onClick={() => fileInput.current?.click()}
          >
            <FileUp size={15} />
            <span>Open data package</span>
          </Button>
          <input
            ref={fileInput}
            type="file"
            accept=".json,application/json"
            className="sr-only"
            aria-label="Open local data package"
            onChange={(e) => void loadFile(e.target.files?.[0])}
          />
          <Button
            variant="ghost"
            size="icon"
            className="mobile-menu"
            aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X /> : <Menu />}
          </Button>
        </div>
      </header>
      <div className={`data-banner ${study.status}`}>
        <span className="data-badge">
          {study.status === "synthetic" ? "Demo workspace" : "Supplied package"}
        </span>
        <span>
          {study.status === "synthetic"
            ? "SYNTHETIC/DEMO — NOT NASA OBSERVATIONS. No measured change or validated flood results."
            : study.science ? `NASA NISAR observations · ${[...new Set(study.science.scenes.map(s=>s.maturity))].join(", ")} · Exploratory water candidates. Review validation and limitations in Science Lab.`
              : "Imported locally. Source metadata is preserved; scientific validity is not verified by this viewer."}
        </span>
        {study !== demoStudy && (
          <button
            onClick={() => {
              setStudy(demoStudy);
              setNotice("Restored the synthetic demo package.");
            }}
          >
            Reset demo
          </button>
        )}
      </div>
      {(notice || error) && (
        <div
          className={error ? "app-notice error" : "app-notice"}
          role={error ? "alert" : "status"}
        >
          {!error && <Check size={17} />}
          <span>{error || notice}</span>
          <button
            onClick={() => {
              setNotice("");
              setError("");
            }}
            aria-label="Dismiss message"
          >
            <X size={16} />
          </button>
        </div>
      )}
      <main id="main-content" tabIndex={-1} ref={main}>
        <PageBoundary key={`${route}-${study.title}`}>
          <Suspense
            fallback={
              <div className="page-loading" role="status">
                Opening workspace…
              </div>
            }
          >
            {route === "home" && <Landing study={study} />}
            {route === "explore" && (
              <Explorer key={JSON.stringify(study)} study={study} />
            )}
            {route === "science" && <ScienceLab study={study} />}
            {route === "story" && (
              <Story key={JSON.stringify(study)} study={study} />
            )}
          </Suspense>
        </PageBoundary>
      </main>
      <footer className="app-footer">
        <span>
          <Activity size={14} /> SARPulse{" "}
          <span className="footer-separator">/</span> Earth’s changes. Revealed
          by radar.
        </span>
        <span>
          Independent Team StarFire project{" "}
          <a
            href="https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/"
            target="_blank"
            rel="noreferrer"
          >
            Challenge <ArrowUpRight size={12} />
          </a>
        </span>
      </footer>
    </div>
  );
}

class PageBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <div className="page-loading">
        <h1>This view could not open</h1>
        <p>Reload to retry loading the application resources.</p>
        <Button onClick={() => location.reload()}>Reload application</Button>
      </div>
    ) : (
      this.props.children
    );
  }
}
