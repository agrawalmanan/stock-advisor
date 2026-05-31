import React from 'react';
import { Clock, Calendar } from 'lucide-react';

const DeliveryTag = ({ tradeType }) => {
  if (!tradeType) return null;

  const icon = tradeType.type === 'Delivery'
    ? <Calendar className="w-4 h-4" />
    : <Clock className="w-4 h-4" />;

  const colorMap = {
    green: 'bg-green-500/10 border-green-500/20 text-green-400',
    orange: 'bg-orange-500/10 border-orange-500/20 text-orange-400',
    blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
  };

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${colorMap[tradeType.color] || colorMap.blue}`}>
      {icon}
      <div>
        <p className="font-medium text-sm">{tradeType.label}</p>
        <p className="text-xs opacity-70">{tradeType.description}</p>
      </div>
    </div>
  );
};

export default DeliveryTag;