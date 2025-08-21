import React, { useState } from 'react'
import { Typography, Container, Grid, Card, Box } from '@mui/material'
import { motion, Variants } from 'framer-motion'
import { GradientText } from './LandingPage'
// MUI Icons imports
import SearchIcon from '@mui/icons-material/Search'
import TuneIcon from '@mui/icons-material/Tune'
import MailOutlineIcon from '@mui/icons-material/MailOutline'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import CreditCardOutlinedIcon from '@mui/icons-material/CreditCardOutlined'
import ShowChartIcon from '@mui/icons-material/ShowChart'
import ForumOutlinedIcon from '@mui/icons-material/ForumOutlined'
import FingerprintIcon from '@mui/icons-material/Fingerprint'

interface FeatureCardProps {
  icon: any
  title: string
  description: string
  index: number
  cardVariants: Variants
}

const FeatureCard = ({ icon: Icon, title, description, index, cardVariants }: FeatureCardProps) => {
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
          <Box sx={{ 
            color: index % 2 === 0 ? 'primary.main' : 'secondary.main', 
            fontSize: { xs: 70, md: 90 }, 
            mb: isHovered ? 1 : 2, 
            transition: 'margin-bottom 0.3s ease-out', 
            textShadow: `0 0 20px ${index % 2 === 0 ? 'rgba(96,165,250,0.7)' : 'rgba(167,139,250,0.7)'}` 
          }}>
            <Icon sx={{ fontSize: 'inherit' }} />
          </Box>
          <Typography variant="h3" sx={{ 
            color: 'text.primary', 
            mb: isHovered ? 1 : 0, 
            transition: 'margin-bottom 0.3s ease-out', 
            fontSize: { xs: '1.5rem', md: '1.65rem' } 
          }}>
            {title}
          </Typography>
          <motion.div 
            initial={false} 
            animate={{ opacity: isHovered ? 1 : 0, height: isHovered ? 'auto' : 0 }} 
            transition={{ duration: 0.3, ease: 'easeOut' }} 
            style={{ overflow: 'hidden', width: '100%' }}
          >
            {isHovered && (
              <Typography variant="body1" sx={{ 
                color: 'text.secondary', 
                mt: 1, 
                fontSize: { xs: '0.95rem', md: '1.05rem' } 
              }}>
                {description}
              </Typography>
            )}
          </motion.div>
        </Card>
      </motion.div>
    </Grid>
  )
}

interface LandingFeaturesProps {
  cardVariants: Variants
}

export function LandingFeatures({ cardVariants }: LandingFeaturesProps) {
  const features = [
    { icon: SearchIcon, title: 'AI‑Powered Web Research & Prospecting', description: 'Automatically discover high‑authority websites and relevant opportunities using your keywords.' },
    { icon: TuneIcon, title: 'Intelligent Prospect Filtering', description: 'Focus on the most valuable leads with criteria‑based refinement.' },
    { icon: MailOutlineIcon, title: 'Verified Email Discovery', description: 'Scrape and suggest likely contact emails and support links.' },
    { icon: DescriptionOutlinedIcon, title: 'Personalized Draft Generation', description: "Create bespoke drafts tailored to each site's content and audience." },
    { icon: CreditCardOutlinedIcon, title: 'Integrated Campaign Flow', description: 'Research → Draft → Send in one place with CSV exports.' },
    { icon: ShowChartIcon, title: 'SEO‑Aware Insights', description: 'Context snippets and links to guidelines/contact pages.' },
    { icon: ForumOutlinedIcon, title: 'Reply‑Aware Workflow', description: 'Prepare for follow‑ups and categorize outcomes (future).' },
    { icon: FingerprintIcon, title: 'Human‑in‑the‑Loop', description: 'You approve/edit everything before sending.' },
  ]

  return (
    <Container component="section" id="features" maxWidth="lg" sx={{ py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
      <GradientText as="h2" variant="h2" sx={{ textAlign: 'center', mb: { xs: 8, md: 12 } }}>
        ALwrity Features: Beyond Traditional Outreach
      </GradientText>
      <Grid container spacing={4}>
        {features.map((f, i) => (
          <FeatureCard key={i} icon={f.icon} title={f.title} description={f.description} index={i} cardVariants={cardVariants} />
        ))}
      </Grid>
    </Container>
  )
}
