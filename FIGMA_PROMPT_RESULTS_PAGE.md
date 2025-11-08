# Figma AI Prompt: Dataset Analysis Results Page for Senalign

## Overview
Design a modern, professional dataset quality analysis results page for a data science SaaS application. The page displays comprehensive analysis results including quality scores, data issues, AI recommendations, and helpful resources. The design should be clean, scannable, and data-focused with excellent information hierarchy.

## Page Layout & Structure

### 1. TOP HEADER BAR (Fixed)
- Full-width header bar spanning the entire page width
- Left side: Back arrow button (clickable icon) + "Dataset Quality Analysis" title + problem description subtitle in smaller text
- Right side: "Export Report" button with download icon
- Add subtle bottom border/shadow to separate from content
- Height: ~80px

### 2. MAIN CONTENT AREA (Scrollable)
- Maximum width: 1200px, centered on page
- Padding: 24px on all sides
- Background: Light neutral gray (#F9FAFB or similar)

### 3. OVERALL SCORE CARD (Hero Section)
- Large prominent card at the top
- Left side: "Overall Quality Score" heading + dataset dimensions (e.g., "50,000 rows × 15 columns")
- Right side: LARGE numerical score (e.g., "87") displayed prominently
- Full-width progress bar at bottom showing the score percentage
- Height: ~140px
- Use thick border (2-3px) to make it stand out

### 4. COLLAPSIBLE SECTION CARDS (Main Content)
Design 8 collapsible section cards in this exact order:

#### Card A: Dataset Overview
- Section header with database icon + "Dataset Overview" title + chevron expand/collapse indicator
- When expanded, show:
  - 3-column grid of stat boxes: Total Rows | Total Columns | Problem Type
  - Each stat box has colored background (light blue, light green, light purple) with thick colored border
  - Below stats: "Column Data Types" section showing grid of small cards displaying data type counts (e.g., "int64: 5", "float64: 3", "object: 7")

#### Card B: Quality Metrics
- Section header with trending-up icon + "Quality Metrics" title + chevron
- When expanded, show:
  - 4-column grid of quality score cards
  - Each card shows: metric name (e.g., "Completeness", "Consistency", "Validity", "Overall") + large score number + small progress bar
  - Each card has colored background based on score (high=green tint, medium=yellow tint, low=red tint) with matching border

#### Card C: Privacy Alert (Conditional - only if PII detected)
- FULL CARD has red/pink background tint with red border
- Shield icon + "Privacy Alert: PII Detected" heading in red
- Description text explaining number of columns with PII
- White background sub-card listing detected PII types as colored badges
- Height: ~160px

#### Card D: Data Quality Issues
- Section header with alert triangle icon + "Data Quality Issues" + chevron
- When expanded, show 3 sub-sections vertically stacked:
  
  **Sub-section D1: Missing Values**
  - Orange warning icon + heading + count (e.g., "Missing Values (5 columns)")
  - 3-column responsive grid of column cards
  - Each card: column name + badge showing missing count + small progress bar
  - Orange color scheme (light orange background, orange border)
  
  **Sub-section D2: Outliers**
  - Red target icon + heading + count (e.g., "Outliers (3 columns)")
  - Same grid layout as D1
  - Red color scheme
  
  **Sub-section D3: Class Imbalance**
  - Purple users icon + heading + count (e.g., "Class Imbalance (2 columns)")
  - Grid of cards showing column name + imbalance ratio badge + distribution breakdown
  - Purple color scheme

#### Card E: AI Recommendations
- Section header with checkmark icon + "AI Recommendations (8)" + chevron
- When expanded, show vertical list of recommendation cards
- Each recommendation card contains:
  - Top: Severity badge (CRITICAL/HIGH/MEDIUM/LOW with matching colors) + category name in bold
  - Middle: Suggestion text description
  - Bottom: Dark code block with syntax-highlighted example code (if available)
- Card has subtle border and padding
- Spacing between cards: 16px

#### Card F: Priority Actions
- FULL CARD has yellow/amber background tint with yellow border
- Alert triangle icon + "Priority Actions" heading
- Bulleted list of action items with colored bullet points
- Each action item on separate line with left padding
- Height: Variable based on number of actions

#### Card G: Helpful Resources
- Section header with book icon + "Helpful Resources (12)" + chevron
- When expanded, show:
  - 2-column responsive grid of resource cards
  - Each resource card shows:
    - Top: Small icon for resource type (github, book, video, etc.) + type label + relevance percentage
    - Middle: Resource title as clickable link
    - Bottom: Brief description text
  - Card has hover effect (subtle background change)
  - Border on all resource cards

#### Card H: Overall Assessment
- Simple card with light gray background
- "Overall Assessment" heading
- Multi-line paragraph of AI-generated summary text
- No collapsible behavior - always visible
- Readable line height and font size

## Visual Design Guidelines

### Typography Hierarchy
- Page title: 24px, bold, dark gray/black
- Section headings: 18px, semi-bold
- Card titles: 16px, semi-bold
- Body text: 14px, regular
- Small text/labels: 12px, regular
- Score numbers: 32-48px, bold

### Spacing & Rhythm
- Between cards: 24px vertical spacing
- Card padding: 24px internal padding
- Section header padding: 16px
- Grid gaps: 16px between grid items
- Consistent 8px spacing unit throughout

### Card Design
- All cards: rounded corners (8-12px border radius)
- Subtle shadow on cards (use soft drop shadow)
- Collapsible sections: clear expand/collapse affordance with chevron icons
- Hover states on interactive elements

### Progress Bars
- Height: 8px
- Rounded ends (fully rounded)
- Background: light gray
- Fill color: varies by score (green for high, yellow for medium, red for low)
- Smooth, filled appearance

### Badges
- Pill-shaped (fully rounded borders)
- Small padding (4px horizontal, 2px vertical)
- Various colors for different types:
  - Severity: Red (critical), Orange (high), Yellow (medium), Blue (low)
  - Resource types: Gray background with subtle border
  - PII types: Red/pink background

### Icons
- Size: 20px for section headers, 16px for inline elements
- Style: Line icons (stroke-based, not filled)
- Consistent weight across all icons
- Color: Match the section theme or use neutral gray

### Color Semantics (Reference for shades, not specific hex values)
- Success/High scores: Green tints and borders
- Warning/Medium: Yellow/Amber tints and borders
- Error/Critical: Red/Pink tints and borders
- Info: Blue tints and borders
- Neutral: Purple tints for special categories
- Code blocks: Dark gray/black background (#1F2937) with light text

### Grid Systems
- Stat boxes: 3 columns on desktop, stack on mobile
- Quality metrics: 4 columns on desktop, 2 on tablet, 1 on mobile
- Issue cards: 3 columns on desktop, 2 on tablet, 1 on mobile
- Resources: 2 columns on desktop, 1 on mobile

## Interactive Elements

### Collapsible Sections
- Clear visual indicator (chevron icon) that rotates when expanded/collapsed
- Smooth animation when toggling (fade and slide)
- Click entire header bar to toggle (not just icon)
- Hover effect on header to indicate clickability

### Buttons
- Primary button (Export): Dark background with white text, rounded corners
- Back button: Icon only, circular or square with rounded corners
- Hover states: Slight darkening or color shift

### Links
- Resource titles: Blue color, underline on hover
- External links: Consider adding small external link icon

## Mobile Responsiveness
- All grids collapse to single column on mobile
- Maintain padding and spacing proportionally
- Score numbers may reduce in size slightly
- Ensure touch-friendly hit targets (minimum 44px)
- Keep header fixed on scroll

## Empty States
If no data exists for a section:
- Show section collapsed by default OR
- Show light gray placeholder message inside section
- Don't remove the section entirely

## Data Density
- Balance between comprehensive information and readability
- Use progressive disclosure (collapsible sections) to prevent overwhelm
- Most important information (overall score, overview, quality metrics) visible by default
- Detailed breakdowns hidden in collapsed sections

## Page Loading States
Consider designing states for:
- Initial page load: Show skeleton screens for cards
- No data available: Empty state with helpful message and back button

## Accessibility Considerations
- High contrast between text and backgrounds
- Large enough touch targets
- Clear visual hierarchy
- Icons accompanied by text labels
- Color not the only indicator (use icons + text too)

## Design Tone
- Professional and trustworthy
- Data-focused and analytical
- Clean and modern (not overly decorative)
- Confident and authoritative
- Helpful and educational (not intimidating)

## Final Notes
- Prioritize scannability - users should quickly grasp data quality at a glance
- Use whitespace generously to prevent visual clutter
- Maintain consistent visual patterns across all sections
- Ensure the design scales well with varying amounts of data
- Focus on STRUCTURE and LAYOUT - Figma will handle specific colors and styling based on its design system