import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';
import { NotificationType } from '../ui/Toast';

// Prompt manager types
interface PromptFile {
  name: string;
  label: string;
  description: string;
}

const PROMPT_FILES: PromptFile[] = [
  {
    name: 'creative',
    label: 'Creative',
    description: 'This prompt ensures AI generates creative, engaging content'
  },
  {
    name: 'polish',
    label: 'Polish',
    description: 'This prompt focuses on script generation and content polishing'
  }
];

// Action level options
const ACTION_LEVELS = ['low', 'medium', 'high', 'OVERLOAD'];
const DEPTH_OPTIONS = ['low', 'medium', 'high'];
const FOLLOW_CREATIVE_OPTIONS = ['low', 'medium', 'high'];
const TONE_OPTIONS = ['casual', 'professional', 'humorous', 'dramatic', 'inspirational'];
const STYLE_OPTIONS = ['conversational', 'narrative', 'instructional', 'poetic', 'technical'];
const PACING_OPTIONS = ['slow', 'medium', 'fast', 'dynamic'];
const AUDIENCE_OPTIONS = ['general', 'technical', 'youth', 'professional', 'seniors'];

interface PromptManagerProps {
  addNotification: (message: string, type: NotificationType) => void;
  config: any;
  showAdvancedEditor?: boolean;
}

