import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import VoiceChat from './VoiceChat';

const QuizModeSelector: React.FC = () => {
  const { user } = useAuth();
  const [selectedMode, setSelectedMode] = useState<'descriptive' | 'quick' | 'multiple' | null>(null);
  const [connectionInfo, setConnectionInfo] = useState<{ url: string; token: string } | null>(null);

  const handleConnect = (url: string, token: string) => {
    setConnectionInfo({ url, token });
  };

  const renderModeDescription = () => {
    switch (selectedMode) {
      case 'descriptive':
        return {
          title: 'Descriptive Voice Quiz',
          description: 'Practice speaking with our AI tutor. Answer questions descriptively and get feedback on grammar, pronunciation, and content accuracy.',
          icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          ),
          bgColor: 'bg-accent-100 dark:bg-accent-900/30',
          buttonColor: 'bg-accent-500 hover:bg-accent-600'
        };
      case 'quick':
        return {
          title: 'Quick Quiz Mode',
          description: 'Rapid-fire questions with a 2-minute timer. Practice quick thinking and concise responses.',
          icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-success-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
          bgColor: 'bg-success-100 dark:bg-success-900/30',
          buttonColor: 'bg-success-500 hover:bg-success-600'
        };
      case 'multiple':
        return {
          title: 'Multiple Choice Quiz',
          description: 'Interactive multiple choice questions that require visual attention. Perfect for testing comprehension.',
          icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-secondary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          ),
          bgColor: 'bg-secondary-100 dark:bg-secondary-900/30',
          buttonColor: 'bg-secondary-500 hover:bg-secondary-600'
        };
      default:
        return null;
    }
  };

  const modeInfo = renderModeDescription();

  if (selectedMode) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <button
            onClick={() => setSelectedMode(null)}
            className="flex items-center text-accent-600 dark:text-accent-400 hover:text-accent-800 dark:hover:text-accent-300 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Back to Mode Selection
          </button>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden mb-8">
          <div className="p-6">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              <div className="flex-shrink-0">
                {modeInfo?.icon}
              </div>
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{modeInfo?.title}</h2>
                <p className="text-gray-600 dark:text-gray-300">{modeInfo?.description}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Voice Control Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden transition-all duration-300 hover:shadow-2xl">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">Voice Session</h2>
                  <div className="flex items-center">
                    <div className="h-3 w-3 rounded-full bg-success-500 animate-pulse mr-2"></div>
                    <span className="text-sm text-gray-500 dark:text-gray-400">Live</span>
                  </div>
                </div>

                <div className="flex flex-col items-center justify-center py-12">
                  <VoiceChat onConnect={handleConnect} />
                </div>
              </div>
            </div>
          </div>

          {/* Info Panel */}
          <div>
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden mb-8 transition-all duration-300 hover:shadow-2xl">
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Session Info</h2>
                {connectionInfo ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Server URL</h3>
                      <p className="mt-1 text-sm text-gray-900 dark:text-white break-all">{connectionInfo.url}</p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Access Token</h3>
                      <p className="mt-1 text-sm text-gray-900 dark:text-white break-all">{connectionInfo.token}</p>
                    </div>
                    <div className="pt-4">
                      <div className="flex items-center text-sm text-success-600 dark:text-success-400">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Connected to server
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="mx-auto h-12 w-12 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                      </svg>
                    </div>
                    <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No active session</h3>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      Start a voice session to see connection details
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* User Info Panel */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden transition-all duration-300 hover:shadow-2xl">
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Your Profile</h2>
                {user ? (
                  <div className="flex items-center">
                    <img className="h-16 w-16 rounded-full object-cover" src={user.picture} alt={user.name} />
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">{user.name}</h3>
                      <p className="text-gray-500 dark:text-gray-400">{user.email}</p>
                      <div className="mt-2 flex items-center text-sm text-success-600 dark:text-success-400">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Active account
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <div className="mx-auto h-12 w-12 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Guest User</h3>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      Sign in to access your profile
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-12">
        <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 dark:text-white mb-4">
          Select Quiz Mode
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Choose from different quiz modes based on your learning objectives. All questions are generated from your uploaded study materials.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Descriptive Voice Quiz */}
        <div 
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden border border-gray-200 dark:border-gray-700 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 cursor-pointer"
          onClick={() => setSelectedMode('descriptive')}
        >
          <div className="p-6">
            <div className="flex justify-center mb-4">
              <div className="h-16 w-16 rounded-full bg-accent-100 dark:bg-accent-900 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
            </div>
            <h2 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-2">Descriptive Quiz</h2>
            <p className="text-gray-600 dark:text-gray-300 text-center mb-4">
              Answer questions with detailed verbal responses. Get comprehensive feedback on grammar, pronunciation, and content.
            </p>
            <div className="bg-accent-50 dark:bg-accent-900/30 rounded-lg p-4 mb-4">
              <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-accent-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Grammar and pronunciation analysis</span>
                </li>
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-accent-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Content accuracy verification</span>
                </li>
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-accent-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Detailed improvement suggestions</span>
                </li>
              </ul>
            </div>
            <button className="w-full py-2 bg-accent-500 hover:bg-accent-600 text-white font-medium rounded-lg transition-colors">
              Select Mode
            </button>
          </div>
        </div>

        {/* Quick Quiz Mode */}
        <div 
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden border border-gray-200 dark:border-gray-700 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 cursor-pointer"
          onClick={() => setSelectedMode('quick')}
        >
          <div className="p-6">
            <div className="flex justify-center mb-4">
              <div className="h-16 w-16 rounded-full bg-success-100 dark:bg-success-900 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-success-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <h2 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-2">Quick Quiz</h2>
            <p className="text-gray-600 dark:text-gray-300 text-center mb-4">
              Fast-paced questions with a 2-minute timer. Practice quick thinking and concise verbal responses.
            </p>
            <div className="bg-success-50 dark:bg-success-900/30 rounded-lg p-4 mb-4">
              <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-success-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>2-minute time limit</span>
                </li>
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-success-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Less than 10-word answers</span>
                </li>
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-success-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Rapid skill building</span>
                </li>
              </ul>
            </div>
            <button className="w-full py-2 bg-success-500 hover:bg-success-600 text-white font-medium rounded-lg transition-colors">
              Select Mode
            </button>
          </div>
        </div>

        {/* Multiple Choice Quiz */}
        <div 
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden border border-gray-200 dark:border-gray-700 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 cursor-pointer"
          onClick={() => setSelectedMode('multiple')}
        >
          <div className="p-6">
            <div className="flex justify-center mb-4">
              <div className="h-16 w-16 rounded-full bg-secondary-100 dark:bg-secondary-900 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-secondary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
            <h2 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-2">Multiple Choice</h2>
            <p className="text-gray-600 dark:text-gray-300 text-center mb-4">
              Interactive multiple choice questions. Requires visual attention and quick decision making.
            </p>
            <div className="bg-secondary-50 dark:bg-secondary-900/30 rounded-lg p-4 mb-4">
              <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-secondary-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Visual question format</span>
                </li>
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-secondary-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Screen-based interaction</span>
                </li>
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-secondary-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Immediate scoring</span>
                </li>
              </ul>
            </div>
            <button className="w-full py-2 bg-secondary-500 hover:bg-secondary-600 text-white font-medium rounded-lg transition-colors">
              Select Mode
            </button>
          </div>
        </div>
      </div>

      {/* Study Material Upload Section */}
      <div className="mt-16 bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-6">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Upload Study Materials</h2>
            <p className="text-gray-600 dark:text-gray-300">
              Upload your school chapters in PDF or PNG format to generate personalized quizzes
            </p>
          </div>
          
          <div className="max-w-2xl mx-auto">
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">Upload your study materials</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                PDF or PNG files containing school chapters will be used to generate your personalized quizzes.
              </p>
              <div className="mt-6">
                <button className="px-4 py-2 bg-accent-500 hover:bg-accent-600 text-white font-medium rounded-lg transition-colors">
                  Select Files
                </button>
              </div>
              <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                All files are processed securely and only used for generating your quizzes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizModeSelector;