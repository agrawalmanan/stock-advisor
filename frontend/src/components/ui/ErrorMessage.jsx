import React from 'react';
import { AlertCircle, Clock } from 'lucide-react';

const ErrorMessage = ({ message, onRetry }) => {
  const isRateLimit = message && (
    message.includes('Rate') || 
    message.includes('Too Many') || 
    message.includes('429') ||
    message.includes('wait')
  );

  return (
    <div className={`${isRateLimit ? 'bg-yellow-500/10 border-yellow-500/20' : 'bg-red-500/10 border-red-500/20'} border rounded-xl p-6 text-center`}>
      {isRateLimit ? (
        <Clock className="w-10 h-10 text-yellow-400 mx-auto mb-3" />
      ) : (
        <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
      )}
      <p className={`${isRateLimit ? 'text-yellow-400' : 'text-red-400'} font-medium mb-1`}>
        {isRateLimit ? 'Too many requests' : 'Something went wrong'}
      </p>
      <p className="dark:text-dark-muted text-gray-500 text-sm mb-4">
        {isRateLimit 
          ? 'Yahoo Finance rate limited us. Please wait 30 seconds and try again.' 
          : message
        }
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className={`px-4 py-2 ${isRateLimit ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/30' : 'bg-red-500/20 border-red-500/30 text-red-400 hover:bg-red-500/30'} border rounded-lg transition-colors text-sm`}
        >
          Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;