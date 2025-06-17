// LoginPage.test.jsx
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import LoginPage from "./LoginPage";

describe("LoginPage", () => {
  test("renders login form with email and password", () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // Check is fields exists
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();

    // Check is "Login" show
    expect(screen.getByText("Login")).toBeInTheDocument();
  });

  test("shows username input in signup mode", () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    fireEvent.click(screen.getByText(/Sign Up/i)); // click for sign-up

    // Username how now
    expect(screen.getByPlaceholderText("Username")).toBeInTheDocument();
  });
});
