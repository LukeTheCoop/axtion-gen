import { useEffect, useState } from 'react';
import styles from '../main.module.css';
import creatorStyles from '../../app/creator/creator.module.css';

// Import quotes from the creator page
import { QUOTES } from '../../app/creator/quotes';

// Define confetti colors constant
const CONFETTI_COLORS = ['#60A5FA', '#34D399', '#818CF8', '#C084FC', '#F472B6'];

interface SuccessOverlayProps {
  onComplete: () => void;
}

export const SuccessOverlay = ({ onComplete }: SuccessOverlayProps) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete();
    }, 2500);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className={creatorStyles.successOverlay}>
      {[...Array(50)].map((_, i) => (
        <div
          key={i}
          className={creatorStyles.confetti}
          style={{
            left: `${Math.random() * 100}%`,
            top: `-20px`,
            backgroundColor: CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)],
            animationDelay: `${Math.random() * 0.5}s`,
          }}
        />
      ))}
      <div className={creatorStyles.successCheck} />
      <div className={creatorStyles.successMessage}>Successfully Created!</div>
    </div>
  );
};

export const LoadingOverlay = () => {
  const [quoteIndex, setQuoteIndex] = useState(0);
  const [currentQuote, setCurrentQuote] = useState(QUOTES[0]);

  useEffect(() => {
    const interval = setInterval(() => {
      const newIndex = Math.floor(Math.random() * QUOTES.length);
      setCurrentQuote(QUOTES[newIndex]);
    }, 6000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className={creatorStyles.loadingOverlay}>
      <div className={creatorStyles.particles}>
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className={creatorStyles.particle}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 8}s`
            }}
          />
        ))}
      </div>
      <div className={creatorStyles.loadingSpinner}>
        <div className={creatorStyles.loadingInner} />
      </div>
      <div className={creatorStyles.quoteContainer}>
        <p className={creatorStyles.quote}>{currentQuote.quote}</p>
        <p className={`${creatorStyles.author} ${currentQuote.category === 'scripture' ? creatorStyles.scripture : ''}`}>
          — {currentQuote.author}
        </p>
      </div>
      <div className={creatorStyles.progressBar} />
    </div>
  );
};

export const SelectionNotification = () => {
  return (
    <div className={creatorStyles.selectionNotification}>
      <div className={creatorStyles.sparkleContainer}>
        {[...Array(100)].map((_, i) => (
          <div
            key={i}
            className={creatorStyles.sparkle}
            style={{
              left: `${50 + (Math.random() - 0.5) * 20}%`,
              top: `${50 + (Math.random() - 0.5) * 20}%`,
              animationDelay: `${Math.random() * 0.8}s`,
            }}
          />
        ))}
      </div>
      <h2 className={creatorStyles.selectionTitle}>Combat Engineer's Valor</h2>
      <p className={creatorStyles.selectionSubtitle}>
        Strategic Defense of Ukraine: A Testament to Military Excellence
      </p>
    </div>
  );
}; 