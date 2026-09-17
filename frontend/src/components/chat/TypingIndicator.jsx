import './TypingIndicator.css';

export default function TypingIndicator() {
  return (
    <div className="message-bubble message-bot typing-indicator" aria-label="Assistant is typing">
      <span></span><span></span><span></span>
    </div>
  );
}
