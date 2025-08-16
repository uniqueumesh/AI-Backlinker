import { useEffect, useState } from 'react'

function HealthBadge() {
  const [status, setStatus] = useState<'checking' | 'up' | 'down'>('checking')
  useEffect(() => {
    const run = async () => {
      try {
        const r = await fetch('http://127.0.0.1:8000/health')
        setStatus(r.ok ? 'up' : 'down')
      } catch {
        setStatus('down')
      }
    }
    run()
  }, [])
  return (
    <div className="inline-flex items-center gap-2 text-xs text-slate-400">
      <span className={
        'inline-block h-2 w-2 rounded-full ' +
        (status === 'up' ? 'bg-emerald-400 shadow-[0_0_0_3px_rgba(16,185,129,.2)]' : 'bg-amber-300 shadow-[0_0_0_3px_rgba(251,191,36,.2)]')
      } />
      <span>{status === 'checking' ? 'Checking backend...' : status === 'up' ? 'Backend online' : 'Backend unreachable'}</span>
    </div>
  )
}

import { ClerkProvider, SignedIn, SignedOut, SignInButton, SignOutButton } from '@clerk/clerk-react'
import { ThemeProvider, createTheme, CssBaseline, AppBar, Toolbar, Button, Container, Box, Typography, IconButton } from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import ResearchPage from './pages/ResearchPage'
// cleaned per plan: minimal landing

const rawClerkKey = (import.meta as any).env.VITE_CLERK_PUBLISHABLE_KEY as string | undefined
const CLERK_PUBLISHABLE_KEY = (rawClerkKey || '').trim()
// Be permissive: Clerk keys start with pk_test_ or pk_live_ and are long
const isValidClerkKey = /^pk_(test|live)_/.test(CLERK_PUBLISHABLE_KEY) && CLERK_PUBLISHABLE_KEY.length > 20

const theme = createTheme({
  palette: { mode: 'dark', primary: { main: '#7aa2ff' }, background: { default: '#070b16', paper: '#0b1020' } },
  shape: { borderRadius: 12 },
  typography: { fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial' },
})

function Shell({ enableAuth }: { enableAuth: boolean }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="sticky" color="transparent" enableColorOnDark elevation={0} sx={{ borderBottom: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(6px)' }}>
        <Toolbar sx={{ maxWidth: 1200, mx: 'auto', width: '100%' }}>
          <IconButton color="inherit" edge="start" sx={{ mr: 1 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ fontWeight: 800, flexGrow: 1 }}>AI Backlinker</Typography>
          {/* Minimal sign-out control when signed in */}
          <SignedIn>
            <SignOutButton>
              <Button size="small" variant="outlined">Sign out</Button>
            </SignOutButton>
          </SignedIn>
        </Toolbar>
      </AppBar>

      <Container sx={{ maxWidth: 900, mt: 6 }}>
        {/* Landing: only Get Started */}
        <SignedOut>
          <Box sx={{ p: 4, border: '1px solid rgba(255,255,255,0.1)', borderRadius: 3, background: 'rgba(255,255,255,0.04)', display: 'grid', placeItems: 'center' }}>
            <SignInButton mode="modal" redirectUrl="/">
              <Button variant="contained" size="large">Get Started</Button>
            </SignInButton>
          </Box>
        </SignedOut>

        {/* Signed in: only research input + table */}
        <SignedIn>
          <ResearchPage />
        </SignedIn>
      </Container>

      <Box component="footer" sx={{ borderTop: '1px solid rgba(255,255,255,0.08)', mt: 4, py: 2 }}>
        <Container sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="caption">© {new Date().getFullYear()} AI Backlinker</Typography>
          <Typography variant="caption" color="text.secondary">Backend: FastAPI · Frontend: React + Tailwind + MUI</Typography>
        </Container>
      </Box>
    </ThemeProvider>
  )
}

export default function App() {
  if (!isValidClerkKey) {
    return <Shell enableAuth={false} />
  }
  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY} appearance={{ variables: { colorPrimary: '#7aa2ff' } }}>
      <Shell enableAuth={true} />
    </ClerkProvider>
  )
}


