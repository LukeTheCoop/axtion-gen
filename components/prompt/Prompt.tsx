import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';
import promptStyles from './Prompt.module.css';

interface PromptProps {
  value: string;
  onChange: (value: string) => void;
  hasSavedPrompt?: boolean;
  isLoadingLastPrompt?: boolean;
  isCheckingForSavedContent?: boolean;
  loadLastPrompt?: () => void;
  isFocused?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  showAdvancedEditor?: boolean;
}

export const Prompt = ({
  value,
  onChange,
  hasSavedPrompt,
  isLoadingLastPrompt,
  isCheckingForSavedContent,
  loadLastPrompt,
  isFocused = false,
  onFocus,
  onBlur,
  showAdvancedEditor = false
}: PromptProps) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Auto-focus the textarea when isFocused becomes true
  useEffect(() => {
    if (isFocused && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isFocused]);
  
  return (
    <motion.div
      className="w-full h-full flex flex-col rounded-xl border-2 border-purple-200/70 dark:border-purple-700/40 bg-gradient-to-br from-purple-50/80 to-indigo-100/80 dark:from-purple-950/50 dark:to-indigo-900/50 shadow-lg relative"
      initial={{ scale: 0.98 }}
      animate={{ 
        scale: isFocused ? 1.02 : 1,
        boxShadow: isFocused 
          ? '0 20px 25px -5px rgba(76, 29, 149, 0.2), 0 10px 10px -5px rgba(76, 29, 149, 0.1)' 
          : '0 4px 6px -1px rgba(76, 29, 149, 0.1), 0 2px 4px -1px rgba(76, 29, 149, 0.06)',
      }}
      transition={{ duration: 0.5, ease: [0.19, 1, 0.22, 1] }}
    >
      <div className="p-5 pb-3 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-purple-800 dark:text-purple-300">Prompt</h2>
        <div className="flex space-x-2">
          <button
            onClick={loadLastPrompt}
            disabled={isLoadingLastPrompt || isCheckingForSavedContent || !hasSavedPrompt}
            className={`px-2 py-1 text-xs rounded-md transition-all duration-300 flex items-center space-x-1 
              ${isLoadingLastPrompt ? 'bg-purple-400 dark:bg-purple-700 cursor-not-allowed' : 'bg-purple-500 hover:bg-purple-600 dark:bg-purple-600 dark:hover:bg-purple-500'}
              text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isLoadingLastPrompt ? (
              <>
                <div className="animate-spin h-3 w-3 border-2 border-white border-opacity-50 border-t-transparent rounded-full"></div>
                <span>Loading...</span>
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Load Last Used</span>
              </>
            )}
          </button>
        </div>
      </div>
      <div className="px-5 flex-1 relative">
        <textarea
          ref={textareaRef}
          className={`w-full h-full resize-none border-0 rounded-lg px-3 py-2 bg-transparent focus:ring-0 focus:outline-none text-sm text-purple-900 dark:text-purple-200
            placeholder-purple-400 dark:placeholder-purple-500 transition-all scrollbar-thin scrollbar-thumb-purple-200 dark:scrollbar-thumb-purple-700 scrollbar-track-transparent`}
          placeholder="Start with a prompt..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={onFocus}
          onBlur={onBlur}
          style={{
            minHeight: '28rem',
            height: '100%'
          }}
        ></textarea>
      </div>
    </motion.div>
  );
}; 