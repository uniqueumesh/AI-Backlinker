import React, { useState, useEffect, type ReactNode } from 'react'
import { createTheme, ThemeProvider, styled } from '@mui/material/styles'
import { Typography, Button, Container, Box, Grid, Card, CardContent, CircularProgress, TextField, List, ListItem, ListItemText } from '@mui/material'
import { motion } from 'framer-motion'
import { SignInButton } from '@clerk/clerk-react'
// MUI Icons imports
import SearchIcon from '@mui/icons-material/Search'
import TuneIcon from '@mui/icons-material/Tune'
import MailOutlineIcon from '@mui/icons-material/MailOutline'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import CreditCardOutlinedIcon from '@mui/icons-material/CreditCardOutlined'
import ShowChartIcon from '@mui/icons-material/ShowChart'
import ForumOutlinedIcon from '@mui/icons-material/ForumOutlined'
import FingerprintIcon from '@mui/icons-material/Fingerprint'
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'

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

const GradientText = styled(Typography)(({ theme }) => ({
  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  backgroundClip: 'text',
  color: 'transparent',
}))

const BigHeadline = styled('div')({
  fontWeight: 900,
  letterSpacing: '-0.02em',
  lineHeight: 0.9,
  fontSize: 'clamp(80px, 14vw, 160px)',
  color: '#EAF1FF',
})

