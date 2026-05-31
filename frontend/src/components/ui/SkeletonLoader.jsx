import React from 'react';

export const SkeletonBlock = ({ className = '' }) => (
  <div className={`skeleton ${className}`}></div>
);

export const StockHeaderSkeleton = () => (
  <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200">
    <SkeletonBlock className="h-8 w-64 mb-3" />
    <SkeletonBlock className="h-10 w-48 mb-2" />
    <SkeletonBlock className="h-5 w-32" />
  </div>
);

export const StockDetailsSkeleton = () => (
  <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[...Array(8)].map((_, i) => (
        <div key={i}>
          <SkeletonBlock className="h-4 w-20 mb-2" />
          <SkeletonBlock className="h-6 w-28" />
        </div>
      ))}
    </div>
  </div>
);

export const ChartSkeleton = () => (
  <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200">
    <SkeletonBlock className="h-6 w-32 mb-4" />
    <SkeletonBlock className="h-72 w-full" />
  </div>
);

export const AnalysisSkeleton = () => (
  <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200">
    <SkeletonBlock className="h-6 w-48 mb-4" />
    <div className="space-y-3">
      {[...Array(4)].map((_, i) => (
        <SkeletonBlock key={i} className="h-10 w-full" />
      ))}
    </div>
  </div>
);

export const AdviceSkeleton = () => (
  <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200">
    <SkeletonBlock className="h-6 w-48 mb-4" />
    <SkeletonBlock className="h-16 w-32 mb-4" />
    <div className="space-y-2">
      {[...Array(4)].map((_, i) => (
        <SkeletonBlock key={i} className="h-5 w-full" />
      ))}
    </div>
  </div>
);

export default SkeletonBlock;