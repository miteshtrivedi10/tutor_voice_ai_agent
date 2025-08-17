import React from 'react';
import { Participant } from 'livekit-client';

interface ParticipantListProps {
  participants: Participant[];
}

const ParticipantList: React.FC<ParticipantListProps> = ({ participants }) => {
  if (participants.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-500 dark:text-gray-400">No other participants in the session</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white">Participants</h3>
      <ul className="space-y-2">
        {participants.map((participant) => (
          <li 
            key={participant.sid} 
            className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
          >
            <div className="flex-shrink-0">
              <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center">
                <span className="text-white font-medium">
                  {participant.name ? participant.name.charAt(0).toUpperCase() : 'U'}
                </span>
              </div>
            </div>
            <div className="ml-3 overflow-hidden">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {participant.name || 'Unnamed Participant'}
              </p>
              <div className="flex items-center mt-1">
                {participant.isSpeaking && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                    Speaking
                  </span>
                )}
                {participant.audioLevel > 0 && (
                  <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                    Audio
                  </span>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ParticipantList;