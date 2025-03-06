'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './creator.module.css';
import mainStyles from '../../components/main.module.css';
import { QUOTES } from './quotes';
import { ToastContainer } from '../../components/ui/Toast';
import { LoadingOverlay, SuccessOverlay, SelectionNotification } from '../../components/ui/Overlay';
import { VoiceSettings } from '../../components/voice/VoiceSettings';
import { PauseFactorSettings } from '../../components/video-settings/PauseFactorSettings';
import { PromptManager } from '../../components/prompt-manager/PromptManager';
import { ContentCreator } from '../../components/content-creator/ContentCreator';
import { ContentForm } from '../../components/content-form/ContentForm';
import { MusicSettings } from '../../components/music/MusicSettings';
import { CaptionSettings } from '../../components/captions/CaptionSettings';
import { NotificationType } from '../../components/ui/Toast';

// Voice settings constants now moved to VoiceSettings component
// We're keeping them here for reference only
const OUTPUT_FORMAT_OPTIONS = [
  { id: "mp3_44100_128", name: "MP3 (44.1kHz, 128kbps)" },
  { id: "mp3_44100_192", name: "MP3 (44.1kHz, 192kbps)" },
  { id: "pcm_16000", name: "PCM (16kHz)" },
  { id: "pcm_22050", name: "PCM (22.05kHz)" },
  { id: "pcm_24000", name: "PCM (24kHz)" }
];

// Removed duplicate Toast and type declarations since we're importing them from components

