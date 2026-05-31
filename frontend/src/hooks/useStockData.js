import { useState, useEffect } from 'react'
import api from '../utils/api'

export default function useStockData(symbol){
  const [data, setData] = useState(null)
  useEffect(()=>{
    if(!symbol) return
    api.get(`/api/stock/${symbol}`).then(r=>setData(r.data)).catch(()=>{})
  },[symbol])
  return data
}
