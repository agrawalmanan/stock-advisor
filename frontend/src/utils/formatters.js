export const formatPrice = (price) => {
  if (price === 'N/A' || price === null || price === undefined) return 'N/A';
  return `₹${Number(price).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const formatChange = (change, changePct) => {
  if (change === 'N/A' || changePct === 'N/A') return { text: 'N/A', color: 'text-gray-400' };

  const num = Number(change);
  const pct = Number(changePct);
  const isPositive = num >= 0;

  return {
    text: `${isPositive ? '+' : ''}${num.toFixed(2)} (${isPositive ? '+' : ''}${pct.toFixed(2)}%)`,
    color: isPositive ? 'text-profit' : 'text-loss',
    arrow: isPositive ? '▲' : '▼',
  };
};

export const formatVolume = (vol) => {
  if (vol === 'N/A' || vol === null || vol === undefined) return 'N/A';
  const num = Number(vol);
  if (num >= 10000000) return `${(num / 10000000).toFixed(2)} Cr`;
  if (num >= 100000) return `${(num / 100000).toFixed(2)} L`;
  return num.toLocaleString('en-IN');
};

export const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now - date;
  const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffHrs < 1) return 'Just now';
  if (diffHrs < 24) return `${diffHrs}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
};

export const getRiskColor = (level) => {
  switch (level) {
    case 'Low': return 'text-profit';
    case 'Medium': return 'text-hold';
    case 'High': return 'text-loss';
    default: return 'text-gray-400';
  }
};

export const getActionColor = (action) => {
  switch (action) {
    case 'BUY': return { text: 'text-profit', bg: 'bg-green-500/20', border: 'border-green-500/30' };
    case 'SELL': return { text: 'text-loss', bg: 'bg-red-500/20', border: 'border-red-500/30' };
    case 'HOLD': return { text: 'text-hold', bg: 'bg-yellow-500/20', border: 'border-yellow-500/30' };
    default: return { text: 'text-gray-400', bg: 'bg-gray-500/20', border: 'border-gray-500/30' };
  }
};