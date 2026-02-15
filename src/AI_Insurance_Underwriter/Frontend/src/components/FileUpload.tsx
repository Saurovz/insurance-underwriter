import React, { useRef } from "react";

interface Props {
  title: string;
  subtitle?: string;
}

export const FileUpload: React.FC<Props> = ({ title, subtitle }) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      console.log("Files selected:", files);
    }
  };

  return (
    <div className="upload-card">
      <label className="upload-title">{title}</label>
      {subtitle && <p className="upload-sub">{subtitle}</p>}

      <div className="upload-box" onClick={handleBrowseClick}>
        <span>☁️ Drag and drop files here</span>

        <button type="button" onClick={handleBrowseClick}>
          Browse files
        </button>

        <input
          ref={fileInputRef}
          type="file"
          style={{ display: "none" }}
          onChange={handleFileChange}
          multiple
          accept=".pdf"
        />
      </div>

      <small>Limit 200MB per file · PDF</small>
    </div>
  );
};
