import React from "react";
import { Sidebar } from "../components/Sidebar";

export const Configuration: React.FC = () => {
  return (
    <div className="layout">
      <Sidebar />

      <div className="content config-page">
        <div className="config-header">
          <h1>
            📄 Policy Configuration
          </h1>
          <p>
            Prepares the system for underwriting workflows.
          </p>
        </div>

        <div className="config-option">
          <label className="checkbox-row">
            <input type="checkbox" />
            <span>
              Upload new policy document
              <span className="muted">
                {" "} (will overwrite existing)
              </span>
            </span>
          </label>
        </div>
      </div>
    </div>
  );
};