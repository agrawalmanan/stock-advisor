import React, { useState } from 'react';
import { Globe, MapPin, Users, Building2 } from 'lucide-react';
import ReadMoreModal from './ReadMoreModal';

const AboutTab = ({ data }) => {
  const [showModal, setShowModal] = useState(false);

  if (!data) return null;

  // Truncate about text to 3 lines (~200 chars)
  const shortAbout = data.about && data.about.length > 200
    ? data.about.substring(0, 200) + '...'
    : data.about;

  return (
    <>
      <div className="space-y-4">
        {/* About Text */}
        <div>
          <p className="dark:text-dark-text text-gray-900 text-sm leading-relaxed">
            {shortAbout || 'No description available.'}
          </p>
          {data.about && data.about.length > 200 && (
            <button
              onClick={() => setShowModal(true)}
              className="text-blue-400 hover:text-blue-300 text-sm font-medium mt-2"
            >
              Read more...
            </button>
          )}
        </div>

        {/* Quick Info */}
        <div className="grid grid-cols-2 gap-3">
          {data.industry && data.industry !== 'N/A' && (
            <div className="flex items-center gap-2">
              <Building2 className="w-3.5 h-3.5 dark:text-dark-muted text-gray-400" />
              <span className="dark:text-dark-muted text-gray-500 text-xs">{data.industry}</span>
            </div>
          )}
          {data.city && data.city !== 'N/A' && (
            <div className="flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 dark:text-dark-muted text-gray-400" />
              <span className="dark:text-dark-muted text-gray-500 text-xs">{data.city}, {data.country}</span>
            </div>
          )}
          {data.employees && data.employees !== 'N/A' && (
            <div className="flex items-center gap-2">
              <Users className="w-3.5 h-3.5 dark:text-dark-muted text-gray-400" />
              <span className="dark:text-dark-muted text-gray-500 text-xs">
                {Number(data.employees).toLocaleString('en-IN')} employees
              </span>
            </div>
          )}
          {data.website && data.website !== 'N/A' && (
            <div className="flex items-center gap-2">
              <Globe className="w-3.5 h-3.5 dark:text-dark-muted text-gray-400" />
              <a
                href={data.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 text-xs truncate"
              >
                {data.website.replace('https://', '').replace('http://', '')}
              </a>
            </div>
          )}
        </div>

        {/* Products Preview */}
        {data.products_services && data.products_services.length > 0 && (
          <div>
            <p className="dark:text-dark-muted text-gray-500 text-xs uppercase tracking-wide font-semibold mb-2">
              Products & Services
            </p>
            <div className="flex flex-wrap gap-1.5">
              {data.products_services.slice(0, 3).map((item, i) => (
                <span
                  key={i}
                  className="text-xs px-2 py-1 dark:bg-dark-border/30 bg-gray-100 dark:text-dark-text text-gray-700 rounded-md"
                >
                  {item}
                </span>
              ))}
              {data.products_services.length > 3 && (
                <button
                  onClick={() => setShowModal(true)}
                  className="text-xs px-2 py-1 text-blue-400 hover:text-blue-300"
                >
                  +{data.products_services.length - 3} more
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Read More Modal */}
      <ReadMoreModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={`About ${data.name}`}
      >
        <div className="space-y-6">
          {/* Full About */}
          <div>
            <h4 className="dark:text-dark-text text-gray-900 font-semibold mb-2">About</h4>
            <p className="dark:text-dark-muted text-gray-600 text-sm leading-relaxed whitespace-pre-line">
              {data.about || 'No description available.'}
            </p>
          </div>

          {/* Products & Services */}
          {data.products_services && data.products_services.length > 0 && (
            <div>
              <h4 className="dark:text-dark-text text-gray-900 font-semibold mb-2">Products & Services</h4>
              <ul className="space-y-1.5">
                {data.products_services.map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-400 mt-1">•</span>
                    <span className="dark:text-dark-muted text-gray-600 text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Subsidiaries */}
          {data.subsidiaries && data.subsidiaries.length > 0 && (
            <div>
              <h4 className="dark:text-dark-text text-gray-900 font-semibold mb-2">Subsidiaries & Brands</h4>
              <div className="flex flex-wrap gap-2">
                {data.subsidiaries.map((item, i) => (
                  <span
                    key={i}
                    className="text-xs px-3 py-1.5 dark:bg-dark-border/30 bg-gray-100 dark:text-dark-text text-gray-700 rounded-lg"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Recent Highlights */}
          {data.recent_highlights && data.recent_highlights.length > 0 && (
            <div>
              <h4 className="dark:text-dark-text text-gray-900 font-semibold mb-2">Recent Highlights</h4>
              <ul className="space-y-1.5">
                {data.recent_highlights.map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-green-400 mt-1">✓</span>
                    <span className="dark:text-dark-muted text-gray-600 text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </ReadMoreModal>
    </>
  );
};

export default AboutTab;