import React, { useEffect, useState } from "react";
import RemoveScoreboardButton from "./RemoveButton";
import { PieChart, Pie, Cell, Legend, Tooltip } from "recharts";
import "./App.css";
import ChallengeMode from "./ChallengeMode";

function App() {
  const [choices, setChoices] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [isChallengeMode, setIsChallengeMode] = useState(false);

  const API_BASE = process.env.REACT_APP_API_BASE_URL;

  const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#8dd1e1"];

  const emojis = {
    rock: "🪨",
    paper: "📄",
    scissors: "✂️",
    lizard: "🦎",
    spock: "🖖",
  };

  const [user, setUser] = useState(null);
  const [level, setLevel] = useState("easy");

  useEffect(() => {
    // 1. Start session
    fetch(`${API_BASE}/start`, {
      method: "GET",
      credentials: "include",  // send cookies
    });

    // 2. Get current user
    fetch(`${API_BASE}/auth/me`, {
      method: "GET",
      credentials: "include",
    })
      .then(res => {
        if (!res.ok) throw new Error("Not authenticated");
        return res.json();
      })
      .then(data => setUser(data))
      .catch(() => setUser(null));
  
    // 3. Fetch choices
    fetch(`${API_BASE}/choices`)
      .then((res) => res.json())
      .then((data) => setChoices(data));

    // 4. Fetch top players
    fetchTopPlayers();
  }, [API_BASE, user]);

  // Get history every 0.5 seconds
  useEffect(() => {
    const fetchHistory = () => {
      fetch(`${API_BASE}/games/history`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ number_of_last: 10 }),
      })
        .then((res) => res.json())
        .then((data) => setHistory(data.data || []))
        .catch(() => setHistory([]));
    };

    fetchHistory(); // fetch history

    const intervalId = setInterval(fetchHistory, 500); // update on 3s

    return () => clearInterval(intervalId);
  }, [API_BASE]);

  const playGame = (id) => {
    setLoading(true);
    fetch(`${API_BASE}/play`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ player: id, level: level, challenge_mode: false }),
    })
      .then((res) => res.json())
      .then((data) => {
        setResult(data);
        fetchTopPlayers();
        setLoading(false);
      });
  };

  const getMoveDisplay = (idOrName) => {
    if (!choices.length) return idOrName;

    if (typeof idOrName === "number") {
      const move = choices.find((c) => c.id === idOrName);
      if (!move) return idOrName;
      return `${emojis[move.name]} ${move.name}`;
    } else if (typeof idOrName === "string") {
      return `${emojis[idOrName] || ""} ${idOrName}`;
    }
    return idOrName;
  };

  const [topPlayers, setTopPlayers] = useState([]);

  const fetchTopPlayers = () => {
    fetch(`${API_BASE}/leaderboard/today`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ last_n_numbers: 10 }),
    })
      .then((res) => res.json())
      .then((data) => setTopPlayers(data || []))
      .catch(() => setTopPlayers([]));
  };

  const handleRemove = () => {
    fetch(`${API_BASE}/results/truncate`, {
      method: "DELETE",
      credentials: "include",
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to delete scoreboard");
        alert("Scoreboard removed!");
        fetchTopPlayers();
      })
      .catch(err => alert(err.message));
  };

  // Move calc
  const getMoveDistribution = (history, key) => {
    const counts = {};
    history.forEach((game) => {
      const move = game[key];
      counts[move] = (counts[move] || 0) + 1;
    });

    const total = history.length;
    const distribution = Object.entries(counts).map(([move, count]) => ({
      name: move,
      value: (count / total) * 100,
    }));

    return distribution;
  };

  useEffect(() => {
    if (isChallengeMode) {
      startChallenge();
    }
  }, [isChallengeMode]);

  const startChallenge = () => {
    fetch(`${API_BASE}/challenge/start`, {
      method: "POST",
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to start challenge");
        return res.json();
      })
  };

  if (isChallengeMode) {
    return (
      <div className="container">
        <div style={{ textAlign: "center", marginTop: "1rem" }}>
          <button
            onClick={() => setIsChallengeMode(false)}
            className="challenge-toggle-button"
          >
            Exit Challenge Mode
          </button>
        </div>
        <ChallengeMode />
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ textAlign: "center", marginTop: "1rem" }}>
        <button
          onClick={() => setIsChallengeMode(true)}
          className="challenge-toggle-button"
        >
          Enter Challenge Mode
        </button>
      </div>
      {user && (
        <p className="user-info">
          Logged in as <strong>{user.name}</strong>
        </p>
      )}

      <div className="difficulty-selector">
        <label htmlFor="difficulty">Computer level:</label>
        <select
          id="difficulty"
          value={level}
          onChange={(e) => setLevel(e.target.value)}
        >
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>

      <div>
        <RemoveScoreboardButton onRemove={handleRemove} />
      </div>

      {topPlayers.length > 0 && (
        <div className="top-players-table-container">
          <h2 style={{ textAlign: "right", marginRight: "2rem" }}>Top 10 Players Today</h2>
          <table className="top-players-table">
            <thead>
              <tr>
                <th>Player</th>
                <th>Wins</th>
              </tr>
            </thead>
            <tbody>
              {topPlayers.map((player, idx) => (
                <tr key={idx}>
                  <td>{player.session_id}</td>
                  <td>{player.wins}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="choices">
        {choices.map((choice) => (
          <button key={choice.id} onClick={() => playGame(choice.id)}>
            {getMoveDisplay(choice.id)}
          </button>
        ))}
      </div>

      {loading && <p className="loading">Thinking...</p>}

      {result && (
        <div className="result">
          <h3 key={Date.now()} className="result-message">
            Result: {result.result}
          </h3>
          <p>Your move: {getMoveDisplay(result.player)}</p>
          <p>Computer move: {getMoveDisplay(result.computer)}</p>
        </div>
      )}

      {/* History */}
      <h2 style={{ marginTop: "3rem", textAlign: "center" }}>Game History</h2>
      <div className="charts-container">
        {/* Player chart */}
        <div>
          <h3 style={{ textAlign: "center" }}>Player Moves</h3>
          <PieChart width={420} height={350}>
            <Pie
              data={getMoveDistribution(history, "player_move")}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={120}
              label={({ name }) => `${emojis[name]} ${name}`}
            >
              {getMoveDistribution(history, "player_move").map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => value.toFixed(2) + "%"} />
            <Legend />
          </PieChart>
        </div>

        {/* Scoreboard table */}
        <div className="history-table-container">
          <table className="history-table">
            <thead>
              <tr>
                <th>When</th>
                <th>Your Move</th>
                <th>Computer Move</th>
                <th>Winner</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan="4" style={{ textAlign: "center" }}>
                    No games played yet
                  </td>
                </tr>
              ) : (
                history.map((h) => (
                  <tr key={h.id}>
                    <td>{new Date(h.played_at).toLocaleString()}</td>
                    <td>{getMoveDisplay(h.player_move)}</td>
                    <td>{getMoveDisplay(h.computer_move)}</td>
                    <td
                      className={`winner ${
                        h.winner === "win"
                          ? "win"
                          : h.winner === "lose"
                          ? "lose"
                          : "draw"
                      }`}
                    >
                      {h.winner.toUpperCase()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Computer chart */}
        <div>
          <h3 style={{ textAlign: "center" }}>Computer Moves</h3>
          <PieChart width={420} height={350}>
            <Pie
              data={getMoveDistribution(history, "computer_move")}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={120}
              label={({ name }) => `${emojis[name]} ${name}`}
            >
              {getMoveDistribution(history, "computer_move").map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => value.toFixed(2) + "%"} />
            <Legend />
          </PieChart>
        </div>
      </div>
    </div>
  );
}

export default App;
