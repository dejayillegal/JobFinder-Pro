import Head from 'next/head';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  return (
    <>
      <Head>
        <title>JobFinder Pro - Resume-Driven Job Matching</title>
        <meta name="description" content="AI-powered job matching platform for India" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="text-2xl font-bold text-blue-600">
                JobFinder Pro
              </div>
              <div className="flex gap-4">
                {isLoggedIn ? (
                  <>
                    <Link href="/upload" className="btn-primary">
                      Upload Resume
                    </Link>
                    <Link href="/matches" className="btn-secondary">
                      My Matches
                    </Link>
                    <button
                      onClick={() => {
                        localStorage.clear();
                        setIsLoggedIn(false);
                      }}
                      className="btn-secondary"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <Link href="/login" className="btn-secondary">
                      Login
                    </Link>
                    <Link href="/register" className="btn-primary">
                      Register
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Find Your Perfect Job Match
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Upload your resume and let our AI-powered platform match you with the best jobs 
              across India. Focus on Bangalore and Remote opportunities.
            </p>
            
            {!isLoggedIn && (
              <Link href="/register" className="inline-block btn-primary text-lg px-8 py-3">
                Get Started - Free
              </Link>
            )}
          </div>

          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="card">
              <div className="text-4xl mb-4">📄</div>
              <h3 className="text-xl font-semibold mb-2">Upload Resume</h3>
              <p className="text-gray-600">
                Upload your PDF, DOCX, or TXT resume. Our AI extracts your skills, experience, and preferences.
              </p>
            </div>

            <div className="card">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-2">AI Matching</h3>
              <p className="text-gray-600">
                Our algorithm scores jobs based on skills (60%), seniority (25%), and location (15%).
              </p>
            </div>

            <div className="card">
              <div className="text-4xl mb-4">💼</div>
              <h3 className="text-xl font-semibold mb-2">Get Matched</h3>
              <p className="text-gray-600">
                Browse personalized job matches with explainable scores and apply directly.
              </p>
            </div>
          </div>

          <div className="mt-16 card max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-4">How It Works</h2>
            <ol className="space-y-3 text-gray-700">
              <li className="flex gap-3">
                <span className="font-bold text-blue-600">1.</span>
                <span>Create a free account or login</span>
              </li>
              <li className="flex gap-3">
                <span className="font-bold text-blue-600">2.</span>
                <span>Upload your resume (PDF, DOCX, or TXT)</span>
              </li>
              <li className="flex gap-3">
                <span className="font-bold text-blue-600">3.</span>
                <span>Wait for background processing to complete (1-2 minutes)</span>
              </li>
              <li className="flex gap-3">
                <span className="font-bold text-blue-600">4.</span>
                <span>View your personalized job matches with match scores</span>
              </li>
              <li className="flex gap-3">
                <span className="font-bold text-blue-600">5.</span>
                <span>Apply to jobs that match your profile</span>
              </li>
            </ol>
          </div>
        </main>

        <footer className="bg-white mt-16 py-8">
          <div className="max-w-7xl mx-auto px-4 text-center text-gray-600">
            <p>&copy; 2025 JobFinder Pro. Built for the Indian job market.</p>
          </div>
        </footer>
      </div>
    </>
  );
}
