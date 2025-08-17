import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useEntranceAnimation } from '../hooks/useAnimation';
import LandingPage from './LandingPage';
import QuizModeSelector from './QuizModeSelector';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const isMainContentVisible = useEntranceAnimation(300);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {!user ? (
        <LandingPage />
      ) : (
        <div className={`transition-opacity duration-1000 ${isMainContentVisible ? 'opacity-100' : 'opacity-0'}`}>
          <QuizModeSelector />
        </div>
      )}
    </div>
  );
};

export default Dashboard;