export default function Creator() {
  // Toast notifications state
  const [notifications, setNotifications] = useState<{ id: string; message: string; type: NotificationType }[]>([]);
  
  // Content creation states
  const [mothership, setMothership] = useState('');
  const [genre, setGenre] = useState('');
  const [videoFormat, setVideoFormat] = useState('mobile');
  const [prompt, setPrompt] = useState('');
  
  // Toggle advanced editor visibility
  const [showAdvancedEditor, setShowAdvancedEditor] = useState(false);
  
  // For saved content handling
  const [hasSavedMothership, setHasSavedMothership] = useState(false);
  const [hasSavedPrompt, setHasSavedPrompt] = useState(false);
  const [isLoadingLastMothership, setIsLoadingLastMothership] = useState(false);
  const [isLoadingLastPrompt, setIsLoadingLastPrompt] = useState(false);
  const [isCheckingForSavedContent, setIsCheckingForSavedContent] = useState(true);
  
  // Config state
  const [config, setConfig] = useState<any>(null);
  const [isLoadingConfig, setIsLoadingConfig] = useState(true);
  
  // Loading and success states
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  
  // Check for saved content on mount
  useEffect(() => {
    const checkForSavedContent = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/config/memory');
        if (response.ok) {
          const data = await response.json();
          setHasSavedMothership(!!data.last_mothership);
          setHasSavedPrompt(!!data.last_prompt);
        } else {
          throw new Error('Failed to fetch saved content');
        }
      } catch (error) {
        console.error('Error checking for saved content:', error);
      } finally {
        setIsCheckingForSavedContent(false);
      }
    };
    
    checkForSavedContent();
  }, []);

  // Fetch config on mount
  useEffect(() => {
    const fetchConfig = async () => {
      setIsLoadingConfig(true);
      try {
        console.log('Fetching configuration...');
        const response = await fetch('http://localhost:8000/api/config');
        if (!response.ok) {
          throw new Error('Failed to fetch configuration');
        }
        
        const data = await response.json();
        console.log('Configuration loaded successfully');
        setConfig(data);
      } catch (error) {
        console.error('Error fetching configuration:', error);
        addNotification('Failed to load configuration', 'error');
      } finally {
        setIsLoadingConfig(false);
      }
    };
    
    fetchConfig();
  }, []);

  // Add a notification
  const addNotification = (message: string, type: NotificationType) => {
    // Create a more unique ID by combining timestamp with a random number
    const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setNotifications(prev => [...prev, { id, message, type }]);
  };
  
  // Remove a notification
  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };

  const handleSuccessComplete = () => {
    setIsSuccess(false);
  };

  const handleShowNotification = () => {
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3500);
  };
  
  const loadLastMothership = async () => {
    setIsLoadingLastMothership(true);
    try {
      const response = await fetch('http://localhost:8000/api/config/memory');
      
      if (!response.ok) {
        throw new Error('Failed to load last mothership content');
      }
      
      const data = await response.json();
      
      if (data.last_mothership) {
        setMothership(data.last_mothership);
        addNotification('Last mothership content loaded', 'success');
      } else {
        throw new Error('No saved mothership content found');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load last mothership';
      addNotification(errorMessage, 'error');
    } finally {
      setIsLoadingLastMothership(false);
    }
  };
  
  const loadLastPrompt = async () => {
    setIsLoadingLastPrompt(true);
    try {
      const response = await fetch('http://localhost:8000/api/config/memory');
      
      if (!response.ok) {
        throw new Error('Failed to load last prompt content');
      }
      
      const data = await response.json();
      
      if (data.last_prompt) {
        setPrompt(data.last_prompt);
        addNotification('Last prompt content loaded', 'success');
      } else {
        throw new Error('No saved prompt content found');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load last prompt';
      addNotification(errorMessage, 'error');
    } finally {
      setIsLoadingLastPrompt(false);
    }
  };
  
  const handleSubmit = async () => {
    if (!mothership) {
      addNotification('Please add mothership content', 'error');
      return;
    }
    
    if (!genre) {
      addNotification('Please select a genre', 'error');
      return;
    }
    
    if (!prompt) {
      addNotification('Please add a prompt', 'error');
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mothership,
          prompt,
          genre,
          options: {
            video_format: videoFormat
          }
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to process content');
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setIsLoading(false);
        setIsSuccess(true);
        
        addNotification(data.message || 'Content successfully created!', 'success');
        
        await fetch('http://localhost:8000/api/config/memory', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ key: 'last_mothership', value: mothership }),
        });
        
        await fetch('http://localhost:8000/api/config/memory', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ key: 'last_prompt', value: prompt }),
        });
        
        if (data.video_urls && data.video_urls.length > 0) {
          console.log('Generated videos:', data.video_urls);
        }
      } else {
        throw new Error(data.message || 'Process completed with errors');
      }
    } catch (error) {
      setIsLoading(false);
      const errorMessage = error instanceof Error ? error.message : 'Failed to process content';
      addNotification(errorMessage, 'error');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-gray-100">
      {isLoading && <LoadingOverlay />}
      {isSuccess && <SuccessOverlay onComplete={handleSuccessComplete} />}
      {showNotification && <SelectionNotification />}
      <ToastContainer notifications={notifications} onClose={removeNotification} />
      
      {isLoadingConfig ? (
        // Loading configuration state
        <div className="flex items-center justify-center h-screen">
          <div className="flex flex-col items-center space-y-4">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <h2 className="text-lg font-medium text-blue-300">Loading Configuration...</h2>
            <p className="text-sm text-gray-400">Please wait while we prepare your workspace</p>
          </div>
        </div>
      ) : (
        // Regular content once config is loaded
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-full mx-auto px-4 md:px-8 lg:px-12 pb-24"
        >
          {/* Header Section */}
          <div className="text-center mb-8 md:mb-12 pt-8">
            <motion.h1 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-4"
            >
              Content Creator Studio
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-gray-400 text-lg max-w-2xl mx-auto"
            >
              Craft your perfect content with our professional creation tools
            </motion.p>
          </div>

          {/* Main Content - 3-column layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Main Content Creation */}
            <div className="space-y-6">
              <ContentCreator
                mothership={mothership}
                setMothership={setMothership}
                hasSavedMothership={hasSavedMothership}
                isLoadingLastMothership={isLoadingLastMothership}
                loadLastMothership={loadLastMothership}
                addNotification={addNotification}
              />
              
              <ContentForm
                genre={genre}
                setGenre={setGenre}
                videoFormat={videoFormat}
                setVideoFormat={setVideoFormat}
                prompt={prompt}
                setPrompt={setPrompt}
                hasSavedPrompt={hasSavedPrompt}
                isLoadingLastPrompt={isLoadingLastPrompt}
                loadLastPrompt={loadLastPrompt}
                showAdvancedEditor={showAdvancedEditor}
                setShowAdvancedEditor={setShowAdvancedEditor}
                handleShowNotification={handleShowNotification}
                isLoading={isLoading}
                handleSubmit={handleSubmit}
                addNotification={addNotification}
              />
            </div>
            
            {/* Middle Column - Audio and Video Settings */}
            <div className="space-y-6">
              <VoiceSettings
                addNotification={addNotification}
                config={config}
              />
              
              <PauseFactorSettings
                addNotification={addNotification}
                config={config}
              />
              
              <MusicSettings
                addNotification={addNotification}
                config={config}
              />
            </div>
            
            {/* Right Column - Caption Settings and Prompt Manager */}
            <div className="space-y-6">
              <CaptionSettings
                addNotification={addNotification}
                config={config}
              />
              
              <PromptManager
                addNotification={addNotification}
                config={config}
                showAdvancedEditor={showAdvancedEditor}
              />
            </div>
          </div>

          {/* Single Large Create Button - Fixed at Bottom */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
            className="fixed bottom-0 left-0 right-0 bg-slate-900/80 backdrop-blur-sm p-4 border-t border-slate-700 z-10"
          >
            <div className="max-w-5xl mx-auto flex items-center justify-between">
              <div className="text-gray-400">
                <p className="text-sm">Ready to create your content?</p>
                <p className="text-xs opacity-70">Make sure all your settings are configured correctly.</p>
              </div>
              
              <motion.button
                onClick={handleSubmit}
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`${isLoading ? 'opacity-70 cursor-not-allowed' : ''} bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white text-lg font-medium py-3 px-10 rounded-xl shadow-lg transition-all duration-300 flex items-center space-x-2`}
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span>Create Content</span>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>

          {/* Footer Info */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-8 text-center text-gray-500 text-sm mb-16"
          >
            Create content by configuring each section separately
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
