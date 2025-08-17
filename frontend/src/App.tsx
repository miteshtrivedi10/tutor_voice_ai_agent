import React from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  // Get Google Client ID from environment variables
  const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>
        <ThemeProvider>
          <ErrorBoundary>
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
              <Header />
              <main className="flex-grow">
                <Dashboard />
              </main>
              <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <p className="text-center text-sm text-gray-500 dark:text-gray-400">
                    © {new Date().getFullYear()} VoiceTutor. All rights reserved.
                  </p>
                </div>
              </footer>
            </div>
          </ErrorBoundary>
        </ThemeProvider>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;