import React from 'react';
import { AlertTriangle } from 'lucide-react';

const Disclaimer = () => {
  return (
    <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 mt-6">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-yellow-500 font-semibold text-sm">Disclaimer</p>
          <p className="dark:text-dark-muted text-gray-500 text-xs mt-1">
            This tool is for educational and personal analysis purposes only. 
            The information provided does not constitute financial advice, 
            investment recommendation, or endorsement. Always consult a 
            qualified financial advisor before making investment decisions. 
            Past performance does not guarantee future results.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Disclaimer;