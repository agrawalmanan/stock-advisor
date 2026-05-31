import React, { useState } from 'react';
import { X, Mail, Lock, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const RegisterModal = ({ isOpen, onClose, onSwitchToLogin }) => {
  const { loginWithGoogle, registerWithEmail } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
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

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setError('');
    const result = await registerWithEmail(name, email, password);
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
        <h2 className="text-xl font-bold dark:text-dark-text text-gray-900 mb-1">Create Account</h2>
        <p className="dark:text-dark-muted text-gray-500 text-sm mb-6">Sign up to save your portfolio & watchlist</p>

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

        {/* Register Form */}
        <form onSubmit={handleRegister} className="space-y-3">
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 dark:text-dark-muted text-gray-400" />
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full pl-10 pr-4 py-3 dark:bg-dark-bg dark:border-dark-border dark:text-dark-text bg-gray-50 border-gray-300 text-gray-900 border rounded-xl focus:outline-none focus:border-blue-500/50 text-sm"
            />
          </div>
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
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 dark:text-dark-muted text-gray-400" />
            <input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        {/* Switch to Login */}
        <p className="text-center dark:text-dark-muted text-gray-500 text-sm mt-4">
          Already have an account?{' '}
          <button
            onClick={onSwitchToLogin}
            className="text-blue-400 hover:text-blue-300 font-medium"
          >
            Login
          </button>
        </p>
      </div>
    </div>
  );
};

export default RegisterModal;