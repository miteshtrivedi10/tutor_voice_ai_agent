// API Configuration
const API_CONFIG = {
  // Default API base URL
  BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    VOICE: '/voice',
    AUTH: '/auth',
    USER: '/user',
  },
  
  // WebSocket URL for LiveKit
  WS_URL: process.env.REACT_APP_LIVEKIT_WS_URL || 'ws://localhost:7880',
};

export default API_CONFIG;