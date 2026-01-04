'use client';

import { useState, useEffect, useCallback } from 'react';
import { MessageList } from './chat/MessageList';
import { ChatInput } from './chat/ChatInput';
import { MessageProps } from './chat/Message';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface SessionInfo {
    session_id: string;
    user_id: string;
    app_name: string;
}

export function ChatInterface() {
    const [messages, setMessages] = useState<MessageProps[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Create a new session when the component mounts
    useEffect(() => {
        createSession();
    }, []);

    const createSession = async () => {
        try {
            setError(null);
            const response = await fetch(`${BACKEND_URL}/chat/session`, {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error(`Failed to create session: ${response.statusText}`);
            }

            const data: SessionInfo = await response.json();
            setSessionInfo(data);
            console.log('✅ Session created:', data.session_id);
        } catch (err) {
            console.error('❌ Failed to create session:', err);
            setError('Failed to connect to the server. Please refresh the page.');
        }
    };

    const sendMessage = useCallback(async (content: string) => {
        if (!sessionInfo) {
            setError('No active session. Please refresh the page.');
            return;
        }

        // Add user message to the list
        const userMessage: MessageProps = { role: 'user', content };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);

        try {
            // Prepare the request payload for ADK
            const payload = {
                appName: sessionInfo.app_name,
                userId: sessionInfo.user_id,
                sessionId: sessionInfo.session_id,
                newMessage: {
                    role: 'user',
                    parts: [{ text: content }]
                }
            };

            // Use SSE streaming endpoint
            const response = await fetch(`${BACKEND_URL}/run_sse`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Request failed: ${response.statusText}`);
            }

            // Process SSE stream
            const reader = response.body?.getReader();
            if (!reader) {
                throw new Error('No response body');
            }

            const decoder = new TextDecoder();
            let assistantContent = '';
            let hasAddedAssistantMessage = false;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));

                            // Extract text content from the event
                            if (data.content?.parts) {
                                for (const part of data.content.parts) {
                                    if (part.text) {
                                        assistantContent += part.text;

                                        // Add or update assistant message
                                        if (!hasAddedAssistantMessage) {
                                            setMessages(prev => [
                                                ...prev,
                                                { role: 'assistant', content: assistantContent, isStreaming: true }
                                            ]);
                                            hasAddedAssistantMessage = true;
                                        } else {
                                            setMessages(prev => {
                                                const updated = [...prev];
                                                const lastIndex = updated.length - 1;
                                                if (updated[lastIndex]?.role === 'assistant') {
                                                    updated[lastIndex] = {
                                                        ...updated[lastIndex],
                                                        content: assistantContent,
                                                        isStreaming: true
                                                    };
                                                }
                                                return updated;
                                            });
                                        }
                                    }
                                }
                            }
                        } catch {
                            // Ignore JSON parse errors for incomplete chunks
                        }
                    }
                }
            }

            // Mark streaming as complete
            if (hasAddedAssistantMessage) {
                setMessages(prev => {
                    const updated = [...prev];
                    const lastIndex = updated.length - 1;
                    if (updated[lastIndex]?.role === 'assistant') {
                        updated[lastIndex] = {
                            ...updated[lastIndex],
                            isStreaming: false
                        };
                    }
                    return updated;
                });
            } else if (!assistantContent) {
                // If no content was received, show an error message
                setMessages(prev => [
                    ...prev,
                    { role: 'assistant', content: 'Sorry, I could not process your request. Please try again.' }
                ]);
            }

        } catch (err) {
            console.error('❌ Error sending message:', err);
            setError('Failed to send message. Please try again.');
            setMessages(prev => [
                ...prev,
                { role: 'assistant', content: 'An error occurred. Please try again.' }
            ]);
        } finally {
            setIsLoading(false);
        }
    }, [sessionInfo]);

    return (
        <div className="flex h-screen flex-col bg-white">
            {/* Header */}
            <header className="flex items-center justify-between border-b px-6 py-4">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600">
                        <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                        </svg>
                    </div>
                    <div>
                        <h1 className="text-lg font-semibold text-slate-800">College Consultant</h1>
                        <p className="text-sm text-slate-500">Your AI guide to US universities</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {sessionInfo && (
                        <span className="text-xs text-slate-400">
                            Session: {sessionInfo.session_id.slice(0, 8)}...
                        </span>
                    )}
                    <button
                        onClick={createSession}
                        className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
                        title="New conversation"
                    >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                    </button>
                </div>
            </header>

            {/* Error Banner */}
            {error && (
                <div className="bg-red-50 px-4 py-2 text-center text-sm text-red-600">
                    {error}
                </div>
            )}

            {/* Messages */}
            <MessageList messages={messages} isLoading={isLoading} />

            {/* Input */}
            <ChatInput onSend={sendMessage} disabled={isLoading || !sessionInfo} />
        </div>
    );
}
