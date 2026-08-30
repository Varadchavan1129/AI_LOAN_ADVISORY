import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';
import { Message as MessageType } from '../types';
import { ResultCard } from './ResultCard';

interface MessageProps {
  message: MessageType;
}

export const Message = ({ message }: MessageProps) => {
  const isUser = message.type === 'user';
  const isResult = message.type === 'result';

  if (isResult && message.result) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full flex justify-start mb-4"
      >
        <ResultCard result={message.result} />
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}

      <div
        className={`max-w-[70%] px-4 py-3 rounded-2xl ${
          isUser
            ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
            : 'bg-white/10 backdrop-blur-lg border border-white/20 text-white'
        }`}
      >
        <p className="text-sm leading-relaxed">{message.content}</p>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/20 backdrop-blur-lg flex items-center justify-center border border-white/30">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </motion.div>
  );
};
