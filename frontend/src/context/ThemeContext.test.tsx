import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../context/ThemeContext';
import React from 'react';

// Create a test component that uses the theme context
const TestComponent: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <button data-testid="toggle-button" onClick={toggleTheme}>
        Toggle Theme
      </button>
    </div>
  );
};

// Create a wrapper component with the theme provider
const WrappedTestComponent: React.FC = () => (
  <ThemeProvider>
    <TestComponent />
  </ThemeProvider>
);

describe('ThemeContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  it('should default to light theme', () => {
    render(<WrappedTestComponent />);
    
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
  });

  it('should toggle theme when button is clicked', () => {
    render(<WrappedTestComponent />);
    
    // Initial theme should be light
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    
    // Click the toggle button
    fireEvent.click(screen.getByTestId('toggle-button'));
    
    // Theme should now be dark
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    
    // Click the toggle button again
    fireEvent.click(screen.getByTestId('toggle-button'));
    
    // Theme should now be light again
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
  });

  it('should persist theme in localStorage', () => {
    render(<WrappedTestComponent />);
    
    // Toggle to dark theme
    fireEvent.click(screen.getByTestId('toggle-button'));
    
    // Check if theme is saved in localStorage
    expect(localStorage.getItem('theme')).toBe('dark');
  });
});