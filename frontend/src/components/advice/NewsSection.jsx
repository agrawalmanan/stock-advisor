import React from 'react';
import { Newspaper, ExternalLink } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const NewsSection = ({ news }) => {
  if (!news || news.length === 0) {
    return (
      <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
        <div className="flex items-center gap-2 mb-4">
          <Newspaper className="w-5 h-5 text-blue-400" />
          <h3 className="dark:text-dark-text text-gray-900 font-semibold">Recent News</h3>
        </div>
        <p className="dark:text-dark-muted text-gray-500 text-sm">No recent news found for this stock.</p>
      </div>
    );
  }

  return (
    <div className="dark:bg-dark-card bg-white rounded-xl p-6 border dark:border-dark-border border-gray-200 transition-colors">
      <div className="flex items-center gap-2 mb-4">
        <Newspaper className="w-5 h-5 text-blue-400" />
        <h3 className="dark:text-dark-text text-gray-900 font-semibold">Recent News</h3>
      </div>

      <div className="space-y-3">
        {news.map((article, i) => (
          <a
            key={i}
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block dark:bg-dark-bg/50 bg-gray-50 rounded-lg p-4 border dark:border-dark-border/50 border-gray-200 dark:hover:border-blue-500/30 hover:border-blue-500/30 transition-colors group"
          >
            <div className="flex items-start gap-3">
              {article.image && (
                <img
                  src={article.image}
                  alt=""
                  className="w-16 h-16 rounded-lg object-cover flex-shrink-0"
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              )}
              <div className="flex-1 min-w-0">
                <p className="dark:text-dark-text text-gray-900 text-sm font-medium group-hover:text-blue-400 transition-colors line-clamp-2">
                  {article.title}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="dark:text-dark-muted text-gray-500 text-xs">{article.source}</span>
                  <span className="dark:text-dark-border text-gray-300 text-xs">•</span>
                  <span className="dark:text-dark-muted text-gray-500 text-xs">{formatDate(article.published_at)}</span>
                  <ExternalLink className="w-3 h-3 dark:text-dark-muted text-gray-400 ml-auto" />
                </div>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};

export default NewsSection;