import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Footer from './Footer';
import './AppShell.css';
import './Footer.css';

export default function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="app-sidebar-brand">AI Health Check</div>
        <nav className="app-sidebar-nav">
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'active' : ''}>
            Dashboard
          </NavLink>
          <NavLink to="/chatbot" className={({ isActive }) => isActive ? 'active' : ''}>
            Chatbot
          </NavLink>
        </nav>
        <div className="app-sidebar-footer">
          <div className="app-sidebar-user">{user?.name}</div>
          <button className="app-sidebar-logout" onClick={handleLogout}>Log out</button>
        </div>
      </aside>
      <div className="app-main">
        <main className="app-main-content">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
}
