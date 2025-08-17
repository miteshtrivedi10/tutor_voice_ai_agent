import React, { useState } from 'react';
import ThemeToggle from './ThemeToggle';
import UserProfile from './UserProfile';
import { useAuth } from '../context/AuthContext';
import GoogleLoginButton from './GoogleLoginButton';

const MobileMenu: React.FC = () => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-md text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-expanded="false"
      >
        <span className="sr-only">Open menu</span>
        {isOpen ? (
          <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        )}
      </button>

      {isOpen && (
        <div className="absolute top-16 left-0 right-0 z-10 bg-white dark:bg-gray-800 shadow-lg rounded-b-lg">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <img src="/homepage_icon.png" alt="VoiceTutor" className="h-8 w-8 rounded-full" />
                <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">VoiceTutor</span>
              </div>
              <ThemeToggle />
            </div>
            
            <div className="p-4">
              {user ? (
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <img className="h-10 w-10 rounded-full object-cover" src={user.picture} alt={user.name} />
                    <div className="ml-3">
                      <div className="text-base font-medium text-gray-900 dark:text-white">{user.name}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{user.email}</div>
                    </div>
                  </div>
                  <UserProfile />
                </div>
              ) : (
                <div className="flex flex-col space-y-4">
                  <div className="text-sm text-gray-700 dark:text-gray-300">
                    Guest User
                  </div>
                  <GoogleLoginButton />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MobileMenu;