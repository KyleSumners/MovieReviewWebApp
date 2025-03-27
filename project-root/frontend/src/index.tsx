import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import TopMovies from "./pages/TopMovies.tsx";
import MovieDetails from "./pages/MovieDetails.tsx";

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<TopMovies />} />
                <Route path="/movie/:movieId" element={<MovieDetails />} />
            </Routes>
        </BrowserRouter>
    </React.StrictMode>
);
