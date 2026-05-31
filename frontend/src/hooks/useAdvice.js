import { useState, useEffect } from 'react'
import api from '../utils/api'

export default function useAdvice(symbol){
  const [advice, setAdvice] = useState(null)
  useEffect(()=>{
    if(!symbol) return
    api.get(`/api/advice/${symbol}`).then(r=>setAdvice(r.data)).catch(()=>{})
  },[symbol])
  return advice
}
