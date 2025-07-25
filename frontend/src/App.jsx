import { useState } from "react";
import ResumeUpload from "./components/ResumeUpload";
import ChatBox from "./components/ChatBox";
import InterviewReport from "./components/InterviewReport";
import { uploadResume, startSession, nextQuestion } from "./api";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [showChat, setShowChat] = useState(false);
  const [initialMessages, setInitialMessages] = useState([]);
  const [showReport, setShowReport] = useState(false);
  const [summaryData, setSummaryData] = useState(null);

  const handleResumeUpload = async (file, jobTitle) => {
    try {
      const result = await uploadResume(file);
      console.log("Resume upload result:", result);

      const info = result.structured_info;
      if (!info || !info.skills || info.skills.length === 0) {
        alert("Could not extract skills from resume. Please try another file.");
        return;
      }

      const newSessionId = "sess_" + Date.now();
      setSessionId(newSessionId);

      const sessionStart = await startSession(newSessionId, info.skills, jobTitle);
      const greetingMessage = { from: "ai", message: sessionStart.prompt };

      setInitialMessages([greetingMessage]);
      setShowChat(true);
    } catch (err) {
      console.error("Resume processing failed:", err);
      alert("Something went wrong while processing the resume.");
    }
  };

  const handleSend = async (userMsg) => {
    try {
      const res = await nextQuestion(sessionId, userMsg);
      console.log("📨 AI response received:", res);

      let prompts = [];
      let isInterviewComplete = false;

      if (typeof res.prompt === "string") {
        prompts = [res.prompt];
      } else if (Array.isArray(res.prompt)) {
        prompts = res.prompt;
      } else if (typeof res.prompt === "object" && res.prompt.message) {
        prompts = [res.prompt.message];
        if (res.prompt.summary) {
          isInterviewComplete = true;
          setSummaryData(res.prompt.summary);
          setTimeout(() => setShowReport(true), 0);
        }
      }

      return { prompt: prompts, isComplete: isInterviewComplete };
    } catch (err) {
      console.error("Chat send failed:", err);
      return {
        prompt: ["Something went wrong. Please try again."],
        isComplete: false,
      };
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2>AI Interviewer</h2>
      
      {!showChat && !showReport ? (
        <ResumeUpload onResumeParsed={handleResumeUpload} />
      ) : showReport ? (
        <InterviewReport
          summary={summaryData}
          onRestart={() => window.location.reload()}
        />
      ) : (
        <ChatBox
          sessionId={sessionId}
          onSend={handleSend}
          initialMessages={initialMessages}
          onComplete={() => setShowReport(true)}
        />
      )}
    </div>
  );
}

export default App;