import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import ForecastChart from "./components/ForecastChart";
import HourlyWeather from "./components/HourlyWeather";

import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : window.location.origin);

const routes = [
  ["/dashboard", "Dashboard"],
  ["/weather", "Live Weather"],
  ["/map", "Map"],
  ["/history", "History"],
  ["/reports", "Reports"],
  ["/analytics", "Analytics"],
  ["/alerts", "Alerts"],
  ["/sih26069", "SIH Extensions"],
  ["/report", "Citizen Report"],
  ["/admin/login", "Admin Login"],
  ["/admin/dashboard", "Admin"],
  ["/admin/reports", "Review"],
  ["/admin/events", "Events"],
  ["/admin/sources", "Sources"],
  ["/admin/audit", "Audit"],
];

function currentPath() {
  return window.location.pathname === "/" ? "/dashboard" : window.location.pathname;
}

function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

  if (!response.ok) {
    let message = `Request failed with ${response.status}`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }

  return response.json();
}

function authHeaders() {
  const token = localStorage.getItem("weathernova_admin_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function StatusPill({ children, tone = "info" }) {
  return <span className={`status-pill status-${tone}`}>{children}</span>;
}

function statusTone(status = "") {
  const normalized = String(status).toUpperCase();

  if (["READY", "IMPLEMENTED", "VERIFIED", "ACTIVE"].includes(normalized)) {
    return "success";
  }

  if (["NOT_RUNNING", "REJECTED", "FAILED"].includes(normalized)) {
    return "danger";
  }

  if (["CONFIGURED", "PENDING", "HEURISTIC_PROTOTYPE"].includes(normalized)) {
    return "warn";
  }

  return "info";
}

function Metric({ label, value, note }) {
  return (
    <div className="analytics-card">
      <span className="analytics-card-label">{label}</span>
      <span className="analytics-card-value">{value ?? 0}</span>
      <span className="analytics-card-description">{note}</span>
    </div>
  );
}

function PageHeader({ eyebrow, title, description }) {
  return (
    <section className="page-header">
      <span className="section-eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
  );
}

function DataTable({ columns, rows, empty = "No data available." }) {
  return (
    <div className="table-wrapper">
      <table className="reports-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} style={{ textAlign: "center" }}>
                {empty}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={row.id || JSON.stringify(row)}>
                {columns.map((column) => (
                  <td key={column.key}>
                    {column.render ? column.render(row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

function useCoreData() {
  const [analytics, setAnalytics] = useState(null);
  const [reports, setReports] = useState([]);
  const [events, setEvents] = useState([]);
  const [sources, setSources] = useState([]);
  const [alerts, setAlerts] = useState({ active_alerts: [], verified_signals: [] });
  const [pipeline, setPipeline] = useState(null);
  const [ingestionJobs, setIngestionJobs] = useState([]);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    setError("");

    try {
      const [summary, reportRows, eventRows, sourceRows, alertRows, pipelineStatus, jobs] =
        await Promise.all([
          request("/analytics/summary"),
          request("/reports/?limit=100"),
          request("/events/"),
          request("/sources/"),
          request("/alerts/"),
          request("/big-data/pipeline"),
          request("/big-data/ingestion-jobs"),
        ]);

      setAnalytics(summary);
      setReports(reportRows);
      setEvents(eventRows);
      setSources(sourceRows);
      setAlerts(alertRows);
      setPipeline(pipelineStatus);
      setIngestionJobs(jobs);
    } catch (err) {
      setError(err.message || "Unable to load WeatherNova data.");
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  return { analytics, reports, events, sources, alerts, pipeline, ingestionJobs, error, reload };
}

function Dashboard({ data }) {
  const { analytics, reports, events, sources, alerts, pipeline, error } = data;

  return (
    <>
      <PageHeader
        eyebrow="SIH26069 Control Room"
        title="WeatherNova Dashboard"
        description="Verified weather intelligence, citizen signals, source health, and operational analytics."
      />
      {error && <div className="error-message">{error}</div>}
      <div className="analytics-cards">
        <Metric label="Reports" value={analytics?.total_reports} note="Collected weather signals" />
        <Metric label="Verified" value={analytics?.verified_reports} note="Confirmed reports" />
        <Metric label="Duplicates" value={analytics?.duplicate_reports} note="Repeated signals" />
        <Metric label="Alerts" value={alerts.active_alerts.length} note="Active event warnings" />
      </div>
      <section className="dashboard-grid">
        <div className="reports-section">
          <div className="reports-header">
            <h2>Operational Coverage</h2>
            <p>Collection and analysis components exposed by the platform.</p>
          </div>
          <div className="coverage-grid">
            {Object.entries(pipeline?.ingestion || {}).map(([name, status]) => (
              <div className="coverage-item" key={name}>
                <span>{name.replaceAll("_", " ")}</span>
                <StatusPill tone={statusTone(status)}>
                  {status}
                </StatusPill>
              </div>
            ))}
          </div>
        </div>
        <div className="reports-section">
          <div className="reports-header">
            <h2>Source Reliability</h2>
            <p>Configured source classes and reliability scores.</p>
          </div>
          <div className="source-list">
            {sources.map((source) => (
              <div className="source-row" key={source.id}>
                <div>
                  <strong>{source.name}</strong>
                  <span>{source.source_type}</span>
                </div>
                <StatusPill tone={source.is_active ? "success" : "warn"}>
                  {Math.round(source.reliability_score * 100)}%
                </StatusPill>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="reports-section">
        <div className="reports-header">
          <h2>Latest Intelligence</h2>
          <p>Recent reports used by WeatherNova.</p>
        </div>
        <DataTable
          rows={reports.slice(0, 8)}
          columns={[
            { key: "source", label: "Source" },
            { key: "event_type", label: "Event" },
            { key: "city", label: "City" },
            { key: "state", label: "State" },
            {
              key: "verification_status",
              label: "Status",
              render: (row) => <StatusPill>{row.verification_status}</StatusPill>,
            },
            { key: "trust_score", label: "Trust" },
          ]}
        />
      </section>
      <EventsPanel events={events} />
    </>
  );
}

function WeatherPage({ reload }) {
  const [city, setCity] = useState("");
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  async function searchWeather(cityName) {
    const trimmed = cityName.trim();

    if (!trimmed) {
      setError("Please enter a city name.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await request(`/weather/?city=${encodeURIComponent(trimmed)}`);
      setWeather(data);
      setCity(data.city);
      setHistory((items) => [data.city, ...items.filter((item) => item !== data.city)].slice(0, 8));
      await reload();
    } catch (err) {
      setError(err.message || "Unable to fetch weather.");
    } finally {
      setLoading(false);
    }
  }

  function useLocation() {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      return;
    }

    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          const data = await request(
            `/weather/location?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`
          );
          await searchWeather(data.city);
        } catch (err) {
          setError(err.message || "Unable to use your location.");
        } finally {
          setLocating(false);
        }
      },
      () => {
        setError("Location permission was denied or unavailable.");
        setLocating(false);
      }
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Live Weather"
        title="Search current weather"
        description="Fetch current conditions, hourly forecast, 7-day outlook, ML classification, duplicate detection, and risk scoring."
      />
      <section className="search-section">
        <form
          className="search-form"
          onSubmit={(event) => {
            event.preventDefault();
            searchWeather(city);
          }}
        >
          <input
            className="search-input"
            value={city}
            onChange={(event) => setCity(event.target.value)}
            placeholder="Search for a city..."
          />
          <button className="search-button" disabled={loading}>
            {loading ? "Loading..." : "Search"}
          </button>
          <button className="search-button secondary-button" type="button" onClick={useLocation} disabled={locating}>
            {locating ? "Locating..." : "Use Location"}
          </button>
        </form>
        {history.length > 0 && (
          <div className="history-list">
            {history.map((item) => (
              <button className="history-chip" key={item} onClick={() => searchWeather(item)}>
                {item}
              </button>
            ))}
          </div>
        )}
        {error && <div className="error-message">{error}</div>}
      </section>
      {weather && (
        <>
          <section className="weather-section">
            <div className="weather-main-card">
              <span className="weather-location">{weather.city}, {weather.state}</span>
              <div className="weather-main-content">
                <div>
                  <h2 className="temperature">
                    {Math.round(weather.temperature)}
                    <span className="temperature-unit">C</span>
                  </h2>
                  <div className="weather-description">{weather.condition}</div>
                </div>
                <div className="current-condition">
                  <span className="condition-icon">{weather.condition_icon}</span>
                  <span className="condition-label">{weather.event_type}</span>
                </div>
              </div>
              <div className="weather-details">
                <Detail label="Humidity" value={`${weather.humidity}%`} />
                <Detail label="Wind" value={`${weather.wind_speed} km/h`} />
                <Detail label="Rain Chance" value={`${weather.precipitation_probability ?? 0}%`} />
                <Detail label="ML Class" value={weather.ml_event_type} />
                <Detail label="ML Confidence" value={`${Math.round((weather.ml_confidence || 0) * 100)}%`} />
                <Detail label="Duplicate" value={weather.is_duplicate ? "Yes" : "No"} />
              </div>
            </div>
            <div className="risk-card">
              <div className="risk-header">
                <div>
                  <h2 className="risk-title">Risk Score</h2>
                  <span className="risk-subtitle">Current weather event risk</span>
                </div>
                <span className="risk-level">{weather.risk?.level}</span>
              </div>
              <div className="risk-score">
                <span className="risk-score-number">{weather.risk?.score ?? 0}</span>
                <span className="risk-score-label">/ 100</span>
              </div>
              <div className="risk-bar">
                <div className="risk-bar-fill" style={{ width: `${weather.risk?.score ?? 0}%` }} />
              </div>
              <div className="risk-reasons">
                {(weather.risk?.reasons || []).map((reason) => (
                  <div className="risk-reason" key={reason}>{reason}</div>
                ))}
              </div>
            </div>
          </section>
          <ForecastChart forecast={weather.forecast || []} />
          <HourlyWeather hourly={weather.hourly || []} />
        </>
      )}
    </>
  );
}

function Detail({ label, value }) {
  return (
    <div className="detail-item">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{value ?? "--"}</span>
    </div>
  );
}

function MapPage({ reports }) {
  const plotted = reports.filter((report) => report.latitude && report.longitude);

  return (
    <>
      <PageHeader
        eyebrow="Weather Map"
        title="Geospatial report view"
        description="Mapped report coordinates with verification context."
      />
      <section className="map-panel">
        <div className="map-canvas">
          {plotted.slice(0, 60).map((report) => (
            <span
              className={`map-point map-${report.verification_status}`}
              key={report.id}
              title={`${report.event_type} in ${report.city}`}
              style={{
                left: `${Math.min(96, Math.max(4, ((Number(report.longitude) + 180) / 360) * 100))}%`,
                top: `${Math.min(92, Math.max(8, (1 - (Number(report.latitude) + 90) / 180) * 100))}%`,
              }}
            />
          ))}
        </div>
      </section>
      <section className="reports-section">
        <DataTable
          rows={plotted}
          columns={[
            { key: "event_type", label: "Event" },
            { key: "city", label: "City" },
            { key: "state", label: "State" },
            { key: "latitude", label: "Lat" },
            { key: "longitude", label: "Lng" },
            {
              key: "verification_status",
              label: "Status",
              render: (row) => <StatusPill>{row.verification_status}</StatusPill>,
            },
          ]}
        />
      </section>
    </>
  );
}

function ReportsPage({ reports, title = "Report review queue" }) {
  const [filters, setFilters] = useState({ event_type: "", state: "", verification_status: "" });
  const eventTypes = [...new Set(reports.map((report) => report.event_type).filter(Boolean))];
  const states = [...new Set(reports.map((report) => report.state).filter(Boolean))];
  const filtered = reports.filter((report) =>
    (!filters.event_type || report.event_type === filters.event_type) &&
    (!filters.state || report.state === filters.state) &&
    (!filters.verification_status || report.verification_status === filters.verification_status)
  );

  return (
    <>
      <PageHeader
        eyebrow="Reports"
        title={title}
        description="Filter, inspect, and export weather reports collected from APIs and citizens."
      />
      <FilterBar filters={filters} setFilters={setFilters} eventTypes={eventTypes} states={states} />
      <div className="action-row">
        <a className="download-button" href={`${API_BASE_URL}/reports/export`}>Export CSV</a>
      </div>
      <section className="reports-section">
        <DataTable
          rows={filtered}
          columns={[
            { key: "source", label: "Source" },
            { key: "event_type", label: "Event" },
            { key: "city", label: "City" },
            { key: "state", label: "State" },
            {
              key: "verification_status",
              label: "Status",
              render: (row) => <StatusPill>{row.verification_status}</StatusPill>,
            },
            { key: "confidence_score", label: "Confidence" },
            { key: "trust_score", label: "Trust" },
            { key: "misinformation_score", label: "Risk" },
            { key: "media_count", label: "Media" },
            { key: "is_duplicate", label: "Duplicate", render: (row) => row.is_duplicate ? "Yes" : "No" },
          ]}
        />
      </section>
      <ReportEvidence reports={filtered.slice(0, 6)} />
    </>
  );
}

function ReportEvidence({ reports }) {
  const rows = reports.filter((report) => (
    report.media_count ||
    report.source_url ||
    report.hashtags?.length ||
    report.verification_notes
  ));

  if (rows.length === 0) {
    return null;
  }

  return (
    <section className="reports-section">
      <div className="reports-header">
        <h2>Evidence and Verification Signals</h2>
        <p>Prototype verification labels expose the signals used; external fact-checking is not claimed.</p>
      </div>
      <div className="evidence-grid">
        {rows.map((report) => (
          <div className="evidence-item" key={report.id}>
            <div className="evidence-title">
              <strong>{report.event_type}</strong>
              <StatusPill tone={statusTone(report.verification_status)}>{report.verification_status}</StatusPill>
            </div>
            <p>{report.verification_notes || "No verification notes recorded."}</p>
            <div className="evidence-meta">
              <span>Trust {Math.round((report.trust_score || 0) * 100)}%</span>
              <span>Misleading risk {Math.round((report.misinformation_score || 0) * 100)}%</span>
              <span>Media {report.media_count || 0}</span>
            </div>
            {report.source_url && <a href={report.source_url} target="_blank" rel="noreferrer">Source reference</a>}
            {report.hashtags?.length > 0 && <div className="tag-list">{report.hashtags.map((tag) => <span key={tag}>{tag}</span>)}</div>}
          </div>
        ))}
      </div>
    </section>
  );
}

function FilterBar({ filters, setFilters, eventTypes, states }) {
  return (
    <section className="filter-bar">
      <select value={filters.event_type} onChange={(event) => setFilters((old) => ({ ...old, event_type: event.target.value }))}>
        <option value="">All events</option>
        {eventTypes.map((item) => <option key={item}>{item}</option>)}
      </select>
      <select value={filters.state} onChange={(event) => setFilters((old) => ({ ...old, state: event.target.value }))}>
        <option value="">All locations</option>
        {states.map((item) => <option key={item}>{item}</option>)}
      </select>
      <select value={filters.verification_status} onChange={(event) => setFilters((old) => ({ ...old, verification_status: event.target.value }))}>
        <option value="">All verification</option>
        <option value="pending">Pending</option>
        <option value="verified">Verified</option>
        <option value="rejected">Rejected</option>
      </select>
    </section>
  );
}

function AnalyticsPage({ analytics }) {
  const colors = ["#38bdf8", "#22c55e", "#f97316", "#eab308", "#f43f5e"];

  return (
    <>
      <PageHeader
        eyebrow="Analytics"
        title="Weather intelligence analytics"
        description="Event distribution, location concentration, severity mix, and verification health."
      />
      <div className="analytics-cards">
        <Metric label="Reports" value={analytics?.total_reports} note="Total stored reports" />
        <Metric label="Events" value={analytics?.total_events} note="Detected weather events" />
        <Metric label="Verified" value={analytics?.verified_reports} note="Verified reports" />
        <Metric label="Duplicates" value={analytics?.duplicate_reports} note="Duplicate reports" />
      </div>
      <section className="analytics-grid">
        <ChartCard title="Reports by Event">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={analytics?.reports_by_event || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,.15)" />
              <XAxis dataKey="event_type" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Bar dataKey="count" fill="#38bdf8" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Events by Severity">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={analytics?.events_by_severity || []} dataKey="count" nameKey="severity" outerRadius={95}>
                {(analytics?.events_by_severity || []).map((entry, index) => (
                  <Cell key={entry.severity} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </section>
    </>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="analytics-chart-card">
      <h2 className="analytics-chart-title">{title}</h2>
      {children}
    </div>
  );
}

function AlertsPage({ alerts }) {
  return (
    <>
      <PageHeader
        eyebrow="Alerts"
        title="Active alert center"
        description="Verified high-signal events and non-normal weather reports."
      />
      <section className="reports-section">
        <DataTable
          rows={alerts.active_alerts}
          columns={[
            { key: "title", label: "Alert" },
            { key: "event_type", label: "Event" },
            { key: "city", label: "City" },
            { key: "state", label: "State" },
            {
              key: "severity",
              label: "Severity",
              render: (row) => <StatusPill tone={row.severity === "high" ? "danger" : "warn"}>{row.severity}</StatusPill>,
            },
            { key: "status", label: "Status" },
          ]}
        />
      </section>
    </>
  );
}

function CitizenReport({ reload }) {
  const [form, setForm] = useState({
    city: "",
    state: "",
    event_type: "Rain",
    description: "",
    latitude: "",
    longitude: "",
    source_url: "",
    media_urls: "",
    hashtags: "",
  });
  const [message, setMessage] = useState("");

  async function submit(event) {
    event.preventDefault();
    setMessage("");

    try {
      await request("/reports/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          latitude: form.latitude ? Number(form.latitude) : null,
          longitude: form.longitude ? Number(form.longitude) : null,
          source: "WeatherNova User",
          verification_status: "pending",
          media_urls: form.media_urls.split(",").map((item) => item.trim()).filter(Boolean),
          hashtags: form.hashtags.split(",").map((item) => item.trim()).filter(Boolean),
        }),
      });
      setMessage("Report submitted for verification.");
      setForm((old) => ({ ...old, description: "", media_urls: "", source_url: "", hashtags: "" }));
      await reload();
    } catch (err) {
      setMessage(err.message || "Unable to submit report.");
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Citizen Reports"
        title="Submit local weather evidence"
        description="Capture metadata required for verification: time, city, state, GPS, source, category, and observation text."
      />
      <form className="form-panel" onSubmit={submit}>
        {["city", "state", "latitude", "longitude", "source_url"].map((field) => (
          <input key={field} value={form[field]} placeholder={field.replace("_", " ")} onChange={(event) => setForm((old) => ({ ...old, [field]: event.target.value }))} />
        ))}
        <select value={form.event_type} onChange={(event) => setForm((old) => ({ ...old, event_type: event.target.value }))}>
          {["Rain", "Thunderstorm", "Snow", "Fog", "Wind", "Extreme Weather", "Clear/Cloudy", "Other"].map((item) => <option key={item}>{item}</option>)}
        </select>
        <input value={form.media_urls} placeholder="Photo/video URLs, comma separated" onChange={(event) => setForm((old) => ({ ...old, media_urls: event.target.value }))} />
        <input value={form.hashtags} placeholder="Hashtags, comma separated" onChange={(event) => setForm((old) => ({ ...old, hashtags: event.target.value }))} />
        <textarea value={form.description} placeholder="Observation, impact, and source notes" onChange={(event) => setForm((old) => ({ ...old, description: event.target.value }))} />
        <button className="search-button">Submit Report</button>
        {message && <div className="error-message">{message}</div>}
      </form>
    </>
  );
}

function SIHExtensionsPage({ data }) {
  const { pipeline, ingestionJobs, sources } = data;
  const streamingRows = [
    pipeline?.streaming?.kafka,
    pipeline?.streaming?.spark,
  ].filter(Boolean);

  return (
    <>
      <PageHeader
        eyebrow="SIH26069 Extensions"
        title="Ingestion, verification, and big-data readiness"
        description="Configuration-driven surfaces for real external connectors. Unconfigured systems are clearly marked and no live data is fabricated."
      />
      <div className="analytics-cards">
        <Metric label="Weather API" value={pipeline?.ingestion?.weather_api || "READY"} note="Open-Meteo remains active" />
        <Metric label="Social" value={pipeline?.ingestion?.social_media || "NOT_CONFIGURED"} note="#IMD and weather hashtag connector" />
        <Metric label="Public Sources" value={pipeline?.ingestion?.public_apis || "NOT_CONFIGURED"} note="Datasets, websites, APIs" />
        <Metric label="Verification" value={pipeline?.analytics?.verification_signals || "HEURISTIC"} note="Transparent prototype signals" />
      </div>
      <section className="dashboard-grid">
        <div className="reports-section">
          <div className="reports-header">
            <h2>Connector Configuration</h2>
            <p>Credentials and source URLs control whether connectors become live.</p>
          </div>
          <div className="coverage-grid">
            {(pipeline?.connectors || []).map((connector) => (
              <div className="coverage-item stacked" key={connector.name}>
                <div>
                  <strong>{connector.name}</strong>
                  <span>{connector.detail}</span>
                </div>
                <StatusPill tone={statusTone(connector.state)}>{connector.state}</StatusPill>
              </div>
            ))}
          </div>
        </div>
        <div className="reports-section">
          <div className="reports-header">
            <h2>Kafka / Spark Runtime</h2>
            <p>Runtime checks do not mark services ready unless endpoints are configured and reachable.</p>
          </div>
          <div className="coverage-grid">
            {streamingRows.map((runtime) => (
              <div className="coverage-item stacked" key={runtime.name}>
                <div>
                  <strong>{runtime.name}</strong>
                  <span>{runtime.detail}</span>
                </div>
                <StatusPill tone={statusTone(runtime.state)}>{runtime.state}</StatusPill>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="reports-section">
        <div className="reports-header">
          <h2>Source Registry</h2>
          <p>Operational status and configuration metadata for source classes.</p>
        </div>
        <DataTable
          rows={sources}
          columns={[
            { key: "name", label: "Source" },
            { key: "source_type", label: "Type" },
            { key: "runtime_status", label: "Runtime", render: (row) => <StatusPill tone={statusTone(row.runtime_status)}>{row.runtime_status || "NOT_CONFIGURED"}</StatusPill> },
            { key: "auth_required", label: "Auth", render: (row) => row.auth_required ? "Required" : "No" },
            { key: "status_notes", label: "Notes" },
          ]}
        />
      </section>
      <section className="reports-section">
        <div className="reports-header">
          <h2>Ingestion Jobs</h2>
          <p>Registered and executed ingestion jobs. Registration alone does not imply data was fetched.</p>
        </div>
        <DataTable
          rows={ingestionJobs}
          empty="No ingestion jobs registered yet."
          columns={[
            { key: "source_name", label: "Source" },
            { key: "source_type", label: "Type" },
            { key: "connector_status", label: "Connector", render: (row) => <StatusPill tone={statusTone(row.connector_status)}>{row.connector_status}</StatusPill> },
            { key: "status", label: "Job" },
            { key: "records_seen", label: "Seen" },
            { key: "records_created", label: "Created" },
            { key: "notes", label: "Notes" },
          ]}
        />
      </section>
      {pipeline?.production_scale_note && <div className="notice-panel">{pipeline.production_scale_note}</div>}
    </>
  );
}

function EventsPanel({ events }) {
  return (
    <section className="events-section">
      <div className="events-header">
        <div>
          <h2>Weather Events</h2>
          <p>Detected and admin-managed weather events.</p>
        </div>
      </div>
      <div className="events-grid">
        {events.length === 0 ? <p>No active events yet.</p> : events.slice(0, 9).map((event) => (
          <div className="event-card" key={event.id}>
            <div className="event-title">{event.title}</div>
            <div className="event-location">{event.city}, {event.state}</div>
            <div className="event-meta">
              <span className={`severity-badge severity-${event.severity}`}>{event.severity}</span>
              <span className="event-status">{event.status}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function AdminLogin() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [message, setMessage] = useState("");

  async function login(event) {
    event.preventDefault();

    try {
      const data = await request("/admin-api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      localStorage.setItem("weathernova_admin_token", data.token);
      navigate("/admin/dashboard");
    } catch (err) {
      setMessage(err.message || "Login failed.");
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Admin"
        title="Admin login"
        description="Authenticate to review reports, manage events, configure sources, and inspect audit logs."
      />
      <form className="form-panel compact-form" onSubmit={login}>
        <input value={form.username} placeholder="Username" onChange={(event) => setForm((old) => ({ ...old, username: event.target.value }))} />
        <input value={form.password} type="password" placeholder="Password" onChange={(event) => setForm((old) => ({ ...old, password: event.target.value }))} />
        <button className="search-button">Login</button>
        {message && <div className="error-message">{message}</div>}
      </form>
    </>
  );
}

function AdminPages({ path, data }) {
  const [adminSummary, setAdminSummary] = useState(null);
  const [audit, setAudit] = useState([]);
  const [message, setMessage] = useState("");

  const loadAdmin = useCallback(async () => {
    try {
      const [summary, auditRows] = await Promise.all([
        request("/admin-api/dashboard", { headers: authHeaders() }),
        request("/admin-api/audit", { headers: authHeaders() }),
      ]);
      setAdminSummary(summary);
      setAudit(auditRows);
      setMessage("");
    } catch (err) {
      setMessage(`${err.message}. Please log in again if your session expired.`);
    }
  }, []);

  useEffect(() => {
    loadAdmin();
  }, [loadAdmin]);

  async function updateReport(report, patch) {
    await request(`/admin-api/reports/${report.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(patch),
    });
    await data.reload();
    await loadAdmin();
  }

  async function updateEvent(event, patch) {
    await request(`/admin-api/events/${event.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(patch),
    });
    await data.reload();
    await loadAdmin();
  }

  if (path === "/admin/audit") {
    return (
      <>
        <PageHeader eyebrow="Admin" title="Audit logs" description="Trace report reviews, event edits, and source management actions." />
        {message && <div className="error-message">{message}</div>}
        <section className="reports-section">
          <DataTable rows={audit} columns={[
            { key: "actor", label: "Actor" },
            { key: "action", label: "Action" },
            { key: "entity_type", label: "Entity" },
            { key: "entity_id", label: "ID" },
            { key: "created_at", label: "Time" },
          ]} />
        </section>
      </>
    );
  }

  if (path === "/admin/events") {
    return (
      <>
        <PageHeader eyebrow="Admin" title="Event management" description="Close, reopen, and classify tracked weather events." />
        <EventsPanel events={data.events} />
        <section className="reports-section">
          {data.events.map((event) => (
            <div className="admin-action-row" key={event.id}>
              <span>{event.title}</span>
              <button onClick={() => updateEvent(event, { status: "active" })}>Active</button>
              <button onClick={() => updateEvent(event, { status: "resolved" })}>Resolved</button>
            </div>
          ))}
        </section>
      </>
    );
  }

  if (path === "/admin/sources") {
    return (
      <>
        <PageHeader eyebrow="Admin" title="Source management" description="Monitor source types, active status, and reliability scoring." />
        <section className="reports-section">
          <DataTable rows={data.sources} columns={[
            { key: "name", label: "Source" },
            { key: "source_type", label: "Type" },
            { key: "reliability_score", label: "Reliability", render: (row) => `${Math.round(row.reliability_score * 100)}%` },
            { key: "runtime_status", label: "Runtime", render: (row) => <StatusPill tone={statusTone(row.runtime_status)}>{row.runtime_status || "NOT_CONFIGURED"}</StatusPill> },
            { key: "is_active", label: "Active", render: (row) => row.is_active ? "Yes" : "No" },
            { key: "status_notes", label: "Notes" },
          ]} />
        </section>
      </>
    );
  }

  if (path === "/admin/reports") {
    return (
      <>
        <PageHeader eyebrow="Admin" title="Report review" description="Verify, reject, or mark duplicate reports." />
        {message && <div className="error-message">{message}</div>}
        <section className="reports-section">
          {data.reports.map((report) => (
            <div className="admin-action-row" key={report.id}>
              <span>{report.event_type} in {report.city} from {report.source} · risk {Math.round((report.misinformation_score || 0) * 100)}% · media {report.media_count || 0}</span>
              <button onClick={() => updateReport(report, { verification_status: "verified", trust_score: 0.9, confidence_score: 0.9 })}>Verify</button>
              <button onClick={() => updateReport(report, { verification_status: "rejected", trust_score: 0.1, misinformation_score: 0.9 })}>Reject</button>
              <button onClick={() => updateReport(report, { is_duplicate: true })}>Duplicate</button>
            </div>
          ))}
        </section>
      </>
    );
  }

  return (
    <>
      <PageHeader eyebrow="Admin" title="Admin dashboard" description="Review operational counts and jump into moderation tools." />
      {message && <div className="error-message">{message}</div>}
      <div className="analytics-cards">
        <Metric label="Pending" value={adminSummary?.pending_reports} note="Awaiting review" />
        <Metric label="Verified" value={adminSummary?.verified_reports} note="Approved reports" />
        <Metric label="Rejected" value={adminSummary?.rejected_reports} note="Rejected reports" />
        <Metric label="Audit" value={adminSummary?.audit_entries} note="Logged actions" />
      </div>
    </>
  );
}

function App() {
  const [path, setPath] = useState(currentPath());
  const data = useCoreData();

  useEffect(() => {
    const onPop = () => setPath(currentPath());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const page = useMemo(() => {
    if (path === "/weather") return <WeatherPage reload={data.reload} />;
    if (path === "/map") return <MapPage reports={data.reports} />;
    if (path === "/history") return <ReportsPage reports={data.reports} title="Historical weather reports" />;
    if (path === "/reports") return <ReportsPage reports={data.reports} />;
    if (path === "/analytics") return <AnalyticsPage analytics={data.analytics} />;
    if (path === "/alerts") return <AlertsPage alerts={data.alerts} />;
    if (path === "/sih26069") return <SIHExtensionsPage data={data} />;
    if (path === "/report") return <CitizenReport reload={data.reload} />;
    if (path === "/admin/login") return <AdminLogin />;
    if (path.startsWith("/admin")) return <AdminPages path={path} data={data} />;
    return <Dashboard data={data} />;
  }, [path, data]);

  return (
    <div className="app">
      <div className="app-container">
        <header className="topbar">
          <button className="brand nav-button" onClick={() => navigate("/dashboard")}>
            <div className="brand-mark">WN</div>
            <div className="brand-text">
              <span className="brand-name">WeatherNova</span>
              <span className="brand-subtitle">Weather Intelligence</span>
            </div>
          </button>
          <div className="system-status"><span className="status-dot" /> API Connected</div>
        </header>
        <nav className="route-nav">
          {routes.map(([href, label]) => (
            <button className={path === href ? "active" : ""} key={href} onClick={() => navigate(href)}>
              {label}
            </button>
          ))}
        </nav>
        <main>{page}</main>
        <footer className="footer">
          <span><strong>WeatherNova</strong> SIH26069 weather intelligence platform</span>
          <span>Open-Meteo / FastAPI / PostgreSQL / React</span>
        </footer>
      </div>
    </div>
  );
}

export default App;
