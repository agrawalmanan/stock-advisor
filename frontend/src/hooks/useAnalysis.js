import { useState, useEffect } from 'react'
import api from '../utils/api'

export default function useAnalysis(symbol){
  const [analysis, setAnalysis] = useState(null)
  useEffect(()=>{
    if(!symbol) return
    api.get(`/api/analysis/${symbol}`).then(r=>setAnalysis(r.data)).catch(()=>{})
  },[symbol])
  return analysis
}
