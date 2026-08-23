import React from 'react'
import { AlertTriangle, RotateCcw } from 'lucide-react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary ha catturato un errore:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-4">
          <div className="max-w-md w-full p-6 rounded-2xl bg-slate-900 border border-red-500/30 text-center space-y-4 shadow-2xl">
            <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto text-red-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-slate-100">Si è verificato un imprevisto</h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Dettaglio errore:
            </p>
            <div className="p-3 bg-slate-950 rounded-xl text-left text-[11px] font-mono text-red-400 border border-red-500/20 overflow-x-auto max-h-40">
              {this.state.error?.toString() || 'Errore sconosciuto'}
              {this.state.error?.stack && (
                <div className="text-[9px] text-slate-500 mt-2 whitespace-pre-wrap">
                  {this.state.error.stack.split('\n').slice(0, 4).join('\n')}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={this.handleReset}
              className="inline-flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition-colors shadow"
            >
              <RotateCcw className="w-4 h-4" /> Ricarica Applicazione
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
