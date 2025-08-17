# VoiceTutor Frontend - Project Context

## Project Overview
VoiceTutor is a modern, responsive React application for AI-powered voice tutoring with Light/Dark themes. The application allows users to practice speaking with an AI tutor through WebRTC voice communication using LiveKit.

### Main Technologies
- React + TypeScript
- Tailwind CSS for styling
- LiveKit for WebRTC communication
- @react-oauth/google for Google authentication

### Architecture
The application follows a component-based architecture with:
- `components/` - React components for UI elements
- `context/` - React context providers for global state (Auth, Theme)
- `hooks/` - Custom React hooks for reusable logic

## Building and Running

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Development Setup
1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file in the root directory with the following variables:
   ```bash
   REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
   REACT_APP_LIVEKIT_SERVER_URL=your_livekit_server_url
   REACT_APP_DEFAULT_THEME=light
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   The application will be available at http://localhost:3000

### Available Scripts
- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner in interactive watch mode
- `npm run build` - Builds the app for production to the `build` folder
- `npm run eject` - Removes the single build dependency

## Development Conventions
- Uses TypeScript for type safety
- Tailwind CSS for styling with a consistent design system
- React Context for state management (Auth, Theme)
- Custom hooks for reusable logic
- Component-based architecture with clear separation of concerns
- Responsive design using Tailwind's responsive utilities
- Dark mode support with system preference detection

## Key Components
- `App.tsx` - Main application component
- `Dashboard.tsx` - Main dashboard showing voice chat interface
- `VoiceChat.tsx` - Voice chat component with controls
- `Header.tsx` - Application header with theme toggle
- `AuthContext.tsx` - Authentication state management
- `ThemeContext.tsx` - Theme state management
- `useVoiceChat.ts` - Custom hook for LiveKit voice chat functionality

## Environment Variables
- `REACT_APP_GOOGLE_CLIENT_ID` - Google OAuth client ID
- `REACT_APP_LIVEKIT_SERVER_URL` - LiveKit server URL
- `REACT_APP_DEFAULT_THEME` - Default theme ('light' or 'dark')