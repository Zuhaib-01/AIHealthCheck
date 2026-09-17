import { useState } from 'react';
import FormField from '../ui/FormField';
import Button from '../ui/Button';
import Alert from '../ui/Alert';
import './AuthForm.css';

export default function AuthForm({ mode, onSubmit }) {
  const isSignup = mode === 'signup';
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await onSubmit(isSignup ? { name, email, password } : { email, password });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <Alert tone="danger">{error}</Alert>

      {isSignup && (
        <FormField
          label="Full name"
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Your name"
          required
        />
      )}

      <FormField
        label="Email address"
        id="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
        required
      />

      <FormField
        label="Password"
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder={isSignup ? 'At least 6 characters' : 'Your password'}
        required
      />

      <Button type="submit" disabled={loading} style={{ width: '100%' }}>
        {loading ? 'Please wait…' : isSignup ? 'Create account' : 'Log in'}
      </Button>
    </form>
  );
}
