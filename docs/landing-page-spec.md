## ALwrity Landing Page — Visual Spec (Gemini-style hero)

### 1. Overview
This document outlines the plan to recreate the landing page's hero section to be visually indistinguishable from the provided Google Gemini screenshot.

**Core Principles:**
- **Visual Goal**: A pixel-perfect match of the Gemini hero (full-bleed canvas, diagonal spotlights, sparse starfield, specific typography, and single CTA).
- **Content**: The existing sections below the hero (Features, Manual vs. ALwrity, etc.) will remain unchanged.
- **Functionality**: This is a frontend-only visual update. The core backend logic, application functionality for signed-in users (`ResearchPage`), and the authentication flow will not be affected. Signed-out users will see this new landing page, and signed-in users will see the application as before.

---

### 2. Hero Section Specification

#### Layout
- **Canvas**: Full-bleed (no boxed/panel edges), with the height filling the initial viewport (`min-height: 100vh`).
- **Vertical Alignment**: The main content block (headline, subheadline, CTA) will be vertically centered.
- **Content Max-Width**: `1600px`, with all text and the CTA center-aligned.
- **Spacing**:
  - Headline → Subheadline: `12–16px`
  - Subheadline → CTA: `24-28px`

#### Background
- **Base Color**: Solid very-dark blue/black (`#0A0A1A`).
- **Spotlights**: A fixed, full-viewport overlay containing two soft, diagonal radial gradients.
  - Left Spotlight: `radial-gradient(1300px 900px at 0% 0%, rgba(122, 162, 255, 0.25), transparent 60%)`
  - Right Spotlight: `radial-gradient(1300px 900px at 100% 0%, rgba(125, 227, 198, 0.15), transparent 60%)`
  - Effect: A soft blur (`filter: blur(10px)`) will be applied to ensure the gradients blend smoothly without hard edges or bands.
- **Starfield**: An extremely sparse pattern of micro-dots to emulate a subtle starfield, created with layered `radial-gradient`s. Density will be kept very low.

#### Typography
- **Font Family**: `Inter`, `sans-serif`.
- **Headline (Wordmark)**
  - Text: `ALwrity`
  - Style: Flat white, no neon glow or shadow.
  - Font Weight: `900`
  - Letter Spacing: `-0.02em`
  - Line Height: `0.9` (very tight)
  - Size (Responsive): `clamp(80px, 14vw, 160px)`
  - Color: `#EAF1FF`
- **Subheadline**
  - Text: `Our most intelligent backlinking models.`
  - Size: `~20px` on desktop (`Typography variant="h6"` is acceptable).
  - Color: `rgba(234, 241, 255, 0.75)`
  - Max Width: `720px`, center-aligned.

#### Call to Action (CTA)
- **Button**: There will be exactly one primary button.
  - Label: `Get Started`
  - Shape: Pill (`borderRadius: 9999px`)
  - Size: `44px` height, `24px` horizontal padding.
  - Background: `linear-gradient(90deg, #4F8CFF, #6BB6FF)`
  - Text Color: Dark ink (`#071124`)
  - Shadow: `0 10px 30px rgba(79, 140, 255, 0.35)`
  - Icon: A simple `›` chevron glyph, vertically centered.
  - Hover Effect: A subtle lift (`transform: translateY(-1px)`) and a slightly stronger shadow.

#### Header/Navigation
- The header will remain minimal to avoid distracting from the hero.
- It will contain the brand name (`ALwrity AI Backlinker`) on the left and the sign-out button for authenticated users.

---

### 3. Implementation Steps (`frontend/src/pages/LandingPage.tsx`)
1.  **Structure**: The main component will use a full-bleed `Box` with `minHeight: 100vh` and `display: grid`, `placeItems: center` to ensure vertical centering.
2.  **Background**: A fixed-position `Box` will be used as an overlay (`z-index: 0`) to render the two spotlights and the starfield background. The main content will sit on top with a higher `z-index`.
3.  **Components**:
    -   A `styled` div (`BigHeadline`) will be created for the main headline to apply the precise typography settings.
    -   A `styled` MUI `Button` (`PillPrimary`) will be created for the CTA to match the design specification.
4.  **Cleanup**: All previous styles that create a boxed layout, animated orbs, or extra buttons will be removed.
5.  **Review**: The final implementation will be checked against the Gemini screenshot and this document's acceptance criteria across different screen sizes.

### 4. Acceptance Criteria
- The hero section is visually identical to the Gemini screenshot at a glance.
- The page is fully responsive, maintaining its appearance on mobile, tablet, and desktop.
- All existing content below the hero section is present and styled correctly.
- The login/logout flow remains unchanged.


