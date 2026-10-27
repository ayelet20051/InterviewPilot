
import { useState } from 'react'
import './App.css'

type Message = {
  id: number
  role: 'assistant' | 'user'
  text: string
}

type ApiResponse = {
  response: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: 'assistant',
      text: 'ברוכה הבאה ל-InterviewPilot! לחצי על "התחלת תרגול" כדי להתחיל.',
    },
  ])

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [started, setStarted] = useState(false)

  async function startInterview() {
    if (loading) return

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/start', {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`שגיאת שרת: ${response.status}`)
      }

      const data: ApiResponse = await response.json()

      setMessages([
        {
          id: Date.now(),
          role: 'assistant',
          text: data.response,
        },
      ])

      setStarted(true)
    } catch (err) {
      setError(
        'לא הצלחנו להתחבר לסוכנת. בדקי ששרת Python פועל ונסי שוב.',
      )
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function sendMessage() {
    const text = input.trim()

    if (!text || loading || !started) return

    setMessages((previous) => [
      ...previous,
      { id: Date.now(), role: 'user', text },
    ])

    setInput('')
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text }),
      })

      if (!response.ok) {
        throw new Error(`שגיאת שרת: ${response.status}`)
      }

      const data: ApiResponse = await response.json()

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now(),
          role: 'assistant',
          text: data.response,
        },
      ])
    } catch (err) {
      setError(
        'לא הצלחנו לקבל תשובה מהסוכנת. בדקי ששרת Python פועל ונסי שוב.',
      )
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell" dir="rtl">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">✦</div>
          <div>
            <h1>InterviewPilot</h1>
            <span>הדרך שלך לקריירה</span>
          </div>
        </div>

        <div className="sidebar-label">סביבת העבודה</div>
        <button className="nav-item active">✧ תרגול ראיונות</button>
        <button className="nav-item">◈ ההתקדמות שלי</button>
        <button className="nav-item">⌘ נושאי לימוד</button>

        <div className="sidebar-bottom">
          <div className="avatar">I</div>
          <div>
            <strong>התרגול האישי שלי</strong>
            <span>מתחילים להתקדם</span>
          </div>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">מרחב התרגול האישי שלך</span>
            <h2>בואי נתכונן להצלחה</h2>
          </div>
          <div className="status-pill">
            <span className="status-dot" />
            {loading ? 'הסוכנת חושבת...' : 'הסוכנת מוכנה'}
          </div>
        </header>

        <section className="welcome-card">
          <div className="welcome-content">
            <span className="welcome-tag">✦ המסע שלך מתחיל כאן</span>
            <h3>כל תשובה מקרבת אותך למטרה.</h3>
            <p>
              תרגלי בקצב שלך, למדי מהמשוב והתקדמי צעד אחר צעד
              לקראת ראיון העבודה הבא שלך.
            </p>
          </div>
          <div className="welcome-art" aria-hidden="true">
            <div className="orbit orbit-one" />
            <div className="orbit orbit-two" />
            <div className="core">✦</div>
          </div>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <span>מספר הודעות</span>
            <strong>{messages.length}</strong>
            <small>בשיחה הנוכחית</small>
          </div>
          <div className="stat-card">
            <span>הנושא שלך</span>
            <strong>פיתוח תוכנה</strong>
            <small>אפשר להתאים בהמשך</small>
          </div>
          <div className="stat-card">
            <span>מצב התרגול</span>
            <strong className="ready-text">
              {started ? 'התרגול פעיל' : 'מוכנה להתחיל'}
            </strong>
            <small>כל צעד הוא התקדמות</small>
          </div>
        </section>

        <section className="chat-panel">
          <div className="chat-header">
            <div className="chat-title-icon">✦</div>
            <div>
              <h3>השיחה שלך עם InterviewPilot</h3>
              <span>תרגול אישי ומותאם לקצב שלך</span>
            </div>
            <span className="live-label">פעיל</span>
          </div>

          <div className="messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message-row ${
                  message.role === 'user' ? 'user-row' : ''
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="message-avatar">✦</div>
                )}
                <div
                  className={`message-bubble ${
                    message.role === 'user'
                      ? 'user-bubble'
                      : 'assistant-bubble'
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row">
                <div className="message-avatar">✦</div>
                <div className="message-bubble assistant-bubble">
                  הסוכנת חושבת על התשובה...
                </div>
              </div>
            )}
          </div>

          {error && <p role="alert">{error}</p>}

          {!started ? (
            <button
              type="button"
              onClick={startInterview}
              disabled={loading}
            >
              {loading ? 'מתחברת לסוכנת...' : 'התחלת תרגול'}
            </button>
          ) : (
            <form
              className="message-form"
              onSubmit={(event) => {
                event.preventDefault()
                void sendMessage()
              }}
            >
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="כתבי כאן את התשובה שלך..."
                aria-label="התשובה שלך"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
              >
                שליחה <span>➤</span>
              </button>
            </form>
          )}

          <p className="chat-note">
            {started
              ? 'השיחה מחוברת לסוכנת Python שלך.'
              : 'לחצי על התחלת תרגול כדי לקבל שאלה מהסוכנת.'}
          </p>
        </section>
      </section>
    </main>
  )
}

export default App
