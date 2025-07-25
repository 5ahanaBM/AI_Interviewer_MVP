import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatBox({ sessionId, onSend, initialMessages = [], onComplete }) {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");

  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = async () => {
    const userMsg = input.trim();
    if (!userMsg) return;

    setMessages((msgs) => [...msgs, { from: "user", message: userMsg }]);
    setInput("");

    try {
      const aiResponse = await onSend(userMsg);
      console.log("AI response received:", aiResponse);

      const prompts = Array.isArray(aiResponse.prompt)
        ? aiResponse.prompt
        : [aiResponse.prompt];

      const aiMessages = prompts
        .filter((msg) => typeof msg === "string")
        .map((msg) => ({ from: "ai", message: msg }));

      setMessages((msgs) => [...msgs, ...aiMessages]);

      if (aiResponse.isComplete && typeof onComplete === "function") {
        setTimeout(() => {
          onComplete();
        }, 800);
      }
    } catch (err) {
      console.error("Error sending message:", err);
      setMessages((msgs) => [
        ...msgs,
        { from: "ai", message: "Something went wrong. Please try again." },
      ]);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "20px" }}>
      <div
        style={{
          width: "60%",
          maxWidth: "800px",
          height: "500px",
          overflowY: "auto",
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "15px",
          backgroundColor: "#f9f9f9",
        }}
      >
        {messages.map((m, idx) => (
          <MessageBubble key={idx} from={m.from} message={m.message} />
        ))}
        <div ref={chatEndRef} />
      </div>

      <div style={{ marginTop: "15px", width: "60%", maxWidth: "800px", display: "flex" }}>
        <textarea
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Type your answer and press Enter..."
          style={{
            flexGrow: 1,
            padding: "10px",
            borderRadius: "6px",
            border: "1px solid #ccc",
            fontSize: "16px",
            resize: "none",
          }}
        />
        <button
          onClick={handleSend}
          style={{
            marginLeft: "10px",
            padding: "10px 16px",
            fontSize: "16px",
            borderRadius: "6px",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
