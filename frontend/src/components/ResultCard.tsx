import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, Info } from 'lucide-react';
import { LoanResult } from '../types';
import { ImprovementPlan } from './ImprovementPlan';

interface ResultCardProps {
  result: LoanResult;
}

export const ResultCard = ({ result }: ResultCardProps) => {
  const getStatusConfig = () => {
    switch (result.status) {
      case 'approved':
        return {
          icon: CheckCircle,
          gradient: 'from-green-400 to-emerald-500',
          bg: 'bg-green-500/10',
          border: 'border-green-500/30',
          iconColor: 'text-green-400',
        };
      case 'conditional':
        return {
          icon: AlertCircle,
          gradient: 'from-yellow-400 to-amber-500',
          bg: 'bg-yellow-500/10',
          border: 'border-yellow-500/30',
          iconColor: 'text-yellow-400',
        };
      case 'rejected':
        return {
          icon: Info,
          gradient: 'from-purple-400 to-indigo-500',
          bg: 'bg-purple-500/10',
          border: 'border-purple-500/30',
          iconColor: 'text-purple-400',
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className="w-full space-y-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className={`w-full p-6 rounded-3xl ${config.bg} backdrop-blur-lg border ${config.border}`}
      >
        <div className="flex items-start gap-4">
          <div className={`flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br ${config.gradient} flex items-center justify-center`}>
            <Icon className="w-6 h-6 text-white" />
          </div>

          <div className="flex-1">
            <h3 className="text-xl font-bold text-white mb-2">{result.title}</h3>
            <p className="text-white/90 leading-relaxed">{result.message}</p>
          </div>
        </div>
      </motion.div>

      {result.advice && <ImprovementPlan advice={result.advice} />}
    </div>
  );
};
