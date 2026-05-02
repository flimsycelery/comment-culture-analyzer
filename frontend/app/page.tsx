'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async () => {
    if (!url.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch('http://localhost:8000/analyse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: url })
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Analysis failed')
      }
      const data = await res.json()
      router.push(`/report/${data.slug}`)
    } catch (e: any) {
      setError(e?.message || 'Something went wrong. Make sure the URL is valid.')
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">

        <div className="mb-2 text-sm text-zinc-500 uppercase tracking-widest">
          AI-powered
        </div>

        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
          Comment Culture
        </h1>

        <p className="text-zinc-400 text-lg mb-12">
          Paste any YouTube URL and instantly understand who is watching, what they feel, and why — in any language.
        </p>

        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
            placeholder="https://youtube.com/watch?v=..."
            className="flex-1 bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-400"
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-white text-black font-semibold px-6 py-3 rounded-xl hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Analysing...' : 'Analyse'}
          </button>
        </div>

        {error && (
          <div className="bg-red-950 border border-red-800 rounded-xl px-4 py-3 text-left mb-4">
            <p className="text-red-400 text-sm font-medium">{error}</p>
            {error.includes('comments disabled') && (
              <p className="text-red-600 text-xs mt-1">
                Try a different video — news channels, official music videos, and some creators disable comments.
              </p>
            )}
          </div>
        )}

        {loading && (
          <div className="mt-8 text-zinc-500 text-sm">
            <div className="animate-pulse">
              Fetching comments → Detecting languages → Scoring with AI → Building your report...
            </div>
            <p className="mt-2 text-zinc-600">This takes about 2 minutes</p>
          </div>
        )}

        <div className="mt-16 grid grid-cols-3 gap-4 text-left">
          {[
            { icon: '🌍', title: 'Multilingual', desc: 'Detects 20+ languages including Hindi, Hinglish, Spanish, Arabic, Korean and more' },
            { icon: '🧠', title: 'Emotion Scoring', desc: 'Rates every comment for sentiment, toxicity and humour using AI' },
            { icon: '📊', title: 'Cultural Narrative', desc: 'AI writes a deep analysis of who is watching and what they feel' }
          ].map((f, i) => (
            <div key={i} className="bg-zinc-900 rounded-xl p-4 border border-zinc-800 hover:border-zinc-600 transition">
              <div className="text-2xl mb-2">{f.icon}</div>
              <div className="font-semibold mb-1 text-sm">{f.title}</div>
              <div className="text-zinc-500 text-xs leading-relaxed">{f.desc}</div>
            </div>
          ))}
        </div>

      </div>
    </main>
  )
}