import { useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Settings as SettingsIcon, Sparkles, Plus, Menu, X, User, LogOut, LogIn } from 'lucide-react'
import { useConversations } from '@/api/chat'
import { useAuth } from '@/contexts/AuthContext'
import ChatThread from './ChatThread'

const Layout = () => {
  const location = useLocation()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const { user, signInWithGoogle, signOut } = useAuth()
  const { data: conversations } = useConversations(!!user)

  const isActive = (path: string) => location.pathname === path
  const recentChats = conversations?.slice(0, 5) || []

  return (
    <div className="flex h-screen bg-[#0A0A0A]">
      {/* Sidebar */}
      <aside className={`border-r border-gray-800/50 flex flex-col transition-all duration-300 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}>
        {/* Logo & Toggle */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-gray-800/50">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-cyan-400" />
              <span className="text-xl font-semibold text-white">genie</span>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className={`p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all ${
              isCollapsed ? 'mx-auto' : ''
            }`}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <Link
            to="/"
            className={`flex items-center gap-3 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-white font-medium transition-all ${
              isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
            }`}
            title="New Goal"
          >
            <Plus className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span>New Goal</span>}
          </Link>

          {/* Recent Chats */}
          {recentChats.length > 0 && (
            <>
              {!isCollapsed && (
                <div className="pt-4 pb-2">
                  <span className="px-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recent Chats
                  </span>
                </div>
              )}
              {recentChats.map((chat) => (
                <ChatThread key={chat.id} conversation={chat} isCollapsed={isCollapsed} />
              ))}
            </>
          )}

          {!isCollapsed && (
            <div className="pt-4 pb-2">
              <span className="px-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Navigation
              </span>
            </div>
          )}


          <Link
            to="/dashboard"
            className={`flex items-center gap-3 rounded-xl text-sm font-medium transition-all ${
              isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
            } ${
              isActive('/dashboard')
                ? 'bg-gray-800 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
            title="Your Goals"
          >
            <Home className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span>Your Goals</span>}
          </Link>

          <Link
            to="/settings"
            className={`flex items-center gap-3 rounded-xl text-sm font-medium transition-all ${
              isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
            } ${
              isActive('/settings')
                ? 'bg-gray-800 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
            title="Settings"
          >
            <SettingsIcon className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span>Settings</span>}
          </Link>
        </nav>

        {/* Footer - User Profile */}
        <div className="p-4 border-t border-gray-800/50">
          {user ? (
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800/50 transition-all ${
                  isCollapsed ? 'justify-center' : ''
                }`}
                title={isCollapsed ? user.email || 'User menu' : ''}
              >
                <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-cyan-400" />
                </div>
                {!isCollapsed && (
                  <div className="flex-1 text-left overflow-hidden">
                    <p className="text-sm text-white truncate">{user.email}</p>
                  </div>
                )}
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowUserMenu(false)}
                  />
                  <div className="absolute bottom-full left-0 right-0 mb-2 bg-[#1A1A1A] border border-gray-800 rounded-lg shadow-xl z-20 overflow-hidden">
                    <button
                      onClick={async () => {
                        await signOut()
                        setShowUserMenu(false)
                      }}
                      className="w-full flex items-center gap-3 px-4 py-3 text-left text-sm text-gray-300 hover:bg-gray-800 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          ) : (
            <button
              onClick={signInWithGoogle}
              className={`w-full flex items-center gap-3 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-all font-medium ${
                isCollapsed ? 'justify-center' : ''
              }`}
              title={isCollapsed ? 'Sign In' : ''}
            >
              <LogIn className="w-4 h-4 flex-shrink-0" />
              {!isCollapsed && <span>Sign In</span>}
            </button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
