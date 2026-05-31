import React from 'react';
import { CheckCircle } from 'lucide-react';

const ReasonsList = ({ reasons }) => {
  if (!reasons || reasons.length === 0) return null;

  return (
    <div>
      <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide font-semibold mb-2">
        Key Reasons
      </p>
      <div className="space-y-2">
        {reasons.map((reason, i) => (
          <div key={i} className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            <p className="dark:text-dark-text text-gray-900 text-sm">{reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReasonsList;