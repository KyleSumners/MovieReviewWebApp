import React from "react";
import ReactDOM from "react-dom/client";
import TopMovies from "./pages/TopMovies.tsx";

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(
  <React.StrictMode>
    <TopMovies />
  </React.StrictMode>
);
