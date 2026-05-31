import React from 'react';
import { X } from 'lucide-react';

const ReadMoreModal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="dark:bg-dark-card bg-white rounded-2xl border dark:border-dark-border border-gray-200 w-full max-w-2xl max-h-[80vh] overflow-hidden relative flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b dark:border-dark-border border-gray-200">
          <h2 className="text-lg font-bold dark:text-dark-text text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg dark:hover:bg-dark-border/50 hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5 dark:text-dark-muted text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

export default ReadMoreModal;