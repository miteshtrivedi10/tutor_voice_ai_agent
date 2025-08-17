import { render, screen } from '@testing-library/react';
import Dashboard from '../components/Dashboard';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import React from 'react';

// Mock the useEntranceAnimation hook
jest.mock('../hooks/useAnimation', () => ({
  useEntranceAnimation: () => true,
}));

// Create a wrapper component with the required providers
const WrappedDashboard: React.FC = () => (
  <AuthProvider>
    <ThemeProvider>
      <Dashboard />
    </ThemeProvider>
  </AuthProvider>
);

describe('Dashboard', () => {
  it('should render the main heading', () => {
    render(<WrappedDashboard />);
    
    expect(screen.getByText('AI Voice Tutor')).toBeInTheDocument();
  });

  it('should render the features section', () => {
    render(<WrappedDashboard />);
    
    expect(screen.getByText('How It Works')).toBeInTheDocument();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByText('Speak Naturally')).toBeInTheDocument();
    expect(screen.getByText('Improve Skills')).toBeInTheDocument();
  });
});