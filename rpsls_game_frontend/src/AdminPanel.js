import React, { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from "recharts";
import "./AdminPanel.css";

function AdminPanel() {
  const [summary, setSummary] = useState(null);
  const [outcomes, setOutcomes] = useState(null);
  const [perDay, setPerDay] = useState([]);
  const [popularMoves, setPopularMoves] = useState([]);
  const API_BASE = process.env.REACT_APP_API_BASE_URL;

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(`${API_BASE}/admin/stats/summary`, { headers: { Authorization: `Bearer ${token}` }, credentials: "include" })
      .then((res) => res.json())
      .then(setSummary);

    fetch(`${API_BASE}/admin/stats/outcomes`,  { headers: { Authorization: `Bearer ${token}` }, credentials: "include" })
      .then((res) => res.json())
      .then(setOutcomes);

    fetch(`${API_BASE}/admin/stats/per-day`,  { headers: { Authorization: `Bearer ${token}` }, credentials: "include" })
      .then((res) => res.json())
      .then(setPerDay);

    fetch(`${API_BASE}/admin/stats/popular-moves`,  { headers: { Authorization: `Bearer ${token}` }, credentials: "include" })
      .then((res) => res.json())
      .then(setPopularMoves);
  }, [API_BASE]);

  const COLORS = ["#00C49F", "#FF8042", "#0088FE"];

  return (
    <div className="admin-container">
      <h1 className="admin-title">Admin Panel</h1>

      {summary && (
        <div className="admin-status">
          <p><strong>Total Users:</strong> {summary.total_users}</p>
          <p><strong>Active Players:</strong> {summary.active_players}</p>
          <p><strong>Total Games:</strong> {summary.total_games}</p>
        </div>
      )}

      {outcomes && (
        <div className="admin-charts">
          <div className="chart-box">
            <h3>Game Outcomes</h3>
            <PieChart width={300} height={250}>
              <Pie
                data={Object.entries(outcomes).map(([k, v]) => ({ name: k, value: v }))}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {Object.entries(outcomes).map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>

          <div className="chart-box">
            <h3>Popular Moves</h3>
            <BarChart width={400} height={250} data={popularMoves}>
              <XAxis dataKey="move" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#4f46e5" radius={[6, 6, 0, 0]} />
            </BarChart>
          </div>
        </div>
      )}

      {perDay.length > 0 && (
        <div className="chart-full">
          <h3>Games per Day</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={perDay}>
              <XAxis dataKey="date" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="games" fill="#764ba2" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default AdminPanel;