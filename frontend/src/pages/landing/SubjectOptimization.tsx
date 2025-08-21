/**
 * Subject Line Optimization Demo Component - AI subject line generation
 */
import React, { useState } from 'react';
import { Typography, Container, Box, Button, TextField, CircularProgress, List, ListItem, ListItemText } from '@mui/material';
import { motion } from 'framer-motion';
import { SignInButton } from '@clerk/clerk-react';
import { GradientText, PillPrimary } from '../LandingPage';

interface SubjectOptimizationProps {
  cardVariants: any;
}

export function SubjectOptimization({ cardVariants }: SubjectOptimizationProps) {
  const [subjectLineInput, setSubjectLineInput] = useState('');
  const [optimizedSubjectLines, setOptimizedSubjectLines] = useState<string[]>([]);
  const [isOptimizingSubjectLine, setIsOptimizingSubjectLine] = useState(false);
  const [subjectLineError, setSubjectLineError] = useState('');
  
  const optimizeSubjectLine = async () => {
    if (!subjectLineInput.trim()) { 
      setSubjectLineError('Please enter a subject line to optimize.'); 
      setOptimizedSubjectLines([]); 
      return;
    }
    setIsOptimizingSubjectLine(true); 
    setSubjectLineError(''); 
    setOptimizedSubjectLines([]);
    await new Promise((r) => setTimeout(r, 600));
    setOptimizedSubjectLines([
      'Quick guest post idea tailored for your audience', 
      'Can I contribute a concise, high‑value post?', 
      'Relevant guest post proposal for your readers', 
      'Idea to add value to your blog this week', 
      'Guest contribution to help your readers succeed'
    ]);
    setIsOptimizingSubjectLine(false);
  };

  return (
    <Container component="section" maxWidth="md" sx={{ textAlign: 'center', py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
      <motion.div initial={{ opacity: 0, y: 50 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.5 }} transition={{ duration: 0.8 }}>
        <GradientText as="h2" variant="h2" sx={{ mb: 4 }}>Optimize Your Subject Lines with AI ✨</GradientText>
        <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>Enter context and get 5 suggestions.</Typography>
        <TextField 
          label="Subject Line Context" 
          multiline 
          rows={3} 
          fullWidth 
          variant="outlined" 
          value={subjectLineInput} 
          onChange={(e) => setSubjectLineInput(e.target.value)} 
          sx={{ mb: 3 }} 
        />
        <PillPrimary onClick={optimizeSubjectLine} disabled={isOptimizingSubjectLine} endIcon={<span style={{ display: 'inline-block', transform: 'translateY(1px)' }}>›</span>}>
          {isOptimizingSubjectLine ? <CircularProgress size={24} sx={{ color: 'white' }} /> : 'Generate Subject Lines'}
        </PillPrimary>
        {subjectLineError && <Typography color="error" sx={{ mt: 2 }}>{subjectLineError}</Typography>}
        {optimizedSubjectLines.length > 0 && (
          <Box sx={{ mt: 4, p: 3, backgroundColor: 'background.paper', borderRadius: '12px', border: '1px solid', borderColor: 'secondary.main', textAlign: 'left', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
            <Typography variant="h5" sx={{ color: 'secondary.light', mb: 2 }}>AI‑Optimized Subject Lines:</Typography>
            <List dense sx={{ color: 'text.primary' }}>
              {optimizedSubjectLines.map((line, idx) => (
                <ListItem key={idx} sx={{ py: 0.5 }}>
                  <ListItemText primary={`• ${line}`} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </motion.div>
    </Container>
  );
}
