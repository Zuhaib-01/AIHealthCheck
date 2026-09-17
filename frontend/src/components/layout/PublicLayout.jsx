import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';
import './Footer.css';

export default function PublicLayout() {
  return (
    <div className="public-layout">
      <Navbar />
      <main className="public-content">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
