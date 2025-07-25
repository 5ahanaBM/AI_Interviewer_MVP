import React, { useState } from "react";

export default function ResumeUpload({ onResumeParsed }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleStartClick = () => {
    if (!selectedFile) {
      alert("Please choose a resume file first.");
      return;
    }
    onResumeParsed(selectedFile); // delegate to parent (App.jsx)
  };

  return (
    <div>
      <label>Upload Resume:</label>
      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <br /><br />
      <button onClick={handleStartClick}>Let’s Get Started</button>
    </div>
  );
}
