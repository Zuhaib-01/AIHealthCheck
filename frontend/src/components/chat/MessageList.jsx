import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import './MessageList.css';

export default function MessageList({ messages, isTyping }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (messages.length === 0 && !isTyping) {
    return (
      <div className="message-list message-list-empty">
        <p>Describe how you're feeling to start a conversation with your AI health assistant.</p>
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((m, i) => (
        <MessageBubble key={i} sender={m.sender} text={m.text} />
      ))}
      {isTyping && <TypingIndicator />}
      <div ref={endRef} />
    </div>
  );
}
