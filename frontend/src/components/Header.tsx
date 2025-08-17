import React from 'react';
import ThemeToggle from './ThemeToggle';
import UserProfile from './UserProfile';
import { useAuth } from '../context/AuthContext';
import MobileMenu from './MobileMenu';

const Header: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <img src="/homepage_icon.png" alt="VoiceTutor" className="h-8 w-8 rounded-full" />
              <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white hidden sm:block">VoiceTutor</span>
            </div>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            <ThemeToggle />
            {user ? (
              <div className="flex items-center space-x-4">
                <UserProfile />
                <button
                  onClick={logout}
                  className="text-sm text-gray-700 dark:text-gray-300 hover:text-accent-600 dark:hover:text-accent-400 transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="text-sm text-gray-700 dark:text-gray-300">
                Guest User
              </div>
            )}
          </div>
          
          {/* Mobile menu button */}
          <MobileMenu />
        </div>
      </div>
    </header>
  );
};

export default Header;