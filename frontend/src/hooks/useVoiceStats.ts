import { useState, useEffect } from 'react';
import { Room } from 'livekit-client';

export const useVoiceStats = (room: Room | null) => {
  const [stats, setStats] = useState({
    duration: 0,
    audioQuality: 'Good',
    connectionStatus: 'Connected',
    latency: 0,
  });

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    
    if (room) {
      // Start timer for session duration
      const startTime = Date.now();
      
      interval = setInterval(() => {
        const duration = Math.floor((Date.now() - startTime) / 1000);
        
        // In a real app, you would get these stats from the LiveKit room
        // For now, we'll simulate them
        const simulatedStats = {
          duration,
          audioQuality: duration % 60 < 10 ? 'Excellent' : duration % 60 < 30 ? 'Good' : 'Fair',
          connectionStatus: 'Connected',
          latency: Math.floor(Math.random() * 50), // Simulate latency between 0-50ms
        };
        
        setStats(simulatedStats);
      }, 1000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [room]);

  return stats;
};