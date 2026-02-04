import React from "react";
import { useNavigate } from "react-router-dom";

import "./styles/app.css";
import "./styles/homepage.css";

const App: React.FC = () => {
  const navigate = useNavigate();
  return (
     <div className="home-container">
      <h2>Welcome 👋</h2>

      <div className="tiles">
       <div
            className="tile"
            // onClick={() => navigate("/videotranscriber")}
             onClick={() => window.open("https://www.google.com", "_blank")}
            >
            <div className="tile-icon">🛡️</div>
            <div className="tile-title">Insurance Underwriting</div>
        </div>


        <div
            className="tile"
            onClick={() => navigate("")}
            >
            <div className="tile-icon">🚀</div>
            <div className="tile-title">Video Transcriber</div>
        </div>
        <div
            className="tile"
            onClick={() => navigate("")}
            >
            <div className="tile-icon">🚀</div>
            <div className="tile-title">Name??</div>
        </div>
        <div
            className="tile"
            onClick={() => navigate("")}
            >
            <div className="tile-icon">🚀</div>
            <div className="tile-title">Name??</div>
        </div>
      </div>
    </div>
  );
};

export default App;