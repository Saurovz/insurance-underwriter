import React, { useEffect, useRef, useState } from "react";
import "./App.css";

const App: React.FC = () => {
  const [rightOpen] = useState(true);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [uploadedVideos, setUploadedVideos] = useState<string[]>([]);
  const [showVideoList, setShowVideoList] = useState(false);
  const [uploadedListOpen, setUploadedListOpen] = useState(false);

  /* Doctor states */
  const [doctorOpen, setDoctorOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [aiText, setAiText] = useState("");

  const editorRef = useRef<HTMLDivElement>(null);

  /* Modal for Video/PDF */
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState<"video" | "pdf" | null>(null);

  const videoLink = "http://localhost:5000/videos/sample.mp4"; // example video
  const linkPDFPresc = "http://localhost:5000/prescription/sample.pdf"; // example PDF

  const openModal = (type: "video" | "pdf") => {
    setModalType(type);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalType(null);
  };

  /* ---------------- Video logic ---------------- */
  const handleViewUploaded = async () => {
    try {
      const res = await fetch("http://localhost:5000/videos-list");
      const files = await res.json();
      setUploadedVideos(files);
      setShowVideoList(true);
    } catch (error) {
      console.error(error);
    }
  };

  const handlePlayVideo = (fileName: string) => {
    setVideoUrl(`http://localhost:5000/videos/${fileName}`);
    setShowVideoList(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setVideoFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!videoFile) return alert("Select a video");

    const formData = new FormData();
    formData.append("video", videoFile);

    const res = await fetch("http://localhost:5000/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (res.ok) {
      setVideoUrl(`http://localhost:5000/videos/${data.file.filename}`);
    }
  };

  /* ---------------- Doctor features ---------------- */

  // mic + wave
  const startListening = () => {
    setIsListening(true);
    setTimeout(() => setIsListening(false), 30000);
  };

  // text-to-speech
  const speakText = () => {
    const text =
      editorRef.current?.innerText || aiText || "No text to speak";
    const utter = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(utter);
  };

  // AI streaming (mock)
  const generatePrescription = () => {
    const response =
      "Take this medicine twice daily after food. Stay hydrated and rest well.";
    setAiText("");

    let i = 0;
    const interval = setInterval(() => {
      setAiText((prev) => prev + response[i]);
      i++;
      if (i >= response.length) clearInterval(interval);
    }, 40);
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

      {/* Main */}
      <main className="main-content">
        <h1>Video Transcriber</h1>

        <div className="content-wrapper">
          <div className={`left-section ${rightOpen ? "" : "full-width"}`}>

            {/* Upload Video */}
            <section className="card">
              <h3>Upload Video</h3>
              <input type="file" accept="video/*" onChange={handleFileChange} />

              <div className="video-actions">
                <button onClick={handleUpload}>Upload Video</button>
                <button
                  onClick={() => {
                    handleViewUploaded();
                    setUploadedListOpen((prev) => !prev);
                  }}
                >
                  {uploadedListOpen ? "▼ Hide Uploaded Videos" : "▶ Show Uploaded Videos"}
                </button>
              </div>

              {uploadedListOpen && uploadedVideos.length > 0 && (
                <div className="uploaded-videos-list" style={{ marginTop: "10px" }}>
                  {uploadedVideos.map((file) => (
                    <button
                      key={file}
                      style={{ display: "block", marginBottom: "6px" }}
                      onClick={() => handlePlayVideo(file)}
                    >
                      ▶ {file}
                    </button>
                  ))}
                </div>
              )}
            </section>

            {/* Video + Transcription */}
            <section className="card">
              <div className="video-transcription-wrapper">
                <div className="video-player">
                  <video controls width="100%" height="220">
                    {videoUrl && <source src={videoUrl} />}
                  </video>
                </div>

                <div className="transcription-box">
                  <textarea
                    placeholder="Transcribed text will appear here..."
                    rows={8}
                  />
                </div>
              </div>
            </section>

            {/* ================= Doctor Advice ================= */}
            <section className="card doctor-card">
              {/* Header */}
              <div className="doctor-header">
                <h3>Doctor’s Advice</h3>
                <span
                  className="chatbot-icon"
                  onClick={() => setDoctorOpen((p) => !p)}
                >
                  🤖
                </span>
              </div>

              {/* Expanded */}
              {doctorOpen && (
                <div className="doctor-body">
                  {/* Mic */}
                  <div className="mic-row">
                    <button onClick={startListening}>🎤 Start Mic</button>
                    {isListening && <div className="wave" />}
                  </div>

                  {/* Speak */}
                  <button className="speak-btn" onClick={speakText}>
                    🔊 Voice Out
                  </button>

                  {/* Rich Text Editor */}
                  <div
                    ref={editorRef}
                    className="rich-editor"
                    contentEditable
                  />

                  {/* AI Output */}
                  <div className="ai-output">{aiText}</div>

                  {/* Prescription */}
                  <button
                    className="prescription-btn"
                    onClick={generatePrescription}
                  >
                    Prescription
                  </button>

                  {/* Links */}
                  <div className="doctor-links">
                    <button
                      className="link-btn"
                      onClick={() => openModal("video")}
                    >
                      Video Link
                    </button>
                    <button
                      className="link-btn"
                      onClick={() => openModal("pdf")}
                    >
                      PDF Prescription
                    </button>
                  </div>
                </div>
              )}
            </section>
          </div>
        </div>
      </main>

      {/* ---------------- Modal for Video/PDF ---------------- */}
      {modalOpen && modalType && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={closeModal}>✖</button>
            {modalType === "video" ? (
              <video controls width="100%" height="300">
                <source src={videoLink} type="video/mp4" />
              </video>
            ) : (
              <iframe src={linkPDFPresc} width="100%" height="400"></iframe>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
