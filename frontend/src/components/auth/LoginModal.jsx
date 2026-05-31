import React, { useState } from 'react';
import { X, Mail, Lock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const LoginModal = ({ isOpen, onClose, onSwitchToRegister }) => {
  const { loginWithGoogle, loginWithEmail } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');
    const result = await loginWithGoogle();
    if (result.success) {
      onClose();
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }
    setLoading(true);
    setError('');
    const result = await loginWithEmail(email, password);
    if (result.success) {
      onClose();
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="dark:bg-dark-card bg-white rounded-2xl border dark:border-dark-border border-gray-200 w-full max-w-md p-6 relative">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 dark:text-dark-muted text-gray-400 hover:text-gray-600 dark:hover:text-dark-text"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <h2 className="text-xl font-bold dark:text-dark-text text-gray-900 mb-1">Welcome back</h2>
        <p className="dark:text-dark-muted text-gray-500 text-sm mb-6">Login to access your portfolio & watchlist</p>

        {/* Google Login */}
        <button
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 border dark:border-dark-border border-gray-300 rounded-xl dark:hover:bg-dark-border/50 hover:bg-gray-50 transition-colors mb-4"
        >
          <span className="text-lg">G</span>
          <span className="dark:text-dark-text text-gray-900 font-medium">Continue with Google</span>
        </button>

        {/* Divider */}
        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 h-px dark:bg-dark-border bg-gray-200" />
          <span className="dark:text-dark-muted text-gray-400 text-xs">OR</span>
          <div className="flex-1 h-px dark:bg-dark-border bg-gray-200" />
        </div>

        {/* Email Login Form */}
        <form onSubmit={handleEmailLogin} className="space-y-3">
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 dark:text-dark-muted text-gray-400" />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-10 pr-4 py-3 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-xl focus:outline-none focus:border-blue-500/50 text-sm"
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 dark:text-dark-muted text-gray-400" />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-10 pr-4 py-3 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-xl focus:outline-none focus:border-blue-500/50 text-sm"
            />
          </div>

          {error && (
            <p className="text-loss text-xs">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl transition-colors disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* Switch to Register */}
        <p className="text-center dark:text-dark-muted text-gray-500 text-sm mt-4">
          Don't have an account?{' '}
          <button
            onClick={onSwitchToRegister}
            className="text-blue-400 hover:text-blue-300 font-medium"
          >
            Register
          </button>
        </p>
      </div>
    </div>
  );
};

export default LoginModal;