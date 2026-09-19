import {
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";


function EventChart({ data = [] }) {
  const chartData = data.map((item) => ({
    name: item.event_type || "Unknown",
    count: item.count || 0,
  }));


  return (
    <div className="chart-card">

      <div className="chart-card-header">

        <div>
          <span className="chart-eyebrow">
            Event Intelligence
          </span>

          <h3>
            Reports by Event Type
          </h3>

          <p>
            Distribution of detected weather conditions.
          </p>
        </div>

        <div className="chart-icon">
          ⚡
        </div>

      </div>


      {chartData.length === 0 ? (

        <div className="empty-chart-small">
          <span>📊</span>
          <p>No event data available.</p>
        </div>

      ) : (

        <div className="chart-container">

          <ResponsiveContainer
            width="100%"
            height={300}
          >

            <BarChart
              data={chartData}
              margin={{
                top: 10,
                right: 10,
                left: -20,
                bottom: 5,
              }}
            >

              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
              />

              <XAxis
                dataKey="name"
                tick={{
                  fontSize: 11,
                }}
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                allowDecimals={false}
                tick={{
                  fontSize: 11,
                }}
                axisLine={false}
                tickLine={false}
              />

              <Tooltip
                cursor={{
                  fill: "rgba(56, 189, 248, 0.06)",
                }}
                contentStyle={{
                  background:
                    "#0f1d30",
                  border:
                    "1px solid rgba(148, 163, 184, 0.2)",
                  borderRadius: "10px",
                  color: "#e2e8f0",
                }}
                labelStyle={{
                  color: "#94a3b8",
                }}
              />

              <Bar
                dataKey="count"
                name="Reports"
                radius={[6, 6, 0, 0]}
              />

            </BarChart>

          </ResponsiveContainer>

        </div>

      )}

    </div>
  );
}


export default EventChart;