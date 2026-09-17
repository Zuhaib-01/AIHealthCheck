import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthForm from '../components/auth/AuthForm';
import Card from '../components/ui/Card';
import './AuthPage.css';

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async ({ name, email, password }) => {
    await signup(name, email, password);
    navigate('/dashboard');
  };

  return (
    <section className="auth-page">
      <Card className="auth-card">
        <h2>Create your account</h2>
        <AuthForm mode="signup" onSubmit={handleSubmit} />
        <p className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </Card>
    </section>
  );
}
