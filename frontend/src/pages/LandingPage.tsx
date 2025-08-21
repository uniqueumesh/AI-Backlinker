import React from 'react'
import { createTheme, ThemeProvider, styled } from '@mui/material/styles'
import { Typography, Button, Container, Box } from '@mui/material'
import { motion, Variants } from 'framer-motion'
import { LandingHero } from './LandingHero'
import { LandingFeatures } from './LandingFeatures'
import { LandingFooter } from './landing'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#60A5FA' }, // Blue from gradient
    secondary: { main: '#A78BFA' }, // Purple from gradient
    background: { default: '#0A0A1A', paper: 'rgba(25, 25, 45, 0.7)' }, // Very dark blue-black
    text: { primary: '#FFFFFF', secondary: '#A0A0B0' }, // Gray for subtle text
  },
  typography: {
    fontFamily: 'Inter, sans-serif',
    h2: { fontWeight: 700, fontSize: '2.5rem', '@media (min-width:600px)': { fontSize: '3.5rem' }, marginBottom: '1rem' },
    h3: { fontWeight: 600, fontSize: '1.75rem' },
    h4: { fontWeight: 600, fontSize: '1.5rem' },
    h5: { fontWeight: 500, fontSize: '1.25rem' },
    body1: { fontSize: '1.125rem' },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '16px',
          backdropFilter: 'blur(5px)',
          background: 'linear-gradient(145deg, rgba(25,25,45,0.7), rgba(15,15,30,0.7))',
          border: '1px solid rgba(96,165,250,0.2)',
          boxShadow: '0 8px 30px rgba(0,0,0,0.2)',
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          '& fieldset': { borderColor: 'rgba(96,165,250,0.4)', transition: 'border-color 0.3s ease' },
          '&:hover fieldset': { borderColor: 'primary.main' },
          '&.Mui-focused fieldset': { borderColor: 'secondary.main', borderWidth: '2px' },
        },
        input: { color: '#FFFFFF', padding: '14px' },
      },
    },
    MuiInputLabel: { styleOverrides: { root: { color: 'text.secondary', '&.Mui-focused': { color: 'secondary.main' } } } },
  },
})

export const GradientText = styled(Typography)(({ theme }) => ({
  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  backgroundClip: 'text',
  color: 'transparent',
}))

export const BigHeadline = styled('div')({
  fontWeight: 900,
  letterSpacing: '-0.02em',
  lineHeight: 0.9,
  fontSize: 'clamp(80px, 14vw, 160px)',
  color: '#EAF1FF',
})

export const PillPrimary = styled(Button)({
  borderRadius: 9999,
  paddingInline: 24,
  height: 44,
  textTransform: 'none',
  fontWeight: 700,
  background: 'linear-gradient(90deg, #4F8CFF, #6BB6FF)',
  color: '#071124',
  boxShadow: '0 10px 30px rgba(79,140,255,.35)',
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-1px)',
    boxShadow: '0 12px 35px rgba(79,140,255,.45)',
  },
})

const BackgroundOverlay = styled(Box)({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  pointerEvents: 'none',
  overflow: 'hidden',
  zIndex: 0,
  '&::before': {
    content: '""',
    position: 'absolute',
    top: '-10%',
    left: '-10%',
    width: '120%',
    height: '120%',
    background: 'radial-gradient(1300px 900px at 0% 0%, rgba(122,162,255,0.35), transparent 60%)', // Increased intensity
    filter: 'blur(10px)',
  },
  '&::after': {
    content: '""',
    position: 'absolute',
    top: '-10%',
    right: '-10%',
    width: '120%',
    height: '120%',
    background: 'radial-gradient(1300px 900px at 100% 0%, rgba(125,227,198,0.25), transparent 60%)', // Increased intensity
    filter: 'blur(10px)',
  },
  // Sparse starfield
  backgroundImage: `
    radial-gradient(1px 1px at 18% 22%, rgba(255,255,255,.35), transparent 60%),
    radial-gradient(1px 1px at 42% 12%, rgba(255,255,255,.30), transparent 60%),
    radial-gradient(1px 1px at 66% 28%, rgba(255,255,255,.25), transparent 60%),
    radial-gradient(1px 1px at 82% 16%, rgba(255,255,255,.30), transparent 60%),
    radial-gradient(1px 1px at 24% 8%, rgba(255,255,255,.25), transparent 60%),
    radial-gradient(1px 1px at 72% 6%, rgba(255,255,255,.20), transparent 60%)
  `,
})

export default function LandingPage() {
  const containerVariants: Variants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.15 } } }
  const itemVariants: Variants = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { type: 'spring', damping: 12, stiffness: 100 } } }
  const cardVariants: Variants = { offscreen: { y: 50, opacity: 0 }, onscreen: { y: 0, opacity: 1, transition: { type: 'spring', bounce: 0.4, duration: 0.8 } } }

  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ backgroundColor: '#0A0A1A', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
        <BackgroundOverlay />

        {/* Minimal Header */}
        <Box component="header" sx={{ position: 'fixed', top: 0, left: 0, width: '100%', zIndex: 1000, py: 2, px: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 800, color: 'white' }}>ALwrity AI Backlinker</Typography>
        </Box>

        <LandingHero containerVariants={containerVariants} itemVariants={itemVariants} />
        <LandingFeatures cardVariants={cardVariants} />
        <LandingFooter cardVariants={cardVariants} />
      </Box>
    </ThemeProvider>
  )
}


