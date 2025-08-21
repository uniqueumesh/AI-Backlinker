/**
 * Footer Component - actual footer with links and copyright
 */
import React from 'react';
import { Typography, Box, Button } from '@mui/material';

interface FooterProps {
  cardVariants: any;
}

export function Footer({ cardVariants }: FooterProps) {
  return (
    <Box component="footer" sx={{ zIndex: 1, width: '100%', backgroundColor: 'rgba(10, 10, 26, 1)', p: 4, color: 'text.secondary', textAlign: 'center' }}>
      <Typography variant="body2" sx={{ mb: 2 }}>&copy; {new Date().getFullYear()} ALwrity Backlinker. All rights reserved.</Typography>
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3 }}>
        <Button color="inherit" sx={{ '&:hover': { color: 'primary.light' } }}>Privacy Policy</Button>
        <Button color="inherit" sx={{ '&:hover': { color: 'primary.light' } }}>Terms of Service</Button>
        <Button color="inherit" sx={{ '&:hover': { color: 'primary.light' } }}>Contact Us</Button>
      </Box>
    </Box>
  );
}
