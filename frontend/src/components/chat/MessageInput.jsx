import { useState } from 'react';
import './MessageInput.css';

export default function MessageInput({ onSend, disabled }) {
  const [value, setValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type your message…"
        disabled={disabled}
        aria-label="Message"
      />
      <button type="submit" disabled={disabled || !value.trim()}>Send</button>
    </form>
  );
}
