import { render, screen, fireEvent } from '@testing-library/react';
import VoiceChat from '../components/VoiceChat';
import React from 'react';

// Mock the useVoiceChat hook
jest.mock('../hooks/useVoiceChat', () => ({
  useVoiceChat: () => ({
    isConnected: false,
    isMuted: false,
    error: null,
    connectToRoom: jest.fn(),
    disconnectFromRoom: jest.fn(),
    toggleMute: jest.fn(),
  }),
}));

// Mock the useAudioVisualizer hook
jest.mock('../hooks/useAnimation', () => ({
  useAudioVisualizer: () => 50,
}));

describe('VoiceChat', () => {
  const mockOnConnect = jest.fn();

  beforeEach(() => {
    mockOnConnect.mockClear();
  });

  it('should render start session button when not connected', () => {
    render(<VoiceChat onConnect={mockOnConnect} />);
    
    expect(screen.getByText('Start Voice Session')).toBeInTheDocument();
  });

  it('should call onConnect when start button is clicked', () => {
    render(<VoiceChat onConnect={mockOnConnect} />);
    
    fireEvent.click(screen.getByText('Start Voice Session'));
    
    expect(mockOnConnect).toHaveBeenCalledTimes(1);
  });
});