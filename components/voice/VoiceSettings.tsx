import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';

// Voice settings default values
export const DEFAULT_VOICE_SETTINGS = {
  voice_id: "AvUYKSeryCcU2BHSM8x7",
  model_id: "eleven_flash_v2",
  stability: 0.5,
  similarity_boost: 0.75,
  speed: 1.15,
  use_speaker_boost: true,
  output_format: "mp3_44100_128"
};

const VOICE_OPTIONS = [
  { id: "AvUYKSeryCcU2BHSM8x7", name: "Default Voice" },
  { id: "LcfcDJNUP1GQjkzn1xUU", name: "Professional Male" },
  { id: "kgG9JYzoq3X4JEzFsieS", name: "Professional Female" },
  { id: "ZQe5zn9AaKMFujKjmjbS", name: "Narrative" },
  { id: "EOXSTnQ6c4FMBKLUZkQn", name: "Emotional" },
  { id: "custom", name: "Custom Voice ID" }
];

const MODEL_OPTIONS = [
  { id: "eleven_flash_v2", name: "Flash V2 (Fastest)" },
  { id: "eleven_multilingual_v2", name: "Multilingual V2" },
  { id: "eleven_turbo_v2", name: "Turbo V2" }
];

const OUTPUT_FORMAT_OPTIONS = [
  { id: "mp3_44100_128", name: "MP3 (44.1kHz, 128kbps)" },
  { id: "mp3_44100_192", name: "MP3 (44.1kHz, 192kbps)" },
  { id: "pcm_16000", name: "PCM (16kHz)" },
  { id: "pcm_22050", name: "PCM (22.05kHz)" },
  { id: "pcm_24000", name: "PCM (24kHz)" }
];

interface VoiceSettingsProps {
  addNotification: (message: string, type: 'success' | 'error' | 'info') => void;
  config: any;
}

