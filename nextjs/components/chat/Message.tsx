'use client';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

export interface MessageProps {
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
}

export function Message({ role, content, isStreaming }: MessageProps) {
    const isUser = role === 'user';

    return (
        <div
            className={cn(
                'flex gap-3 p-4',
                isUser ? 'flex-row-reverse' : 'flex-row'
            )}
        >
            {/* Avatar */}
            <Avatar className="h-8 w-8 shrink-0">
                <AvatarFallback
                    className={cn(
                        'text-sm font-medium',
                        isUser
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-200 text-slate-700'
                    )}
                >
                    {isUser ? 'U' : 'AI'}
                </AvatarFallback>
            </Avatar>

            {/* Message Bubble */}
            <div
                className={cn(
                    'max-w-[80%] rounded-2xl px-4 py-3',
                    isUser
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-900'
                )}
            >
                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {content}
                    {isStreaming && (
                        <span className="ml-1 inline-block animate-pulse">▋</span>
                    )}
                </div>
            </div>
        </div>
    );
}
