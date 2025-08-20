import React from 'react';
import { Card, Avatar, Badge } from 'flowbite-react';
import { Participant as LiveKitParticipant } from 'livekit-client';

interface ParticipantListProps {
  participants: LiveKitParticipant[];
}

const ParticipantList: React.FC<ParticipantListProps> = ({ participants }) => {
  // Separate local participant from remote participants
  const localParticipant = participants.find(p => p.isLocal);
  const remoteParticipants = participants.filter(p => !p.isLocal);
  
  // Combine participants with local participant first
  const orderedParticipants = localParticipant 
    ? [localParticipant, ...remoteParticipants] 
    : remoteParticipants;

  return (
    <Card className="card-modern">
      <div className="card-modern-header flex items-center justify-between">
        <h3 className="text-lg font-bold">Participants</h3>
        <Badge color="info">{participants.length}</Badge>
      </div>
      <div className="card-modern-body space-y-3">
        {orderedParticipants.map((participant) => (
          <div 
            key={participant.sid} 
            className={`flex items-center justify-between p-3 rounded-xl transition-all duration-200 ${
              participant.isSpeaking 
                ? 'bg-gradient-to-r from-accent-100 to-accent-50 dark:from-accent-900/50 dark:to-accent-900/30 border-l-4 border-accent-500' 
                : 'bg-gray-50 dark:bg-gray-700/50'
            }`}
          >
            <div className="flex items-center">
              <Avatar rounded size="sm" />
              <div className="ml-3">
                <p className="font-medium">
                  {participant.name || participant.identity}
                  {participant.isLocal && (
                    <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">(You)</span>
                  )}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {participant.isSpeaking && (
                <Badge color="success" size="xs">
                  Speaking
                </Badge>
              )}
              {!participant.isMicrophoneEnabled && (
                <Badge color="warning" size="xs">
                  Muted
                </Badge>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default ParticipantList;