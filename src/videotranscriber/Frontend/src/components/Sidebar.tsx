import React from "react";

interface SidebarProps {
  temperature: number;
  setTemperature: React.Dispatch<React.SetStateAction<number>>;
  topK: number;
  setTopK: React.Dispatch<React.SetStateAction<number>>;
  topP: number;
  setTopP: React.Dispatch<React.SetStateAction<number>>;
  maxTokens: number;
  setMaxTokens: React.Dispatch<React.SetStateAction<number>>;
  repeatPenalty: number;
  setRepeatPenalty: React.Dispatch<React.SetStateAction<number>>;
  contentWindow: number;
  setContentWindow: React.Dispatch<React.SetStateAction<number>>;
}

const Sidebar: React.FC<SidebarProps> = ({
  temperature,
  setTemperature,
  topK,
  setTopK,
  topP,
  setTopP,
  maxTokens,
  setMaxTokens,
  repeatPenalty,
  setRepeatPenalty,
  contentWindow,
  setContentWindow,
}) => {
  return (
    <aside className="sidebar">
      <ul className="menu-list">
        {/* <li className="menu-item active">
            🏠 <span>Home</span>
        </li> */}
        <li className="menu-item active">
            🎥 <span>Video Transcriber</span>
        </li>
      </ul>

      <div className="divider" />

      <div className="model-settings">
        <h3>AI Settings</h3>
      <div className="section">
        <label className="section-label">Model</label>
        <div className="select-wrapper">
            <select className="dropdown">
            <option>mistral:instruct</option>
            <option>llama3</option>
            </select>
        </div>
        </div>


        <div className="section">
          <label>Model Parameters</label>

          <div className="slider-group">
            <span>Temperature</span>
            <span>{temperature}</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
            />
          </div>

          <div className="slider-group">
            <span>Top K</span>
            <span>{topK}</span>
            <input
              type="range"
              min="1"
              max="100"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
            />
          </div>

          <div className="slider-group">
            <span>Top P</span>
            <span>{topP}</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={topP}
              onChange={(e) => setTopP(parseFloat(e.target.value))}
            />
          </div>

          <div className="slider-group">
            <span>Max Tokens</span>
            <span>{maxTokens}</span>
            <input
              type="range"
              min="100"
              max="4096"
              step="100"
              value={maxTokens}
              onChange={(e) => setMaxTokens(Number(e.target.value))}
            />
          </div>

          <div className="slider-group">
            <span>Repeat Penalty</span>
            <span>{repeatPenalty}</span>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={repeatPenalty}
              onChange={(e) => setRepeatPenalty(parseFloat(e.target.value))}
            />
          </div>

          <div className="slider-group">
            <span>Content Window</span>
            <span>{contentWindow}</span>
            <input
              type="range"
              min="1024"
              max="8192"
              step="512"
              value={contentWindow}
              onChange={(e) => setContentWindow(Number(e.target.value))}
            />
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
