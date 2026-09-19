import { useEffect, useState } from "react";

import AnalyticsCards from "./components/AnalyticsCards";
import EventChart from "./components/EventChart";
import EventsList from "./components/EventsList";
import ForecastChart from "./components/ForecastChart";
import HourlyWeather from "./components/HourlyWeather";
import SeverityChart from "./components/SeverityChart";
import StateChart from "./components/StateChart";

import "./App.css";

const API_BASE_URL =
  "http://127.0.0.1:8000";


function App() {
  const [city, setCity] =
    useState("");

  const [weather, setWeather] =
    useState(null);

  const [analytics, setAnalytics] =
    useState(null);

  const [reports, setReports] =
    useState([]);

  const [events, setEvents] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [refreshing, setRefreshing] =
    useState(false);

  const [locating, setLocating] =
    useState(false);

  const [error, setError] =
    useState("");

  const [searchHistory, setSearchHistory] =
    useState([]);

  const [lastUpdated, setLastUpdated] =
    useState(null);

  const [reportForm, setReportForm] =
    useState({
      city: "",
      state: "",
      event_type: "Clear/Cloudy",
      description: "",
    });

  const [reportSubmitting, setReportSubmitting] =
    useState(false);

  const [reportMessage, setReportMessage] =
    useState("");


  async function loadAnalytics() {
    const response =
      await fetch(
        `${API_BASE_URL}/analytics/summary`
      );

    if (!response.ok) {
      throw new Error(
        "Unable to load analytics."
      );
    }

    const data =
      await response.json();

    setAnalytics(data);
  }


  async function loadReports() {
    const response =
      await fetch(
        `${API_BASE_URL}/reports/`
      );

    if (!response.ok) {
      throw new Error(
        "Unable to load reports."
      );
    }

    const data =
      await response.json();

    setReports(data);
  }


  async function loadEvents() {
    const response =
      await fetch(
        `${API_BASE_URL}/events/`
      );

    if (!response.ok) {
      throw new Error(
        "Unable to load events."
      );
    }

    const data =
      await response.json();

    setEvents(data);
  }


  async function searchWeather(cityName) {
    const trimmedCity =
      cityName.trim();

    if (!trimmedCity) {
      setError(
        "Please enter a city name."
      );

      return;
    }

    setLoading(true);
    setError("");
    setWeather(null);

    try {
      const response =
        await fetch(
          `${API_BASE_URL}/weather/?city=${encodeURIComponent(
            trimmedCity
          )}`
        );

      if (!response.ok) {
        let message =
          "Unable to fetch weather data.";

        try {
          const errorData =
            await response.json();

          if (errorData.detail) {
            message =
              errorData.detail;
          }
        } catch (err) {
          // Keep default error message.
        }

        throw new Error(message);
      }

      const data =
        await response.json();

      setWeather(data);

      setCity(data.city);

      setLastUpdated(
        new Date()
      );

      setSearchHistory(
        (previousHistory) => {
          const existingCities =
            previousHistory.filter(
              (item) =>
                item.toLowerCase() !==
                data.city.toLowerCase()
            );

          return [
            data.city,
            ...existingCities,
          ].slice(0, 6);
        }
      );

      setReportForm(
        (previousForm) => ({
          ...previousForm,
          city: data.city || previousForm.city,
          state: data.state || previousForm.state,
          event_type:
            data.event_type ||
            previousForm.event_type,
        })
      );

      await Promise.all([
        loadAnalytics(),
        loadReports(),
        loadEvents(),
      ]);
    } catch (err) {
      console.error(
        "Weather search error:",
        err
      );

      setError(
        err.message ||
          "Something went wrong while fetching weather."
      );
    } finally {
      setLoading(false);
    }
  }


  async function refreshWeather(
    showLoading = false
  ) {
    if (!city.trim()) {
      return;
    }

    if (showLoading) {
      setRefreshing(true);
    }

    setError("");

    try {
      const response =
        await fetch(
          `${API_BASE_URL}/weather/?city=${encodeURIComponent(
            city.trim()
          )}`
        );

      if (!response.ok) {
        throw new Error(
          "Unable to refresh weather data."
        );
      }

      const data =
        await response.json();

      setWeather(data);

      setCity(data.city);

      setLastUpdated(
        new Date()
      );

      setReportForm(
        (previousForm) => ({
          ...previousForm,
          city: data.city || previousForm.city,
          state: data.state || previousForm.state,
          event_type:
            data.event_type ||
            previousForm.event_type,
        })
      );

      await Promise.all([
        loadAnalytics(),
        loadReports(),
        loadEvents(),
      ]);
    } catch (err) {
      console.error(
        "Weather refresh error:",
        err
      );

      if (showLoading) {
        setError(
          err.message ||
            "Unable to refresh weather data."
        );
      }
    } finally {
      if (showLoading) {
        setRefreshing(false);
      }
    }
  }


  async function handleManualRefresh() {
    await refreshWeather(true);
  }


  function handleUseMyLocation() {
    if (!navigator.geolocation) {
      setError(
        "Geolocation is not supported by your browser."
      );

      return;
    }

    setLocating(true);
    setError("");

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } =
          position.coords;

        try {
          const response =
            await fetch(
              `${API_BASE_URL}/weather/location?latitude=${encodeURIComponent(
                latitude
              )}&longitude=${encodeURIComponent(
                longitude
              )}`
            );

          if (!response.ok) {
            let message =
              "Unable to determine your city.";

            try {
              const errorData =
                await response.json();

              if (errorData.detail) {
                message = errorData.detail;
              }
            } catch (err) {
              // Keep default error message.
            }

            throw new Error(message);
          }

          const locationData =
            await response.json();

          const rawDetectedCity =
            locationData.city;

          if (!rawDetectedCity) {
            throw new Error(
              "Unable to determine a city from your location."
            );
          }

          const detectedCity =
            rawDetectedCity
              .replace(/\s+(rural|urban)$/i, "")
              .trim();

          setCity(detectedCity);

          await searchWeather(
            detectedCity
          );
        } catch (err) {
          console.error(
            "Location search error:",
            err
          );

          setError(
            err.message ||
              "Unable to use your current location."
          );
        } finally {
          setLocating(false);
        }
      },
      (geoError) => {
        console.error(
          "Geolocation error:",
          geoError
        );

        if (geoError.code === 1) {
          setError(
            "Location permission was denied. Please allow location access in your browser."
          );
        } else if (geoError.code === 2) {
          setError(
            "Your location could not be determined."
          );
        } else if (geoError.code === 3) {
          setError(
            "Location request timed out. Please try again."
          );
        } else {
          setError(
            "Unable to access your location."
          );
        }

        setLocating(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000,
      }
    );
  }


  function handleSearch(event) {
    event.preventDefault();

    searchWeather(city);
  }


  async function handleHistorySearch(
    historyCity
  ) {
    setCity(historyCity);

    await searchWeather(
      historyCity
    );
  }


  function handleReportInputChange(event) {
    const {
      name,
      value,
    } = event.target;

    setReportForm(
      (previousForm) => ({
        ...previousForm,
        [name]: value,
      })
    );

    setReportMessage("");
  }


  async function handleReportSubmit(event) {
    event.preventDefault();

    const trimmedCity =
      reportForm.city.trim();

    const trimmedState =
      reportForm.state.trim();

    const trimmedDescription =
      reportForm.description.trim();

    if (!trimmedCity) {
      setReportMessage(
        "Please enter the city."
      );

      return;
    }

    if (!trimmedState) {
      setReportMessage(
        "Please enter the state or region."
      );

      return;
    }

    if (!trimmedDescription) {
      setReportMessage(
        "Please describe the weather condition."
      );

      return;
    }

    setReportSubmitting(true);
    setReportMessage("");
    setError("");

    try {
      const response =
        await fetch(
          `${API_BASE_URL}/reports/`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              source: "WeatherNova User",
              description:
                trimmedDescription,
              event_type:
                reportForm.event_type,
              city: trimmedCity,
              state: trimmedState,
              latitude:
                weather?.latitude ?? null,
              longitude:
                weather?.longitude ?? null,
              verification_status:
                "pending",
              confidence_score: 0.0,
              trust_score: 0.0,
              is_duplicate: false,
            }),
          }
        );

      if (!response.ok) {
        let message =
          "Unable to submit weather report.";

        try {
          const errorData =
            await response.json();

          if (errorData.detail) {
            if (Array.isArray(errorData.detail)) {
              message =
                errorData.detail
                  .map(
                    (item) =>
                      item.msg
                  )
                  .join(", ");
            } else {
              message =
                errorData.detail;
            }
          }
        } catch (err) {
          // Keep default message.
        }

        throw new Error(message);
      }

      await response.json();

      setReportMessage(
        "Weather report submitted successfully."
      );

      setReportForm(
        (previousForm) => ({
          ...previousForm,
          description: "",
        })
      );

      await Promise.all([
        loadAnalytics(),
        loadReports(),
        loadEvents(),
      ]);
    } catch (err) {
      console.error(
        "Report submission error:",
        err
      );

      setReportMessage(
        err.message ||
          "Unable to submit weather report."
      );
    } finally {
      setReportSubmitting(false);
    }
  }


  useEffect(() => {
    if (!city.trim() || !weather) {
      return undefined;
    }

    const refreshInterval =
      setInterval(
        () => {
          refreshWeather();
        },
        10 * 60 * 1000
      );

    return () => {
      clearInterval(
        refreshInterval
      );
    };
  }, [city, weather]);


  function formatLastUpdated() {
    if (!lastUpdated) {
      return "Waiting for search";
    }

    return lastUpdated.toLocaleTimeString(
      undefined,
      {
        hour: "2-digit",
        minute: "2-digit",
      }
    );
  }


  return (
    <div className="app">

      <div className="app-container">

        <header className="topbar">

          <div className="brand">

            <div className="brand-mark">
              🌩️
            </div>

            <div className="brand-text">

              <span className="brand-name">
                WeatherNova
              </span>

              <span className="brand-subtitle">
                Weather Intelligence
              </span>

            </div>

          </div>


          <div className="system-status">

            <span className="status-dot" />

            API Connected

          </div>

        </header>


        <main>

          <section className="hero">

            <div className="hero-content">

              <span className="hero-eyebrow">
                Real-Time Weather Intelligence
              </span>

              <h1>
                Understand the weather.
                <br />
                Before it changes.
              </h1>

              <p className="hero-description">
                WeatherNova combines live weather
                conditions, forecasts, risk analysis,
                events, and verified reports into one
                intelligence dashboard.
              </p>

            </div>

          </section>


          <section className="search-section">

            <form
              className="search-form"
              onSubmit={handleSearch}
            >

              <div className="search-input-wrapper">

                <input
                  className="search-input"
                  type="text"
                  value={city}
                  onChange={(event) =>
                    setCity(
                      event.target.value
                    )
                  }
                  placeholder="Search for a city..."
                  disabled={
                    loading ||
                    refreshing
                  }
                />

              </div>


              <button
                className="search-button"
                type="submit"
                disabled={
                  loading ||
                  refreshing ||
                  locating
                }
              >

                {loading
                  ? "Loading..."
                  : "Search Weather"}

              </button>


              <button
                className="search-button"
                type="button"
                onClick={handleUseMyLocation}
                disabled={
                  loading ||
                  refreshing ||
                  locating
                }
              >

                {locating
                  ? "Locating..."
                  : "📍 Use My Location"}

              </button>

            </form>


            {searchHistory.length > 0 && (

              <div className="search-history">

                <span>
                  Recent searches
                </span>

                <div className="history-list">

                  {searchHistory.map(
                    (historyCity) => (

                      <button
                        type="button"
                        className="history-chip"
                        key={historyCity}
                        onClick={() =>
                          handleHistorySearch(
                            historyCity
                          )
                        }
                        disabled={
                          loading ||
                          refreshing
                        }
                      >

                        <span>
                          📍
                        </span>

                        {historyCity}

                      </button>

                    )
                  )}

                </div>

              </div>

            )}


            {error && (

              <div className="error-message">
                {error}
              </div>

            )}

          </section>


          {loading && (

            <section className="loading-section">

              <div className="loading-card">

                <div className="loading-spinner" />

                <div className="loading-content">

                  <strong>
                    Fetching weather intelligence
                  </strong>

                  <span>
                    Getting live conditions, forecast,
                    risk analysis, and weather events...
                  </span>

                </div>

              </div>

            </section>

          )}


          {weather && !loading && (

            <>

              <section className="weather-section">

                <div className="weather-main-card">

                  <span className="weather-location">
                    {weather.city},{" "}
                    {weather.state}
                  </span>


                  <div className="weather-main-content">

                    <div>

                      <p className="temperature">

                        {weather.temperature ??
                          "--"}

                        <span className="temperature-unit">
                          °C
                        </span>

                      </p>


                      <div className="weather-description">
                        {weather.description ||
                          weather.condition ||
                          "Current conditions"}
                      </div>

                    </div>


                    <div className="current-condition">

                      <span className="condition-icon">
                        {weather.condition_icon ||
                          "🌤️"}
                      </span>

                      <span className="condition-label">
                        {weather.condition ||
                          "Unknown conditions"}
                      </span>

                    </div>

                  </div>
                  <div className="ml-prediction-card">

                    <div className="ml-prediction-title">
                      🤖 ML Weather Prediction
                    </div>

                    <div className="ml-prediction-content">

                      <div>
                        <span className="ml-label">
                          Predicted Event
                        </span>

                        <span className="ml-value">
                          {weather.ml_event_type ||
                            "Unavailable"}
                        </span>
                      </div>

                      <div>
                        <span className="ml-label">
                          Confidence
                        </span>

                        <span className="ml-value">
                          {weather.ml_confidence != null
                            ? `${Math.round(
                                weather.ml_confidence * 100
                              )}%`
                            : "Unavailable"}
                        </span>
                      </div>

                    </div>

                  </div>


                  <div className="weather-details">

                    <div className="detail-item">

                      <span className="detail-label">
                        Rain Chance
                      </span>

                      <span className="detail-value">
                        {weather.precipitation_probability ??
                          0}
                        %
                      </span>

                    </div>


                    <div className="detail-item">

                      <span className="detail-label">
                        Latitude
                      </span>

                      <span className="detail-value">
                        {weather.latitude ??
                          "--"}
                      </span>

                    </div>


                    <div className="detail-item">

                      <span className="detail-label">
                        Longitude
                      </span>

                      <span className="detail-value">
                        {weather.longitude ??
                          "--"}
                      </span>

                    </div>


                    <div className="detail-item">

                      <span className="detail-label">
                        Last Updated
                      </span>

                      <span className="detail-value">
                        {formatLastUpdated()}
                      </span>

                    </div>


                    <div className="detail-item">

                      <span className="detail-label">
                        Event Type
                      </span>

                      <span className="detail-value">
                        {weather.event_type ||
                          "Normal"}
                      </span>

                    </div>


                    <div className="detail-item">

                      <span className="detail-label">
                        Auto Refresh
                      </span>

                      <span className="detail-value">
                        Every 10 min
                      </span>

                    </div>

                  </div>

                </div>


                <div className="risk-card">

                  <div className="risk-header">

                    <div>

                      <h2 className="risk-title">
                        Weather Risk
                      </h2>

                      <span className="risk-subtitle">
                        Current atmospheric risk assessment
                      </span>

                    </div>


                    <span className="risk-level">
                      {weather.risk?.level ||
                        "Unknown"}
                    </span>

                  </div>


                  <div className="risk-score">

                    <span className="risk-score-number">
                      {weather.risk?.score ??
                        0}
                    </span>

                    <span className="risk-score-label">
                      / 100
                    </span>

                  </div>


                  <div className="risk-bar">

                    <div
                      className="risk-bar-fill"
                      style={{
                        width: `${Math.min(
                          weather.risk?.score ??
                            0,
                          100
                        )}%`,
                      }}
                    />

                  </div>


                  <div className="risk-reasons">

                    <div className="risk-reasons-title">
                      Risk factors
                    </div>


                    {(
                      weather.risk?.reasons ||
                      []
                    ).map(
                      (reason, index) => (

                        <div
                          className="risk-reason"
                          key={`${reason}-${index}`}
                        >
                          {reason}
                        </div>

                      )
                    )}

                  </div>

                </div>

              </section>


              <div className="weather-actions">

                <button
                  type="button"
                  className="refresh-button"
                  onClick={
                    handleManualRefresh
                  }
                  disabled={
                    refreshing ||
                    loading
                  }
                >

                  <span
                    className={
                      refreshing
                        ? "refresh-icon spinning"
                        : "refresh-icon"
                    }
                  >
                    ↻
                  </span>

                  {refreshing
                    ? "Refreshing..."
                    : "Refresh Weather"}

                </button>

                <span className="refresh-note">
                  Automatically updates every 10 minutes
                </span>

              </div>


              <ForecastChart
                forecast={
                  weather.forecast || []
                }
              />


              <HourlyWeather
                hourly={
                  weather.hourly || []
                }
              />

            </>

          )}


          {/* Report Submission */}

          <section
            className="reports-section"
            style={{
              marginTop: "32px",
            }}
          >

            <div className="reports-header">

              <h2>
                Submit Weather Report
              </h2>

              <p>
                Share a local weather observation with WeatherNova.
              </p>

            </div>


            <form
              onSubmit={handleReportSubmit}
              style={{
                display: "grid",
                gap: "16px",
                padding: "24px",
                borderRadius: "16px",
                border:
                  "1px solid rgba(148, 163, 184, 0.16)",
                background:
                  "rgba(15, 29, 48, 0.65)",
              }}
            >

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: "16px",
                }}
              >

                <div>
                  <label
                    htmlFor="report-city"
                    style={{
                      display: "block",
                      marginBottom: "7px",
                      fontSize: "13px",
                      color: "#94a3b8",
                    }}
                  >
                    City
                  </label>

                  <input
                    id="report-city"
                    name="city"
                    type="text"
                    value={reportForm.city}
                    onChange={
                      handleReportInputChange
                    }
                    placeholder="Enter city"
                    disabled={
                      reportSubmitting
                    }
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "12px 14px",
                      borderRadius: "10px",
                      border:
                        "1px solid rgba(148, 163, 184, 0.2)",
                      background:
                        "rgba(2, 8, 23, 0.55)",
                      color: "#e2e8f0",
                      outline: "none",
                    }}
                  />

                </div>


                <div>
                  <label
                    htmlFor="report-state"
                    style={{
                      display: "block",
                      marginBottom: "7px",
                      fontSize: "13px",
                      color: "#94a3b8",
                    }}
                  >
                    State / Region
                  </label>

                  <input
                    id="report-state"
                    name="state"
                    type="text"
                    value={reportForm.state}
                    onChange={
                      handleReportInputChange
                    }
                    placeholder="Enter state or region"
                    disabled={
                      reportSubmitting
                    }
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "12px 14px",
                      borderRadius: "10px",
                      border:
                        "1px solid rgba(148, 163, 184, 0.2)",
                      background:
                        "rgba(2, 8, 23, 0.55)",
                      color: "#e2e8f0",
                      outline: "none",
                    }}
                  />

                </div>


                <div>
                  <label
                    htmlFor="report-event-type"
                    style={{
                      display: "block",
                      marginBottom: "7px",
                      fontSize: "13px",
                      color: "#94a3b8",
                    }}
                  >
                    Event Type
                  </label>

                  <select
                    id="report-event-type"
                    name="event_type"
                    value={
                      reportForm.event_type
                    }
                    onChange={
                      handleReportInputChange
                    }
                    disabled={
                      reportSubmitting
                    }
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "12px 14px",
                      borderRadius: "10px",
                      border:
                        "1px solid rgba(148, 163, 184, 0.2)",
                      background:
                        "#0f1d30",
                      color: "#e2e8f0",
                      outline: "none",
                    }}
                  >

                    <option value="Clear/Cloudy">
                      Clear / Cloudy
                    </option>

                    <option value="Rain">
                      Rain
                    </option>

                    <option value="Thunderstorm">
                      Thunderstorm
                    </option>

                    <option value="Snow">
                      Snow
                    </option>

                    <option value="Fog">
                      Fog
                    </option>

                    <option value="Wind">
                      Strong Wind
                    </option>

                    <option value="Extreme Weather">
                      Extreme Weather
                    </option>

                    <option value="Other">
                      Other
                    </option>

                  </select>

                </div>

              </div>


              <div>

                <label
                  htmlFor="report-description"
                  style={{
                    display: "block",
                    marginBottom: "7px",
                    fontSize: "13px",
                    color: "#94a3b8",
                  }}
                >
                  Weather Observation
                </label>

                <textarea
                  id="report-description"
                  name="description"
                  value={
                    reportForm.description
                  }
                  onChange={
                    handleReportInputChange
                  }
                  placeholder="Describe what you are observing..."
                  rows="4"
                  disabled={
                    reportSubmitting
                  }
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    padding: "12px 14px",
                    borderRadius: "10px",
                    border:
                      "1px solid rgba(148, 163, 184, 0.2)",
                    background:
                      "rgba(2, 8, 23, 0.55)",
                    color: "#e2e8f0",
                    outline: "none",
                    resize: "vertical",
                    fontFamily:
                      "inherit",
                  }}
                />

              </div>


              {reportMessage && (

                <div
                  style={{
                    padding: "11px 14px",
                    borderRadius: "10px",
                    background:
                      reportMessage.includes(
                        "successfully"
                      )
                        ? "rgba(34, 197, 94, 0.10)"
                        : "rgba(239, 68, 68, 0.10)",
                    border:
                      reportMessage.includes(
                        "successfully"
                      )
                        ? "1px solid rgba(34, 197, 94, 0.2)"
                        : "1px solid rgba(239, 68, 68, 0.2)",
                    color:
                      reportMessage.includes(
                        "successfully"
                      )
                        ? "#86efac"
                        : "#fca5a5",
                    fontSize: "14px",
                  }}
                >
                  {reportMessage}
                </div>

              )}


              <div>

                <button
                  type="submit"
                  className="search-button"
                  disabled={
                    reportSubmitting
                  }
                >
                  {reportSubmitting
                    ? "Submitting..."
                    : "Submit Weather Report"}
                </button>

              </div>

            </form>

          </section>


          {analytics && (

            <section className="analytics-section">

              <div className="section-heading">

                <span className="section-eyebrow">
                  Intelligence Layer
                </span>

                <h2>
                  Weather Analytics
                </h2>

                <p>
                  Aggregated signals from WeatherNova's
                  collected weather reports and events.
                </p>

              </div>


              <AnalyticsCards
                analytics={analytics}
              />


              <div className="analytics-grid">

                <EventChart
                  data={
                    analytics.reports_by_event ||
                    []
                  }
                />


                <StateChart
                  data={
                    analytics.reports_by_state ||
                    []
                  }
                />


                <SeverityChart
                  data={
                    analytics.events_by_severity ||
                    []
                  }
                />

              </div>

            </section>

          )}


          <EventsList
            events={events}
          />


          <section className="reports-section">

            <div className="reports-header">

              <h2>
                Recent Weather Reports
              </h2>

              <p>
                Latest reports processed by WeatherNova.
              </p>

            </div>


            <div className="table-wrapper">

              <table className="reports-table">

                <thead>

                  <tr>

                    <th>
                      Source
                    </th>

                    <th>
                      Event
                    </th>

                    <th>
                      Location
                    </th>

                    <th>
                      Status
                    </th>

                    <th>
                      Trust
                    </th>

                    <th>
                      Time
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {reports.length === 0 ? (

                    <tr>

                      <td
                        colSpan="6"
                        style={{
                          textAlign:
                            "center",
                        }}
                      >
                        No weather reports yet.
                      </td>

                    </tr>

                  ) : (

                    reports.map(
                      (report) => (

                        <tr
                          key={report.id}
                        >

                          <td className="report-source">
                            {report.source}
                          </td>

                          <td className="report-event">
                            {report.event_type}
                          </td>

                          <td>
                            {report.city},{" "}
                            {report.state}
                          </td>

                          <td>

                            <span className="report-status">
                              {report.verification_status}
                            </span>

                          </td>

                          <td>
                            {report.trust_score}
                          </td>

                          <td>
                            {report.timestamp
                              ? new Date(
                                  report.timestamp
                                ).toLocaleString()
                              : "--"}
                          </td>

                        </tr>

                      )
                    )

                  )}

                </tbody>

              </table>

            </div>

          </section>


        </main>


        <footer className="footer">

          <span>
            <strong>
              WeatherNova
            </strong>{" "}
            Weather Intelligence Platform
          </span>

          <span>
            Open-Meteo · FastAPI · PostgreSQL
          </span>

        </footer>

      </div>

    </div>
  );
}


export default App;