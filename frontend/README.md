# VoiceTutor - AI Voice Tutoring Application

A modern, responsive React application for AI-powered voice tutoring with Light/Dark themes.

## Features

- 🌗 Light/Dark theme toggle with system preference detection
- 🔐 Google OAuth authentication
- 🎤 WebRTC voice communication using LiveKit
- 📱 Fully responsive design
- 🎨 Modern UI with Tailwind CSS
- 🚀 Production-ready with TypeScript

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd voice-tutor
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm start
   ```

The application will be available at http://localhost:3000

## Project Structure

```
src/
├── components/          # React components
├── context/             # React context providers
├── hooks/               # Custom React hooks
├── App.tsx              # Main application component
└── index.tsx            # Entry point
```

## Available Scripts

### `npm start`

Runs the app in development mode.

### `npm test`

Launches the test runner in interactive watch mode.

### `npm run build`

Builds the app for production to the `build` folder.

### `npm run eject`

Removes the single build dependency.

## Dependencies

- React + TypeScript
- Tailwind CSS for styling
- LiveKit for WebRTC communication
- @react-oauth/google for Google authentication

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
REACT_APP_LIVEKIT_SERVER_URL=your_livekit_server_url
```

## Deployment

To deploy the application:

1. Build the production version:
   ```bash
   npm run build
   ```

2. Deploy the contents of the `build` directory to your preferred hosting platform.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.