import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, User, Zap } from 'lucide-react';
import api from '../services/api';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/auth/login', { username, password });
      localStorage.setItem('damha_token', res.data.access_token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || '로그인 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-950 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-600/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-brand-500/5 rounded-full blur-3xl" />

      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo area */}
        <div className="text-center mb-10 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 mb-4 shadow-lg shadow-brand-600/20">
            <Zap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-surface-50">DAMHA <span className="text-brand-500">자동화</span></h1>
          <p className="text-surface-200/60 text-sm mt-1">마케팅 제안서 자동화 대시보드</p>
        </div>

        {/* Login form */}
        <form onSubmit={handleSubmit} className="animate-slide-up">
          <div className="bg-surface-900/80 backdrop-blur-xl border border-surface-800 rounded-2xl p-8 shadow-2xl">
            <div className="space-y-5">
              {/* Username */}
              <div>
                <label className="text-xs font-medium text-surface-200/60 uppercase tracking-wider mb-2 block">관리자 계정</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-200/40" />
                  <input
                    id="login-username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="사용자명"
                    className="w-full pl-10 pr-4 py-3 bg-surface-800/70 border border-surface-700 rounded-xl text-surface-50 placeholder:text-surface-200/30 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition-all"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="text-xs font-medium text-surface-200/60 uppercase tracking-wider mb-2 block">비밀번호</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-200/40" />
                  <input
                    id="login-password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-3 bg-surface-800/70 border border-surface-700 rounded-xl text-surface-50 placeholder:text-surface-200/30 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition-all"
                    required
                  />
                </div>
              </div>

              {/* Error message */}
              {error && (
                <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2">
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                id="login-submit"
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-brand-600/25 hover:shadow-brand-500/40 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '로그인 중...' : '로그인'}
              </button>
            </div>
          </div>
        </form>

        <p className="text-center text-surface-200/30 text-xs mt-8">
          © 2026 주식회사 담하. 내부 관리 시스템.
        </p>
      </div>
    </div>
  );
}
