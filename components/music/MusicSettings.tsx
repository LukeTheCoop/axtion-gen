import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import mainStyles from '../main.module.css';
import styles from './music.module.css';

// List of YouTube video IDs (without hardcoded titles)
const MUSIC_TRACK_IDS = [
  "F0cdbR5ognY",
  "NEnephbahLA",
  "fk4BbF7B29w",
  "Lrle0x_DHBM",
  "RSW8qYXyfRQ",
  "X8LUd51IuiA",
  "zUzyX34I7FM",
  "cbHkzwa0QmM",
  "wJUbXZc-etA",
  "0dT9siTP70Y",
  "U8F5G5wR1mk",
  "H58vbez_m4E",
  "BDHM8cyJQa8",
  "w1cUk-jt8go",
  "F5MKvQ3IDNs",
  "aMYxkySU8Lc",
  "2KsrI8PiShw",
  "7qqUiKPfV2Y",
  "WQR8fbPFJ9E",
  "kPa7bsKwL-c",
  "NHFq31K5_XY",
  "Cv6tuzHUuuk", // September by Earth, Wind & Fire
  "6ib9lk9gvGY"  // More popular songs
];

// YouTube API Key - in a real application, this should be stored securely on the server side
// For the purposes of this demo, we'll simulate fetching without an actual API key
// const YOUTUBE_API_KEY = 'YOUR_API_KEY_HERE';

// Default music settings
const DEFAULT_MUSIC_SETTINGS = {
  track_id: "Otv8MxIiv80",
  start_time: "0:00",
  volume: 0.2
};

interface MusicSettingsProps {
  addNotification: (message: string, type: 'success' | 'error' | 'info') => void;
  config: any;
}

interface MusicTrack {
  id: string;
  name: string | null;
  loading?: boolean;
}

