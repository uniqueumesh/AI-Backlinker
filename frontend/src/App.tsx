import { ClerkProvider, SignedIn, SignedOut, SignOutButton } from '@clerk/clerk-react'
import { ThemeProvider, createTheme, CssBaseline, AppBar, Toolbar, Button, Container, Box, Typography, IconButton } from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import ResearchPage from './pages/ResearchPage'
import LandingPage from './pages/LandingPage'

const rawClerkKey = (import.meta as any).env.VITE_CLERK_PUBLISHABLE_KEY as string | undefined
const CLERK_PUBLISHABLE_KEY = (rawClerkKey || '').trim()
const isValidClerkKey = /^pk_(test|live)_/.test(CLERK_PUBLISHABLE_KEY) && CLERK_PUBLISHABLE_KEY.length > 20

const theme = createTheme({
  palette: { mode: 'dark', primary: { main: '#7aa2ff' }, background: { default: '#070b16', paper: '#0b1020' } },
  shape: { borderRadius: 12 },
  typography: { fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial' },
})

function AppShell() {
  // This shell is now only for signed-in users.
  return (
    <>
      <AppBar position="sticky" color="transparent" enableColorOnDark elevation={0} sx={{ borderBottom: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(6px)' }}>
        <Toolbar sx={{ maxWidth: 1200, mx: 'auto', width: '100%' }}>
          <IconButton color="inherit" edge="start" sx={{ mr: 1 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ fontWeight: 800, flexGrow: 1 }}>ALwrity AI Backlinker</Typography>
          <SignOutButton>
            <Button size="small" variant="outlined">Sign out</Button>
          </SignOutButton>
        </Toolbar>
      </AppBar>

      <Container sx={{ maxWidth: 900, mt: 6 }}>
        <ResearchPage />
      </Container>

      <Box component="footer" sx={{ borderTop: '1px solid rgba(255,255,255,0.08)', mt: 4, py: 2 }}>
        <Container sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="caption">© {new Date().getFullYear()} ALwrity Backlinker</Typography>
          <Typography variant="caption" color="text.secondary">Backend: FastAPI · Frontend: React + Tailwind + MUI</Typography>
        </Container>
      </Box>
    </>
  )
}

export default function App() {
  if (!isValidClerkKey) {
    // Fallback for missing Clerk key - shows landing page without auth.
    return <LandingPage />
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY} appearance={{ variables: { colorPrimary: '#7aa2ff' } }}>
        <SignedOut>
          <LandingPage />
        </SignedOut>
        <SignedIn>
          <AppShell />
        </SignedIn>
      </ClerkProvider>
    </ThemeProvider>
  )
}


