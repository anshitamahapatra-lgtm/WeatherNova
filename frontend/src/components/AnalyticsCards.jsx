function AnalyticsCards({ analytics }) {
  return (
    <section className="analytics-cards">

      <div className="analytics-card">
        <div className="analytics-icon">
          📊
        </div>

        <div>
          <span className="analytics-label">
            Total Reports
          </span>

          <strong>
            {analytics?.total_reports ?? 0}
          </strong>
        </div>
      </div>


      <div className="analytics-card">
        <div className="analytics-icon">
          🌩️
        </div>

        <div>
          <span className="analytics-label">
            Total Events
          </span>

          <strong>
            {analytics?.total_events ?? 0}
          </strong>
        </div>
      </div>


      <div className="analytics-card">
        <div className="analytics-icon">
          ✅
        </div>

        <div>
          <span className="analytics-label">
            Verified Reports
          </span>

          <strong>
            {analytics?.verified_reports ?? 0}
          </strong>
        </div>
      </div>


      <div className="analytics-card">
        <div className="analytics-icon">
          ⚠️
        </div>

        <div>
          <span className="analytics-label">
            Duplicate Reports
          </span>

          <strong>
            {analytics?.duplicate_reports ?? 0}
          </strong>
        </div>
      </div>

    </section>
  );
}


export default AnalyticsCards;