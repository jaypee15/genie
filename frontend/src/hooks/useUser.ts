import { useState, useEffect } from 'react'

export const useUser = () => {
  const [userId, setUserId] = useState<string | null>(null)

  useEffect(() => {
    let stored = localStorage.getItem('genie_user_id')
    
    if (!stored) {
      stored = crypto.randomUUID()
      localStorage.setItem('genie_user_id', stored)
    }
    
    setUserId(stored)
  }, [])

  return { userId }
}

