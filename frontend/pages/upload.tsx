import { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import api from '@/lib/api';

export default function Upload() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<any>(null);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/api/resume/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setJobId(response.data.job_id);
      pollStatus(response.data.job_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
      setUploading(false);
    }
  };

  const pollStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/api/resume/status/${id}`);
        setStatus(response.data);

        if (response.data.status === 'completed') {
          clearInterval(interval);
          setUploading(false);
          setTimeout(() => router.push('/matches'), 2000);
        } else if (response.data.status === 'failed') {
          clearInterval(interval);
          setUploading(false);
          setError(response.data.error || 'Processing failed');
        }
      } catch (err) {
        clearInterval(interval);
        setUploading(false);
        setError('Failed to check status');
      }
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Upload Resume</h1>
          <Link href="/matches" className="btn-secondary">
            View Matches
          </Link>
        </div>

        <div className="card">
          <p className="text-gray-600 mb-6">
            Upload your resume in PDF, DOCX, or TXT format. Our AI will analyze your skills, 
            experience, and preferences to find matching jobs.
          </p>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {!jobId && (
            <div className="space-y-4">
              <div>
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.txt"
                  className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 p-2"
                />
              </div>

              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="btn-primary"
              >
                Upload & Process
              </button>
            </div>
          )}

          {jobId && status && (
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Processing Status</h3>
                <p className="text-sm text-gray-600 mb-2">Job ID: {jobId}</p>
                <p className="text-sm">Status: <span className="font-semibold">{status.status}</span></p>
                <p className="text-sm">Progress: {status.progress}%</p>
                
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${status.progress}%` }}
                  ></div>
                </div>

                {status.status === 'completed' && (
                  <div className="mt-4 text-green-600 font-semibold">
                    ✓ Complete! Redirecting to matches...
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
