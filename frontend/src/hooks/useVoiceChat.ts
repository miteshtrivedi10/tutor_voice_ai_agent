import { useState, useCallback } from 'react';
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
        setParticipants(prev => [...prev, participant]);
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
      
      // Connect to the room
      await newRoom.connect(url, token);
      
      // Enable microphone only (no camera)
      await newRoom.localParticipant.setMicrophoneEnabled(true);
      
      setRoom(newRoom);
      setIsConnected(true);
      setParticipants(Array.from(newRoom.remoteParticipants.values()));
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