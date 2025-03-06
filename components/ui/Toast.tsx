import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Notification types
export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface ToastNotification {
  id: string;
  message: string;
  type: NotificationType;
}

// Toast notification component
interface ToastProps {
  notification: ToastNotification;
  onClose: (id: string) => void;
}

export const Toast = ({ notification, onClose }: ToastProps) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(notification.id);
    }, 3000);
    
    return () => clearTimeout(timer);
  }, [notification.id, onClose]);
  
  const bgColor = 
    notification.type === 'success' ? 'from-green-500 to-emerald-600' :
    notification.type === 'error' ? 'from-red-500 to-rose-600' :
    notification.type === 'warning' ? 'from-yellow-500 to-amber-600' :
    'from-blue-500 to-indigo-600';
  
  const iconColor = 
    notification.type === 'success' ? 'text-green-400' :
    notification.type === 'error' ? 'text-red-400' :
    notification.type === 'warning' ? 'text-yellow-400' :
    'text-blue-400';
  
  const icon = 
    notification.type === 'success' ? (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    ) : notification.type === 'error' ? (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    ) : notification.type === 'warning' ? (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ) : (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    );
  
  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.9 }}
      className={`flex items-center p-4 mb-3 bg-gradient-to-r ${bgColor} text-white rounded-xl shadow-lg`}
    >
      <div className={`flex-shrink-0 ${iconColor}`}>
        {icon}
      </div>
      <div className="ml-3 font-medium">{notification.message}</div>
      <button 
        onClick={() => onClose(notification.id)} 
        className="ml-auto flex-shrink-0 text-white hover:text-gray-200 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
    </motion.div>
  );
};

// Toast container component
interface ToastContainerProps {
  notifications: ToastNotification[];
  onClose: (id: string) => void;
}

export const ToastContainer = ({ notifications, onClose }: ToastContainerProps) => {
  return (
    <div className="fixed top-4 right-4 z-50 w-72">
      <AnimatePresence>
        {notifications.map(notification => (
          <Toast key={notification.id} notification={notification} onClose={onClose} />
        ))}
      </AnimatePresence>
    </div>
  );
}; 