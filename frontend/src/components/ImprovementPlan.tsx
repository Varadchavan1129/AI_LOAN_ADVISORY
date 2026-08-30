import { motion } from 'framer-motion';
import { Lightbulb } from 'lucide-react';

interface ImprovementPlanProps {
  advice: string;
}

export const ImprovementPlan = ({ advice }: ImprovementPlanProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="w-full p-6 rounded-3xl bg-white/10 backdrop-blur-lg border border-white/20"
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center">
          <Lightbulb className="w-5 h-5 text-white" />
        </div>

        <div className="flex-1">
          <h4 className="text-lg font-semibold text-white mb-2">Improvement Plan</h4>
          <p className="text-white/90 leading-relaxed mb-4">{advice}</p>

          <div className="pt-4 border-t border-white/10">
            <p className="text-xs text-white/60">
              This advice is provided for informational purposes only and does not constitute legal or financial advice.
              Please consult with a qualified professional for personalized guidance.
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
