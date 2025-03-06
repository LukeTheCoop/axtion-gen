import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';

// Default pause factor
export const DEFAULT_PAUSE_FACTOR = 0.25;

// PauseFactorSettings props interface
interface PauseFactorSettingsProps {
  addNotification: (message: string, type: 'success' | 'error' | 'info') => void;
  config: any;
}

export const PauseFactorSettings = ({ addNotification, config }: PauseFactorSettingsProps) => {
  const [pauseFactor, setPauseFactor] = useState(config?.audio?.pause_factor || DEFAULT_PAUSE_FACTOR);
  const isLoading = !config;
  const [saveTimeout, setSaveTimeout] = useState<NodeJS.Timeout | null>(null);
  
  // Update pause factor when config changes
  useEffect(() => {
    if (config && config.audio && config.audio.pause_factor !== undefined) {
      setPauseFactor(config.audio.pause_factor);
    }
  }, [config]);
  
  // Auto-save when pause factor changes
  useEffect(() => {
    if (isLoading) return;
    
    // Clear any existing timeout
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }
    
    // Set a new timeout to save after 500ms of inactivity
    const timeout = setTimeout(() => {
      savePauseFactor();
    }, 500);
    
    setSaveTimeout(timeout);
    
    // Cleanup on unmount
    return () => {
      if (saveTimeout) {
        clearTimeout(saveTimeout);
      }
    };
  }, [pauseFactor]);
  
  const savePauseFactor = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/config/audio', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pause_factor: pauseFactor
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update pause factor');
      }
      
      addNotification('Pause factor updated', 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update pause factor';
      addNotification(errorMessage, 'error');
    }
  };
  
  const handlePauseFactorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    setPauseFactor(value);
  };
  
  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      className={`${mainStyles.container} p-4`}
      style={{ '--gradient-from': '#2563EB', '--gradient-to': '#4338CA' } as React.CSSProperties}
    >
      <h3 className={mainStyles.heading}>Video Timing Settings</h3>
      <div className="space-y-3 mt-3">
        <div>
          <div className="flex items-center justify-between mb-1">
            <label htmlFor="pauseFactor" className="block text-sm font-medium text-gray-300">
              Pause Factor
            </label>
            <span className="text-sm text-gray-400 font-medium">
              {pauseFactor.toFixed(2)}
            </span>
          </div>
          <div className="flex items-center">
            <input
              id="pauseFactor"
              type="range"
              min="0"
              max="2"
              step="0.01"
              value={pauseFactor}
              onChange={handlePauseFactorChange}
              className="w-full accent-blue-500 bg-slate-700 h-2 rounded-lg appearance-none cursor-pointer"
            />
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0</span>
            <span>1</span>
            <span>2</span>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Controls pause duration between video clips (default: 0.25)
          </p>
        </div>
        
        <p className="text-xs text-blue-300/70 italic mt-2">
          Settings are automatically saved when changed
        </p>
      </div>
    </motion.div>
  );
}; 