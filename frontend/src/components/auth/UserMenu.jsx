import React, { useState, useRef, useEffect } from 'react';
import { LogOut, User, Heart, Briefcase } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const UserMenu = () => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
    navigate('/');
  };

  return (
    <div ref={menuRef} className="relative">
      {/* Avatar Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-xl dark:hover:bg-dark-border/50 hover:bg-gray-100 transition-colors"
      >
        {user.photoURL ? (
          <img
            src={user.photoURL}
            alt=""
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-blue-400" />
          </div>
        )}
        <span className="dark:text-dark-text text-gray-900 text-sm font-medium hidden md:block">
          {user.displayName}
        </span>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-56 dark:bg-dark-card bg-white border dark:border-dark-border border-gray-200 rounded-xl shadow-2xl z-50 overflow-hidden">
          {/* User Info */}
          <div className="px-4 py-3 border-b dark:border-dark-border border-gray-100">
            <p className="dark:text-dark-text text-gray-900 text-sm font-medium">{user.displayName}</p>
            <p className="dark:text-dark-muted text-gray-500 text-xs">{user.email}</p>
          </div>

          {/* Menu Items */}
          <div className="py-1">
            <button
              onClick={() => { navigate('/watchlist'); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-4 py-2.5 dark:hover:bg-dark-border/50 hover:bg-gray-50 transition-colors text-left"
            >
              <Heart className="w-4 h-4 dark:text-dark-muted text-gray-400" />
              <span className="dark:text-dark-text text-gray-900 text-sm">My Watchlist</span>
            </button>
            <button
              onClick={() => { navigate('/portfolio'); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-4 py-2.5 dark:hover:bg-dark-border/50 hover:bg-gray-50 transition-colors text-left"
            >
              <Briefcase className="w-4 h-4 dark:text-dark-muted text-gray-400" />
              <span className="dark:text-dark-text text-gray-900 text-sm">My Portfolio</span>
            </button>
          </div>

          {/* Logout */}
          <div className="border-t dark:border-dark-border border-gray-100 py-1">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2.5 dark:hover:bg-dark-border/50 hover:bg-gray-50 transition-colors text-left"
            >
              <LogOut className="w-4 h-4 text-loss" />
              <span className="text-loss text-sm">Logout</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;