import React from 'react';
import { useVoiceChat } from '../hooks/useVoiceChat';
import { useAudioVisualizer } from '../hooks/useAnimation';
import API_CONFIG from '../config/api';

interface VoiceControlProps {
  onConnect: (url: string, token: string) => void;
}

const VoiceControl: React.FC<VoiceControlProps> = ({ onConnect }) => {
  const { isConnected, isMuted, error, connectToRoom, disconnectFromRoom, toggleMute } = useVoiceChat();
  const audioLevel = useAudioVisualizer(isConnected && !isMuted);

  const handleConnect = () => {
    // In a real app, you would get these from your backend
    // For now, we'll use dummy values
    const url = API_CONFIG.WS_URL;
    const token = 'dummy-token';
    onConnect(url, token);
    connectToRoom(url, token);
  };

  // Generate bars for audio visualization
  const renderAudioBars = () => {
    const bars = [];
    const barCount = 15;
    
    for (let i = 0; i < barCount; i++) {
      const barHeight = Math.max(5, Math.min(100, audioLevel * (0.7 + Math.random() * 0.3)));
      bars.push(
        <div
          key={i}
          className="w-2 bg-blue-500 rounded-t transition-all duration-100 ease-out"
          style={{ height: `${barHeight}%` }}
        />
      );
    }
    
    return bars;
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      {error && (
        <div className="p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-100 rounded-lg w-full">
          {error}
        </div>
      )}

      {!isConnected ? (
        <button
          onClick={handleConnect}
          className="btn-primary"
        >
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
            Start Voice Session
          </div>
        </button>
      ) : (
        <div className="flex flex-col items-center space-y-6 w-full">
          {/* Audio visualization */}
          <div className="flex items-end justify-center space-x-1 h-24 w-full">
            {renderAudioBars()}
          </div>
          
          <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button
              onClick={toggleMute}
              className={`font-medium shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-opacity-50 flex items-center ${
                isMuted
                  ? 'btn-warning'
                  : 'btn-danger'
              }`}
            >
              {isMuted ? (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM12.293 7.293a1 1 0 011.414 0L15 8.586l1.293-1.293a1 1 0 111.414 1.414L16.414 10l1.293 1.293a1 1 0 01-1.414 1.414L15 11.414l-1.293 1.293a1 1 0 01-1.414-1.414L13.586 10l-1.293-1.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  Unmute Microphone
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                  </svg>
                  Mute Microphone
                </>
              )}
            </button>

            <button
              onClick={disconnectFromRoom}
              className="btn-dark flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              End Session
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceControl;