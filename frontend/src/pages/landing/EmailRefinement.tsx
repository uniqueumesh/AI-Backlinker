/**
 * Email Refinement Demo Component - interactive AI email improvement
 */
import React, { useState } from 'react';
import { Typography, Container, Box, Button, TextField, CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';
import { SignInButton } from '@clerk/clerk-react';
import { GradientText, PillPrimary } from '../LandingPage';

interface EmailRefinementProps {
  cardVariants: any;
}

export function EmailRefinement({ cardVariants }: EmailRefinementProps) {
  const [emailDraft, setEmailDraft] = useState('');
  const [refinedMessage, setRefinedMessage] = useState('');
  const [isRefining, setIsRefining] = useState(false);
  const [refineError, setRefineError] = useState('');
  
  const refineEmailDraft = async () => {
    if (!emailDraft.trim()) { 
      setRefineError('Please enter an email draft to refine.'); 
      setRefinedMessage(''); 
      return;
    }
    setIsRefining(true); 
    setRefineError(''); 
    setRefinedMessage('');
    await new Promise((r) => setTimeout(r, 800));
    setRefinedMessage('Hi there — Thanks for the great content on your site. I\'d love to contribute a concise, actionable guest post tailored to your audience. If you\'re open to it, I can share a few topic ideas this week. Cheers!');
    setIsRefining(false);
  };

  return (
    <Container component="section" maxWidth="md" sx={{ textAlign: 'center', py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
      <motion.div initial={{ opacity: 0, y: 50 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.5 }} transition={{ duration: 0.8 }}>
        <GradientText as="h2" variant="h2" sx={{ mb: 4 }}>Refine Your Outreach with AI ✨</GradientText>
        <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>Paste your email draft below and see an improved version.</Typography>
        <TextField 
          label="Your Email Draft" 
          multiline 
          rows={6} 
          fullWidth 
          variant="outlined" 
          value={emailDraft} 
          onChange={(e) => setEmailDraft(e.target.value)} 
          sx={{ mb: 3 }} 
        />
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
  );
}
