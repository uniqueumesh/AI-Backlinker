/**
 * Landing Footer Container - orchestrates footer sections and demos
 */
import React from 'react';
import { Container, Box } from '@mui/material';
import { motion } from 'framer-motion';
import { SignInButton } from '@clerk/clerk-react';
import { ManualVsAI } from './ManualVsAI';
import { EmailRefinement } from './EmailRefinement';
import { SubjectOptimization } from './SubjectOptimization';
import { Footer } from './Footer';

interface LandingFooterProps {
  cardVariants: any; // Framer Motion variants
}

export function LandingFooter({ cardVariants }: LandingFooterProps) {
  return (
    <>
      <ManualVsAI cardVariants={cardVariants} />
      
      <EmailRefinement cardVariants={cardVariants} />
      
      <SubjectOptimization cardVariants={cardVariants} />

      {/* Final CTA Section */}
      <Container component="section" maxWidth="md" sx={{ textAlign: 'center', py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
        <motion.div initial={{ opacity: 0, y: 50 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.5 }} transition={{ duration: 0.8 }}>
          <motion.h2 
            className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400"
            style={{ marginBottom: '2rem' }}
          >
            Ready to Redefine Your Domain Authority?
          </motion.h2>
          <motion.p 
            className="text-xl text-slate-300 mb-12"
            style={{ marginBottom: '3rem' }}
          >
            Join the future of backlinking with ALwrity Backlinker.
          </motion.p>
          <SignInButton mode="modal" forceRedirectUrl="/">
            <motion.button 
              className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 px-8 py-4 text-lg font-bold text-white shadow-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started with ALwrity Today
            </motion.button>
          </SignInButton>
        </motion.div>
      </Container>

      <Footer cardVariants={cardVariants} />
    </>
  );
}
