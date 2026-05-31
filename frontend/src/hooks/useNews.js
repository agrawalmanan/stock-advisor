import { useState, useEffect } from 'react'
import api from '../utils/api'

export default function useNews(symbol){
  const [news, setNews] = useState([])
  useEffect(()=>{
    if(!symbol) return
    api.get(`/api/news/${symbol}`).then(r=>setNews(r.data)).catch(()=>{})
  },[symbol])
  return news
}
