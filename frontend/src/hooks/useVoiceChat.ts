import { useState, useCallback, useEffect } from 'react';
import { Room, RoomEvent, Participant, Track, RemoteTrack } from 'livekit-client';

export const useVoiceChat = () => {
  const [room, setRoom] = useState<Room | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);

  const connectToRoom = useCallback(async (url: string, token: string) => {
    try {
      setError(null);
      const newRoom = new Room();
      
      // Set up event listeners
      newRoom.on(RoomEvent.ParticipantConnected, (participant) => {
        setParticipants(prev => {
          // Check if participant already exists to avoid duplicates
          if (prev.some(p => p.sid === participant.sid)) {
            return prev;
          }
          return [...prev, participant];
        });
      });
      
      newRoom.on(RoomEvent.ParticipantDisconnected, (participant) => {
        setParticipants(prev => prev.filter(p => p.sid !== participant.sid));
      });
      
      newRoom.on(RoomEvent.Disconnected, () => {
        setIsConnected(false);
        setParticipants([]);
      });
      
      // Listen for remote audio tracks
      newRoom.on(RoomEvent.TrackSubscribed, (track: RemoteTrack, publication, participant) => {
        if (track.kind === Track.Kind.Audio) {
          const audioElement = track.attach();
          // Append audio element to document body
          document.body.appendChild(audioElement);
        }
      });
      
      // Listen for speaking events
      newRoom.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
        // Update participants with speaking status
        setParticipants(prev => {
          return prev.map(participant => {
            const isSpeaking = speakers.some(speaker => speaker.sid === participant.sid);
            // Update speaking status for this participant
            return Object.assign(participant, { isSpeaking });
          });
        });
      });
      
      // Connect to the room
      await newRoom.connect(url, token);
      
      // Enable microphone only (no camera)
      await newRoom.localParticipant.setMicrophoneEnabled(true);
      
      setRoom(newRoom);
      setIsConnected(true);
      
      // Add local participant to the participants list
      const allParticipants = [newRoom.localParticipant, ...Array.from(newRoom.remoteParticipants.values())];
      setParticipants(allParticipants);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect to room');
      setIsConnected(false);
    }
  }, []);

  const disconnectFromRoom = useCallback(async () => {
    if (room) {
      // Clean up audio elements
      room.remoteParticipants.forEach(participant => {
        participant.trackPublications.forEach(publication => {
          if (publication.track) {
            publication.track.detach();
          }
        });
      });
      
      await room.disconnect();
      setRoom(null);
      setIsConnected(false);
      setParticipants([]);
    }
  }, [room]);

  const toggleMute = useCallback(async () => {
    if (room) {
      const isEnabled = room.localParticipant.isMicrophoneEnabled;
      await room.localParticipant.setMicrophoneEnabled(!isEnabled);
      setIsMuted(!isEnabled);
    }
  }, [room]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  return {
    room,
    isConnected,
    isMuted,
    error,
    participants,
    connectToRoom,
    disconnectFromRoom,
    toggleMute
  };
};