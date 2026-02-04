import React from "react";
import { NavLink } from "react-router-dom";

export const Sidebar: React.FC = () => {
  return (
    <div className="sidebar">
      <h3 className="logo">
        <NavLink to="">🏠 Home</NavLink>
      </h3>


      <nav>
        <NavLink to="/application">📄 Application</NavLink>
        <NavLink to="/detail">📊 Detail</NavLink>
        <NavLink to="/configuration">⚙️ Configure</NavLink>
      </nav>
    </div>
  );
};