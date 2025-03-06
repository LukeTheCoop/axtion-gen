import { useState } from 'react';
import { motion } from 'framer-motion';
import { Genre } from '../genre/Genre';
import { VideoFormat } from '../video-format/VideoFormat';
import { Prompt } from '../prompt/Prompt';
import mainStyles from '../main.module.css';
import { NotificationType } from '../ui/Toast';

interface ContentFormProps {
  genre: string;
  setGenre: (value: string) => void;
  videoFormat: string;
  setVideoFormat: (value: string) => void;
  prompt: string;
  setPrompt: (value: string) => void;
  hasSavedPrompt: boolean;
  isLoadingLastPrompt: boolean;
  loadLastPrompt: () => Promise<void>;
  showAdvancedEditor: boolean;
  setShowAdvancedEditor: (value: boolean) => void;
  handleShowNotification: () => void;
  isLoading: boolean;
  handleSubmit: () => Promise<void>;
  addNotification: (message: string, type: NotificationType) => void;
}

export const ContentForm = ({
  genre,
  setGenre,
  videoFormat,
  setVideoFormat,
  prompt,
  setPrompt,
  hasSavedPrompt,
  isLoadingLastPrompt,
  loadLastPrompt,
  showAdvancedEditor,
  setShowAdvancedEditor,
  handleShowNotification,
  isLoading,
  handleSubmit,
  addNotification
}: ContentFormProps) => {
  // State to track which container is expanded
  const [activeContainer, setActiveContainer] = useState<'promptContainer' | null>(null);
  
  // Function to handle container focus
  const handleContainerFocus = (container: 'prompt') => {
    setActiveContainer(`${container}Container`);
  };
  
  // Function to reset expanded state
  const handleContainerBlur = () => {
    // Small delay to prevent flickering when clicking within the same container
    setTimeout(() => {
      setActiveContainer(null);
    }, 100);
  };
  
  // Handle next or submit button click
  const handleNextOrSubmit = () => {
    if (!prompt.trim()) {
      addNotification('Please write a prompt', 'error');
      return;
    }
    
    if (!genre) {
      addNotification('Please select a genre', 'error');
      return;
    }
    
    handleSubmit();
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={mainStyles.container}
      style={{ '--gradient-from': '#3B82F6', '--gradient-to': '#8B5CF6' } as React.CSSProperties}
    >
      <h2 className={mainStyles.heading}>
        Create Content
      </h2>
      
      {/* Genre Selection */}
      <div className="mb-4">
        <label className={mainStyles.label} style={{ '--label-color': '#93C5FD' } as React.CSSProperties}>Genre</label>
        <Genre value={genre} onChange={setGenre} />
      </div>
      
      {/* Video Format Selection */}
      <div className="mb-4">
        <label className={mainStyles.label} style={{ '--label-color': '#93C5FD' } as React.CSSProperties}>Video Format</label>
        <VideoFormat value={videoFormat} onChange={setVideoFormat} />
      </div>

      {/* Advanced Editor Toggle */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <label className={mainStyles.label} style={{ '--label-color': '#93C5FD' } as React.CSSProperties}>Advanced Editor</label>
          <button 
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200 ${
              showAdvancedEditor ? 
              'bg-gradient-to-r from-blue-500 to-indigo-600 text-white' : 
              'bg-slate-700 text-gray-400 hover:bg-slate-600 hover:text-gray-300'
            }`}
            onClick={() => setShowAdvancedEditor(!showAdvancedEditor)}
          >
            {showAdvancedEditor ? 'Hide' : 'Show'}
          </button>
        </div>
      </div>
      
      {/* Prompt Container */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <label className={mainStyles.label} style={{ '--label-color': '#93C5FD' } as React.CSSProperties}>Prompt</label>
          
          {hasSavedPrompt && (
            <button
              onClick={loadLastPrompt}
              disabled={isLoadingLastPrompt}
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
            >
              {isLoadingLastPrompt ? 'Loading...' : 'Load Last Prompt'}
            </button>
          )}
        </div>
        
        <Prompt 
          value={prompt} 
          onChange={setPrompt} 
          isFocused={activeContainer === 'promptContainer'} 
          onFocus={() => handleContainerFocus('prompt')}
          onBlur={handleContainerBlur}
          showAdvancedEditor={showAdvancedEditor}
        />
      </div>
    </motion.div>
  );
}; 