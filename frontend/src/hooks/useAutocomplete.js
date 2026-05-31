import stocks from '../data/nse_stocks.json'

export default function useAutocomplete(query){
  if(!query) return []
  const q = query.toLowerCase()
  return stocks.filter(s=> (s.name||'').toLowerCase().includes(q) || (s.symbol||'').toLowerCase().includes(q)).slice(0,10)
}
