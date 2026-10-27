
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './style.css'
import App from './App'
import './App.css'

const rootElement = document.getElementById('app')

if (!rootElement) {
  throw new Error('לא נמצא רכיב app בקובץ HTML')
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
