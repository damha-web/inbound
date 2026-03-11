import { Clock, Loader2, Eye, CheckCircle, AlertTriangle, Send } from 'lucide-react';

const STATUS_CONFIG = {
  '대기': {
    icon: Clock,
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/20',
    dot: 'bg-amber-400',
  },
  '생성중': {
    icon: Loader2,
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    border: 'border-blue-500/20',
    dot: 'bg-blue-400',
    animate: true,
  },
  '검토대기': {
    icon: Eye,
    bg: 'bg-purple-500/10',
    text: 'text-purple-400',
    border: 'border-purple-500/20',
    dot: 'bg-purple-400',
  },
  '승인': {
    icon: CheckCircle,
    bg: 'bg-teal-500/10',
    text: 'text-teal-400',
    border: 'border-teal-500/20',
    dot: 'bg-teal-400',
  },
  '발송중': {
    icon: Send,
    bg: 'bg-sky-500/10',
    text: 'text-sky-400',
    border: 'border-sky-500/20',
    dot: 'bg-sky-400',
    animate: true,
  },
  '발송완료': {
    icon: CheckCircle,
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    border: 'border-emerald-500/20',
    dot: 'bg-emerald-400',
  },
  '오류': {
    icon: AlertTriangle,
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    border: 'border-red-500/20',
    dot: 'bg-red-400',
  },
};

export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG['대기'];
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${config.bg} ${config.text} ${config.border} ${config.animate ? 'status-generating' : ''}`}>
      <Icon className={`w-3 h-3 ${config.animate ? 'animate-spin' : ''}`} />
      {status}
    </span>
  );
}
