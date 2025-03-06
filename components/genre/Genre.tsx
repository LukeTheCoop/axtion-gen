import { motion } from 'framer-motion';
import mainStyles from '../main.module.css';

interface GenreProps {
  value: string;
  onChange: (value: string) => void;
}

export const Genre = ({ value, onChange }: GenreProps) => {
  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.2 }}
    >
      <label className={mainStyles.label} style={{ '--label-color': '#7DD3FC' } as React.CSSProperties}>Genre</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={mainStyles.select}
        style={{ '--focus-color': '#7DD3FC' } as React.CSSProperties}
      >
        <option value="" className="bg-slate-800">Select a genre</option>
        <option value="military_animation" className="bg-slate-800">Military Animation</option>
        <option value="realistic" className="bg-slate-800">Realistic</option>
      </select>
    </motion.div>
  );
}; 