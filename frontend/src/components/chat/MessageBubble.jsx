export default function MessageBubble({ sender, text }) {
  return (
    <div className={`message-bubble message-${sender}`}>
      {text}
    </div>
  );
}
