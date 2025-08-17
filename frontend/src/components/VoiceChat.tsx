import React, { useState } from 'react';
import { useVoiceChat } from '../hooks/useVoiceChat';
import { useAudioVisualizer } from '../hooks/useAnimation';
import { useVoiceStats } from '../hooks/useVoiceStats';
import ParticipantList from './ParticipantList';
import VoiceStats from './VoiceStats';
import Spinner from './Spinner';

interface VoiceChatProps {
  onConnect: (url: string, token: string) => void;
}

const VoiceChat: React.FC<VoiceChatProps> = ({ onConnect }) => {
  const { 
    room,
    isConnected, 
    isMuted, 
    error, 
    participants, 
    connectToRoom, 
    disconnectFromRoom, 
    toggleMute 
  } = useVoiceChat();
  
  const audioLevel = useAudioVisualizer(isConnected && !isMuted);
  const stats = useVoiceStats(room);
  const [isLoading, setIsLoading] = useState(false);

  const handleConnect = async () => {
    setIsLoading(true);
    try {
      // Connect to backend to get room details
      const response = await fetch('http://localhost:8000/voice', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // In a real app, you might want to send user info or session details
        body: JSON.stringify({}),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to connect to backend: ${response.status} ${response.statusText}`);
      }
      
      const { token, ws_url } = await response.json();
      
      // Pass connection info to parent component
      onConnect(ws_url, token);
      
      // Connect to LiveKit room
      await connectToRoom(ws_url, token);
    } catch (err) {
      console.error('Connection error:', err);
      // Handle error appropriately
    } finally {
      setIsLoading(false);
    }
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
          className="w-2 bg-gradient-to-t from-accent-400 to-accent-600 rounded-t transition-all duration-100 ease-out"
          style={{ height: `${barHeight}%` }}
        />
      );
    }
    
    return bars;
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 w-full">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-600 dark:text-gray-300">Connecting to voice session...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center space-y-4 w-full">
      {error && (
        <div className="p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-100 rounded-lg w-full">
          {error}
        </div>
      )}

      {!isConnected ? (
        <button
          onClick={handleConnect}
          className="px-6 py-3 bg-gradient-to-r from-accent-500 to-secondary-600 hover:from-accent-600 hover:to-secondary-700 text-white font-medium rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-50"
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
          {/* Voice statistics */}
          <VoiceStats 
            duration={stats.duration}
            audioQuality={stats.audioQuality}
            connectionStatus={stats.connectionStatus}
            latency={stats.latency}
          />
          
          {/* Audio visualization */}
          <div className="flex items-end justify-center space-x-1 h-24 w-full">
            {renderAudioBars()}
          </div>
          
          {/* Participant list */}
          <div className="w-full max-w-md">
            <ParticipantList participants={participants} />
          </div>
          
          <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button
              onClick={toggleMute}
              className={`px-6 py-3 font-medium rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-opacity-50 flex items-center ${
                isMuted
                  ? 'bg-gradient-to-r from-warning-500 to-amber-600 hover:from-warning-600 hover:to-amber-700 text-white focus:ring-warning-500'
                  : 'bg-gradient-to-r from-accent-500 to-secondary-600 hover:from-accent-600 hover:to-secondary-700 text-white focus:ring-accent-500'
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
              className="px-6 py-3 bg-gradient-to-r from-gray-600 to-gray-800 hover:from-gray-700 hover:to-gray-900 text-white font-medium rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-opacity-50 flex items-center"
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

export default VoiceChat;