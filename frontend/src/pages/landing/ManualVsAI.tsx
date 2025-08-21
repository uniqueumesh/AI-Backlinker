/**
 * Manual vs AI Comparison Component - shows benefits of automation
 */
import React from 'react';
import { Typography, Container, Grid, Card, Box } from '@mui/material';
import { motion } from 'framer-motion';
import { GradientText } from '../LandingPage';
// MUI Icons imports
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

interface ManualVsAIProps {
  cardVariants: any;
}

export function ManualVsAI({ cardVariants }: ManualVsAIProps) {
  const comparisonSteps = [
    { step: '1. Prospect Identification', manual: { icon: AssignmentTurnedInIcon, description: 'Hours spent manually searching for relevant websites and filtering noise.' }, alwrity: { icon: AutoAwesomeIcon, description: 'AI pinpoints high‑authority, niche‑relevant prospects from your keywords.' } },
    { step: '2. Contact Discovery', manual: { icon: AssignmentTurnedInIcon, description: 'Frustrating scraping for emails; many are outdated or generic forms.' }, alwrity: { icon: AutoAwesomeIcon, description: 'Extracts likely contact emails and support links for direct outreach.' } },
    { step: '3. Content Opportunity Analysis', manual: { icon: AssignmentTurnedInIcon, description: 'Guesswork on what to pitch; generic suggestions with low engagement.' }, alwrity: { icon: AutoAwesomeIcon, description: 'Analyzes content gaps and suggests angles tailored to each site.' } },
    { step: '4. Email Personalization & Generation', manual: { icon: AssignmentTurnedInIcon, description: 'Time‑consuming manual writing; low personalization and response rates.' }, alwrity: { icon: AutoAwesomeIcon, description: 'Generates concise, friendly drafts personalized to the target site.' } },
    { step: '5. Outreach & Follow‑Ups', manual: { icon: AssignmentTurnedInIcon, description: 'Disorganized tracking and missed follow‑ups.' }, alwrity: { icon: AutoAwesomeIcon, description: 'One flow to send, track outcomes, and prepare follow‑ups.' } },
    { step: '6. Performance & Optimization', manual: { icon: AssignmentTurnedInIcon, description: 'Limited insight and slow iteration.' }, alwrity: { icon: AutoAwesomeIcon, description: 'Actionable context and exports to iterate quickly.' } },
  ];

  return (
    <Container component="section" maxWidth="lg" sx={{ py: { xs: 8, md: 12 }, px: 2, zIndex: 1, backgroundColor: '#0A0A1A' }}>
      <GradientText as="h2" variant="h2" sx={{ textAlign: 'center', mb: { xs: 8, md: 12 } }}>
        The Backlinking Evolution: Manual vs. ALwrity
      </GradientText>
      <Grid container spacing={6} alignItems="flex-start">
        {comparisonSteps.map((item, index) => (
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
  );
}
