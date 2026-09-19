import "./HourlyWeather.css";

function HourlyWeather({ hourly }) {
  if (!hourly || hourly.length === 0) {
    return null;
  }

  function formatHour(value, index) {
    if (!value) {
      return "--";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    if (index === 0) {
      return "Now";
    }

    return date.toLocaleTimeString(undefined, {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  return (
    <section className="hourly-section">
      <div className="hourly-header">
        <div>
          <span className="hourly-eyebrow">
            Short-Term Outlook
          </span>

          <h2 className="hourly-title">
            Hourly Weather
          </h2>

          <p className="hourly-subtitle">
            Next 24 hours at a glance
          </p>
        </div>

        <span className="hourly-count">
          {hourly.length} hours
        </span>
      </div>

      <div className="hourly-scroll">
        <div className="hourly-list">
          {hourly.map((hour, index) => (
            <article
              className={`hourly-card ${
                index === 0 ? "hourly-card-current" : ""
              }`}
              key={hour.time || index}
            >
              <div className="hourly-time">
                {formatHour(hour.time, index)}
              </div>

              <div className="hourly-icon">
                {hour.icon || "🌡️"}
              </div>

              <div className="hourly-temperature">
                {hour.temperature ?? "--"}
                <span>°C</span>
              </div>

              <div className="hourly-condition">
                {hour.condition || "Unknown"}
              </div>

              <div className="hourly-divider" />

              <div className="hourly-metric">
                <span className="hourly-metric-label">
                  Rain
                </span>
                <span className="hourly-metric-value">
                  {hour.precipitation_probability ?? 0}%
                </span>
              </div>

              <div className="hourly-metric">
                <span className="hourly-metric-label">
                  Wind
                </span>
                <span className="hourly-metric-value">
                  {hour.wind_speed ?? "--"} km/h
                </span>
              </div>
            </article>
          ))}
        </div>
      </div>

      <div className="hourly-scroll-hint">
        <span>←</span>
        Scroll to explore the next 24 hours
        <span>→</span>
      </div>
    </section>
  );
}

export default HourlyWeather;
