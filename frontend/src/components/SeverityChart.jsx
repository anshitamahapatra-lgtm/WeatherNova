import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from "recharts";


function SeverityChart({ data = [] }) {
  const chartData = data.map((item) => ({
    name: item.severity || "Unknown",
    value: item.count || 0,
  }));


  const severityOrder = [
    "high",
    "moderate",
    "low",
    "normal",
    "unknown",
  ];


  const sortedData = [...chartData].sort(
    (a, b) => {
      return (
        severityOrder.indexOf(
          a.name.toLowerCase()
        ) -
        severityOrder.indexOf(
          b.name.toLowerCase()
        )
      );
    }
  );


  return (
    <div className="chart-card">

      <div className="chart-card-header">

        <div>
          <span className="chart-eyebrow">
            Risk Intelligence
          </span>

          <h3>
            Events by Severity
          </h3>

          <p>
            Distribution of weather event severity.
          </p>
        </div>

        <div className="chart-icon">
          ⚠️
        </div>

      </div>


      {sortedData.length === 0 ? (

        <div className="empty-chart-small">
          <span>⚠️</span>
          <p>No severity data available.</p>
        </div>

      ) : (

        <div className="chart-container">

          <ResponsiveContainer
            width="100%"
            height={300}
          >

            <PieChart>

              <Pie
                data={sortedData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="45%"
                innerRadius={65}
                outerRadius={100}
                paddingAngle={3}
              >

                {sortedData.map(
                  (entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                    />
                  )
                )}

              </Pie>


              <Tooltip
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


              <Legend
                verticalAlign="bottom"
                height={36}
                iconType="circle"
                wrapperStyle={{
                  fontSize: "11px",
                  color: "#94a3b8",
                }}
              />

            </PieChart>

          </ResponsiveContainer>

        </div>

      )}

    </div>
  );
}


export default SeverityChart;