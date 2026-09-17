import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Button from '../ui/Button';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="navbar">
      <Link to="/" className="navbar-brand">AI Health Check</Link>
      <nav className="navbar-links">
        <Link to="/about">About</Link>
        {user ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Button variant="ghost" onClick={handleLogout}>Log out</Button>
          </>
        ) : (
          <>
            <Link to="/login">Log in</Link>
            <Button as={Link} to="/signup" variant="primary">Sign up</Button>
          </>
        )}
      </nav>
    </header>
  );
}
