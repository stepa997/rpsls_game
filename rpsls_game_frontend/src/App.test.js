import React from "react";
import { act, render, fireEvent, screen, waitFor } from "@testing-library/react";
import App from "./App";

test("renders choices and top players after fetch", async () => {
  global.fetch = jest.fn((url) => {
    if (url.endsWith("/auth/me")) {
      return Promise.resolve({ ok: true, json: async () => ({ id: 1, name: "user1" }) });
    } else if (url.endsWith("/choices")) {
      return Promise.resolve({ ok: true, json: async () => [{ id: 1, name: "rock" }, { id: 2, name: "paper" }] });
    } else if (url.endsWith("/leaderboard/today")) {
      return Promise.resolve({ ok: true, json: async () => [{ session_id: "session1", wins: 5 }, { session_id: "session2", wins: 3 }] });
    }
    return Promise.resolve({ ok: true, json: async () => ({}) });
  });

  render(<App />);

  await waitFor(() => {
    expect(screen.getByText(/🪨 rock/i)).toBeInTheDocument();
    expect(screen.getByText(/📄 paper/i)).toBeInTheDocument();
    expect(screen.getByText(/Top 10 Players Today/i)).toBeInTheDocument();
  });

  expect(screen.getByText("session1")).toBeInTheDocument();
  expect(screen.getByText("5")).toBeInTheDocument();
});
