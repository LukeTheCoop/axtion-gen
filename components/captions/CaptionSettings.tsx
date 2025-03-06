import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';
import { NotificationType } from '../ui/Toast';

// Caption style options
interface CaptionStyle {
  name: string;
  label: string;
  description: string;
  previewStyle?: React.CSSProperties;
}

const CAPTION_STYLES: CaptionStyle[] = [
  {
    name: 'default',
    label: 'Default',
    description: 'White text on semi-transparent black background, using Helvetica font (35px mobile, 45px landscape)',
    previewStyle: {
      color: 'white',
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      padding: '8px 12px',
      borderRadius: '4px',
      fontFamily: 'Helvetica, Arial, sans-serif',
      fontSize: '16px',
      textAlign: 'center',
      maxWidth: '100%'
    }
  },
  {
    name: 'modern',
    label: 'Modern',
    description: 'Larger SF Compact Text Medium font (40px mobile, 50px landscape) with higher positioning and more opaque background',
    previewStyle: {
      color: 'white',
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      padding: '10px 14px',
      borderRadius: '6px',
      fontFamily: 'SF Pro Text, Segoe UI, system-ui, sans-serif',
      fontSize: '17px',
      fontWeight: 500,
      textAlign: 'center',
      maxWidth: '100%'
    }
  },
  {
    name: 'vibrant',
    label: 'Vibrant',
    description: 'Bold yellow text on semi-transparent blue background, using Avenir font (38px mobile, 48px landscape)',
    previewStyle: {
      color: '#FFEB3B',
      backgroundColor: 'rgba(25, 118, 210, 0.8)',
      padding: '8px 14px',
      borderRadius: '5px',
      fontFamily: 'Avenir, Montserrat, sans-serif',
      fontSize: '16px',
      fontWeight: 'bold',
      textAlign: 'center',
      maxWidth: '100%'
    }
  }
];

interface CaptionSettingsProps {
  addNotification: (message: string, type: NotificationType) => void;
  config: any;
}

export const CaptionSettings = ({ addNotification, config }: CaptionSettingsProps) => {
  // Caption settings state
  const [captionsEnabled, setCaptionsEnabled] = useState(false);
  const [activeCaptionStyle, setActiveCaptionStyle] = useState<string>(CAPTION_STYLES[0].name);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // Use config when available
  useEffect(() => {
    if (config) {
      // Check if captions are enabled
      if (config.captions && config.captions.enabled !== undefined) {
        setCaptionsEnabled(config.captions.enabled);
      }
      
      // Check for active caption style
      if (config.captions && config.captions.style) {
        setActiveCaptionStyle(config.captions.style);
      }
      
      setIsLoading(false);
    }
  }, [config]);
  
  // Toggle captions enabled/disabled
  const toggleCaptionsEnabled = async () => {
    setIsSaving(true);
    try {
      const response = await fetch('http://localhost:8000/api/config/captions', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          enabled: !captionsEnabled
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update caption status');
      }
      
      setCaptionsEnabled(!captionsEnabled);
      addNotification(`Captions ${!captionsEnabled ? 'enabled' : 'disabled'} successfully`, 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update caption status';
      addNotification(errorMessage, 'error');
    } finally {
      setIsSaving(false);
    }
  };
  
  // Set active caption style
  const setCaptionStyle = async (styleName: string) => {
    if (styleName === activeCaptionStyle) return;
    
    setIsSaving(true);
    try {
      const response = await fetch('http://localhost:8000/api/config/captions', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          style: styleName
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update caption style');
      }
      
      setActiveCaptionStyle(styleName);
      addNotification('Caption style updated successfully', 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update caption style';
      addNotification(errorMessage, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center py-4">
          <div className="h-8 w-8 border-3 border-t-transparent border-purple-500 rounded-full animate-spin"></div>
          <div className="ml-3 text-purple-300 font-medium text-sm">Loading caption settings...</div>
        </div>
      ) : (
        <>
          {/* Enable/Disable Captions Toggle */}
          <div className="flex items-center justify-between bg-slate-800/30 p-3 rounded-lg">
            <div>
              <label className="text-gray-200 font-medium">Captions</label>
              <p className="text-xs text-gray-400 mt-1">Enable or disable captions on videos</p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`relative w-14 h-7 transition-colors rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 ${captionsEnabled ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gray-600'}`}
              onClick={toggleCaptionsEnabled}
              disabled={isSaving}
            >
              <span
                className={`absolute left-1 top-1 bg-white w-5 h-5 rounded-full transition-transform duration-200 ${
                  captionsEnabled ? 'transform translate-x-7' : ''
                }`}
              />
            </motion.button>
          </div>
          
          {/* Caption Style Selection (only shown if captions are enabled) */}
          {captionsEnabled && (
            <div className="mt-4">
              <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                Caption Style
              </label>
              
              {/* Style Selection Tabs */}
              <div className="flex bg-slate-900/30 rounded-xl p-1 mt-2">
                {CAPTION_STYLES.map((style) => (
                  <button
                    key={style.name}
                    onClick={() => setCaptionStyle(style.name)}
                    disabled={isSaving}
                    className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                      activeCaptionStyle === style.name
                        ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                        : 'text-gray-400 hover:text-gray-100'
                    }`}
                  >
                    {style.label}
                  </button>
                ))}
              </div>
              
              {/* Style Preview */}
              <div className="mt-4 mb-2 p-4 bg-black/30 rounded-lg flex justify-center items-center h-24">
                <div style={CAPTION_STYLES.find(s => s.name === activeCaptionStyle)?.previewStyle}>
                  Sample caption text
                </div>
              </div>
              
              {/* Style Description */}
              <div className="text-xs text-gray-400 italic mt-2">
                {CAPTION_STYLES.find(s => s.name === activeCaptionStyle)?.description}
              </div>
              
              {isSaving && (
                <div className="mt-2 text-xs text-purple-300 flex items-center">
                  <div className={`${mainStyles.loading} w-3 h-3 mr-2`}></div>
                  Saving settings...
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}; 