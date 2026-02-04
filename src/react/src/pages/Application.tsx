import React from "react";
import { Sidebar } from "../components/Sidebar";
import { FileUpload } from "../components/FileUpload";

export const Application: React.FC = () => {
  return (
    <div className="layout">
      <Sidebar />

      <div className="content">
        <h1>📄 Customer Underwriting Management</h1>
        <p className="subtitle">
          Processes application forms and lab reports for underwriting decisions.
        </p>

        <FileUpload title="1. Application Upload *" />
        <FileUpload
          title="2. Lab Reports Upload *"
          subtitle="Upload one or more medical documents"
        />
        <FileUpload
          title="3. KYC Document Upload (Optional)"
          subtitle="Upload Aadhaar or PAN card"
        />
      </div>
    </div>
  );
};