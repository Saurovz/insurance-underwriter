import React, { useEffect, useRef, useState } from "react";
import "./App.css";
import Sidebar from "./components/Sidebar";

const API_BASE = "http://127.0.0.1:8001";

const App: React.FC = () => {
  // state
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [uploadedVideos, setUploadedVideos] = useState<string[]>([]);
  const [uploadedListOpen, setUploadedListOpen] = useState(true);

  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcriptionText, setTranscriptionText] = useState("");
  const [currentPatientId, setCurrentPatientId] = useState<string>("");

  const [doctorOpen, setDoctorOpen] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [doctorAdvice, setDoctorAdvice] = useState("");
  const editorRef = useRef<HTMLDivElement>(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const [isSavingAdvice, setIsSavingAdvice] = useState(false);
  const [pdfUrl, setPdfUrl] = useState("");
  const [htmlUrl, setHtmlUrl] = useState("");
  const [prescriptionOpen, setPrescriptionOpen] = useState(false);

  const recognitionRef = useRef<any>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // AI Model Parameters State
  const [temperature, setTemperature] = useState(0.7);
  const [topK, setTopK] = useState(40);
  const [topP, setTopP] = useState(0.9);
  const [maxTokens, setMaxTokens] = useState(1024);
  const [repeatPenalty, setRepeatPenalty] = useState(1.1);
  const [contentWindow, setContentWindow] = useState(4096);

  // Chatbot state
  const [chatbotOpen, setChatbotOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<
    Array<{ role: string; content: string }>
  >([]);
  const [chatInput, setChatInput] = useState("");
  const [isChatbotReady, setIsChatbotReady] = useState(false);
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const chatBodyRef = useRef<HTMLDivElement>(null);

  // --- speech recognition setup ---
  useEffect(() => {
    if ("webkitSpeechRecognition" in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = "en-US";

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + " ";
          }
        }
        if (finalTranscript && editorRef.current) {
          const curr = editorRef.current.innerText || "";
          editorRef.current.innerText = curr + finalTranscript;
          setDoctorAdvice(curr + finalTranscript);
        }
      };

      recognitionRef.current.onerror = (err: any) => {
        console.warn("SpeechRecognition error:", err);
        if (err.error === "no-speech") {
          console.log("No speech detected, continuing...");
        } else {
          setIsListening(false);
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [chatMessages]);

  // Initialize chatbot when transcription is complete
  useEffect(() => {
    if (
      currentPatientId &&
      transcriptionText &&
      !transcriptionText.includes("⏳") &&
      !transcriptionText.includes("❌")
    ) {
      initializeChatbot();
    }
  }, [currentPatientId, transcriptionText]);

  // ---------- Handlers ----------

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;

    if (videoUrl) {
      try {
        URL.revokeObjectURL(videoUrl);
      } catch {}
    }

    const url = URL.createObjectURL(f);
    setVideoFile(f);
    setVideoUrl(url);

    setUploadedVideos((p) => [f.name, ...p]);
    setTranscriptionText("");
    setCurrentPatientId("");
    setDoctorAdvice("");
    if (editorRef.current) editorRef.current.innerText = "";
    setPdfUrl("");
    setHtmlUrl("");
    setPrescriptionOpen(false);
    
    // Reset chatbot
    setIsChatbotReady(false);
    setChatMessages([]);
    setChatbotOpen(false);
  };

  const handleTranscribeClick = async () => {
    if (!videoFile) return alert("Please choose a video file first.");

    // Auto-play video when transcription starts
    if (videoRef.current) {
      try {
        await videoRef.current.play();
        console.log("🎬 Video playback started");
      } catch (error) {
        console.warn("⚠️ Auto-play blocked by browser:", error);
      }
    }

    setIsTranscribing(true);
    setTranscriptionText("⏳ Uploading video and extracting audio...");

    const form = new FormData();
    form.append("video", videoFile);

    try {
      console.log("🚀 Sending request to:", `${API_BASE}/upload-video`);

      const res = await fetch(`${API_BASE}/upload-video`, {
        method: "POST",
        body: form,
      });

      console.log("✅ Response status:", res.status, res.statusText);

      if (!res.ok) {
        const errorText = await res.text();
        console.error("❌ Response not OK:", errorText);
        throw new Error(`Server error: ${res.status} - ${errorText}`);
      }

      const body = await res.json();
      console.log("📦 Response body:", body);

      const transcription =
        body?.english_transcription || body?.transcription || body?.text || "";

      const patientId = body?.patient_id || "";

      if (!transcription) {
        console.warn("⚠️ No transcription in response");
      }

      setCurrentPatientId(patientId);
      setTranscriptionText(
        transcription || "✅ Upload complete — no transcription returned."
      );

      // Auto-open doctor's advice section
      setDoctorOpen(true);
    } catch (err: any) {
      console.error("❌ Fetch error details:", err);

      let errorMessage = "❌ Error processing file. ";

      if (err.message.includes("Failed to fetch")) {
        errorMessage +=
          "Cannot connect to backend. Check:\n" +
          "1. Backend is running on http://127.0.0.1:8001\n" +
          "2. CORS is configured correctly\n" +
          "3. No firewall blocking the connection";
      } else if (err.message.includes("NetworkError")) {
        errorMessage += "Network error - check your internet connection";
      } else {
        errorMessage += err.message;
      }

      setTranscriptionText(errorMessage);
    } finally {
      setIsTranscribing(false);
    }
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition not supported in this browser.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const saveDoctorAdvice = async (silent = false) => {
    if (!currentPatientId) {
      if (!silent) alert("Please transcribe patient video first.");
      return false;
    }

    const advice = editorRef.current?.innerText?.trim() || doctorAdvice.trim();

    if (!advice) {
      if (!silent) alert("Please provide doctor's advice before saving.");
      return false;
    }

    setIsSavingAdvice(true);

    try {
      console.log("💾 Saving doctor advice...");
      const res = await fetch(`${API_BASE}/doctor-advice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: currentPatientId,
          doctor_advice: advice,
          input_type: isListening ? "voice" : "text",
        }),
      });

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();
      console.log("✅ Advice saved:", data);

      if (!silent) alert("✓ Doctor's advice saved successfully!");
      return true;
    } catch (e) {
      console.error("❌ Save advice error:", e);
      if (!silent) alert("Could not save advice. See console.");
      return false;
    } finally {
      setIsSavingAdvice(false);
    }
  };

  const generatePrescription = async () => {
    if (!currentPatientId) {
      alert("Please transcribe patient video first.");
      return;
    }

    const advice = editorRef.current?.innerText?.trim() || doctorAdvice.trim();

    if (!advice) {
      alert("Please provide doctor's advice before generating prescription.");
      return;
    }

    // Save advice first (silently)
    setIsGenerating(true);
    const saved = await saveDoctorAdvice(true);

    if (!saved) {
      setIsGenerating(false);
      alert("Failed to save doctor's advice. Cannot generate prescription.");
      return;
    }

    try {
      console.log("📋 Generating prescription...");
      const res = await fetch(`${API_BASE}/generate-prescription`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ patient_id: currentPatientId }),
      });

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();
      console.log("✅ Prescription generated:", data);

      if (data.pdf_url) setPdfUrl(`${API_BASE}${data.pdf_url}`);
      if (data.video_url) setHtmlUrl(`${API_BASE}${data.video_url}`);

      // Auto-open prescription section
      setPrescriptionOpen(true);

      alert("✓ Prescription generated successfully!");
    } catch (e: any) {
      console.error("❌ Generate prescription error:", e);
      alert(
        "Generation failed: " + (e.message || "Unknown error. See console.")
      );
    } finally {
      setIsGenerating(false);
    }
  };

  // ---------- Chatbot Functions ----------

  const initializeChatbot = async () => {
    if (!currentPatientId) {
      console.log("⚠️ No patient ID for chatbot");
      return;
    }

    try {
      console.log("🤖 Initializing chatbot...");
      const res = await fetch(`${API_BASE}/chatbot/init`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ patient_id: currentPatientId }),
      });

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();
      console.log("✓ Chatbot initialized:", data);
      setIsChatbotReady(true);

      // Add welcome message
      setChatMessages([
        {
          role: "assistant",
          content:
            "Hello! I'm your medical assistant. I can answer questions about the patient's symptoms and condition. What would you like to know?",
        },
      ]);
    } catch (e) {
      console.error("❌ Chatbot init error:", e);
      setIsChatbotReady(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !currentPatientId || isSendingMessage) return;

    const userMessage = chatInput.trim();
    setChatInput("");

    // Add user message to chat
    setChatMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsSendingMessage(true);

    try {
      const res = await fetch(`${API_BASE}/chatbot/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: currentPatientId,
          question: userMessage,
        }),
      });

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();

      // Add assistant response
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer },
      ]);
    } catch (e: any) {
      console.error("❌ Chat error:", e);
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsSendingMessage(false);
    }
  };

  // ---------- render ----------
  return (
    <div className="app-container">
      {/* Sidebar Component */}
      <Sidebar
        temperature={temperature}
        setTemperature={setTemperature}
        topK={topK}
        setTopK={setTopK}
        topP={topP}
        setTopP={setTopP}
        maxTokens={maxTokens}
        setMaxTokens={setMaxTokens}
        repeatPenalty={repeatPenalty}
        setRepeatPenalty={setRepeatPenalty}
        contentWindow={contentWindow}
        setContentWindow={setContentWindow}
      />

      <main className="main-content">
        {/* NEW CLEAN HERO SECTION */}
        <div className="hero-section-clean">
          <div className="hero-left">
            <div className="hero-badge">
              <span className="badge-icon">⚡</span>
              <span>AI-Powered Medical Assistant</span>
            </div>
            <h1 className="hero-title">
              Video Transcriber
            </h1>
            <p className="hero-description">
              Transform patient consultations into intelligent medical records with AI-powered transcription
            </p>
          </div>
          <div className="hero-right">
            <div className="feature-pill">
              <span className="pill-icon">🚀</span>
              <span>Fast Processing</span>
            </div>
            <div className="feature-pill">
              <span className="pill-icon">🔒</span>
              <span>Secure & Private</span>
            </div>
            <div className="feature-pill">
              <span className="pill-icon">🤖</span>
              <span>AI Technology</span>
            </div>
          </div>
        </div>

        {/* Upload Section */}
        <div className="card upload-section enhanced-card">
          <div className="card-header">
            <div className="header-icon">📤</div>
            <h2 className="card-title">Upload Patient Video</h2>
          </div>
          
          <div className="upload-area">
            <label className="upload-btn-modern">
              <input type="file" accept="video/*" onChange={handleFileSelect} />
              <span className="btn-icon">🎥</span>
              <span className="btn-text">Choose Video File</span>
            </label>
          </div>

          <div
            className="uploaded-header blue-accordion"
            onClick={() => setUploadedListOpen(!uploadedListOpen)}
          >
            <div className="folder-label">
              <span className="folder-icon">📂</span>
              <span>Uploaded Videos</span>
            </div>
            <span className="arrow">{uploadedListOpen ? "▾" : "▸"}</span>
          </div>

          {uploadedListOpen && (
            <div className="uploaded-panel">
              {uploadedVideos.length > 0 ? (
                uploadedVideos.map((v, i) => (
                  <div key={i} className="uploaded-video-item">
                    <span className="video-icon">🎬</span>
                    <span className="video-name">{v}</span>
                  </div>
                ))
              ) : (
                <div className="empty-msg">
                  <div className="empty-icon">📹</div>
                  <p>No videos uploaded yet</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Workspace Section */}
        <div className="card workspace-section enhanced-card">
          <div className="workspace-row">
            {/* Video player */}
            <div className="video-player-container">
              <div className="player-header">
                <span className="player-badge">Patient Video</span>
              </div>
              <div className="video-player">
                {videoUrl ? (
                  <video ref={videoRef} src={videoUrl} controls loop />
                ) : (
                  <div className="video-placeholder">
                    <div className="placeholder-content">
                      <div className="placeholder-icon">🎬</div>
                      <p className="placeholder-text">No Video Selected</p>
                      <p className="placeholder-hint">Upload a video to begin</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Transcription panel */}
            <div className="transcription-container">
              <div className="transcription-header">
                <span className="transcription-badge">AI Transcription</span>
              </div>
              <div className="transcription-box">
                <textarea
                  placeholder="AI-generated transcription will appear here..."
                  value={transcriptionText}
                  readOnly
                />
              </div>
            </div>
          </div>

          {/* Transcribe button */}
          <div className="transcribe-actions">
            <button
              className="transcribe-btn-modern"
              onClick={handleTranscribeClick}
              disabled={!videoFile || isTranscribing}
            >
              {isTranscribing ? (
                <>
                  <span className="spinner"></span>
                  <span>Processing Video...</span>
                </>
              ) : (
                <>
                  <span className="btn-icon-large">🎬</span>
                  <span>Start Transcription</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Doctor's Advice Section */}
        <div className="card doctor-card enhanced-card">
          <div
            className="uploaded-header"
            onClick={() => setDoctorOpen(!doctorOpen)}
          >
            <div className="folder-label">
              <span className="folder-icon">🩺</span>
              <span>Doctor's Advice</span>
            </div>
            <div className="arrow">{doctorOpen ? "▾" : "▸"}</div>
          </div>

          {doctorOpen && (
            <div className="doctor-body">
              {/* Mic controls */}
              <div className="mic-row">
                <button
                  className={`speak-btn ${isListening ? "listening" : ""}`}
                  onClick={toggleListening}
                  disabled={!currentPatientId}
                  title={
                    !currentPatientId
                      ? "Please transcribe patient video first"
                      : ""
                  }
                >
                  {isListening ? "⏹ Stop Mic" : "🎤 Start Mic"}
                </button>
                {isListening && (
                  <div className="mic-status">
                    <div className="wave" />
                    <span style={{ fontSize: 12, color: "#ef4444" }}>
                      Listening...
                    </span>
                  </div>
                )}
              </div>

              {/* Editable text area */}
              <div
                ref={editorRef}
                className="rich-editor"
                contentEditable={!!currentPatientId}
                onInput={() =>
                  setDoctorAdvice(editorRef.current?.innerText || "")
                }
                suppressContentEditableWarning
              />

              {/* Action buttons */}
              <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
                <button
                  className="prescription-btn"
                  onClick={generatePrescription}
                  disabled={isGenerating || !currentPatientId}
                >
                  {isGenerating
                    ? "⏳ Generating..."
                    : "📄 Generate Prescription"}
                </button>
                <button
                  className="save-advice-btn"
                  onClick={() => saveDoctorAdvice(false)}
                  disabled={isSavingAdvice || !currentPatientId}
                >
                  {isSavingAdvice ? "💾 Saving..." : "💾 Save Advice"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Prescription Display Section */}
        {(pdfUrl || htmlUrl) && (
          <div className="card prescription-card enhanced-card">
            <div
              className="uploaded-header"
              onClick={() => setPrescriptionOpen(!prescriptionOpen)}
            >
              <div className="folder-label">
                <span className="folder-icon">📋</span>
                <span>Generated Prescription</span>
              </div>
              <div className="arrow">{prescriptionOpen ? "▾" : "▸"}</div>
            </div>

            {prescriptionOpen && (
              <div className="prescription-body">
                <div className="prescription-tabs">
                  <button
                    className="tab-btn active"
                    onClick={() => window.open(htmlUrl, "_blank")}
                  >
                    🌐 Open HTML
                  </button>
                  <button
                    className="tab-btn"
                    onClick={() => window.open(pdfUrl, "_blank")}
                  >
                    📄 Open PDF
                  </button>
                  <a
                    href={pdfUrl}
                    download="prescription.pdf"
                    className="tab-btn"
                  >
                    ⬇️ Download PDF
                  </a>
                </div>

                {/* Preview iframe */}
                <div className="prescription-preview">
                  <iframe
                    src={htmlUrl}
                    className="prescription-iframe"
                    title="Prescription Preview"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Floating Chatbot */}
      {isChatbotReady && (
        <>
          {/* Floating Chat Button */}
          {!chatbotOpen && (
            <button
              className="chatbot-float-btn"
              onClick={() => setChatbotOpen(true)}
              title="Ask about patient"
            >
              💬
            </button>
          )}

          {/* Chat Window */}
          {chatbotOpen && (
            <div className="chatbot-window">
              <div className="chatbot-header">
                <span>🤖 Medical Assistant</span>
                <button
                  onClick={() => setChatbotOpen(false)}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "white",
                    cursor: "pointer",
                    fontSize: "18px",
                  }}
                >
                  ✖
                </button>
              </div>

              <div className="chatbot-body" ref={chatBodyRef}>
                {chatMessages.map((msg, idx) => (
                  <div key={idx} className={`chat-message ${msg.role}`}>
                    {msg.content}
                  </div>
                ))}
                {isSendingMessage && (
                  <div className="chat-message assistant">
                    <em>Thinking...</em>
                  </div>
                )}
              </div>

              <div className="chatbot-footer">
                <input
                  type="text"
                  placeholder="Ask about patient symptoms..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && sendChatMessage()}
                  disabled={isSendingMessage}
                />
                <button
                  onClick={sendChatMessage}
                  disabled={!chatInput.trim() || isSendingMessage}
                  style={{
                    background: "#2563eb",
                    color: "white",
                    border: "none",
                    padding: "8px 16px",
                    borderRadius: "6px",
                    cursor: "pointer",
                  }}
                >
                  Send
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default App;
