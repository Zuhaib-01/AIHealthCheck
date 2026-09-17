import { useEffect, useState } from 'react';
import { api } from '../../api/client';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './ChatWindow.css';

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getChatHistory()
      .then((data) => {
        const loaded = (data.history || []).flatMap((turn) => [
          { sender: 'user', text: turn.message },
          { sender: 'bot', text: turn.response },
        ]);
        setMessages(loaded);
      })
      .catch(() => setError('Could not load your chat history.'))
      .finally(() => setLoadingHistory(false));
  }, []);

  const handleSend = async (text) => {
    setError('');
    setMessages((prev) => [...prev, { sender: 'user', text }]);
    setIsTyping(true);
    try {
      const data = await api.sendMessage(text);
      setMessages((prev) => [...prev, { sender: 'bot', text: data.reply }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">AI Medical Assistant</div>
      {error && <div className="chat-error">{error}</div>}
      {loadingHistory ? (
        <div className="chat-loading">Loading conversation…</div>
      ) : (
        <MessageList messages={messages} isTyping={isTyping} />
      )}
      <MessageInput onSend={handleSend} disabled={isTyping || loadingHistory} />
    </div>
  );
}
