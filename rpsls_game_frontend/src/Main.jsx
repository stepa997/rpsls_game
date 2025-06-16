import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./LoginPage";
import App from "./App";

function Main() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/play" element={<App />} />
      </Routes>
    </Router>
  );
}

export default Main;
