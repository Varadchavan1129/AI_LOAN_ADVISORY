import { useEffect, useRef } from 'react';
import { Message as MessageType } from '../types';
import { Message } from './Message';
import { LoadingDots } from './LoadingDots';

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
}

export const MessageList = ({ messages, isLoading }: MessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      {isLoading && <LoadingDots />}
      <div ref={messagesEndRef} />
    </div>
  );
};
