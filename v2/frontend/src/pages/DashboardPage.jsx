import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search, Filter, RefreshCw, FileText, Send, Eye, AlertCircle,
  TrendingUp, Users, Clock, CheckCircle, Loader2, ChevronDown
} from 'lucide-react';
import api from '../services/api';
import Layout from '../components/Layout';
import StatusBadge from '../components/StatusBadge';

const STATUS_OPTIONS = ['전체', '대기', '생성중', '검토대기', '발송완료', '오류'];

export default function DashboardPage() {
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState([]);
  const [stats, setStats] = useState({ total: 0, pending: 0, generating: 0, review: 0, sent: 0, error: 0 });
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('전체');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('timestamp');
  const [sortOrder, setSortOrder] = useState('desc');
  const [generatingRows, setGeneratingRows] = useState(new Set());

  const fetchData = useCallback(async () => {
    try {
      const params = {};
      if (filterStatus !== '전체') params.status = filterStatus;
      if (searchQuery) params.search = searchQuery;
      params.sort_by = sortBy;
      params.sort_order = sortOrder;

      const [subRes, statsRes] = await Promise.all([
        api.get('/submissions', { params }),
        api.get('/submissions/stats'),
      ]);
      setSubmissions(subRes.data.items);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    } finally {
      setLoading(false);
    }
  }, [filterStatus, searchQuery, sortBy, sortOrder]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000); // Auto-refresh every 15s
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleGenerate = async (item) => {
    if (generatingRows.has(item.row_index)) return;
    setGeneratingRows(prev => new Set(prev).add(item.row_index));

    try {
      await api.post('/proposals/generate', {
        row_index: item.row_index,
        company_name: item.company_name,
        location: item.location,
        targets: item.targets,
        email: item.email,
        industry: '의료',
      });
      // Start polling status
      pollStatus(item.row_index);
    } catch (err) {
      setGeneratingRows(prev => {
        const next = new Set(prev);
        next.delete(item.row_index);
        return next;
      });
    }
  };

  const pollStatus = (rowIndex) => {
    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/proposals/${rowIndex}/status`);
        if (res.data.status === '검토대기' || res.data.status === '오류') {
          clearInterval(interval);
          setGeneratingRows(prev => {
            const next = new Set(prev);
            next.delete(rowIndex);
            return next;
          });
          fetchData();
        }
      } catch {
        clearInterval(interval);
      }
    }, 5000);
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const statCards = [
    { label: '총 접수', value: stats.total, icon: Users, color: 'from-blue-500 to-blue-600', shadow: 'shadow-blue-500/20' },
    { label: '대기 중', value: stats.pending, icon: Clock, color: 'from-amber-500 to-orange-500', shadow: 'shadow-amber-500/20' },
    { label: '검토 대기', value: stats.review, icon: Eye, color: 'from-purple-500 to-violet-600', shadow: 'shadow-purple-500/20' },
    { label: '발송 완료', value: stats.sent, icon: CheckCircle, color: 'from-emerald-500 to-green-600', shadow: 'shadow-emerald-500/20' },
  ];

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-surface-50">대시보드</h1>
            <p className="text-surface-200/50 text-sm mt-1">수집된 데이터 관리 및 제안서 생성</p>
          </div>
          <button
            id="refresh-data"
            onClick={() => { setLoading(true); fetchData(); }}
            className="flex items-center gap-2 px-4 py-2 bg-surface-800 hover:bg-surface-700 border border-surface-700 rounded-xl text-sm text-surface-200 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((card) => (
            <div key={card.label} className="relative overflow-hidden bg-surface-900/80 backdrop-blur border border-surface-800 rounded-2xl p-5 group hover:border-surface-700 transition-all">
              <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${card.color} opacity-5 rounded-full -mr-6 -mt-6 group-hover:opacity-10 transition-opacity`} />
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${card.color} ${card.shadow} shadow-lg flex items-center justify-center`}>
                  <card.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-surface-50">{card.value}</p>
                  <p className="text-xs text-surface-200/50">{card.label}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Filters & Search */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-200/40" />
            <input
              id="search-input"
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="병원명 또는 지역 검색..."
              className="w-full pl-10 pr-4 py-2.5 bg-surface-900 border border-surface-800 rounded-xl text-sm text-surface-50 placeholder:text-surface-200/30 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500/50 transition-all"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-200/40" />
            <select
              id="status-filter"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="pl-10 pr-10 py-2.5 bg-surface-900 border border-surface-800 rounded-xl text-sm text-surface-50 appearance-none focus:outline-none focus:ring-2 focus:ring-brand-500/40 cursor-pointer"
            >
              {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-200/40 pointer-events-none" />
          </div>
        </div>

        {/* Data Table */}
        <div className="bg-surface-900/80 backdrop-blur border border-surface-800 rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-800">
                  {[
                    { key: 'receipt_id', label: '#' },
                    { key: 'timestamp', label: '접수일' },
                    { key: 'company_name', label: '병원/기업명' },
                    { key: 'location', label: '지역' },
                    { key: 'targets', label: '타겟' },
                    { key: 'email', label: '이메일' },
                    { key: 'status', label: '상태' },
                    { key: 'actions', label: '액션' },
                  ].map(col => (
                    <th
                      key={col.key}
                      onClick={() => col.key !== 'actions' && handleSort(col.key)}
                      className={`px-4 py-3 text-left text-xs font-semibold text-surface-200/60 uppercase tracking-wider ${col.key !== 'actions' ? 'cursor-pointer hover:text-surface-200/80' : ''}`}
                    >
                      <div className="flex items-center gap-1">
                        {col.label}
                        {sortBy === col.key && (
                          <span className="text-brand-500">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                        )}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-800/50">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-12 text-center">
                      <Loader2 className="w-6 h-6 animate-spin text-brand-500 mx-auto mb-2" />
                      <p className="text-surface-200/40 text-sm">데이터 로딩 중...</p>
                    </td>
                  </tr>
                ) : submissions.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-12 text-center">
                      <AlertCircle className="w-8 h-8 text-surface-200/20 mx-auto mb-2" />
                      <p className="text-surface-200/40 text-sm">수집된 데이터가 없습니다</p>
                    </td>
                  </tr>
                ) : submissions.map((item) => (
                  <tr key={item.row_index} className="hover:bg-surface-800/30 transition-colors group">
                    <td className="px-4 py-3 text-surface-200/50 font-mono text-xs">{item.receipt_id}</td>
                    <td className="px-4 py-3 text-surface-200/70 text-xs whitespace-nowrap">{item.timestamp}</td>
                    <td className="px-4 py-3 text-surface-50 font-medium">{item.company_name}</td>
                    <td className="px-4 py-3 text-surface-200/70">{item.location}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {item.targets.split(',').map((t, i) => (
                          <span key={i} className="px-2 py-0.5 bg-brand-500/10 text-brand-400 text-xs rounded-full border border-brand-500/20">
                            {t.trim()}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-surface-200/60 text-xs">{item.email}</td>
                    <td className="px-4 py-3"><StatusBadge status={item.status} /></td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 opacity-70 group-hover:opacity-100 transition-opacity">
                        {(item.status === '대기' || item.status === '오류') && (
                          <button
                            id={`generate-${item.row_index}`}
                            onClick={() => handleGenerate(item)}
                            disabled={generatingRows.has(item.row_index)}
                            className="flex items-center gap-1 px-3 py-1.5 bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium rounded-lg transition-colors disabled:opacity-50"
                            title="제안서 생성"
                          >
                            {generatingRows.has(item.row_index) ? (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                              <FileText className="w-3 h-3" />
                            )}
                            생성
                          </button>
                        )}
                        {(item.status === '검토대기' || item.status === '발송완료') && (
                          <button
                            id={`preview-${item.row_index}`}
                            onClick={() => navigate(`/preview/${item.row_index}`, { state: item })}
                            className="flex items-center gap-1 px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 text-xs font-medium rounded-lg border border-purple-500/20 transition-colors"
                            title="미리보기"
                          >
                            <Eye className="w-3 h-3" />
                            보기
                          </button>
                        )}
                        {item.status === '검토대기' && (
                          <button
                            id={`send-${item.row_index}`}
                            onClick={() => navigate(`/preview/${item.row_index}`, { state: { ...item, autoSend: true } })}
                            className="flex items-center gap-1 px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 text-xs font-medium rounded-lg border border-emerald-500/20 transition-colors"
                            title="전송하기"
                          >
                            <Send className="w-3 h-3" />
                            전송
                          </button>
                        )}
                        {item.status === '생성중' && (
                          <span className="flex items-center gap-1 text-xs text-amber-400 status-generating">
                            <Loader2 className="w-3 h-3 animate-spin" />
                            생성중...
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
}
