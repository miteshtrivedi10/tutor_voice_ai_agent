import React from 'react';
import { Spinner as FlowbiteSpinner } from 'flowbite-react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'accent';
}

const Spinner: React.FC<SpinnerProps> = ({ size = 'md', color = 'primary' }) => {
  // Map our custom colors to Flowbite colors
  const colorMap = {
    primary: 'info',
    secondary: 'purple',
    accent: 'warning'
  };

  return (
    <div className="flex justify-center">
      <FlowbiteSpinner 
        size={size} 
        color={colorMap[color]} 
        aria-label="Loading..." 
      />
    </div>
  );
};

export default Spinner;