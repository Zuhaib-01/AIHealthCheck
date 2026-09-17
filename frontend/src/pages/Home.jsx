import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import './Home.css';

export default function Home() {
  const { user } = useAuth();

  return (
    <section className="home-hero">
      <div className="home-hero-text">
        <h1>Talk through your symptoms before you decide what to do next.</h1>
        <p>
          AI Health Check listens to what you're feeling, cross-references it against
          symptom and condition data, and gives you a plain-language starting point —
          not a diagnosis, a direction.
        </p>
        <div className="home-hero-actions">
          {user ? (
            <Button as={Link} to="/dashboard">Go to dashboard</Button>
          ) : (
            <>
              <Button as={Link} to="/signup">Get started</Button>
              <Button as={Link} to="/login" variant="secondary">Log in</Button>
            </>
          )}
        </div>
      </div>

      <div className="home-hero-preview" aria-hidden="true">
        <div className="preview-bubble preview-bubble-user">I've had a headache and mild fever since yesterday.</div>
        <div className="preview-bubble preview-bubble-bot">That combination is worth watching. Here's what usually helps first, and when it's time to see someone.</div>
      </div>
    </section>
  );
}
