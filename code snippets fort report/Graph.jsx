<LineChart data={metrics}>
  <XAxis dataKey="timestamp" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="value" stroke="#1976d2" />
</LineChart>