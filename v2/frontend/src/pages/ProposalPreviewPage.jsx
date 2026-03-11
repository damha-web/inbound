import { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Send, Monitor, Smartphone, RefreshCw,
  CheckCircle, X, Loader2, AlertTriangle, Mail
} from 'lucide-react';
import api from '../services/api';
import Layout from '../components/Layout';

export default function ProposalPreviewPage() {
  const { rowIndex } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const itemData = location.state || {};

  const [html, setHtml] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('desktop'); // desktop | mobile
  const [showSendModal, setShowSendModal] = useState(false);
  const [sending, setSending] = useState(false);
  const [sendResult, setSendResult] = useState(null);

  useEffect(() => {
    fetchHtml();
  }, [rowIndex]);

  const fetchHtml = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/proposals/${rowIndex}/html`);
      setHtml(res.data);
    } catch (err) {
      setError('제안서를 불러올 수 없습니다. 먼저 생성해주세요.');
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    setSending(true);
    setSendResult(null);
    try {
      // Retrieve proposal_path from task status
      const statusRes = await api.get(`/proposals/${rowIndex}/status`);
      const proposalPath = statusRes.data.proposal_path || itemData.proposal_path;

      const res = await api.post('/email/send', {
        row_index: parseInt(rowIndex),
        to_email: itemData.email,
        company_name: itemData.company_name,
        proposal_path: proposalPath,
      });
      setSendResult({ success: true, message: res.data.message, sent_at: res.data.sent_at });
    } catch (err) {
      setSendResult({ success: false, message: err.response?.data?.detail || '발송 실패' });
    } finally {
      setSending(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-4 animate-fade-in">
        {/* Top bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              id="back-button"
              onClick={() => navigate('/')}
              className="p-2 hover:bg-surface-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-surface-200/60" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-surface-50">
                제안서 미리보기
              </h1>
              <p className="text-surface-200/50 text-sm">
                {itemData.company_name || '—'} · {itemData.email || '—'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* View mode toggle */}
            <div className="flex bg-surface-800 rounded-lg p-0.5 border border-surface-700">
              <button
                id="view-desktop"
                onClick={() => setViewMode('desktop')}
                className={`p-2 rounded-md transition-colors ${viewMode === 'desktop' ? 'bg-surface-700 text-surface-50' : 'text-surface-200/40 hover:text-surface-200/60'}`}
              >
                <Monitor className="w-4 h-4" />
              </button>
              <button
                id="view-mobile"
                onClick={() => setViewMode('mobile')}
                className={`p-2 rounded-md transition-colors ${viewMode === 'mobile' ? 'bg-surface-700 text-surface-50' : 'text-surface-200/40 hover:text-surface-200/60'}`}
              >
                <Smartphone className="w-4 h-4" />
              </button>
            </div>

            {/* Actions */}
            <button
              id="regenerate-button"
              onClick={fetchHtml}
              className="flex items-center gap-2 px-4 py-2 bg-surface-800 hover:bg-surface-700 border border-surface-700 rounded-xl text-sm text-surface-200 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              새로고침
            </button>
            <button
              id="send-button"
              onClick={() => setShowSendModal(true)}
              disabled={!html || !!error}
              className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-semibold rounded-xl shadow-lg shadow-brand-600/25 hover:shadow-brand-500/40 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
              전송하기
            </button>
          </div>
        </div>

        {/* Preview area */}
        <div className="flex justify-center">
          <div
            className={`bg-white rounded-2xl overflow-hidden shadow-2xl border border-surface-800 transition-all duration-300 ${
              viewMode === 'mobile' ? 'w-[375px]' : 'w-full max-w-4xl'
            }`}
            style={{ minHeight: '600px' }}
          >
            {loading ? (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <Loader2 className="w-8 h-8 animate-spin text-brand-500 mx-auto mb-3" />
                  <p className="text-gray-500 text-sm">제안서 로딩 중...</p>
                </div>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
                  <p className="text-gray-600">{error}</p>
                </div>
              </div>
            ) : (
              <iframe
                id="proposal-iframe"
                srcDoc={html}
                className="w-full border-0"
                style={{ minHeight: '800px', height: '100%' }}
                title="Proposal Preview"
              />
            )}
          </div>
        </div>

        {/* Send Confirmation Modal */}
        {showSendModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-surface-900 border border-surface-800 rounded-2xl w-full max-w-md p-6 animate-slide-up shadow-2xl">
              {sendResult ? (
                // Result view
                <div className="text-center py-4">
                  {sendResult.success ? (
                    <>
                      <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-8 h-8 text-emerald-400" />
                      </div>
                      <h3 className="text-lg font-bold text-surface-50 mb-2">발송 완료!</h3>
                      <p className="text-surface-200/60 text-sm mb-1">{sendResult.message}</p>
                      <p className="text-surface-200/40 text-xs">{sendResult.sent_at}</p>
                    </>
                  ) : (
                    <>
                      <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-4">
                        <AlertTriangle className="w-8 h-8 text-red-400" />
                      </div>
                      <h3 className="text-lg font-bold text-surface-50 mb-2">발송 실패</h3>
                      <p className="text-red-400 text-sm">{sendResult.message}</p>
                    </>
                  )}
                  <button
                    onClick={() => { setShowSendModal(false); setSendResult(null); if (sendResult.success) navigate('/'); }}
                    className="mt-6 px-6 py-2.5 bg-surface-800 hover:bg-surface-700 rounded-xl text-sm text-surface-200 transition-colors"
                  >
                    {sendResult.success ? '대시보드로 돌아가기' : '닫기'}
                  </button>
                </div>
              ) : (
                // Confirmation view
                <>
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-bold text-surface-50">이메일 전송 확인</h3>
                    <button onClick={() => setShowSendModal(false)} className="p-1 hover:bg-surface-800 rounded-lg">
                      <X className="w-5 h-5 text-surface-200/40" />
                    </button>
                  </div>

                  <div className="space-y-4 mb-6">
                    <div className="bg-surface-800/50 rounded-xl p-4 space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="w-4 h-4 text-surface-200/40" />
                        <span className="text-surface-200/60">수신자:</span>
                        <span className="text-surface-50 font-medium">{itemData.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-surface-200/60 ml-6">고객사:</span>
                        <span className="text-surface-50 font-medium">{itemData.company_name}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-surface-200/60 ml-6">제목:</span>
                        <span className="text-surface-50 text-xs">[담하 마케팅 제안서] {itemData.company_name} 맞춤 마케팅 전략 제안</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowSendModal(false)}
                      className="flex-1 py-2.5 bg-surface-800 hover:bg-surface-700 rounded-xl text-sm text-surface-200 transition-colors"
                    >
                      취소
                    </button>
                    <button
                      id="confirm-send"
                      onClick={handleSend}
                      disabled={sending}
                      className="flex-1 py-2.5 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-semibold rounded-xl shadow-lg shadow-brand-600/25 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {sending ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          발송 중...
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          전송하기
                        </>
                      )}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
