import { Component, ReactNode } from 'react'

type Props = { children: ReactNode }
type State = { hasError: boolean; message?: string }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(err: unknown): State {
    return { hasError: true, message: (err as any)?.message || 'Unknown error' }
  }

  componentDidCatch(error: unknown) {
    // eslint-disable-next-line no-console
    console.error('UI crashed:', error)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 16, color: '#fff', background: '#1f2937', minHeight: '100vh' }}>
          <h1 style={{ fontSize: 20, margin: 0 }}>Something went wrong.</h1>
          <p style={{ opacity: 0.8 }}>{this.state.message}</p>
        </div>
      )
    }
    return this.props.children
  }
}



