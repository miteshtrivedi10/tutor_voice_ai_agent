import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useEntranceAnimation } from '../hooks/useAnimation';



const AnimatedMessage: React.FC<{ 
  text: string; 
  isTyping?: boolean; 
}> = ({ text, isTyping = false }) => {
  // Simply display the full text without typing animation or indicator
  return (
    <div>
      <p className="text-sm">{text}</p>
    </div>
  );
};

const HomePage: React.FC = () => {
  const { login } = useAuth();
  const isContentVisible = useEntranceAnimation(300);
  
  // State for conversation flow
  const [conversationState, setConversationState] = useState<'idle' | 'ai1.typing' | 'ai1.complete' | 'student.typing' | 'student.complete' | 'ai2.typing' | 'ai2.complete' | 'loop'>('idle');
  
  const aiQuestion = "What are the causes of high blood pressure?";
  const studentAnswer = "It is caused by not doing physical exercise.";
  const aiFeedback = "That's good Harshi! Though you could have answered more elaboratively as - High blood pressure is caused by lack of physical exercise, consuming food rich in salt & fat and having stress and anxiety.";
  
  // Reset and start conversation loop
  useEffect(() => {
    const startConversation = () => {
      setConversationState('ai1.typing');
    };

    const timer = setTimeout(startConversation, 1000);
    return () => clearTimeout(timer);
  }, []);
  
  // Handle conversation flow
  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];
    
    const scheduleNext = (nextState: typeof conversationState, delay: number) => {
      const timer = setTimeout(() => {
        setConversationState(nextState);
      }, delay);
      timers.push(timer);
    };
    
    switch (conversationState) {
      case 'ai1.typing':
        scheduleNext('ai1.complete', 1500);
        break;
      case 'ai1.complete':
        scheduleNext('student.typing', 1000);
        break;
      case 'student.typing':
        scheduleNext('student.complete', 1500);
        break;
      case 'student.complete':
        scheduleNext('ai2.typing', 1000);
        break;
      case 'ai2.typing':
        scheduleNext('ai2.complete', 2000);
        break;
      case 'ai2.complete':
        scheduleNext('loop', 2000);
        break;
      case 'loop':
        // Reset for continuous loop
        setConversationState('idle');
        timers.push(setTimeout(() => {
          setConversationState('ai1.typing');
        }, 500));
        break;
    }
    
    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [conversationState]);

  return (
    <div className={`transition-opacity duration-1000 ${isContentVisible ? 'opacity-100' : 'opacity-0'}`}>
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-accent-50 to-secondary-100 dark:from-gray-800 dark:to-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="relative z-10 pb-8 sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="sm:text-center lg:text-left">
                <div className="flex items-center justify-center lg:justify-start mb-4">
                  <img src="/homepage_icon.png" alt="AI Tutor" className="h-12 w-12 mr-3" />
                  <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 dark:text-white sm:text-5xl md:text-6xl">
                    <span className="block">AI Powered</span>
                    <span className="block text-accent-600 dark:text-accent-400">Study Buddy</span>
                  </h1>
                </div>
                <p className="mt-3 text-base text-gray-600 dark:text-gray-300 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                  Transform your learning experience with our interactive voice-based tutoring platform. 
                  Practice speaking, get real-time feedback, and improve your skills faster.
                </p>
                <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                  <div className="rounded-md shadow">
                    <button
                      onClick={login}
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-accent-500 hover:bg-accent-600 md:py-4 md:text-lg md:px-10"
                    >
                      <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                        <path
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                          fill="#fff"
                        />
                        <path
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                          fill="#fff"
                        />
                        <path
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                          fill="#fff"
                        />
                        <path
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                          fill="#fff"
                        />
                      </svg>
                      Start Learning
                    </button>
                  </div>
                  <div className="mt-3 sm:mt-0 sm:ml-3">
                    <button
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-accent-700 bg-accent-100 hover:bg-accent-200 dark:text-accent-300 dark:bg-accent-900/50 dark:hover:bg-accent-800 md:py-4 md:text-lg md:px-10"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                      </svg>
                      How It Works
                    </button>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
        <div className="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2 flex items-center justify-center p-8">
          <div className="relative w-full max-w-lg">
            <div className="absolute inset-0 bg-gradient-to-r from-accent-400 to-secondary-500 rounded-full blur-3xl opacity-30 animate-pulse"></div>
            <div className="relative bg-white dark:bg-gray-800 rounded-3xl shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-700">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="h-3 w-3 rounded-full bg-red-500 mr-2"></div>
                    <div className="h-3 w-3 rounded-full bg-yellow-500 mr-2"></div>
                    <div className="h-3 w-3 rounded-full bg-green-500"></div>
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Study Session</div>
                </div>
                <div className="space-y-4">
                  {/* AI Friend Question */}
                  <div className="flex items-start">
                    <div className="flex-shrink-0 h-10 w-10 rounded-full bg-accent-100 dark:bg-accent-900 flex items-center justify-center">
                      <img src="/homepage_icon.png" alt="AI Tutor" className="h-6 w-6" />
                    </div>
                    <div className="ml-3">
                      <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-tl-none px-4 py-2">
                        <AnimatedMessage 
                          text={aiQuestion}
                          isTyping={conversationState === 'ai1.typing'}
                        />
                      </div>
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1 text-accent-500" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                        </svg>
                        Just now
                      </div>
                    </div>
                  </div>
                  
                  {/* Harshi's Answer */}
                  <div className="flex items-start justify-end">
                    <div className="mr-3">
                      <div className="bg-accent-500 text-white rounded-2xl rounded-tr-none px-4 py-2">
                        <AnimatedMessage 
                          text={studentAnswer}
                          isTyping={conversationState === 'student.typing'}
                        />
                      </div>
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400 text-right flex items-center justify-end">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1 text-accent-500" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                        </svg>
                        Just now
                      </div>
                    </div>
                    <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
                      <span className="text-gray-600 dark:text-gray-300 font-bold">H</span>
                    </div>
                  </div>
                  
                  {/* AI Friend Feedback */}
                  <div className="flex items-start">
                    <div className="flex-shrink-0 h-10 w-10 rounded-full bg-accent-100 dark:bg-accent-900 flex items-center justify-center">
                      <img src="/homepage_icon.png" alt="AI Tutor" className="h-6 w-6" />
                    </div>
                    <div className="ml-3">
                      <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-tl-none px-4 py-2">
                        <AnimatedMessage 
                          text={aiFeedback}
                          isTyping={conversationState === 'ai2.typing'}
                        />
                      </div>
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1 text-accent-500" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                        </svg>
                        Just now
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Audio visualization bars */}
                <div className="mt-4 flex items-center justify-center space-x-1 h-6">
                  <div className="w-1 bg-accent-400 rounded-t animate-pulse" style={{ height: '40%' }}></div>
                  <div className="w-1 bg-accent-500 rounded-t animate-pulse" style={{ height: '70%', animationDelay: '0.1s' }}></div>
                  <div className="w-1 bg-accent-600 rounded-t animate-pulse" style={{ height: '100%', animationDelay: '0.2s' }}></div>
                  <div className="w-1 bg-accent-500 rounded-t animate-pulse" style={{ height: '70%', animationDelay: '0.3s' }}></div>
                  <div className="w-1 bg-accent-400 rounded-t animate-pulse" style={{ height: '40%', animationDelay: '0.4s' }}></div>
                  <div className="w-1 bg-accent-500 rounded-t animate-pulse" style={{ height: '60%', animationDelay: '0.5s' }}></div>
                  <div className="w-1 bg-accent-600 rounded-t animate-pulse" style={{ height: '90%', animationDelay: '0.6s' }}></div>
                  <div className="w-1 bg-accent-500 rounded-t animate-pulse" style={{ height: '60%', animationDelay: '0.7s' }}></div>
                  <div className="w-1 bg-accent-400 rounded-t animate-pulse" style={{ height: '30%', animationDelay: '0.8s' }}></div>
                </div>
                
                <div className="mt-2 text-center">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-accent-100 text-accent-800 dark:bg-accent-900 dark:text-accent-200">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                    </svg>
                    Voice session in progress
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-12 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:text-center">
            <h2 className="text-base text-accent-600 dark:text-accent-400 font-semibold tracking-wide uppercase">Powerful Features</h2>
            <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
              Everything you need to master speaking
            </p>
            <p className="mt-4 max-w-2xl text-xl text-gray-600 dark:text-gray-300 lg:mx-auto">
              Our AI-powered platform provides comprehensive tools for language learning through conversation.
            </p>
          </div>

          <div className="mt-10">
            <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
              <div className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-accent-500 text-white">
                  <img src="/homepage_icon.png" alt="AI Tutor" className="h-8 w-8" />
                </div>
                <div className="ml-16">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Natural Conversation Practice</h3>
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400">
                    Engage in realistic conversations with our AI tutor that adapts to your skill level and learning goals.
                  </p>
                </div>
              </div>

              <div className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-secondary-500 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div className="ml-16">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Real-time Feedback</h3>
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400">
                    Get instant feedback on pronunciation, grammar, and fluency to accelerate your learning progress.
                  </p>
                </div>
              </div>

              <div className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-success-500 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-16">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Multiple Quiz Modes</h3>
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400">
                    Choose from descriptive, quick, or multiple choice quizzes based on your uploaded study materials.
                  </p>
                </div>
              </div>

              <div className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-warning-500 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="ml-16">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Progress Tracking</h3>
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400">
                    Monitor your improvement over time with detailed analytics and personalized learning insights.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-gray-50 dark:bg-gray-900 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-base text-accent-600 dark:text-accent-400 font-semibold tracking-wide uppercase">Simple Process</h2>
            <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
              Get started in three easy steps
            </p>
          </div>

          <div className="mt-10">
            <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-3 md:gap-x-8 md:gap-y-10">
              <div className="flex flex-col items-center text-center">
                <div className="flex-shrink-0 h-20 w-20 rounded-full bg-accent-100 dark:bg-accent-900 flex items-center justify-center">
                  <span className="text-2xl font-bold text-accent-600 dark:text-accent-400">1</span>
                </div>
                <div className="mt-5">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Upload Study Materials</h3>
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400">
                    Upload your school chapters in PDF or PNG format. Our AI will create a knowledge base from your materials.
                  </p>
                </div>
              </div>

              <div className="flex flex-col items-center text-center">
                <div className="flex-shrink-0 h-20 w-20 rounded-full bg-secondary-100 dark:bg-secondary-900 flex items-center justify-center">
                  <span className="text-2xl font-bold text-secondary-600 dark:text-secondary-400">2</span>
                </div>
                <div className="mt-5">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Choose Quiz Mode</h3>
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400">
                    Select from descriptive, quick, or multiple choice quiz modes based on your learning objectives.
                  </p>
                </div>
              </div>

              <div className="flex flex-col items-center text-center">
                <div className="flex-shrink-0 h-20 w-20 rounded-full bg-success-100 dark:bg-success-900 flex items-center justify-center">
                  <span className="text-2xl font-bold text-success-600 dark:text-success-400">3</span>
                </div>
                <div className="mt-5">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Practice & Improve</h3>
                  <p className="mt-2 text-base text-gray-600 dark:text-gray-400">
                    Engage with the AI tutor through voice conversation and receive personalized feedback to improve.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-accent-600 to-secondary-700 dark:from-accent-800 dark:to-secondary-900">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
          <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            <span className="block">Ready to transform your learning?</span>
            <span className="block text-accent-200 flex items-center justify-center lg:justify-start">
              <img src="/homepage_icon.png" alt="AI Tutor" className="h-8 w-8 mr-2" />
              Start speaking with AI today.
            </span>
          </h2>
          <div className="mt-8 flex lg:mt-0 lg:flex-shrink-0">
            <div className="inline-flex rounded-md shadow">
              <button
                onClick={login}
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-accent-600 bg-white hover:bg-accent-50"
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                Get Started
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;