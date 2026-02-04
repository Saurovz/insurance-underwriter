import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { Application } from "./pages/Application";
import { Detail } from "./pages/Detail";
import { Configuration } from "./pages/Configuration";
// import { HomePage } from "./pages/HomePage";


import "./styles/app.css";
import "./styles/detail.css";
import "./styles/configure.css";
import "./styles/homepage.css";

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Default route */}
        <Route path="/" element={<Navigate to="/application" replace />} />

        {/* Pages */}
        {/* <Route path="/homepage" element={<HomePage />} /> */}
        <Route path="/application" element={<Application />} />
        <Route path="/detail" element={<Detail />} />
        <Route path="/configuration" element={<Configuration />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/application" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;