import { useState } from 'react';
import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';
import { Genre } from '../genre/Genre';
import { VideoFormat } from '../video-format/VideoFormat';
import { NotificationType } from '../ui/Toast';

interface ContentCreatorProps {
  addNotification: (message: string, type: NotificationType) => void;
  mothership: string;
  setMothership: (value: string) => void;
  hasSavedMothership: boolean;
  isLoadingLastMothership: boolean;
  loadLastMothership: () => Promise<void>;
}

export const ContentCreator = ({ 
  addNotification,
  mothership,
  setMothership,
  hasSavedMothership,
  isLoadingLastMothership,
  loadLastMothership
}: ContentCreatorProps) => {
  const [isInputFocused, setIsInputFocused] = useState(false);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
      className={mainStyles.container}
      style={{ '--gradient-from': '#F59E0B', '--gradient-to': '#EF4444' } as React.CSSProperties}
    >
      <h2 className={mainStyles.heading}>
        Mothership Content
      </h2>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center mb-2">
          <label className={mainStyles.label} style={{ '--label-color': '#FCD34D' } as React.CSSProperties}>Content</label>
          
          {hasSavedMothership && (
            <button
              onClick={loadLastMothership}
              disabled={isLoadingLastMothership}
              className="text-xs text-amber-400 hover:text-amber-300 transition-colors"
            >
              {isLoadingLastMothership ? 'Loading...' : 'Load Last Content'}
            </button>
          )}
        </div>
        
        <div className={`${mainStyles.textareaContainer} ${isInputFocused ? mainStyles.focused : ''}`}>
          <textarea
            value={mothership}
            onChange={(e) => setMothership(e.target.value)}
            onFocus={() => setIsInputFocused(true)}
            onBlur={() => setIsInputFocused(false)}
            className={mainStyles.textarea}
            style={{ '--focus-color': '#FCD34D' } as React.CSSProperties}
            placeholder="Enter your mothership content here..."
            rows={8}
          />
        </div>
        
        <div className="flex justify-between text-xs text-gray-400">
          <span>{mothership.length} characters</span>
          <span>{mothership.split('\n').length} lines</span>
        </div>
      </div>
    </motion.div>
  );
}; 