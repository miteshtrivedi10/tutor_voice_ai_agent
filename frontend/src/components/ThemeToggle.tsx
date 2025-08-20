import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { DarkThemeToggle } from 'flowbite-react';

const ThemeToggle: React.FC = () => {
  const { toggleTheme } = useTheme();

  return (
    <DarkThemeToggle 
      onClick={toggleTheme} 
      className="mr-2"
    />
  );
};

export default ThemeToggle;