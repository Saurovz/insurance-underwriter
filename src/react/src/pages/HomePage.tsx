import React from "react";
import { useNavigate } from "react-router-dom";

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <h2>Welcome 👋</h2>

      <div className="tiles">
       <div
            className="tile"
            onClick={() => navigate("/application")}
            >
            <div className="tile-icon">🛡️</div>
            <div className="tile-title">Insurance Underwriting</div>
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

export default HomePage;
