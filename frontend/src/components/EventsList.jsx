function EventsList({ events, loading }) {
  return (
    <section className="events-section">

      <div className="section-heading">

        <div>

          <h2>
            Active Weather Events
          </h2>

          <p>
            Weather events detected by WeatherNova.
          </p>

        </div>


        {loading && (
          <span>
            Loading...
          </span>
        )}

      </div>


      <div className="events-grid">

        {events.length === 0 ? (

          <div className="empty-events">

            <p>
              No weather events available yet.
            </p>

          </div>

        ) : (

          events.map((event) => (

            <div
              className="event-card"
              key={event.id}
            >

              <div className="event-card-top">

                <span className="event-type">
                  {event.event_type}
                </span>

                <span
                  className={
                    `severity-badge severity-${event.severity}`
                  }
                >
                  {event.severity}
                </span>

              </div>


              <h3>
                {event.title}
              </h3>


              <p className="event-location">
                📍 {event.city}
                {event.state
                  ? `, ${event.state}`
                  : ""}
              </p>


              <div className="event-details">

                <span>
                  Status:{" "}
                  <strong>
                    {event.status}
                  </strong>
                </span>

                <span>
                  Started:{" "}
                  <strong>
                    {event.start_time
                      ? new Date(
                          event.start_time
                        ).toLocaleString()
                      : "--"}
                  </strong>
                </span>

              </div>

            </div>

          ))

        )}

      </div>

    </section>
  );
}


export default EventsList;