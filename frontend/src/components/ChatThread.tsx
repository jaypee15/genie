import { Conversation } from '@/types/chat'
import { MessageSquare } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

interface ChatThreadProps {
  conversation: Conversation
  isCollapsed?: boolean
}

const ChatThread = ({ conversation, isCollapsed }: ChatThreadProps) => {
  const location = useLocation()
  const isActive = location.pathname === `/chat/${conversation.id}`

  const title = conversation.title || 'New conversation'
  const displayTitle = title.length > 30 ? `${title.substring(0, 30)}...` : title

  return (
    <Link
      to={`/chat/${conversation.id}`}
      className={`flex items-center gap-3 rounded-xl text-sm transition-all ${
        isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
      } ${
        isActive
          ? 'bg-gray-800 text-white'
          : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
      }`}
      title={isCollapsed ? title : undefined}
    >
      <MessageSquare className="w-4 h-4 flex-shrink-0" />
      {!isCollapsed && <span className="truncate">{displayTitle}</span>}
    </Link>
  )
}

export default ChatThread

