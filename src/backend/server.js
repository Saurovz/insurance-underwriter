const express = require("express");
const multer = require("multer");
const cors = require("cors");
const path = require("path");
const fs = require("fs");

const app = express();
app.use(cors());

// Expose videos folder to the browser
app.use("/videos", express.static(path.join(__dirname, "videos")));

// Configure multer storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, "videos"));
  },
  filename: (req, file, cb) => {
    // Prefix file with timestamp for sorting later
    cb(null, Date.now() + "-" + file.originalname);
  },
});

const upload = multer({ storage });

// Upload route
app.post("/upload", upload.single("video"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: "No file uploaded" });
  }
  res.json({ file: req.file });
});

// Get list of uploaded videos (latest first)
app.get("/videos-list", (req, res) => {
  const videosDir = path.join(__dirname, "videos");
  fs.readdir(videosDir, (err, files) => {
    if (err) {
      return res.status(500).json({ message: "Cannot read videos folder" });
    }

    // Sort descending by timestamp in filename (latest first)
    files.sort((a, b) => {
      const timeA = parseInt(a.split("-")[0]);
      const timeB = parseInt(b.split("-")[0]);
      return timeB - timeA;
    });

    res.json(files);
  });
});

// Start server
app.listen(5000, () => {
  console.log("Backend running on http://localhost:5000");
});
