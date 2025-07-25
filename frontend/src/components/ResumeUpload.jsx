import { useState } from "react";

export default function ResumeUpload({ onResumeParsed }) {
  const [file, setFile] = useState(null);
  const [jobTitle, setJobTitle] = useState("");

  const handleChange = (e) => setFile(e.target.files[0]);

  const handleUpload = () => {
    if (!file) {
      alert("Please select a resume file.");
      return;
    }
    onResumeParsed(file, jobTitle);
  };

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto", textAlign: "center" }}>
      <h3>Upload Your Resume</h3>
      <p>PDF and doc formats are supported.</p>

      <input type="file" accept=".pdf,.txt" onChange={handleChange} />
      <br /><br />

      <label htmlFor="jobTitle"><strong>Target Job Title / Description (optional)</strong></label>
      <br />
      <input
        type="text"
        id="jobTitle"
        placeholder="e.g. ML Engineer, Frontend Developer"
        value={jobTitle}
        onChange={(e) => setJobTitle(e.target.value)}
        style={{ width: "100%", marginTop: "8px", padding: "8px" }}
      />
      <br /><br />

      <button onClick={handleUpload}>Let's Get Started</button>
    </div>
  );
}