export const PromptManager = ({ addNotification, config, showAdvancedEditor = false }: PromptManagerProps) => {
  // Prompt manager state
  const [promptCategory, setPromptCategory] = useState('military');
  const [creativePrompt, setCreativePrompt] = useState('');
  const [storyArcCount, setStoryArcCount] = useState(1);
  const [depthOfMothership, setDepthOfMothership] = useState('medium');
  const [actionLevel, setActionLevel] = useState('high');
  const [favoriteVideos, setFavoriteVideos] = useState<string[]>([]);
  const [availableVideos, setAvailableVideos] = useState<string[]>([]);
  
  // New creative prompt options
  const [tone, setTone] = useState('professional');
  const [style, setStyle] = useState('narrative');
  const [creativityLevel, setCreativityLevel] = useState(7);

  // Polish prompt state
  const [polishPrompt, setPolishPrompt] = useState('');
  const [duration, setDuration] = useState('60sec');
  const [followCreative, setFollowCreative] = useState('high');
  const [specificCommands, setSpecificCommands] = useState<string[]>([]);
  const [newCommand, setNewCommand] = useState('');
  
  // New polish prompt options
  const [pacing, setPacing] = useState('medium');
  const [targetAudience, setTargetAudience] = useState('general');
  const [clarityLevel, setClarityLevel] = useState(8);

  const [activePromptType, setActivePromptType] = useState<string>(PROMPT_FILES[0].name);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Refs for auto-save
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Load initial data when component mounts or config changes
  useEffect(() => {
    setIsLoading(true);
    
    if (config) {
      try {
        console.log('Loading prompt data from config');
        loadPromptData();
        
        // Load video list for favorite videos selection
        if (config.video_list && config.video_list[promptCategory]) {
          setAvailableVideos(config.video_list[promptCategory]);
        } else {
          console.warn(`No video list found for category: ${promptCategory}`);
          setAvailableVideos([]);
        }
      } catch (error) {
        console.error('Error loading prompt data:', error);
        addNotification('Failed to load prompt data', 'error');
      } finally {
        // Set loading to false regardless of outcome
        setIsLoading(false);
      }
    }
  }, [config, promptCategory]);
  
  const loadPromptData = () => {
    if (!config) {
      console.warn('Config is not available yet');
      return;
    }
    
    if (!config.prompts) {
      console.warn('Config does not contain prompts data');
      return;
    }
    
    if (!config.prompts[promptCategory]) {
      console.warn(`No prompts found for category: ${promptCategory}`);
      return;
    }
    
    // Load creative prompt data
    const creativeConfig = config.prompts[promptCategory].creative || {};
    setCreativePrompt(creativeConfig.prompt || '');
    setStoryArcCount(creativeConfig.story_arc_count || 1);
    setDepthOfMothership(creativeConfig.depth_of_mothership || 'medium');
    setActionLevel(creativeConfig.action_level || 'high');
    setFavoriteVideos(creativeConfig.favorite_videos || []);
    
    // Load new creative options
    setTone(creativeConfig.tone || 'professional');
    setStyle(creativeConfig.style || 'narrative');
    setCreativityLevel(creativeConfig.creativity_level || 7);
    
    // Load polish prompt data
    const polishConfig = config.prompts[promptCategory].polish || {};
    setPolishPrompt(polishConfig.prompt || '');
    setDuration(polishConfig.duration || '60sec');
    setFollowCreative(polishConfig.follow_creative || 'high');
    setSpecificCommands(polishConfig.specific_commands || []);
    
    // Load new polish options
    setPacing(polishConfig.pacing || 'medium');
    setTargetAudience(polishConfig.target_audience || 'general');
    setClarityLevel(polishConfig.clarity_level || 8);
    
    console.log('Prompt data loaded successfully');
  };
  
  // Auto-save function
  const autoSave = (path: string, value: any) => {
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    
    autoSaveTimeoutRef.current = setTimeout(async () => {
      setIsSaving(true);
      try {
        // Extract the category from the path (e.g., "prompts.military.creative.prompt" -> "military")
        const pathParts = path.split('.');
        if (pathParts.length >= 2 && pathParts[0] === 'prompts') {
          const category = pathParts[1];
          
          // First, get the current configuration for this category
          const configResponse = await fetch(`http://localhost:8000/api/config/prompts/${category}`);
          let currentConfig: Record<string, any> = {};
          
          if (configResponse.ok) {
            currentConfig = await configResponse.json();
          }
          
          // Create a nested object structure for the remaining path parts
          // But preserve any existing values at each level
          const remainingPath = pathParts.slice(2);
          let configUpdate: Record<string, any> = currentConfig;
          
          // Create a deep clone of current config to avoid modifying it
          configUpdate = JSON.parse(JSON.stringify(configUpdate));
          
          // Navigate to the correct nested position and set the value
          let currentLevel: Record<string, any> = configUpdate;
          for (let i = 0; i < remainingPath.length - 1; i++) {
            const key = remainingPath[i];
            if (!currentLevel[key]) {
              currentLevel[key] = {};
            }
            currentLevel = currentLevel[key];
          }
          
          // Set the value at the final level
          const finalKey = remainingPath[remainingPath.length - 1];
          currentLevel[finalKey] = value;
          
          console.log('Saving updated config:', JSON.stringify(configUpdate, null, 2));
          
          const response = await fetch(`http://localhost:8000/api/config/prompts/${category}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(configUpdate),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to save: ${path}`);
          }
          
          addNotification('Saved successfully', 'success');
        } else {
          // Fallback to using the value endpoint if not a prompt path
          const response = await fetch(`http://localhost:8000/api/config/value?path=${encodeURIComponent(path)}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(value),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to save: ${path}`);
          }
          
          addNotification('Saved successfully', 'success');
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to save';
        addNotification(errorMessage, 'error');
      } finally {
        setIsSaving(false);
      }
    }, 500); // Debounce for 500ms
  };
  
  // Handler for creative prompt changes
  const handleCreativePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setCreativePrompt(value);
    autoSave(`prompts.${promptCategory}.creative.prompt`, value);
  };
  
  // Handler for story arc count changes
  const handleStoryArcCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setStoryArcCount(value);
    autoSave(`prompts.${promptCategory}.creative.story_arc_count`, value);
  };
  
  // Handler for depth of mothership changes
  const handleDepthOfMothershipChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setDepthOfMothership(value);
    autoSave(`prompts.${promptCategory}.creative.depth_of_mothership`, value);
  };
  
  // Handler for action level changes
  const handleActionLevelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setActionLevel(value);
    autoSave(`prompts.${promptCategory}.creative.action_level`, value);
  };
  
  // Handler for favorite videos changes
  const handleFavoriteVideoToggle = (video: string) => {
    const updatedVideos = favoriteVideos.includes(video)
      ? favoriteVideos.filter(v => v !== video)
      : [...favoriteVideos, video];
    
    setFavoriteVideos(updatedVideos);
    autoSave(`prompts.${promptCategory}.creative.favorite_videos`, updatedVideos);
  };
  
  // Handlers for new creative options
  const handleToneChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setTone(value);
    autoSave(`prompts.${promptCategory}.creative.tone`, value);
  };
  
  const handleStyleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setStyle(value);
    autoSave(`prompts.${promptCategory}.creative.style`, value);
  };
  
  const handleCreativityLevelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setCreativityLevel(value);
    autoSave(`prompts.${promptCategory}.creative.creativity_level`, value);
  };
  
  // Handler for polish prompt changes
  const handlePolishPromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setPolishPrompt(value);
    autoSave(`prompts.${promptCategory}.polish.prompt`, value);
  };
  
  // Handler for duration changes
  const handleDurationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setDuration(value);
    autoSave(`prompts.${promptCategory}.polish.duration`, value);
  };
  
  // Handler for follow creative changes
  const handleFollowCreativeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFollowCreative(value);
    autoSave(`prompts.${promptCategory}.polish.follow_creative`, value);
  };
  
  // Handlers for new polish options
  const handlePacingChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setPacing(value);
    autoSave(`prompts.${promptCategory}.polish.pacing`, value);
  };
  
  const handleTargetAudienceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setTargetAudience(value);
    autoSave(`prompts.${promptCategory}.polish.target_audience`, value);
  };
  
  const handleClarityLevelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setClarityLevel(value);
    autoSave(`prompts.${promptCategory}.polish.clarity_level`, value);
  };
  
  // Handler for adding a new specific command
  const handleAddSpecificCommand = () => {
    if (!newCommand.trim()) return;
    
    const updatedCommands = [...specificCommands, newCommand.trim()];
    setSpecificCommands(updatedCommands);
    setNewCommand('');
    autoSave(`prompts.${promptCategory}.polish.specific_commands`, updatedCommands);
  };
  
  // Handler for removing a specific command
  const handleRemoveSpecificCommand = (index: number) => {
    const updatedCommands = specificCommands.filter((_, i) => i !== index);
    setSpecificCommands(updatedCommands);
    autoSave(`prompts.${promptCategory}.polish.specific_commands`, updatedCommands);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.7 }}
      className={mainStyles.container}
      style={{ '--gradient-from': '#A855F7', '--gradient-to': '#EC4899' } as React.CSSProperties}
    >
      <h2 className={mainStyles.heading}>
        Prompt Manager {isSaving && <span className="text-xs text-gray-400 ml-2">(Saving...)</span>}
      </h2>
      
      {isLoading ? (
        // Loading state
        <div className="flex flex-col items-center justify-center py-8 space-y-4">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-purple-300 font-medium">Loading prompt data...</p>
        </div>
      ) : !config || !config.prompts || !config.prompts[promptCategory] ? (
        // Error state - couldn't load data
        <div className="py-8 text-center">
          <p className="text-red-400 font-medium">Could not load prompt data</p>
          <p className="text-gray-400 text-sm mt-2">Please check your connection and try refreshing the page</p>
        </div>
      ) : (
        // Normal content when data is loaded
        <div className="space-y-6">
          {/* Category Selection */}
          <div>
            <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>Category</label>
            <select
              value={promptCategory}
              onChange={(e) => setPromptCategory(e.target.value)}
              className={mainStyles.select}
              style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
            >
              <option value="military" className="bg-slate-800">Military</option>
              {/* Add more categories as needed */}
            </select>
          </div>
          
          {/* Prompt Type Tabs */}
          <div className="flex bg-slate-900/30 rounded-xl p-1">
            {PROMPT_FILES.map((file) => (
              <button
                key={file.name}
                onClick={() => setActivePromptType(file.name)}
                className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activePromptType === file.name
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                    : 'text-gray-400 hover:text-gray-100'
                }`}
              >
                {file.label}
              </button>
            ))}
          </div>
          
          {/* Creative Prompt Configuration */}
          {activePromptType === 'creative' && (
            <div className="space-y-4">
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Creative Prompt
                </label>
                <textarea
                  value={creativePrompt}
                  onChange={handleCreativePromptChange}
                  className={mainStyles.textarea}
                  style={{ 
                    '--focus-color': '#C084FC',
                    minHeight: '12rem',
                    fontFamily: 'monospace'
                  } as React.CSSProperties}
                  placeholder="Enter creative prompt content..."
                  spellCheck="false"
                />
              </div>
              
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Story Arc Count (1-10)
                </label>
                <div className="flex items-center space-x-4">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={storyArcCount}
                    onChange={handleStoryArcCountChange}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <span className="text-gray-300 w-8 text-center">{storyArcCount}</span>
                </div>
              </div>
              
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Depth of Mothership
                </label>
                <select
                  value={depthOfMothership}
                  onChange={handleDepthOfMothershipChange}
                  className={mainStyles.select}
                  style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                >
                  {DEPTH_OPTIONS.map(option => (
                    <option key={option} value={option} className="bg-slate-800">
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Action Level
                </label>
                <select
                  value={actionLevel}
                  onChange={handleActionLevelChange}
                  className={mainStyles.select}
                  style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                >
                  {ACTION_LEVELS.map(option => (
                    <option key={option} value={option} className="bg-slate-800">
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* New Creative Options */}
              {showAdvancedEditor && (
                <>
                  <div>
                    <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                      Tone
                    </label>
                    <select
                      value={tone}
                      onChange={handleToneChange}
                      className={mainStyles.select}
                      style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                    >
                      {TONE_OPTIONS.map(option => (
                        <option key={option} value={option} className="bg-slate-800">
                          {option.charAt(0).toUpperCase() + option.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                      Style
                    </label>
                    <select
                      value={style}
                      onChange={handleStyleChange}
                      className={mainStyles.select}
                      style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                    >
                      {STYLE_OPTIONS.map(option => (
                        <option key={option} value={option} className="bg-slate-800">
                          {option.charAt(0).toUpperCase() + option.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                      Creativity Level (1-10): {creativityLevel}
                    </label>
                    <div className="flex items-center space-x-4">
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={creativityLevel}
                        onChange={handleCreativityLevelChange}
                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                      />
                      <span className="text-gray-300 w-8 text-center">{creativityLevel}</span>
                    </div>
                  </div>
                </>
              )}
              
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Favorite Videos
                </label>
                <div className="max-h-60 overflow-y-auto bg-slate-800/50 rounded-xl p-3 space-y-2">
                  {availableVideos.length > 0 ? (
                    availableVideos.map((video) => (
                      <div key={video} className="flex items-center">
                        <input
                          type="checkbox"
                          id={`video-${video}`}
                          checked={favoriteVideos.includes(video)}
                          onChange={() => handleFavoriteVideoToggle(video)}
                          className="mr-2 h-4 w-4 text-purple-500 rounded focus:ring-purple-500 bg-gray-700 border-gray-600"
                        />
                        <label htmlFor={`video-${video}`} className="text-sm text-gray-300 cursor-pointer">
                          {video.replace(/_/g, ' ').replace('.mp4', '')}
                        </label>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-400 py-2">No videos available for this category</p>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* Polish Prompt Configuration */}
          {activePromptType === 'polish' && (
            <div className="space-y-4">
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Polish Prompt
                </label>
                <textarea
                  value={polishPrompt}
                  onChange={handlePolishPromptChange}
                  className={mainStyles.textarea}
                  style={{ 
                    '--focus-color': '#C084FC',
                    minHeight: '12rem',
                    fontFamily: 'monospace'
                  } as React.CSSProperties}
                  placeholder="Enter polish prompt content..."
                  spellCheck="false"
                />
              </div>
              
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Duration
                </label>
                <input
                  type="text"
                  value={duration}
                  onChange={handleDurationChange}
                  className={mainStyles.input}
                  style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                  placeholder="e.g. 60sec"
                />
              </div>
              
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Follow Creative
                </label>
                <select
                  value={followCreative}
                  onChange={handleFollowCreativeChange}
                  className={mainStyles.select}
                  style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                >
                  {FOLLOW_CREATIVE_OPTIONS.map(option => (
                    <option key={option} value={option} className="bg-slate-800">
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* New Polish Options */}
              {showAdvancedEditor && (
                <>
                  <div>
                    <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                      Pacing
                    </label>
                    <select
                      value={pacing}
                      onChange={handlePacingChange}
                      className={mainStyles.select}
                      style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                    >
                      {PACING_OPTIONS.map(option => (
                        <option key={option} value={option} className="bg-slate-800">
                          {option.charAt(0).toUpperCase() + option.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                      Target Audience
                    </label>
                    <select
                      value={targetAudience}
                      onChange={handleTargetAudienceChange}
                      className={mainStyles.select}
                      style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                    >
                      {AUDIENCE_OPTIONS.map(option => (
                        <option key={option} value={option} className="bg-slate-800">
                          {option.charAt(0).toUpperCase() + option.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                      Clarity Level (1-10): {clarityLevel}
                    </label>
                    <div className="flex items-center space-x-4">
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={clarityLevel}
                        onChange={handleClarityLevelChange}
                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                      />
                      <span className="text-gray-300 w-8 text-center">{clarityLevel}</span>
                    </div>
                  </div>
                </>
              )}
              
              <div>
                <label className={mainStyles.label} style={{ '--label-color': '#C084FC' } as React.CSSProperties}>
                  Specific Commands
                </label>
                <div className="space-y-2">
                  {specificCommands.map((command, index) => (
                    <div key={index} className="flex items-center bg-slate-800/50 rounded-lg p-2">
                      <p className="flex-1 text-sm text-gray-300">{command}</p>
                      <button
                        onClick={() => handleRemoveSpecificCommand(index)}
                        className="ml-2 text-red-400 hover:text-red-300 transition-colors"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  ))}
                  
                  <div className="flex mt-2">
                    <input
                      type="text"
                      value={newCommand}
                      onChange={(e) => setNewCommand(e.target.value)}
                      className={mainStyles.input + " flex-1 mr-2"}
                      style={{ '--focus-color': '#C084FC' } as React.CSSProperties}
                      placeholder="Add new command..."
                      onKeyDown={(e) => e.key === 'Enter' && handleAddSpecificCommand()}
                    />
                    <button
                      onClick={handleAddSpecificCommand}
                      className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Character Count - show for both prompt types */}
          <div className="flex justify-between text-xs text-gray-400">
            <span>
              {activePromptType === 'creative' ? creativePrompt.length : polishPrompt.length} characters
            </span>
            <span>
              {activePromptType === 'creative' ? creativePrompt.split('\n').length : polishPrompt.split('\n').length} lines
            </span>
          </div>
        </div>
      )}
    </motion.div>
  );
}; 