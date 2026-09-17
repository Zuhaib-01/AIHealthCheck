import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthForm from '../components/auth/AuthForm';
import Card from '../components/ui/Card';
import './AuthPage.css';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async ({ email, password }) => {
    await login(email, password);
    navigate('/dashboard');
  };

  return (
    <section className="auth-page">
      <Card className="auth-card">
        <h2>Log in</h2>
        <AuthForm mode="login" onSubmit={handleSubmit} />
        <p className="auth-switch">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
      </Card>
    </section>
  );
}
