'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

interface ChatInputProps {
    onSend: (message: string) => void;
    disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
    const [input, setInput] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        const trimmedInput = input.trim();
        if (trimmedInput && !disabled) {
            onSend(trimmedInput);
            setInput('');
            // Reset textarea height
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Auto-resize textarea
    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value);
        const textarea = e.target;
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    };

    return (
        <div className="border-t bg-white px-4 py-4">
            <div className="mx-auto flex max-w-3xl items-end gap-3">
                <div className="relative flex-1">
                    <Textarea
                        ref={textareaRef}
                        value={input}
                        onChange={handleInput}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about any US college..."
                        disabled={disabled}
                        className="max-h-[200px] min-h-[52px] resize-none rounded-2xl border-slate-200 pr-12 text-base focus-visible:ring-blue-500"
                        rows={1}
                    />
                </div>
                <Button
                    onClick={handleSend}
                    disabled={disabled || !input.trim()}
                    className="h-[52px] w-[52px] shrink-0 rounded-2xl bg-blue-600 hover:bg-blue-700"
                    size="icon"
                >
                    <svg
                        className="h-5 w-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                        />
                    </svg>
                </Button>
            </div>
            <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-slate-400">
                Press Enter to send, Shift+Enter for new line
            </p>
        </div>
    );
}
