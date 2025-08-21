import React from 'react'
import { Typography, Container, Box } from '@mui/material'
import { motion, Variants } from 'framer-motion'
import { SignInButton } from '@clerk/clerk-react'
import { PillPrimary, BigHeadline } from './LandingPage'

interface LandingHeroProps {
  containerVariants: Variants
  itemVariants: Variants
}

export function LandingHero({ containerVariants, itemVariants }: LandingHeroProps) {
  return (
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
            <SignInButton mode="modal" forceRedirectUrl="/">
              <PillPrimary endIcon={<span style={{ display: 'inline-block', transform: 'translateY(1px)' }}>›</span>}>
                Get Started
              </PillPrimary>
            </SignInButton>
          </motion.div>
        </motion.div>
      </Container>
    </Box>
  )
}
