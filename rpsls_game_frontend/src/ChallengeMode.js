import React, { useEffect, useState } from "react";
import "./App.css";

function ChallengeMode() {
  const [choices, setChoices] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [level, setLevel] = useState(null);
  const [status, setStatus] = useState(null);
  const API_BASE = process.env.REACT_APP_API_BASE_URL;

  const emojis = {
    rock: "🪨",
    paper: "📄",
    scissors: "✂️",
    lizard: "🦎",
    spock: "🖖",
  };

  useEffect(() => {
    // Start session
    fetch(`${API_BASE}/start`, { method: "GET", credentials: "include" });

    // Check user auth
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

    // Load choices
    fetch(`${API_BASE}/choices`)
      .then(res => res.json())
      .then(data => setChoices(data));
    
    // Fetch challenge status
    fetch(`${API_BASE}/challenge/status`, {
        method: "GET",
        credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setStatus(data))
      .catch(() => setStatus(null));

    fetchStatus();

  }, [API_BASE]);

  const fetchStatus = () => {
    fetch(`${API_BASE}/challenge/status`, {
        method: "GET",
        credentials: "include",
    })
        .then((res) => res.json())
        .then((data) => {
          setStatus(data);
          setLevel(data.level);
        })
          .catch(() => {
          setStatus(null);
          setLevel(null);
        });
  };

  const playGame = (id) => {
    setLoading(true);
    fetch(`${API_BASE}/play`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ player: id, level: level, challenge_mode: true }),
    })
      .then(res => res.json())
      .then(data => {
        setResult(data);
        setLoading(false);
        fetchStatus();
      });
  };

  const getMoveDisplay = (idOrName) => {
    if (!choices.length) return idOrName;
    if (typeof idOrName === "number") {
      const move = choices.find((c) => c.id === idOrName);
      return move ? `${emojis[move.name]} ${move.name}` : idOrName;
    }
    return `${emojis[idOrName] || ""} ${idOrName}`;
  };

  if (!user) {
    return <p style={{ textAlign: "center" }}>You must be logged in to play challenge mode.</p>;
  }

  return (
    <div className="challenge-container">
        <h1 style={{ textAlign: "center" }}>Challenge Mode</h1>

        {status && (
            <div className="challenge-status">
                <p><strong>Level:</strong> {status.level}</p>
                <p><strong>Round:</strong> {status.round}</p>
                <p><strong>Wins:</strong> {status.wins}</p>
                <p><strong>Games:</strong> {status.games}</p>
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
          <div className="result-row">
            <div className="result">
              <h3 className="result-message">Result: {result.result}</h3>
              <p>Your move: {getMoveDisplay(result.player)}</p>
              <p>Computer move: {getMoveDisplay(result.computer)}</p>
            </div>

            {result.comment && (
              <div className="ai-comment">
                <h4>🧠 AI Commentator:</h4>
                <p>{result.comment}</p>
              </div>
            )}
          </div>
        )}
    </div>
  );
}

export default ChallengeMode;
