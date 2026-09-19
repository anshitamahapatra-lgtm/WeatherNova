import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";


function formatDate(dateString) {
  if (!dateString) {
    return "--";
  }

  const date = new Date(
    `${dateString}T00:00:00`
  );

  return date.toLocaleDateString(
    undefined,
    {
      weekday: "short",
      month: "short",
      day: "numeric",
    }
  );
}


function ForecastChart({ forecast = [] }) {
  const chartData = forecast.map((day) => ({
    ...day,

    day: formatDate(day.date),

    maxTemperature:
      day.temperature_max,

    minTemperature:
      day.temperature_min,

    rainChance:
      day.precipitation_probability ?? 0,
  }));


  return (
    <section className="forecast-card">

      <div className="chart-header">

        <div>

          <span className="chart-eyebrow">
            Forecast Intelligence
          </span>

          <h3>
            7-Day Weather Forecast
          </h3>

          <span>
            Temperature and precipitation outlook
          </span>

        </div>

      </div>


      {chartData.length === 0 ? (

        <div className="empty-chart">

          <p>
            No forecast data available.
          </p>

        </div>

      ) : (

        <>

          <div className="forecast-days">

            {chartData.map(
              (day, index) => (

                <div
                  className="forecast-day"
                  key={`${day.date}-${index}`}
                >

                  <span className="forecast-date">
                    {day.day}
                  </span>


                  <span className="forecast-icon">
                    {day.icon || "🌡️"}
                  </span>


                  <strong className="forecast-condition">
                    {day.condition ||
                      "Unknown"}
                  </strong>


                  <div className="forecast-temperatures">

                    <span>
                      {day.maxTemperature ??
                        "--"}°C
                    </span>

                    <span>
                      {day.minTemperature ??
                        "--"}°C
                    </span>

                  </div>


                  <span className="forecast-rain">
                    💧{" "}
                    {day.rainChance}%
                  </span>

                </div>

              )
            )}

          </div>


          <div className="forecast-chart-wrapper">

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <LineChart
                data={chartData}
                margin={{
                  top: 15,
                  right: 15,
                  left: 0,
                  bottom: 15,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />


                <XAxis
                  dataKey="day"
                  tick={{
                    fontSize: 12,
                  }}
                />


                <YAxis
                  yAxisId="temperature"
                  allowDecimals={false}
                  tick={{
                    fontSize: 12,
                  }}
                />


                <Tooltip
                  formatter={(
                    value,
                    name
                  ) => {

                    if (
                      name ===
                      "Max Temperature"
                    ) {
                      return [
                        `${value}°C`,
                        name,
                      ];
                    }

                    if (
                      name ===
                      "Min Temperature"
                    ) {
                      return [
                        `${value}°C`,
                        name,
                      ];
                    }

                    return [
                      `${value}%`,
                      name,
                    ];
                  }}
                />


                <Line
                  yAxisId="temperature"
                  type="monotone"
                  dataKey="maxTemperature"
                  name="Max Temperature"
                  strokeWidth={3}
                  dot={{
                    r: 4,
                  }}
                />


                <Line
                  yAxisId="temperature"
                  type="monotone"
                  dataKey="minTemperature"
                  name="Min Temperature"
                  strokeWidth={3}
                  dot={{
                    r: 4,
                  }}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>

        </>

      )}

    </section>
  );
}


export default ForecastChart;