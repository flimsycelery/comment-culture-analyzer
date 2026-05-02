import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Comment Culture',
  description: 'AI-powered YouTube comment analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}