export const VoiceSettings = ({ addNotification, config }: VoiceSettingsProps) => {
  const voiceSettings = config?.audio?.voice || DEFAULT_VOICE_SETTINGS;
  const isLoading = !config;
  
  // Voice settings state
  const [voiceSettingsState, setVoiceSettingsState] = useState(voiceSettings);
  const [selectedVoiceOption, setSelectedVoiceOption] = useState(
    voiceSettings.voice_id
  );
  const [customVoiceId, setCustomVoiceId] = useState("");
  const [saveTimeout, setSaveTimeout] = useState<NodeJS.Timeout | null>(null);
  
  // Update settings when config is loaded
  useEffect(() => {
    if (config && config.audio && config.audio.voice) {
      setVoiceSettingsState(config.audio.voice);
      // Determine if the voice_id is from our predefined options or if it's a custom one
      const isPresetVoice = VOICE_OPTIONS.some(voice => voice.id === config.audio.voice.voice_id && voice.id !== 'custom');
      
      if (isPresetVoice) {
        setSelectedVoiceOption(config.audio.voice.voice_id);
      } else {
        // It's a custom voice ID
        setSelectedVoiceOption('custom');
        setCustomVoiceId(config.audio.voice.voice_id);
        console.log('Initialized with custom voice ID:', config.audio.voice.voice_id);
      }
    } else if (config) {
      // If config exists but audio.voice doesn't, use default settings
      console.log('Voice settings not found in config, using defaults');
      setVoiceSettingsState(DEFAULT_VOICE_SETTINGS);
      setSelectedVoiceOption(DEFAULT_VOICE_SETTINGS.voice_id);
    }
  }, [config]);

  // Auto-save when settings change
  useEffect(() => {
    if (isLoading) return;
    
    // Clear any existing timeout
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }
    
    // Set a new timeout to save after 1 second of inactivity
    const timeout = setTimeout(() => {
      saveVoiceSettings();
    }, 1000);
    
    setSaveTimeout(timeout);
    
    // Cleanup on unmount
    return () => {
      if (saveTimeout) {
        clearTimeout(saveTimeout);
      }
    };
  }, [voiceSettingsState]);

  const saveVoiceSettings = async () => {
    // Don't save if we have a custom voice option selected but no ID
    if (selectedVoiceOption === 'custom' && !customVoiceId) {
      return;
    }
    
    // Log voice settings for debugging
    console.log('Saving voice settings:', JSON.stringify(voiceSettingsState, null, 2));
    
    try {
      const response = await fetch('http://localhost:8000/api/config/voice', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(voiceSettingsState),
      });

      if (!response.ok) {
        throw new Error('Failed to update audio settings');
      }
      
      addNotification('Voice settings saved', 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update voice settings';
      console.error('Voice settings update error:', error);
      addNotification(errorMessage, 'error');
    }
  };
  
  const handleVoiceSettingChange = (field: keyof typeof DEFAULT_VOICE_SETTINGS, value: any) => {
    setVoiceSettingsState((prev: typeof DEFAULT_VOICE_SETTINGS) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleVoiceOptionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOption = e.target.value;
    setSelectedVoiceOption(selectedOption);
    
    if (selectedOption !== 'custom') {
      handleVoiceSettingChange('voice_id', selectedOption);
    } else if (customVoiceId) {
      // If custom is selected and we already have a custom ID, use it
      handleVoiceSettingChange('voice_id', customVoiceId);
    } else {
      // If custom is selected but we don't have a custom ID yet, initialize with empty string
      // This ensures the backend knows we want a custom ID even if it's not set yet
      handleVoiceSettingChange('voice_id', '');
    }
  };
  
  const handleCustomVoiceIdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCustomVoiceId(value);
    
    // Update the actual voice_id in settings
    if (selectedVoiceOption === 'custom') {
      handleVoiceSettingChange('voice_id', value);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.5 }}
      className={mainStyles.container}
      style={{ '--gradient-from': '#60A5FA', '--gradient-to': '#34D399' } as React.CSSProperties}
    >
      <h2 className={mainStyles.heading}>
        Voice Settings
      </h2>
      
      <div className="space-y-6">
        {/* Voice ID */}
        <div>
          <label className={mainStyles.label} style={{ '--label-color': '#34D399' } as React.CSSProperties}>Voice</label>
          <select
            value={selectedVoiceOption}
            onChange={handleVoiceOptionChange}
            className={mainStyles.select}
          >
            {VOICE_OPTIONS.map(voice => (
              <option key={voice.id} value={voice.id} className="bg-slate-800">
                {voice.name}
              </option>
            ))}
          </select>
          
          {selectedVoiceOption === 'custom' && (
            <div className="mt-2">
              <input
                type="text"
                value={customVoiceId}
                onChange={handleCustomVoiceIdChange}
                placeholder="Enter custom voice ID..."
                className={`${mainStyles.input} ${!customVoiceId && 'border-red-400/60'}`}
                style={{ '--focus-color': '#34D399' } as React.CSSProperties}
              />
              {!customVoiceId ? (
                <p className="text-xs text-red-400 mt-1">
                  Please enter a valid ElevenLabs voice ID
                </p>
              ) : (
                <p className="text-xs text-blue-300/80 mt-1">
                  Using custom ElevenLabs voice ID: {customVoiceId.substring(0, 8)}...
                </p>
              )}
            </div>
          )}
        </div>
        
        {/* Model ID */}
        <div>
          <label className={mainStyles.label} style={{ '--label-color': '#34D399' } as React.CSSProperties}>Model</label>
          <select
            value={voiceSettingsState.model_id}
            onChange={(e) => handleVoiceSettingChange('model_id', e.target.value)}
            className={mainStyles.select}
          >
            {MODEL_OPTIONS.map(model => (
              <option key={model.id} value={model.id} className="bg-slate-800">
                {model.name}
              </option>
            ))}
          </select>
        </div>
        
        {/* Stability Slider */}
        <div>
          <label className={mainStyles.label} style={{ '--label-color': '#34D399' } as React.CSSProperties}>
            Stability: {voiceSettingsState.stability.toFixed(2)}
          </label>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">0.0</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={voiceSettingsState.stability}
              onChange={(e) => handleVoiceSettingChange('stability', parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <span className="text-xs text-gray-400">1.0</span>
          </div>
        </div>
        
        {/* Similarity Boost Slider */}
        <div>
          <label className={mainStyles.label} style={{ '--label-color': '#34D399' } as React.CSSProperties}>
            Similarity Boost: {voiceSettingsState.similarity_boost.toFixed(2)}
          </label>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">0.0</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={voiceSettingsState.similarity_boost}
              onChange={(e) => handleVoiceSettingChange('similarity_boost', parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <span className="text-xs text-gray-400">1.0</span>
          </div>
        </div>
        
        {/* Speed Slider */}
        <div>
          <label className={mainStyles.label} style={{ '--label-color': '#34D399' } as React.CSSProperties}>
            Speed: {voiceSettingsState.speed.toFixed(2)}x
          </label>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">0.5x</span>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.05"
              value={voiceSettingsState.speed}
              onChange={(e) => handleVoiceSettingChange('speed', parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <span className="text-xs text-gray-400">2.0x</span>
          </div>
        </div>
        
        {/* Speaker Boost Toggle */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="speakerBoost"
            checked={voiceSettingsState.use_speaker_boost}
            onChange={(e) => handleVoiceSettingChange('use_speaker_boost', e.target.checked)}
            className="w-5 h-5 bg-slate-900 border-slate-600 rounded focus:ring-blue-500 text-blue-500"
          />
          <label htmlFor="speakerBoost" className="ml-2 text-md font-medium text-blue-300">
            Speaker Boost
          </label>
        </div>
        
        {/* Output Format */}
        <div>
          <label className={mainStyles.label} style={{ '--label-color': '#34D399' } as React.CSSProperties}>Output Format</label>
          <select
            value={voiceSettingsState.output_format}
            onChange={(e) => handleVoiceSettingChange('output_format', e.target.value)}
            className={mainStyles.select}
          >
            {OUTPUT_FORMAT_OPTIONS.map(format => (
              <option key={format.id} value={format.id} className="bg-slate-800">
                {format.name}
              </option>
            ))}
          </select>
        </div>
        
        {/* Note about auto-saving */}
        <p className="text-sm text-blue-300/70 italic">
          Settings are automatically saved when changed
        </p>
      </div>
    </motion.div>
  );
}; 