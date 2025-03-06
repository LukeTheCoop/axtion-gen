import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';
import mothershipStyles from './Mothership.module.css';

// Hero story content
const HERO_STORY = `Strategic Defense of Ukraine: The Sacrifice of Engineer Vitalii Skakun

On February 24, 2022, during the initial phase of Russian military operations in southern Ukraine, a strategic confrontation unfolded at the Henichesk bridge in Kherson Oblast. This critical infrastructure served as the primary transit point connecting Crimea to mainland Ukraine, representing a key tactical objective for advancing Russian forces.

Combat Engineer Vitalii Volodymyrovych Skakun, a 25-year-old serviceman of Ukraine's 35th Naval Infantry Brigade, assessed the imminent tactical situation. With Russian armored columns advancing rapidly, Engineer Skakun voluntarily undertook a critical defensive operation: the strategic demolition of the bridge to prevent enemy force projection into the region.

Operating under severe time constraints, Engineer Skakun methodically placed explosive charges at key structural points. As Russian mechanized units approached within striking distance, it became apparent that standard remote detonation protocols were no longer viable. In accordance with military doctrine and demonstrating extraordinary valor, Skakun communicated his tactical decision to his command: manual detonation would be necessary. The resulting controlled demolition successfully neutralized the bridge's capacity, creating a decisive tactical advantage for Ukrainian forces, though at the cost of Engineer Skakun's life.

This strategic defensive action provided Ukrainian military command with essential time to consolidate defensive positions and reorganize tactical assets. In recognition of his exemplary service and supreme sacrifice, President Volodymyr Zelenskyy conferred upon Engineer Skakun the Order of the Gold Star and the title of Hero of Ukraine. His actions represent the highest standards of military engineering excellence and tactical decision-making under extreme combat conditions, setting a precedent for professional military conduct in modern defensive operations.`;

interface MothershipProps {
  value: string;
  onChange: (value: string) => void;
  onShowNotification: () => void;
  hasSavedMothership: boolean;
  isLoadingLastMothership: boolean;
  isCheckingForSavedContent: boolean;
  loadLastMothership: () => void;
  isFocused?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
}

export const Mothership = ({
  value,
  onChange,
  onShowNotification,
  hasSavedMothership,
  isLoadingLastMothership,
  isCheckingForSavedContent,
  loadLastMothership,
  isFocused = false,
  onFocus,
  onBlur
}: MothershipProps) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Auto-focus the textarea when isFocused becomes true
  useEffect(() => {
    if (isFocused && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isFocused]);
  
  const handlePresetClick = () => {
    onChange(HERO_STORY);
    onShowNotification();
  };
  
  return (
    <motion.div
      className="w-full h-full flex flex-col rounded-xl border-2 border-blue-200/70 dark:border-blue-700/40 bg-gradient-to-br from-blue-50/80 to-blue-100/80 dark:from-blue-950/50 dark:to-blue-900/50 shadow-lg relative"
      initial={{ scale: 0.98 }}
      animate={{ 
        scale: isFocused ? 1.02 : 1,
        boxShadow: isFocused 
          ? '0 20px 25px -5px rgba(30, 64, 175, 0.2), 0 10px 10px -5px rgba(30, 64, 175, 0.1)' 
          : '0 4px 6px -1px rgba(30, 64, 175, 0.1), 0 2px 4px -1px rgba(30, 64, 175, 0.06)',
      }}
      transition={{ duration: 0.5, ease: [0.19, 1, 0.22, 1] }}
    >
      <div className="p-5 pb-3 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-blue-800 dark:text-blue-300">Mothership</h2>
        <div className="flex space-x-2">
          <button
            onClick={loadLastMothership}
            disabled={isLoadingLastMothership || isCheckingForSavedContent || !hasSavedMothership}
            className={`px-2 py-1 text-xs rounded-md transition-all duration-300 flex items-center space-x-1 
              ${isLoadingLastMothership ? 'bg-blue-400 dark:bg-blue-700 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-500'}
              text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isLoadingLastMothership ? (
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
          className={`w-full h-full resize-none border-0 rounded-lg px-3 py-2 bg-transparent focus:ring-0 focus:outline-none text-sm text-blue-900 dark:text-blue-200
            placeholder-blue-400 dark:placeholder-blue-500 transition-all scrollbar-thin scrollbar-thumb-blue-200 dark:scrollbar-thumb-blue-700 scrollbar-track-transparent`}
          placeholder="Start with a mothership..."
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
