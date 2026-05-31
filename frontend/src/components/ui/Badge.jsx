import React from 'react';

const Badge = ({ text, color = 'gray', size = 'sm' }) => {
  const colorMap = {
    green: 'bg-green-500/20 text-green-400 border-green-500/30',
    red: 'bg-red-500/20 text-red-400 border-red-500/30',
    yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    orange: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    gray: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    purple: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  };

  const sizeMap = {
    xs: 'text-xs px-1.5 py-0.5',
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };

  return (
    <span className={`inline-flex items-center font-medium rounded-md border ${colorMap[color] || colorMap.gray} ${sizeMap[size]}`}>
      {text}
    </span>
  );
};

export default Badge;