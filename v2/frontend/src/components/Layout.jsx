import { useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, FileText, Settings, LogOut, Zap
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: '대시보드', icon: LayoutDashboard },
  { path: '/history', label: '발송 이력', icon: FileText },
  { path: '/settings', label: '설정', icon: Settings },
];

export default function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('damha_token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-surface-950 flex">
      {/* Sidebar */}
      <aside className="w-60 bg-surface-900/50 border-r border-surface-800 flex flex-col fixed h-full z-20">
        {/* Logo */}
        <div className="p-5 border-b border-surface-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-lg shadow-brand-600/20">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-surface-50">DAMHA</h1>
              <p className="text-[10px] text-surface-200/40 tracking-wider uppercase">Automation V2</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                id={`nav-${item.label}`}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all ${
                  isActive
                    ? 'bg-brand-600/15 text-brand-400 font-medium border border-brand-500/20'
                    : 'text-surface-200/50 hover:text-surface-200/80 hover:bg-surface-800/50'
                }`}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="p-3 border-t border-surface-800">
          <button
            id="logout-button"
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-surface-200/40 hover:text-red-400 hover:bg-red-500/5 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            로그아웃
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 ml-60 p-6 lg:p-8">
        {children}
      </main>
    </div>
  );
}
