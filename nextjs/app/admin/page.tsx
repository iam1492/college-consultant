'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function AdminPage() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState<{ type: 'success' | 'error' | null, message: string }>({ type: null, message: '' });
    const [resultData, setResultData] = useState<any>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
            setResultData(null);
            setStatus({ type: null, message: '' });
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setStatus({ type: 'error', message: 'Please select a file first.' });
            return;
        }

        setUploading(true);
        setStatus({ type: null, message: '' });
        setResultData(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Pointing to FastAPI backend directly for MVP. Ensure CORS is enabled on Backend.
            // Makefile run logic: `uv run adk api_server app --log_level=INFO --allow_origins="*"`
            // This suggests CORS is allowed for all.
            const response = await fetch('http://localhost:8000/upload/', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                setStatus({ type: 'success', message: `Successfully processed: ${result.filename}` });
                setResultData(result);
                setFile(null); // Clear input
            } else {
                setStatus({ type: 'error', message: result.error || 'Upload failed' });
            }
        } catch (error) {
            console.error(error);
            setStatus({ type: 'error', message: 'An error occurred during upload. Is the backend running?' });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="container mx-auto p-10">
            <Card className="w-full max-w-2xl mx-auto">
                <CardHeader>
                    <CardTitle>College Registry Update (CDS Upload)</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            Select CDS PDF
                        </label>
                        <Input
                            type="file"
                            accept=".pdf"
                            onChange={handleFileChange}
                            disabled={uploading}
                        />
                    </div>

                    <Button onClick={handleUpload} disabled={!file || uploading} className="w-full">
                        {uploading ? 'Uploading & Extracting...' : 'Upload and Process'}
                    </Button>

                    {status.type && (
                        <Alert variant={status.type === 'error' ? 'destructive' : 'default'} className={status.type === 'success' ? 'border-green-500 text-green-700 bg-green-50' : ''}>
                            <AlertTitle>{status.type === 'error' ? 'Error' : 'Success'}</AlertTitle>
                            <AlertDescription>
                                {status.message}
                            </AlertDescription>
                        </Alert>
                    )}

                    {resultData && (
                        <div className="mt-4 p-4 bg-slate-100 rounded-md text-sm overflow-auto max-h-96">
                            <h3 className="font-bold mb-2">Processing Result:</h3>
                            <pre>{JSON.stringify(resultData, null, 2)}</pre>
                            {resultData.agent_response_saved && (
                                <p className="mt-2 text-xs text-gray-500">
                                    Raw Agent Response Saved to: {resultData.agent_response_saved}
                                </p>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
