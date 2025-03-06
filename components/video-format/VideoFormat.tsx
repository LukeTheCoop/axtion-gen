import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';

interface VideoFormatProps {
  value: string;
  onChange: (value: string) => void;
}

export const VideoFormat = ({ value, onChange }: VideoFormatProps) => {
  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.2 }}
    >
      <label className={mainStyles.label} style={{ '--label-color': '#4ADE80' } as React.CSSProperties}>Video Format</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={mainStyles.select}
        style={{ '--focus-color': '#4ADE80' } as React.CSSProperties}
      >
        <option value="mobile" className="bg-slate-800">Mobile</option>
        <option value="landscape" className="bg-slate-800">Landscape</option>
      </select>
    </motion.div>
  );
}; 