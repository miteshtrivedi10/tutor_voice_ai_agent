import React, { useState } from 'react';
import { useVoiceChat } from '../hooks/useVoiceChat';
import { useAudioVisualizer } from '../hooks/useAnimation';
import { useVoiceStats } from '../hooks/useVoiceStats';
import ParticipantList from './ParticipantList';
import VoiceStats from './VoiceStats';
import Spinner from './Spinner';
import API_CONFIG from '../config/api';
import { Alert } from 'flowbite-react';
import { ShimmerButton } from './ui/shimmer-button';

interface VoiceChatProps {
  onConnect: (url: string, token: string) => void;
  onDisconnect?: () => void;
}

const VoiceChat: React.FC<VoiceChatProps> = ({ onConnect, onDisconnect }) => {
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
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.VOICE}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'skip_zrok_interstitial': '1'
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

  const handleDisconnect = async () => {
    await disconnectFromRoom();
    // Notify parent component that we've disconnected
    if (onDisconnect) {
      onDisconnect();
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
        <Alert color="failure" className="w-full">
          <span>{error}</span>
        </Alert>
      )}

      {!isConnected ? (
        <button
          onClick={handleConnect}
          className="btn-primary w-full md:w-auto btn-lg"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
          </svg>
          Start Voice Session
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
            <ShimmerButton
              onClick={toggleMute}
              className={`w-full md:w-auto px-8 py-4 text-base rounded-2xl shadow-lg ${isMuted ? "" : "mr-2"}`}
              shimmerColor={isMuted ? "#000000" : "#ffffff"}
              background={isMuted ? "rgba(251, 191, 36, 1)" : "rgba(56, 189, 248, 1)"}
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
            </ShimmerButton>

            <ShimmerButton
              onClick={handleDisconnect}
              className="w-full md:w-auto px-8 py-4 text-base rounded-2xl shadow-lg ml-2"
              shimmerColor="#ffffff"
              background="rgba(239, 68, 68, 1)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 011 1v1a1 1 0 01-1 1H4a1 1 0 01-1-1V5zm0 4a1 1 0 011-1h12a1 1 0 011 1v1a1 1 0 01-1 1H4a1 1 0 01-1-1V9zm0 4a1 1 0 011-1h12a1 1 0 011 1v1a1 1 0 01-1 1H4a1 1 0 01-1-1v-1z" clipRule="evenodd" />
              </svg>
              Disconnect
            </ShimmerButton>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceChat;