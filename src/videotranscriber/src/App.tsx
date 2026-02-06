import React, { useState } from "react";
import "./App.css";

const App: React.FC = () => {
  const [rightOpen, setRightOpen] = useState(true);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>("");

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setVideoFile(e.target.files[0]);
    }
  };

  // Handle upload button click
  const handleUpload = async () => {
    if (!videoFile) {
      alert("Please select a video first");
      return;
    }

    const formData = new FormData();
    formData.append("video", videoFile);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        alert("Video uploaded successfully");
        setVideoUrl(`http://localhost:5000/videos/${data.file.filename}`);
      } else {
        alert("Upload failed");
      }
    } catch (error) {
      console.error(error);
      alert("Error uploading video");
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <h2>Menu</h2>
        <ul>
          <li>Video Transcriber</li>
        </ul>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <h1>Video Transcriber</h1>

        <div className="content-wrapper">
          {/* Left Section */}
          <div className={`left-section ${rightOpen ? "" : "full-width"}`}>
            {/* Upload Video */}
            <section className="card">
              <h3>Upload Video</h3>
              <input
                type="file"
                accept="video/*"
                onChange={handleFileChange}
              />
              <div className="video-actions">
                <button onClick={handleUpload}>Upload Video</button>
              </div>
            </section>

            {/* Video & Transcription */}
            <section className="card">
              <div className="video-transcription-wrapper">
                {/* Video Player */}
                <div className="video-player">
                  <video controls width="100%" height="220">
                    {videoUrl && (
                      <source src={videoUrl} type="video/mp4" />
                    )}
                    Your browser does not support the video tag.
                  </video>
                </div>

                {/* Transcription Section */}
                <div className="transcription-box">
                  <textarea
                    placeholder="Transcribed text will appear here..."
                    rows={8}
                  />
                </div>
              </div>

              <div className="video-actions">
                <button>View Uploaded Video</button>
                <button>Save Transcript</button>
              </div>
            </section>

            {/* Doctor Chat */}
            <section className="card">
              <h3>Doctor Advice Chat</h3>
              <div className="chat-box">
                <textarea
                  className="doctor-textarea"
                  placeholder="Doctor type prescription here..."
                  rows={6}
                />
              </div>
            </section>

            {/* Response */}
            <section className="card">
              <h3>Response</h3>
              <button className="voice-btn">🔊 Voice Out</button>
              <textarea placeholder="Write your text here..." rows={3} />
            </section>
          </div>

          {/* Expand Button */}
          {!rightOpen && (
            <button
              className="expand-btn"
              onClick={() => setRightOpen(true)}
              aria-label="Expand right panel"
              title="Expand"
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          )}
        </div>

        <button className="submit-btn">Submit & Generate PDF</button>
      </main>
    </div>
  );
};

export default App;
