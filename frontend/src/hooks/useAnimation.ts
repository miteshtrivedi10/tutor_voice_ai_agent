import { useState, useEffect } from 'react';

// Simple hook for adding entrance animations
export const useEntranceAnimation = (delay = 0) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, delay);

    return () => clearTimeout(timer);
  }, [delay]);

  return isVisible;
};

// Simple hook for microphone audio visualization
export const useAudioVisualizer = (isActive: boolean) => {
  const [audioLevel, setAudioLevel] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isActive) {
      interval = setInterval(() => {
        // Simulate audio levels (in a real app, this would come from the WebRTC stream)
        setAudioLevel(Math.random() * 100);
      }, 100);
    } else {
      setAudioLevel(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive]);

  return audioLevel;
};