export const MusicSettings = ({ addNotification, config }: MusicSettingsProps) => {
  const musicSettings = config?.music || DEFAULT_MUSIC_SETTINGS;
  const isLoading = !config;
  const [showMusicPlayer, setShowMusicPlayer] = useState(true);
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [selectedTrackId, setSelectedTrackId] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<string | number>('0:00');
  const [selectedStartTime, setSelectedStartTime] = useState<string | number | null>(null);
  const [trimAudio, setTrimAudio] = useState(0.0); // Default trim value
  const [volume, setVolume] = useState(0.2); // Default volume at 20%
  const [customUrl, setCustomUrl] = useState('');
  const [useCustomUrl, setUseCustomUrl] = useState(false);
  const [customVideoId, setCustomVideoId] = useState<string | null>(null);
  const [customVideoTitle, setCustomVideoTitle] = useState<string | null>(null);
  const [startTimeTimeout, setStartTimeTimeout] = useState<NodeJS.Timeout | null>(null);
  const [trimAudioTimeout, setTrimAudioTimeout] = useState<NodeJS.Timeout | null>(null);
  const [volumeTimeout, setVolumeTimeout] = useState<NodeJS.Timeout | null>(null);
  
  // Track information with fetched titles
  const [musicTracks, setMusicTracks] = useState<MusicTrack[]>(
    MUSIC_TRACK_IDS.map(id => ({ id, name: null, loading: true }))
  );
  
  // Get current track
  const currentTrack = musicTracks[currentTrackIndex];
  
  // Fetch video titles from YouTube
  useEffect(() => {
    const fetchVideoTitles = async () => {
      // In a real implementation, this would be a proper YouTube API call
      // For this demonstration, we're simulating title fetching
      try {
        // Create a copy of the tracks
        const updatedTracks = [...musicTracks];
        
        // For each track that doesn't have a name yet, fetch it
        for (let i = 0; i < updatedTracks.length; i++) {
          if (!updatedTracks[i].name) {
            const id = updatedTracks[i].id;
            
            // For a real implementation, use the YouTube API
            // For this demo, we'll use a fetch to the oEmbed endpoint which doesn't require API keys
            try {
              const response = await fetch(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${id}&format=json`);
              
              if (response.ok) {
                const data = await response.json();
                updatedTracks[i] = {
                  ...updatedTracks[i],
                  name: data.title,
                  loading: false
                };
              } else {
                // Fallback if we can't get the title
                updatedTracks[i] = {
                  ...updatedTracks[i],
                  name: `YouTube Video (ID: ${id})`,
                  loading: false
                };
              }
            } catch (error) {
              console.error('Error fetching video title:', error);
              // Fallback if we can't get the title
              updatedTracks[i] = {
                ...updatedTracks[i],
                name: `YouTube Video (ID: ${id})`,
                loading: false
              };
            }
            
            // Update the state after each video to show progress
            setMusicTracks([...updatedTracks]);
            
            // Small delay to prevent rate limiting
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        }
      } catch (error) {
        console.error('Error fetching video titles:', error);
        addNotification('Failed to load some video titles', 'error');
      }
    };
    
    fetchVideoTitles();
  }, []);
  
  // Use config music settings when they become available
  useEffect(() => {
    if (musicSettings && !isLoading) {
      setSelectedTrackId(musicSettings.track_id || DEFAULT_MUSIC_SETTINGS.track_id);
      
      // Handle start time - could be a number (seconds) from backend or a string (MM:SS) from UI
      if (musicSettings.start_time !== undefined) {
        setSelectedStartTime(musicSettings.start_time);
        
        // If start_time is a number, convert to MM:SS format for display in the input field
        if (typeof musicSettings.start_time === 'number') {
          const minutes = Math.floor(musicSettings.start_time / 60);
          const seconds = Math.floor(musicSettings.start_time % 60);
          const formattedTime = `${minutes}:${seconds.toString().padStart(2, '0')}`;
          setStartTime(formattedTime);
        } else {
          setStartTime(musicSettings.start_time);
        }
      } else {
        setSelectedStartTime(DEFAULT_MUSIC_SETTINGS.start_time);
        setStartTime(DEFAULT_MUSIC_SETTINGS.start_time);
      }
      
      setTrimAudio(musicSettings.trim_audio !== undefined ? parseFloat(musicSettings.trim_audio) : 0.0);
      setVolume(musicSettings.volume !== undefined ? musicSettings.volume : DEFAULT_MUSIC_SETTINGS.volume);
      
      // Check if this is a track from our list
      const trackIndex = MUSIC_TRACK_IDS.indexOf(musicSettings.track_id || '');
      if (trackIndex !== -1) {
        setCurrentTrackIndex(trackIndex);
        setUseCustomUrl(false);
      } else if (musicSettings.track_id) {
        // It's a custom URL
        setCustomVideoId(musicSettings.track_id);
        setCustomVideoTitle(musicSettings.custom_title || 'Custom YouTube Track');
        setUseCustomUrl(true);
      }
    }
  }, [musicSettings, isLoading]);
  
  // Handle next track
  const handleNextTrack = () => {
    const nextIndex = currentTrackIndex === musicTracks.length - 1 ? 0 : currentTrackIndex + 1;
    setCurrentTrackIndex(nextIndex);
  };
  
  // Handle previous track
  const handlePrevTrack = () => {
    const prevIndex = currentTrackIndex === 0 ? musicTracks.length - 1 : currentTrackIndex - 1;
    setCurrentTrackIndex(prevIndex);
  };
  
  // Handle start time change
  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStartTime = e.target.value;
    setStartTime(newStartTime);
    
    // Clear any existing timeout
    if (startTimeTimeout) {
      clearTimeout(startTimeTimeout);
    }
    
    // Immediately trigger a save with the new start time
    if (selectedTrackId) {
      const timeoutId = setTimeout(() => {
        console.log('Saving start time change:', newStartTime);
        saveTimeChange(newStartTime);
      }, 500);
      
      setStartTimeTimeout(timeoutId);
    }
  };
  
  // Handle volume change
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    
    // Clear any existing timeout
    if (volumeTimeout) {
      clearTimeout(volumeTimeout);
    }
    
    // Set a new timeout to save after 500ms of inactivity
    const timeoutId = setTimeout(() => {
      console.log('Saving volume change:', newVolume);
      saveVolumeChange(newVolume);
    }, 500);
    
    setVolumeTimeout(timeoutId);
  };
  
  // Handle trim audio change
  const handleTrimAudioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTrimAudio = parseFloat(e.target.value);
    setTrimAudio(newTrimAudio);
    
    // Clear any existing timeout
    if (trimAudioTimeout) {
      clearTimeout(trimAudioTimeout);
    }
    
    // Set a new timeout to save after 500ms of inactivity
    const timeoutId = setTimeout(() => {
      console.log('Saving trim audio change:', newTrimAudio);
      saveTrimAudioChange(newTrimAudio);
    }, 500);
    
    setTrimAudioTimeout(timeoutId);
  };
  
  // Handle custom URL change
  const handleCustomUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomUrl(e.target.value);
    
    // Try to extract video ID when URL changes
    const videoId = extractYouTubeId(e.target.value);
    if (videoId) {
      setCustomVideoId(videoId);
      
      // Try to fetch the title of the custom video
      fetchVideoTitle(videoId).then(title => {
        if (title) {
          setCustomVideoTitle(title);
          
          // Auto-select the track when we have a valid URL and title
          const trackId = videoId;
          const trackTitle = title || 'Custom YouTube track';
          
          // Update local state
          setSelectedTrackId(trackId);
          setSelectedStartTime(startTime);
          
          // Auto-save the selection
          setTimeout(() => {
            saveCustomTrack(trackId, trackTitle);
          }, 500);
        }
      });
    }
  };
  
  // Helper function to save custom track
  const saveCustomTrack = async (trackId: string, trackTitle: string) => {
    try {
      // Convert startTime to number, whether it's already a number or a string in MM:SS format
      let totalSeconds: number;
      if (typeof startTime === 'number') {
        totalSeconds = startTime;
      } else if (typeof startTime === 'string') {
        const timeComponents = startTime.split(':');
        const minutes = parseInt(timeComponents[0]) || 0;
        const seconds = parseInt(timeComponents[1]) || 0;
        totalSeconds = minutes * 60 + seconds;
      } else {
        totalSeconds = 0; // Default if unexpected type
      }
      
      const response = await fetch('http://localhost:8000/api/config/music', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          track_id: trackId,
          start_time: totalSeconds,
          trim_audio: trimAudio,
          volume: volume,
          custom_title: trackTitle
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update music settings');
      }
      
      const displayTitle = trackTitle.length > 30 ? trackTitle.substring(0, 30) + '...' : trackTitle;
      addNotification(`Music track "${displayTitle}" selected`, 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update music settings';
      addNotification(errorMessage, 'error');
    }
  };
  
  // Fetch a single video title
  const fetchVideoTitle = async (videoId: string): Promise<string | null> => {
    try {
      const response = await fetch(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`);
      
      if (response.ok) {
        const data = await response.json();
        return data.title;
      }
    } catch (error) {
      console.error('Error fetching video title:', error);
    }
    return null;
  };
  
  // Toggle between preset tracks and custom URL
  const toggleCustomUrl = () => {
    setUseCustomUrl(prev => !prev);
    if (!useCustomUrl && !customVideoId) {
      // If switching to custom URL and no ID set yet, clear the selection
      setSelectedTrackId(null);
      setSelectedStartTime(null);
    } else if (useCustomUrl && selectedTrackId !== customVideoId) {
      // If switching back to presets and the selection was a custom URL
      setSelectedTrackId(currentTrack.id);
    }
  };
  
  // Extract YouTube video ID from URL
  const extractYouTubeId = (url: string): string | null => {
    // Handle different YouTube URL formats
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    
    if (match && match[2].length === 11) {
      return match[2];
    }
    
    return null;
  };
  
  // Handle track selection
  const handleSelectTrack = async () => {
    let trackId: string;
    let trackTitle: string;
    
    if (useCustomUrl) {
      if (!customVideoId) {
        addNotification('Please enter a valid YouTube URL', 'error');
        return;
      }
      trackId = customVideoId;
      // Use URL as title if we don't have a proper title
      trackTitle = customVideoTitle || 'Custom YouTube track';
    } else {
      trackId = currentTrack.id;
      trackTitle = currentTrack.name || `YouTube Video (ID: ${currentTrack.id})`;
    }
    
    // Update local state
    setSelectedTrackId(trackId);
    setSelectedStartTime(startTime);
    
    // Convert startTime to number, whether it's already a number or a string in MM:SS format
    let totalSeconds: number;
    if (typeof startTime === 'number') {
      totalSeconds = startTime;
    } else if (typeof startTime === 'string') {
      const timeComponents = startTime.split(':');
      const minutes = parseInt(timeComponents[0]) || 0;
      const seconds = parseInt(timeComponents[1]) || 0;
      totalSeconds = minutes * 60 + seconds;
    } else {
      totalSeconds = 0; // Default if unexpected type
    }
    
    // Send to music endpoint with PUT instead of POST
    try {
      const response = await fetch('http://localhost:8000/api/config/music', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          track_id: trackId,
          start_time: totalSeconds,
          trim_audio: trimAudio,
          volume: volume,
          custom_title: useCustomUrl ? trackTitle : undefined
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update music settings');
      }
      
      const displayTitle = trackTitle.length > 30 ? trackTitle.substring(0, 30) + '...' : trackTitle;
      addNotification(`Music track "${displayTitle}" selected with start time ${startTime}`, 'success');
      
      // If this was a custom URL, store the title
      if (useCustomUrl) {
        setCustomVideoTitle(trackTitle);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update music settings';
      addNotification(errorMessage, 'error');
    }
  };
  
  // Display a shortened version of the track name
  const getShortTrackName = (name: string) => {
    return name.length > 40 ? name.substring(0, 40) + '...' : name;
  };
  
  // Get the currently displayed video ID
  const getCurrentVideoId = () => {
    if (useCustomUrl) {
      return customVideoId || '';
    }
    return currentTrack.id;
  };
  
  // Get the currently displayed video title
  const getCurrentVideoTitle = () => {
    if (useCustomUrl) {
      return customVideoTitle || 'Custom YouTube Track';
    }
    
    if (currentTrack.loading) {
      return 'Loading title...';
    }
    
    return currentTrack.name || `YouTube Video (ID: ${currentTrack.id})`;
  };
  
  // Function to save time change
  const saveTimeChange = async (newTime: string | number) => {
    try {
      // Convert newTime to number, whether it's already a number or a string in MM:SS format
      let totalSeconds: number;
      if (typeof newTime === 'number') {
        totalSeconds = newTime;
      } else if (typeof newTime === 'string') {
        const timeComponents = newTime.split(':');
        const minutes = parseInt(timeComponents[0]) || 0;
        const seconds = parseInt(timeComponents[1]) || 0;
        totalSeconds = minutes * 60 + seconds;
      } else {
        totalSeconds = 0; // Default if unexpected type
      }
      
      const response = await fetch('http://localhost:8000/api/config/music', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_time: totalSeconds
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save time');
      }
      
      const displayTime = typeof newTime === 'string' ? newTime : `${Math.floor(totalSeconds / 60)}:${(totalSeconds % 60).toString().padStart(2, '0')}`;
      addNotification(`Start time updated to ${displayTime}`, 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save time';
      console.error('Error saving time:', errorMessage);
      addNotification(errorMessage, 'error');
    }
  };
  
  // Function to save volume change
  const saveVolumeChange = async (newVolume: number) => {
    try {
      const response = await fetch('http://localhost:8000/api/config/music', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          volume: newVolume
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save volume');
      }
      
      addNotification(`Volume updated to ${Math.round(newVolume * 100)}%`, 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save volume';
      console.error('Error saving volume:', errorMessage);
      addNotification(errorMessage, 'error');
    }
  };
  
  // Function to save trim audio change
  const saveTrimAudioChange = async (newTrimAudio: number) => {
    try {
      const response = await fetch('http://localhost:8000/api/config/music', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          trim_audio: newTrimAudio
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save trim audio');
      }
      
      addNotification(`Trim audio updated to ${newTrimAudio.toFixed(1)}s`, 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save trim audio';
      console.error('Error saving trim audio:', errorMessage);
      addNotification(errorMessage, 'error');
    }
  };
  
  // Function to save current settings
  const saveCurrentSettings = async () => {
    if (!selectedTrackId) return;
    
    // Convert startTime to number, whether it's already a number or a string in MM:SS format
    let totalSeconds: number;
    if (typeof startTime === 'number') {
      totalSeconds = startTime;
    } else if (typeof startTime === 'string') {
      const timeComponents = startTime.split(':');
      const minutes = parseInt(timeComponents[0]) || 0;
      const seconds = parseInt(timeComponents[1]) || 0;
      totalSeconds = minutes * 60 + seconds;
    } else {
      totalSeconds = 0; // Default if unexpected type
    }
    
    console.log('Auto-save triggered with:', { 
      track_id: selectedTrackId, 
      start_time: totalSeconds, 
      trim_audio: trimAudio,
      volume: volume 
    });
    
    try {
      const musicSettingsData = {
        track_id: selectedTrackId,
        start_time: totalSeconds,
        trim_audio: trimAudio,
        volume: volume,
        ...(useCustomUrl && customVideoTitle ? { custom_title: customVideoTitle } : {})
      };
      
      // Save music settings to the API
      const response = await fetch('http://localhost:8000/api/config/music', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(musicSettingsData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save music settings');
      }
      
      console.log('Auto-save successful');
      // Silent save, no need for notification every time
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save music settings';
      console.error('Auto-save error:', errorMessage);
      // We don't want to spam notifications on auto-save, so only log the error
    }
  };
  
  // Add auto-selection when browsing through tracks
  useEffect(() => {
    if (!useCustomUrl && !isLoading && currentTrack && currentTrack.id && !currentTrack.loading) {
      // Auto-select the current track when browsing
      setSelectedTrackId(currentTrack.id);
      
      // Save the selection after a short delay
      const timeout = setTimeout(() => {
        handleSelectTrack();
      }, 1000);
      
      return () => clearTimeout(timeout);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentTrackIndex, currentTrack?.id, currentTrack?.loading, isLoading, useCustomUrl]);
  
  // Implementing auto-save for settings changes
  useEffect(() => {
    if (!isLoading && selectedTrackId) {
      // Create a timeout to save changes after a brief delay
      const timeout = setTimeout(() => {
        saveCurrentSettings();
      }, 1000);
      
      return () => clearTimeout(timeout);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [volume, startTime, trimAudio, selectedTrackId, isLoading]);
  
  // Clean up timeouts when component unmounts
  useEffect(() => {
    return () => {
      if (startTimeTimeout) clearTimeout(startTimeTimeout);
      if (trimAudioTimeout) clearTimeout(trimAudioTimeout);
      if (volumeTimeout) clearTimeout(volumeTimeout);
    };
  }, [startTimeTimeout, trimAudioTimeout, volumeTimeout]);
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.5 }}
      className={`${mainStyles.container} h-full flex flex-col`}
      style={{ '--gradient-from': '#F472B6', '--gradient-to': '#EC4899' } as React.CSSProperties}
    >
      <h2 className={mainStyles.heading}>
        Background Music
      </h2>
      
      <div className="flex flex-col flex-grow space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-300 font-medium">Choose Your Soundtrack</span>
          <button 
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200 ${
              showMusicPlayer ? 
              'bg-gradient-to-r from-pink-500 to-rose-500 text-white' : 
              'bg-slate-700 text-gray-400 hover:bg-slate-600 hover:text-gray-300'
            }`}
            onClick={() => setShowMusicPlayer(!showMusicPlayer)}
          >
            {showMusicPlayer ? 'Hide Player' : 'Show Player'}
          </button>
        </div>
        
        <div className={styles.sourceToggle}>
          <button
            className={`${styles.sourceToggleBtn} ${!useCustomUrl ? styles.activeSourceToggleBtn : ''}`}
            onClick={() => useCustomUrl && toggleCustomUrl()}
          >
            Browse Library
          </button>
          <button
            className={`${styles.sourceToggleBtn} ${useCustomUrl ? styles.activeSourceToggleBtn : ''}`}
            onClick={() => !useCustomUrl && toggleCustomUrl()}
          >
            Custom URL
          </button>
        </div>
        
        {selectedTrackId && (
          <div className={styles.selectedTrack}>
            <p className={styles.selectedTrackText}>
              <span className="font-semibold">Selected:</span> {useCustomUrl && customVideoTitle 
                ? getShortTrackName(customVideoTitle) 
                : (musicTracks.find(track => track.id === selectedTrackId)?.name 
                    ? getShortTrackName(musicTracks.find(track => track.id === selectedTrackId)!.name!) 
                    : 'Loading title...')}
              {selectedStartTime && (
                <span className="ml-2 text-pink-200/80">
                  (Start at {selectedStartTime})
                </span>
              )}
            </p>
          </div>
        )}
        
        <AnimatePresence>
          {showMusicPlayer && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="flex-grow flex flex-col space-y-4"
            >
              {useCustomUrl && (
                <div className={styles.customUrlContainer}>
                  <label htmlFor="customUrl" className="text-sm font-medium text-pink-300">YouTube URL:</label>
                  <input
                    id="customUrl"
                    type="text"
                    value={customUrl}
                    onChange={handleCustomUrlChange}
                    placeholder="https://www.youtube.com/watch?v=..."
                    className={styles.customUrlInput}
                  />
                  <p className="text-xs text-pink-200/70 mt-1">
                    Enter any YouTube video URL to use as background music
                  </p>
                  
                  {customVideoId && (
                    <div className="mt-3 text-xs text-green-300">
                      <p>Custom track ready: {customVideoTitle || 'Custom YouTube Track'}</p>
                      <p className="italic mt-1">Settings will auto-save after changes</p>
                    </div>
                  )}
                </div>
              )}
              
              <div className={styles.playerWrapper}>
                <iframe 
                  className={styles.playerIframe}
                  src={`https://www.youtube.com/embed/${getCurrentVideoId()}?autoplay=0`}
                  title={`YouTube music player - ${getCurrentVideoTitle()}`}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              </div>
              
              <div className={styles.trackInfo}>
                <h3 className="text-lg font-semibold text-pink-300 mb-1">
                  {currentTrack.loading ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-pink-200" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Loading title...
                    </span>
                  ) : getShortTrackName(getCurrentVideoTitle())}
                </h3>
                {!useCustomUrl && (
                  <p className="text-sm text-pink-200/80">
                    Track {currentTrackIndex + 1} of {musicTracks.length}
                  </p>
                )}
              </div>
              
              <div className={styles.startTimeContainer}>
                <label htmlFor="startTime" className="text-sm font-medium text-pink-300">Start Time (mm:ss):</label>
                <input
                  id="startTime"
                  type="text"
                  value={startTime}
                  onChange={handleStartTimeChange}
                  placeholder="0:00"
                  pattern="[0-9]*:[0-5][0-9]"
                  className={styles.startTimeInput}
                />
                <p className="text-xs text-pink-200/70 mt-1">
                  Enter the time in the track where you want the music to begin
                </p>
              </div>
              
              <div className={styles.volumeContainer}>
                <label htmlFor="volume" className="text-sm font-medium text-pink-300">Volume: {Math.round(volume * 100)}%</label>
                <input
                  id="volume"
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={volume}
                  onChange={handleVolumeChange}
                  className={styles.volumeSlider}
                />
                <p className="text-xs text-pink-200/70 mt-1">
                  Adjust the volume level for the background music
                </p>
              </div>
              
              <div className={styles.volumeContainer}>
                <label htmlFor="trimAudio" className="text-sm font-medium text-pink-300">Trim Audio: {trimAudio.toFixed(1)}s</label>
                <input
                  id="trimAudio"
                  type="range"
                  min="0"
                  max="60"
                  step="0.5"
                  value={trimAudio}
                  onChange={handleTrimAudioChange}
                  className={styles.volumeSlider}
                />
                <p className="text-xs text-pink-200/70 mt-1">
                  Adjust how much to trim from the audio (in seconds)
                </p>
              </div>
              
              {!useCustomUrl && (
                <div className="flex flex-col space-y-3 mt-auto">
                  <div className={styles.controlButtons}>
                    <button
                      onClick={handlePrevTrack}
                      className={styles.navButton}
                      aria-label="Previous track"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                    
                    <div className="text-center text-sm text-pink-300">
                      {currentTrack.loading ? (
                        <span className="flex items-center justify-center">
                          <svg className="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Loading...
                        </span>
                      ) : (
                        <span>Browse through tracks</span>
                      )}
                    </div>
                    
                    <button
                      onClick={handleNextTrack}
                      className={styles.navButton}
                      aria-label="Next track"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                  
                  <div className="text-center text-xs text-pink-200/60 italic mt-2">
                    Settings auto-save when you change volume, start time, or select a track
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}; 