import { useState, useEffect } from 'react';
import Link from 'next/link';
import api from '@/lib/api';

interface JobMatch {
  id: number;
  title: string;
  company: string;
  location: string;
  excerpt: string;
  url: string;
  match_score: number;
  skills_score: number;
  seniority_score: number;
  location_score: number;
  top_factors: { name: string; weight: number }[];
  source: string;
}

export default function Matches() {
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [minScore, setMinScore] = useState(30);

  useEffect(() => {
    fetchMatches();
  }, [minScore]);

  const fetchMatches = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/matches', {
        params: { min_score: minScore }
      });
      setMatches(response.data.matches);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load matches');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Your Job Matches</h1>
          <Link href="/upload" className="btn-primary">
            Upload New Resume
          </Link>
        </div>

        <div className="card mb-6">
          <label className="block text-sm font-medium mb-2">
            Minimum Match Score: {minScore}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="w-full"
          />
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">Loading matches...</div>
        ) : matches.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-600 mb-4">No matches found. Try uploading your resume first!</p>
            <Link href="/upload" className="btn-primary">
              Upload Resume
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((match) => (
              <div key={match.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h2 className="text-xl font-bold text-gray-900">{match.title}</h2>
                    <p className="text-gray-600">{match.company}</p>
                    <p className="text-sm text-gray-500">{match.location} · {match.source}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-blue-600">
                      {Math.round(match.match_score)}%
                    </div>
                    <div className="text-sm text-gray-500">Match</div>
                  </div>
                </div>

                <p className="text-gray-700 mb-4">{match.excerpt}</p>

                <div className="mb-4">
                  <div className="text-sm font-semibold mb-2">Match Breakdown:</div>
                  {match.top_factors.map((factor, idx) => (
                    <div key={idx} className="flex items-center gap-2 mb-1">
                      <div className="text-sm text-gray-600 w-32">{factor.name}</div>
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${factor.weight}%` }}
                        ></div>
                      </div>
                      <div className="text-sm font-semibold w-12 text-right">
                        {Math.round(factor.weight)}%
                      </div>
                    </div>
                  ))}
                </div>

                <a
                  href={match.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary inline-block"
                >
                  Apply Now →
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
