'use client';

import { useEffect, useRef } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Message, MessageProps } from './Message';

interface MessageListProps {
    messages: MessageProps[];
    isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isLoading]);

    return (
        <ScrollArea className="flex-1 px-4">
            <div className="mx-auto max-w-3xl py-6">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-24 text-center">
                        <div className="mb-4 rounded-full bg-blue-100 p-4">
                            <svg
                                className="h-8 w-8 text-blue-600"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                                />
                            </svg>
                        </div>
                        <h2 className="mb-2 text-xl font-semibold text-slate-800">
                            Welcome to College Consultant
                        </h2>
                        <p className="max-w-md text-slate-500">
                            Ask me anything about US colleges - admission rates, tuition,
                            programs, deadlines, and more.
                        </p>
                        <div className="mt-8 grid gap-2 text-sm text-slate-400">
                            <p>Try asking:</p>
                            <div className="space-y-1">
                                <p className="italic">&quot;What is the admission rate of Harvard?&quot;</p>
                                <p className="italic">&quot;해밀턴 대학교의 유학생 비율은?&quot;</p>
                                <p className="italic">&quot;Tell me about Stanford&apos;s tuition&quot;</p>
                            </div>
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((message, index) => (
                            <Message key={index} {...message} />
                        ))}
                        {isLoading && (
                            <div className="flex gap-3 p-4">
                                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200">
                                    <span className="text-sm font-medium text-slate-700">AI</span>
                                </div>
                                <div className="flex items-center gap-1 rounded-2xl bg-slate-100 px-4 py-3">
                                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '0ms' }} />
                                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '150ms' }} />
                                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        )}
                    </>
                )}
                <div ref={scrollRef} />
            </div>
        </ScrollArea>
    );
}
