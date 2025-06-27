import React, { useState } from "react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./LoginPage.css";

function LoginPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [mode, setMode] = useState("login"); // or "signup"
  const [isAdmin, setIsAdmin] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const endpoint =
      mode === "login" ? "/auth/login" : "/auth/signup";

    const body =
      mode === "login"
        ? { email: form.email, password: form.password }
        : form;

    const response = await fetch(process.env.REACT_APP_API_BASE_URL + endpoint, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      if (data.is_admin) {
        navigate("/admin");
      } else {
        navigate("/play");
      }
    } else {
      alert("Authentication failed");
    }
  };

  useEffect(() => {
    fetch(process.env.REACT_APP_API_BASE_URL + "/auth/me", {
      method: "GET",
      credentials: "include",
    })
      .then(res => {
        if (!res.ok) throw new Error("Not authenticated");
        return res.json();
      })
      .then(data => {
        if (data.is_admin) {
          setIsAdmin(true);
        }
      })
      .catch(() => {
        setIsAdmin(false);
      });
  }, []);

  const handleGuest = async () => {
    if (isAdmin) {
      alert("Admin users cannot use guest mode.");
      return;
    }

    const res = await fetch(process.env.REACT_APP_API_BASE_URL + "/auth/guest", {
      method: "GET",
      credentials: "include",
    });

    if (res.ok) {
      navigate("/play");
      setTimeout(() => {
        window.location.reload();
      }, 100);
    } else {
      alert("Guest login failed");
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>{mode === "login" ? "Welcome Back" : "Create Account"}</h2>

        {mode === "signup" && (
          <input
            name="name"
            type="text"
            placeholder="Username"
            value={form.name}
            onChange={handleChange}
            required
          />
        )}

        <input
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />

        <input
          name="password"
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />

        <button type="submit" className="login-btn">
          {mode === "login" ? "Login" : "Sign Up"}
        </button>

        <div className="switch-mode" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
          <span className="dark-text">
            {mode === "login"
              ? "Don't have an account? Sign Up"
              : "Already have an account? Login"}
          </span>
        </div>

        <div className="or-separator">OR</div>

        <button type="button" className="guest-btn" onClick={handleGuest}>
          Continue as Guest
        </button>
      </form>
    </div>
  );
}

export default LoginPage;
