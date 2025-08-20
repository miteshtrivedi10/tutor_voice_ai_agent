import React from 'react';
import { Card, Badge } from 'flowbite-react';

interface VoiceStatsProps {
  duration: number;
  audioQuality: string;
  connectionStatus: string;
  latency: number;
}

const VoiceStats: React.FC<VoiceStatsProps> = ({ 
  duration, 
  audioQuality, 
  connectionStatus, 
  latency 
}) => {
  // Determine badge color based on connection status
  const getConnectionStatusColor = () => {
    if (connectionStatus === 'Connected') return 'success';
    if (connectionStatus === 'Connecting') return 'warning';
    return 'failure';
  };

  // Determine badge color based on audio quality
  const getAudioQualityColor = () => {
    if (audioQuality === 'Excellent' || audioQuality === 'Good') return 'success';
    if (audioQuality === 'Fair') return 'warning';
    return 'failure';
  };

  // Format duration from seconds to MM:SS
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="w-full mb-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">Duration</p>
          <p className="text-lg font-semibold">{formatDuration(duration)}</p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">Audio Quality</p>
          <Badge color={getAudioQualityColor()} className="mx-auto">
            {audioQuality}
          </Badge>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">Connection</p>
          <Badge color={getConnectionStatusColor()} className="mx-auto">
            {connectionStatus}
          </Badge>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">Latency</p>
          <p className="text-lg font-semibold">{latency}ms</p>
        </div>
      </div>
    </Card>
  );
};

export default VoiceStats;