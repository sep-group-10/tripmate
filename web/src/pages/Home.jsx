import { useState } from 'react'
import axios from 'axios'

function Home() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')

  const checkBackendConnection = async () => {
    setStatus('loading')
    setResult(null)
    setErrorMessage('')

    try {
      const response = await axios.get('http://localhost:8000/health')
      setResult(response.data)
      setStatus('success')
    } catch (error) {
      setErrorMessage(
        error.code === 'ERR_NETWORK'
          ? 'Could not reach the backend. Please make sure the server is running.'
          : 'Something went wrong while checking the backend connection.'
      )
      setStatus('error')
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
        AI Tourism Platform Web App
      </h1>

      <button
        type="button"
        onClick={checkBackendConnection}
        disabled={status === 'loading'}
        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg shadow hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
      >
        {status === 'loading' ? 'Checking...' : 'Check Backend Connection'}
      </button>

      {status === 'success' && result && (
        <div className="mt-6 px-4 py-3 rounded-lg bg-green-100 border border-green-300 text-green-800 text-center">
          Backend is connected. Status: <span className="font-semibold">{result.status}</span>
        </div>
      )}

      {status === 'error' && (
        <div className="mt-6 px-4 py-3 rounded-lg bg-red-100 border border-red-300 text-red-800 text-center">
          {errorMessage}
        </div>
      )}
    </div>
  )
}

export default Home
