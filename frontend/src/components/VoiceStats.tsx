import React from 'react';

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
  // Format duration as MM:SS
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Get quality color based on audio quality
  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'Excellent': return 'text-green-500';
      case 'Good': return 'text-blue-500';
      case 'Fair': return 'text-yellow-500';
      case 'Poor': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-2xl">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
        <div className="text-sm text-gray-500 dark:text-gray-400">Duration</div>
        <div className="text-xl font-bold text-gray-900 dark:text-white">{formatDuration(duration)}</div>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
        <div className="text-sm text-gray-500 dark:text-gray-400">Audio Quality</div>
        <div className={`text-xl font-bold ${getQualityColor(audioQuality)}`}>{audioQuality}</div>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
        <div className="text-sm text-gray-500 dark:text-gray-400">Connection</div>
        <div className="text-xl font-bold text-green-500">{connectionStatus}</div>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
        <div className="text-sm text-gray-500 dark:text-gray-400">Latency</div>
        <div className="text-xl font-bold text-gray-900 dark:text-white">{latency}ms</div>
      </div>
    </div>
  );
};

export default VoiceStats;