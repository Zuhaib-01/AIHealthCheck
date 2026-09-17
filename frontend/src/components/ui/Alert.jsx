import './Alert.css';

export default function Alert({ tone = 'danger', children }) {
  if (!children) return null;
  return <div className={`alert alert-${tone}`} role="alert">{children}</div>;
}
