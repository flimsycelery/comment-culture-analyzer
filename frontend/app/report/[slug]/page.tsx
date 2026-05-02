'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

interface TopComment {
  text: string
  likes: number
  language: string
}

interface Report {
  slug: string
  narrative: string
  funniest_comment: string
  unhinged_comment: string
  language_breakdown: Record<string, number>
  emotion_fingerprint: Record<string, number>
  total_comments: number
  created_at: string
  top_themes: {
    video_title: string
    video_thumbnail: string
    channel: string
    avg_toxicity: number
    top_comments: TopComment[]
    vibe: string
    audience_type: string
  }
}

const EMOTION_COLORS: Record<string, string> = {
  hype: '#f59e0b',
  nostalgia: '#8b5cf6',
  appreciation: '#10b981',
  roast: '#ef4444',
  cringe: '#f97316',
  political: '#3b82f6',
  grief: '#6366f1',
  other: '#6b7280'
}

function ToxicityMeter({ score }: { score: number }) {
  const pct = (score / 10) * 100
  const color = score < 3 ? '#10b981' : score < 6 ? '#f59e0b' : '#ef4444'
  const label = score < 3 ? 'Low' : score < 6 ? 'Moderate' : 'High'
  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs uppercase tracking-widest text-zinc-500">Toxicity Level</span>
        <span className="text-sm font-semibold" style={{ color }}>{label} ({score}/10)</span>
      </div>
      <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-1000" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  )
}

export default function ReportPage() {
  const { slug } = useParams()
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    fetch(`http://localhost:8000/report/${slug}`)
      .then(res => {
        if (!res.ok) throw new Error('Report not found')
        return res.json()
      })
      .then(data => { setReport(data); setLoading(false) })
      .catch(() => { setError('Report not found'); setLoading(false) })
  }, [slug])

  const handleCopy = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleTweet = () => {
    if (!report) return
    const text = `Just analysed "${report.top_themes?.video_title}" on Comment Culture — vibe: ${report.top_themes?.vibe} 🎯\n\nCheck the full report:`
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(window.location.href)}`)
  }

  if (loading) return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="animate-pulse text-zinc-500">Loading report...</div>
    </div>
  )

  if (error || !report) return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-red-400">{error}</div>
    </div>
  )

  const langData = Object.entries(report.language_breakdown).map(([name, value]) => ({ name, value }))
  const emotionData = Object.entries(report.emotion_fingerprint).map(([name, value]) => ({ name, value }))
  const meta = report.top_themes

  return (
    <main className="min-h-screen bg-black text-white px-4 py-12">
      <div className="max-w-3xl mx-auto">

        {/* nav */}
        <div className="flex items-center justify-between mb-10">
          <a href="/" className="text-zinc-500 text-sm hover:text-white transition">← Comment Culture</a>
          <div className="flex gap-2">
            <button onClick={handleCopy} className="text-sm border border-zinc-700 px-4 py-2 rounded-xl hover:border-zinc-500 transition">
              {copied ? '✓ Copied!' : 'Copy Link'}
            </button>
            <button onClick={handleTweet} className="text-sm bg-white text-black font-semibold px-4 py-2 rounded-xl hover:bg-zinc-200 transition">
              Tweet Report
            </button>
          </div>
        </div>

        {/* video header */}
        {meta?.video_thumbnail && (
          <div className="flex gap-4 mb-8 bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
            <img src={meta.video_thumbnail} alt="thumbnail" className="w-32 h-20 object-cover rounded-xl flex-shrink-0" />
            <div className="flex flex-col justify-center">
              <p className="text-xs text-zinc-500 mb-1">{meta.channel}</p>
              <h2 className="font-semibold text-white leading-snug">{meta.video_title}</h2>
              <div className="flex items-center gap-3 mt-2">
                <span className="text-xs text-zinc-500">{report.total_comments} comments analysed</span>
                {meta.vibe && (
                  <span className="text-xs bg-zinc-800 border border-zinc-700 px-2 py-0.5 rounded-full">
                    vibe: {meta.vibe}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* narrative */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
          <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-3">Cultural Analysis</h2>
          <p className="text-zinc-200 leading-relaxed text-lg">{report.narrative}</p>
          {meta?.audience_type && (
            <div className="mt-4 pt-4 border-t border-zinc-800">
              <span className="text-xs text-zinc-500 uppercase tracking-widest">Audience — </span>
              <span className="text-zinc-400 text-sm">{meta.audience_type}</span>
            </div>
          )}
        </div>

        {/* toxicity meter */}
        {meta?.avg_toxicity !== undefined && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
            <ToxicityMeter score={meta.avg_toxicity} />
          </div>
        )}

        {/* charts */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
            <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-4">Languages</h2>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={langData} layout="vertical">
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" tick={{ fill: '#a1a1aa', fontSize: 12 }} width={60} />
                <Tooltip contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8 }} />
                <Bar dataKey="value" fill="#ffffff" radius={4} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
            <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-4">Emotion Fingerprint</h2>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={emotionData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value">
                  {emotionData.map((entry, i) => (
                    <Cell key={i} fill={EMOTION_COLORS[entry.name] || '#6b7280'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-wrap gap-2 mt-2">
              {emotionData.map((entry, i) => (
                <span key={i} className="text-xs px-2 py-1 rounded-full" style={{ background: (EMOTION_COLORS[entry.name] || '#6b7280') + '33', color: EMOTION_COLORS[entry.name] || '#fff' }}>
                  {entry.name} {entry.value}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* funniest + unhinged */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
            <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-3">😂 Funniest Comment</h2>
            <p className="text-zinc-200 italic leading-relaxed">"{report.funniest_comment}"</p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
            <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-3">🤯 Most Unhinged</h2>
            <p className="text-zinc-200 italic leading-relaxed">"{report.unhinged_comment}"</p>
          </div>
        </div>

        {/* top liked comments */}
        {meta?.top_comments && meta.top_comments.length > 0 && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
            <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-4">👑 Most Liked Comments</h2>
            <div className="space-y-3">
              {meta.top_comments.map((c, i) => (
                <div key={i} className="flex gap-3 items-start border-b border-zinc-800 pb-3 last:border-0 last:pb-0">
                  <span className="text-zinc-600 text-sm w-4 flex-shrink-0">{i + 1}</span>
                  <p className="text-zinc-300 text-sm flex-1 leading-relaxed">{c.text}</p>
                  <div className="flex items-center gap-1 text-zinc-500 text-xs flex-shrink-0">
                    <span>♥</span>
                    <span>{c.likes.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* footer */}
        <div className="text-center text-zinc-600 text-xs mt-8">
          Built with Sarvam AI · Groq · Supabase · Next.js
        </div>

      </div>
    </main>
  )
}