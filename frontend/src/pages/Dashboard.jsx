import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const [recentTurns, setRecentTurns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getChatHistory()
      .then((data) => setRecentTurns((data.history || []).slice(-3).reverse()))
      .catch(() => setRecentTurns([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="dashboard-page">
      <h1>Welcome back, {user?.name}</h1>
      <p>Stay on top of what you've discussed and explored so far.</p>

      <Card className="dashboard-cta">
        <div>
          <h3>Open the chatbot</h3>
          <p>Continue your conversation with your AI health assistant.</p>
        </div>
        <Button as={Link} to="/chatbot">Open chatbot</Button>
      </Card>

      <h2>Recent conversation</h2>
      {loading ? (
        <p>Loading…</p>
      ) : recentTurns.length === 0 ? (
        <Card><p>No conversations yet — anything you chat about will show up here.</p></Card>
      ) : (
        <div className="results-list">
          {recentTurns.map((turn, i) => (
            <Card key={i} className="result-row">
              <div>
                <strong>You asked</strong>
                <span className="result-date">{turn.created_at}</span>
              </div>
              <p>{turn.message}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
