import { render, screen, fireEvent } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/AuthContext';
import React from 'react';

// Create a test component that uses the auth context
const TestComponent: React.FC = () => {
  const { user, login, logout } = useAuth();
  
  return (
    <div>
      {user ? (
        <div>
          <span data-testid="user-name">{user.name}</span>
          <span data-testid="user-email">{user.email}</span>
          <button data-testid="logout-button" onClick={logout}>
            Logout
          </button>
        </div>
      ) : (
        <div>
          <span data-testid="no-user">No user</span>
          <button 
            data-testid="login-button" 
            onClick={login}
          >
            Login
          </button>
        </div>
      )}
    </div>
  );
};

// Create a wrapper component with the auth provider
const WrappedTestComponent: React.FC = () => (
  <AuthProvider>
    <TestComponent />
  </AuthProvider>
);

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  it('should show no user initially', () => {
    render(<WrappedTestComponent />);
    
    expect(screen.getByTestId('no-user')).toBeInTheDocument();
  });

  it('should login user and display user info', () => {
    render(<WrappedTestComponent />);
    
    // Click the login button
    fireEvent.click(screen.getByTestId('login-button'));
    
    // Check if user info is displayed
    expect(screen.getByTestId('user-name')).toHaveTextContent('Demo Student');
    expect(screen.getByTestId('user-email')).toHaveTextContent('student@voicetutor.com');
  });

  it('should logout user', () => {
    render(<WrappedTestComponent />);
    
    // Login first
    fireEvent.click(screen.getByTestId('login-button'));
    
    // Verify user is logged in
    expect(screen.getByTestId('user-name')).toBeInTheDocument();
    
    // Click the logout button
    fireEvent.click(screen.getByTestId('logout-button'));
    
    // Check if user is logged out
    expect(screen.getByTestId('no-user')).toBeInTheDocument();
  });

  it('should persist user in localStorage', () => {
    render(<WrappedTestComponent />);
    
    // Click the login button
    fireEvent.click(screen.getByTestId('login-button'));
    
    // Check if user is saved in localStorage
    const storedUser = localStorage.getItem('user');
    expect(storedUser).not.toBeNull();
    
    const user = JSON.parse(storedUser!);
    expect(user.name).toBe('Demo Student');
    expect(user.email).toBe('student@voicetutor.com');
  });
});