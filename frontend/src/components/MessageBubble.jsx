export default function MessageBubble({ message, from }) {
  const isUser = from === "user";
  return (
    <div style={{ textAlign: isUser ? "right" : "left", margin: "10px" }}>
      <div style={{
        display: "inline-block",
        padding: "8px 12px",
        borderRadius: "12px",
        background: isUser ? "#DCF8C6" : "#F1F0F0"
      }}>
        {message}
      </div>
    </div>
  );
}
