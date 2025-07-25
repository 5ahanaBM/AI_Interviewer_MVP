export default function InterviewReport({ summary, onRestart }) {
  return (
    <div style={{ padding: "20px", border: "1px solid #ccc" }}>
      <h3>Interview Summary</h3>
      <p><strong>Total Questions Asked:</strong> {summary.total_questions}</p>
      <p><strong>Follow-up Questions:</strong> {summary.followups}</p>
      <p><strong>Skills Covered:</strong> {summary.skills.join(", ")}</p>
      <p><strong>Feedback:</strong> {summary.feedback}</p>
      <p><strong>Score:</strong> {summary.score}/5</p>
{/* 
      <button onClick={onRestart} style={{ marginTop: "20px" }}>
        Restart Interview
      </button> */}
    </div>
  );
}