const PillPrimary = styled(Button)({
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

const FeatureCard = ({ icon: Icon, title, description, index, cardVariants }: any) => {
  const [isHovered, setIsHovered] = useState(false)
  return (
    <Grid item xs={12} sm={6} md={6}>
      <motion.div initial="offscreen" whileInView="onscreen" viewport={{ once: true, amount: 0.3 }} variants={cardVariants}>
        <Card
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          sx={{
            backgroundColor: 'background.paper',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            p: 3,
            minHeight: { xs: '180px', md: '220px' },
            position: 'relative',
            overflow: 'hidden',
            border: '1px solid rgba(96,165,250,0.4)',
            transition: 'all 0.4s ease-in-out',
            '&:hover': {
              borderColor: 'rgba(96,165,250,0.8)',
              transform: 'translateY(-12px) scale(1.02)',
              boxShadow: '0 20px 60px rgba(96,165,250,0.5), 0 0 40px rgba(167,139,250,0.4), 0 0 80px rgba(96,165,250,0.2) inset',
            },
          }}>
          <Box sx={{ color: index % 2 === 0 ? 'primary.main' : 'secondary.main', fontSize: { xs: 70, md: 90 }, mb: isHovered ? 1 : 2, transition: 'margin-bottom 0.3s ease-out', textShadow: `0 0 20px ${index % 2 === 0 ? 'rgba(96,165,250,0.7)' : 'rgba(167,139,250,0.7)'}` }}>
            <Icon sx={{ fontSize: 'inherit' }} />
          </Box>
          <Typography variant="h3" sx={{ color: 'text.primary', mb: isHovered ? 1 : 0, transition: 'margin-bottom 0.3s ease-out', fontSize: { xs: '1.5rem', md: '1.65rem' } }}>{title}</Typography>
          <motion.div initial={false} animate={{ opacity: isHovered ? 1 : 0, height: isHovered ? 'auto' : 0 }} transition={{ duration: 0.3, ease: 'easeOut' }} style={{ overflow: 'hidden', width: '100%' }}>
            {isHovered && (<Typography variant="body1" sx={{ color: 'text.secondary', mt: 1, fontSize: { xs: '0.95rem', md: '1.05rem' } }}>{description}</Typography>)}
          </motion.div>
        </Card>
      </motion.div>
    </Grid>
  )
}

export default function LandingPage() {
  const containerVariants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.15 } } }
  const itemVariants = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { type: 'spring', damping: 12, stiffness: 100 } } }
  const cardVariants = { offscreen: { y: 50, opacity: 0 }, onscreen: { y: 0, opacity: 1, transition: { type: 'spring', bounce: 0.4, duration: 0.8 } } }

  // AI Demo states (stubbed)
  const [emailDraft, setEmailDraft] = useState('')
  const [refinedMessage, setRefinedMessage] = useState('')
  const [isRefining, setIsRefining] = useState(false)
  const [refineError, setRefineError] = useState('')
  const refineEmailDraft = async () => {
    if (!emailDraft.trim()) { setRefineError('Please enter an email draft to refine.'); setRefinedMessage(''); return }
    setIsRefining(true); setRefineError(''); setRefinedMessage('')
    await new Promise((r) => setTimeout(r, 800))
    setRefinedMessage('Hi there — Thanks for the great content on your site. I\'d love to contribute a concise, actionable guest post tailored to your audience. If you\'re open to it, I can share a few topic ideas this week. Cheers!')
    setIsRefining(false)
  }
  const [subjectLineInput, setSubjectLineInput] = useState('')
  const [optimizedSubjectLines, setOptimizedSubjectLines] = useState<string[]>([])
  const [isOptimizingSubjectLine, setIsOptimizingSubjectLine] = useState(false)
  const [subjectLineError, setSubjectLineError] = useState('')
  const optimizeSubjectLine = async () => {
    if (!subjectLineInput.trim()) { setSubjectLineError('Please enter a subject line to optimize.'); setOptimizedSubjectLines([]); return }
    setIsOptimizingSubjectLine(true); setSubjectLineError(''); setOptimizedSubjectLines([])
    await new Promise((r) => setTimeout(r, 600))
    setOptimizedSubjectLines(['Quick guest post idea tailored for your audience', 'Can I contribute a concise, high‑value post?', 'Relevant guest post proposal for your readers', 'Idea to add value to your blog this week', 'Guest contribution to help your readers succeed'])
    setIsOptimizingSubjectLine(false)
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ backgroundColor: '#0A0A1A', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
        <BackgroundOverlay />

        {/* Minimal Header */}
        <Box component="header" sx={{ position: 'fixed', top: 0, left: 0, width: '100%', zIndex: 1000, py: 2, px: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 800, color: 'white' }}>ALwrity AI Backlinker</Typography>
        </Box>

        <Box component="main" id="home" sx={{ minHeight: '100vh', width: '100%', display: 'grid', placeItems: 'center', position: 'relative', zIndex: 1 }}>
          <Container maxWidth={false} sx={{ maxWidth: 1600, textAlign: 'center', px: 2 }}>
            <motion.div initial="hidden" animate="visible" variants={containerVariants}>
              <motion.div variants={itemVariants}>
                <BigHeadline>ALwrity</BigHeadline>
              </motion.div>
              <motion.div variants={itemVariants}>
                <Typography variant="h6" sx={{ color: 'rgba(234,241,255,.75)', mt: 1.5, mb: 3.5, maxWidth: 720, mx: 'auto', fontWeight: 400, lineHeight: 1.4 }}>
                  Our most intelligent backlinking models.
                </Typography>
              </motion.div>
              <motion.div variants={itemVariants}>
                <SignInButton mode="modal" redirectUrl="/">
                  <PillPrimary endIcon={<span style={{ display: 'inline-block', transform: 'translateY(1px)' }}>›</span>}>
                    Get Started
                  </PillPrimary>
                </SignInButton>
              </motion.div>
            </motion.div>
          </Container>
        </Box>

        {/* Feature Section */}
        <Container component="section" id="features" maxWidth="lg" sx={{ py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
          <GradientText component="h2" variant="h2" sx={{ textAlign: 'center', mb: { xs: 8, md: 12 } }}>ALwrity Features: Beyond Traditional Outreach</GradientText>
          <Grid container spacing={4}>
            {[
              { icon: SearchIcon, title: 'AI‑Powered Web Research & Prospecting', description: 'Automatically discover high‑authority websites and relevant opportunities using your keywords.' },
              { icon: TuneIcon, title: 'Intelligent Prospect Filtering', description: 'Focus on the most valuable leads with criteria‑based refinement.' },
              { icon: MailOutlineIcon, title: 'Verified Email Discovery', description: 'Scrape and suggest likely contact emails and support links.' },
              { icon: DescriptionOutlinedIcon, title: 'Personalized Draft Generation', description: 'Create bespoke drafts tailored to each site’s content and audience.' },
              { icon: CreditCardOutlinedIcon, title: 'Integrated Campaign Flow', description: 'Research → Draft → Send in one place with CSV exports.' },
              { icon: ShowChartIcon, title: 'SEO‑Aware Insights', description: 'Context snippets and links to guidelines/contact pages.' },
              { icon: ForumOutlinedIcon, title: 'Reply‑Aware Workflow', description: 'Prepare for follow‑ups and categorize outcomes (future).' },
              { icon: FingerprintIcon, title: 'Human‑in‑the‑Loop', description: 'You approve/edit everything before sending.' },
            ].map((f, i) => (
              <FeatureCard key={i} icon={f.icon} title={f.title} description={f.description} index={i} cardVariants={cardVariants} />
            ))}
          </Grid>
        </Container>

        {/* Manual vs ALwrity section */}
        <Container component="section" maxWidth="lg" sx={{ py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
          <GradientText component="h2" variant="h2" sx={{ textAlign: 'center', mb: { xs: 8, md: 12 } }}>
            The Backlinking Evolution: Manual vs. ALwrity
          </GradientText>
          <Grid container spacing={6} alignItems="flex-start">
            {[
              { step: '1. Prospect Identification', manual: { icon: AssignmentTurnedInIcon, description: 'Hours spent manually searching for relevant websites and filtering noise.' }, alwrity: { icon: AutoAwesomeIcon, description: 'AI pinpoints high‑authority, niche‑relevant prospects from your keywords.' } },
              { step: '2. Contact Discovery', manual: { icon: AssignmentTurnedInIcon, description: 'Frustrating scraping for emails; many are outdated or generic forms.' }, alwrity: { icon: AutoAwesomeIcon, description: 'Extracts likely contact emails and support links for direct outreach.' } },
              { step: '3. Content Opportunity Analysis', manual: { icon: AssignmentTurnedInIcon, description: 'Guesswork on what to pitch; generic suggestions with low engagement.' }, alwrity: { icon: AutoAwesomeIcon, description: 'Analyzes content gaps and suggests angles tailored to each site.' } },
              { step: '4. Email Personalization & Generation', manual: { icon: AssignmentTurnedInIcon, description: 'Time‑consuming manual writing; low personalization and response rates.' }, alwrity: { icon: AutoAwesomeIcon, description: 'Generates concise, friendly drafts personalized to the target site.' } },
              { step: '5. Outreach & Follow‑Ups', manual: { icon: AssignmentTurnedInIcon, description: 'Disorganized tracking and missed follow‑ups.' }, alwrity: { icon: AutoAwesomeIcon, description: 'One flow to send, track outcomes, and prepare follow‑ups.' } },
              { step: '6. Performance & Optimization', manual: { icon: AssignmentTurnedInIcon, description: 'Limited insight and slow iteration.' }, alwrity: { icon: AutoAwesomeIcon, description: 'Actionable context and exports to iterate quickly.' } },
            ].map((item, index) => (
              <Grid item xs={12} key={index}>
                <motion.div initial="offscreen" whileInView="onscreen" viewport={{ once: true, amount: 0.2 }} variants={cardVariants}>
                  <Card sx={{ p: 4, mb: 4, textAlign: 'left' }}>
                    <Typography variant="h4" sx={{ color: 'text.primary', mb: 3, fontWeight: 'bold' }}>{item.step}</Typography>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Box sx={{ p: 3, border: '1px dashed #FF6B6B', borderRadius: '12px', height: '100%', display: 'flex', flexDirection: 'column' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <item.manual.icon sx={{ color: '#FF6B6B', fontSize: 32, mr: 1.5 }} />
                            <Typography variant="h5" sx={{ color: '#FF6B6B', fontWeight: 'bold' }}>Traditional Manual Process</Typography>
                          </Box>
                          <Typography variant="body1" sx={{ color: 'text.secondary' }}>{item.manual.description}</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Box sx={{ p: 3, border: '1px dashed #6EE7B7', borderRadius: '12px', height: '100%', display: 'flex', flexDirection: 'column' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <item.alwrity.icon sx={{ color: '#6EE7B7', fontSize: 32, mr: 1.5 }} />
                            <Typography variant="h5" sx={{ color: '#6EE7B7', fontWeight: 'bold' }}>ALwrity AI Solution</Typography>
                          </Box>
                          <Typography variant="body1" sx={{ color: 'text.secondary' }}>{item.alwrity.description}</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>

        {/* AI Demo Sections (Stubbed) */}
        <Container component="section" maxWidth="md" sx={{ textAlign: 'center', py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
          <motion.div initial={{ opacity: 0, y: 50 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.5 }} transition={{ duration: 0.8 }}>
            <GradientText component="h2" variant="h2" sx={{ mb: 4 }}>Refine Your Outreach with AI ✨</GradientText>
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>Paste your email draft below and see an improved version.</Typography>
            <TextField label="Your Email Draft" multiline rows={6} fullWidth variant="outlined" value={emailDraft} onChange={(e) => setEmailDraft(e.target.value)} sx={{ mb: 3 }} />
            <PillPrimary onClick={refineEmailDraft} disabled={isRefining} endIcon={<span style={{ display: 'inline-block', transform: 'translateY(1px)' }}>›</span>}>
              {isRefining ? <CircularProgress size={24} sx={{ color: 'white' }} /> : 'Refine with ALwrity AI'}
            </PillPrimary>
            {refineError && <Typography color="error" sx={{ mt: 2 }}>{refineError}</Typography>}
            {refinedMessage && (
              <Box sx={{ mt: 4, p: 3, backgroundColor: 'background.paper', borderRadius: '12px', border: '1px solid', borderColor: 'primary.main', textAlign: 'left', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
                <Typography variant="h5" sx={{ color: 'primary.light', mb: 2 }}>AI‑Refined Message:</Typography>
                <Typography variant="body1" sx={{ color: 'text.primary', whiteSpace: 'pre-wrap' }}>{refinedMessage}</Typography>
              </Box>
            )}
          </motion.div>
        </Container>

        <Container component="section" maxWidth="md" sx={{ textAlign: 'center', py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
          <motion.div initial={{ opacity: 0, y: 50 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.5 }} transition={{ duration: 0.8 }}>
            <GradientText component="h2" variant="h2" sx={{ mb: 4 }}>Optimize Your Subject Lines with AI ✨</GradientText>
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>Enter context and get 5 suggestions.</Typography>
            <TextField label="Subject Line Context" multiline rows={3} fullWidth variant="outlined" value={subjectLineInput} onChange={(e) => setSubjectLineInput(e.target.value)} sx={{ mb: 3 }} />
            <PillPrimary onClick={optimizeSubjectLine} disabled={isOptimizingSubjectLine} endIcon={<span style={{ display: 'inline-block', transform: 'translateY(1px)' }}>›</span>}>
              {isOptimizingSubjectLine ? <CircularProgress size={24} sx={{ color: 'white' }} /> : 'Generate Subject Lines'}
            </PillPrimary>
            {subjectLineError && <Typography color="error" sx={{ mt: 2 }}>{subjectLineError}</Typography>}
            {optimizedSubjectLines.length > 0 && (
              <Box sx={{ mt: 4, p: 3, backgroundColor: 'background.paper', borderRadius: '12px', border: '1px solid', borderColor: 'secondary.main', textAlign: 'left', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
                <Typography variant="h5" sx={{ color: 'secondary.light', mb: 2 }}>AI‑Optimized Subject Lines:</Typography>
                <List dense sx={{ color: 'text.primary' }}>{optimizedSubjectLines.map((line, idx) => (<ListItem key={idx} sx={{ py: 0.5 }}><ListItemText primary={`• ${line}`} /></ListItem>))}</List>
              </Box>
            )}
          </motion.div>
        </Container>

        {/* Final CTA Section */}
        <Container component="section" maxWidth="md" sx={{ textAlign: 'center', py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
          <motion.div initial={{ opacity: 0, y: 50 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.5 }} transition={{ duration: 0.8 }}>
            <GradientText component="h2" variant="h2" sx={{ mb: 4 }}>Ready to Redefine Your Domain Authority?</GradientText>
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 6 }}>Join the future of backlinking with ALwrity Backlinker.</Typography>
            <SignInButton mode="modal" redirectUrl="/">
              <PillPrimary>Get Started with ALwrity Today</PillPrimary>
            </SignInButton>
          </motion.div>
        </Container>

        <Box component="footer" sx={{ zIndex: 1, width: '100%', backgroundColor: 'rgba(10, 10, 26, 1)', p: 4, color: 'text.secondary', textAlign: 'center' }}>
          <Typography variant="body2" sx={{ mb: 2 }}>&copy; {new Date().getFullYear()} ALwrity Backlinker. All rights reserved.</Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3 }}>
            <Button color="inherit" sx={{ '&:hover': { color: 'primary.light' } }}>Privacy Policy</Button>
            <Button color="inherit" sx={{ '&:hover': { color: 'primary.light' } }}>Terms of Service</Button>
            <Button color="inherit" sx={{ '&:hover': { color: 'primary.light' } }}>Contact Us</Button>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  )
}


