export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="site-footer">
      <span>© {year} AI Health Check</span>
      <span className="site-footer-note">Not a substitute for professional medical advice.</span>
    </footer>
  );
}
