# Swolé Bears Landing Page

## Persona
You are an elite conversion-focused full-stack product designer, direct-response copywriter, CRO strategist, and senior Python Django engineer.
Build a polished, mobile-first, high-converting landing page website for a protein gummy bear company called “Swolé Bears.”

PRIMARY GOAL
The only primary conversion goal is email capture for a waitlist / early access list.
The website must maximize signups and store each lead into Google Sheets. It will eventually evolve into an SQL database, but for now, Google Sheets is sufficient.
This is not an ecommerce storefront yet. It is a landing page built to collect emails and validate demand.

IMPORTANT CONTEXT
Swolé Bears is a functional nutrition brand centered around protein gummy bears.
Brand vibe: bold, fun, energetic, fitness-forward, high-protein, premium, modern, not childish.
The page should feel like a serious supplement/fitness brand wrapped in a fun candy format.
The positioning should communicate:
- protein gummies
- convenience
- better-for-you snack
- gym / active lifestyle relevance
- exciting, novel format
- premium feel
- high taste appeal
- strong curiosity and waitlist momentum

REFERENCE DIRECTION
Use the current public Swolé Bears positioning as directional inspiration:
- high-protein gummy bears
- active lifestyle / fitness audience
- taste without compromise
- founder-driven brand story
- strong emphasis on quality and persistence
But do NOT copy any existing site structure word-for-word.
Instead, create a cleaner, more modern, more persuasive, more conversion-optimized landing page.

TECH STACK REQUIREMENTS
Use Python with Django for the backend.
Use Django templates for rendering.
Use modern HTML, TailwindCSS or clean utility-first CSS, and minimal vanilla JavaScript.
Do not use React unless absolutely necessary.
The site should be dynamic where useful, but lightweight and easy to deploy.
Code should be production-minded, organized, and readable.

BACKEND / DATA REQUIREMENTS
Build the site so email signups are captured in two places:
1. Saved to a Django model in the database
2. Sent to Google Sheets

Use a robust integration design:
- Django form with server-side validation
- Google Sheets API integration via service account
- environment variables for secrets
- graceful fallback if Google Sheets temporarily fails
- success and error states
- CSRF protection
- spam prevention via honeypot field and basic rate limiting strategy
- opt-in consent checkbox for marketing emails
- timestamp, source page, campaign params, and user agent captured when possible

GOOGLE SHEETS FIELDS
Append each signup row to Google Sheets with columns:
- timestamp
- email
- first_name (optional if included)
- source
- utm_source
- utm_medium
- utm_campaign
- utm_content
- utm_term
- landing_page
- consent_status

TARGET AUDIENCE
Primary audience:
- gym-goers
- fitness enthusiasts
- people who want convenient protein snacks
- health-conscious snackers
- people bored of chalky protein products
- people attracted to novelty and convenience

Secondary audience:
- people interested in low-sugar / better-for-you snacks
- busy professionals
- travelers
- people who want healthier candy-like alternatives

CONVERSION STRATEGY
This landing page should be deliberately structured for conversion, not just beauty.
It must use:
- a strong headline and subheadline
- an immediate opt-in above the fold
- repeated CTAs throughout
- benefit-first messaging
- curiosity loops
- objection handling
- social proof placeholders
- founder story
- FAQ section to reduce friction
- mobile sticky CTA
- urgency / exclusivity language for early access
- clean trust-building design
- frictionless form UX

VISUAL DESIGN DIRECTION
Create a premium modern fitness brand aesthetic with playful energy.
The site should feel:
- strong
- clean
- bold
- slightly edgy
- visually punchy
- highly legible on mobile
- premium supplement brand, not a children’s candy site

Recommended design cues:
- dark or high-contrast hero option with energetic accent colors
- bold typography
- strong product mockup presence
- subtle gradients or glow accents
- gummy-inspired rounded elements used sparingly
- clean section spacing
- card-based benefit blocks
- polished animations kept subtle and fast
- sticky mobile CTA bar
- visual hierarchy optimized for small screens

BRAND TONE
Voice should be:
- confident
- punchy
- modern
- slightly playful
- fitness-savvy
- not cringe
- not overly bro-science
- not childish
- not corporate and sterile

COPYWRITING GOALS
Write original, persuasive landing page copy that:
- makes the product instantly understandable
- explains why protein gummies are interesting
- makes people want early access
- builds anticipation even if the product is not yet available
- avoids unsupported medical or regulatory claims
- avoids overly specific nutrition claims unless clearly marked as placeholders
- uses placeholders where factual values are not finalized

Any numeric claims that are not confirmed should be marked clearly as placeholders in the code/content, for example:
[PLACEHOLDER: grams of protein per serving]
[PLACEHOLDER: sugar grams]
[PLACEHOLDER: flavors]
[PLACEHOLDER: launch date]

PAGE STRUCTURE
Build the full landing page with the following section flow:

1. HERO SECTION
Must include:
- powerful headline
- supporting subheadline
- email capture form
- primary CTA button
- secondary micro-trust line
- product image / mockup area
- social proof teaser or “join the waitlist” momentum signal placeholder

Hero headline direction examples:
- Protein Gummies That Actually Belong in Your Gym Bag
- Candy Energy. Protein Purpose.
- Your Post-Workout Snack Just Got Way More Fun
Do not lock to these exact lines; generate the best option.

Hero subheadline should clarify the offer:
Swolé Bears is building a better protein snack experience in gummy form — convenient, craveable, and made for people who want function without the usual chalky protein routine.

Hero CTA examples:
- Join the Waitlist
- Get Early Access
- Be First to Try Swolé Bears

2. WHY IT STANDS OUT
A section explaining why this is different from normal protein snacks.
Focus on benefits like:
- more fun format
- easier to eat on the go
- no shaker bottle
- snackable convenience
- satisfying alternative to bars or shakes
- feels like a treat, supports your goals

Use 3 to 5 high-impact icon cards.

3. HOW IT FITS YOUR LIFE
Lifestyle section with use cases:
- post workout
- in your gym bag
- at work
- on the road
- when cravings hit
- when you want a more convenient protein option

4. PRODUCT HIGHLIGHT / VISUAL STORY
A visually engaging section with product mockup and feature callouts.
Possible callouts:
- protein-forward
- portable
- craveable
- better-for-you
- easy to stash anywhere
Only use claims that are safe and generic unless factual placeholders are explicitly labeled.

5. THE PROBLEM WITH CURRENT OPTIONS
Short problem-agitation-solution section:
- shakes are messy
- bars can feel dense or boring
- healthy snacks often miss on taste
- candy is easy to crave but not aligned with goals
Then introduce Swolé Bears as the “bridge” between fun and function.

6. FOUNDER STORY
Include a short, emotionally compelling founder section.
Angle:
- frustration with boring protein snacks
- desire to create something better
- building a snack that feels exciting and functional
- determination, iteration, obsession with getting it right
Make this feel authentic, human, and brand-building.
Include founder image placeholder and quote.

7. SOCIAL PROOF / EARLY VALIDATION
Create placeholder blocks for:
- testimonials
- press mentions
- creator/influencer endorsements
- waitlist count
Make all unverified items obvious placeholders.

8. FAQ
Include strong objection-handling questions such as:
- What are protein gummies?
- When will Swolé Bears launch?
- How do I get early access?
- Will there be different flavors?
- Is this a meal replacement?
- How will I know when you launch?
- Who is this for?
- What makes Swolé Bears different from bars and shakes?
Keep answers persuasive but compliant.

9. FINAL CTA SECTION
Repeat the strongest promise and invite the user to join the waitlist.
Make the final CTA feel urgent and exclusive.

10. FOOTER
Include:
- brand name
- email signup mini-form
- social links placeholders
- privacy policy link
- terms link
- copyright
- contact email placeholder

FORM UX REQUIREMENTS
Use a friction-light main form:
- email required
- first name optional
- consent checkbox required
- hidden honeypot field
- loading state on submit
- inline validation
- success confirmation state
- failure message with retry option

Also:
- preserve UTM parameters through the session
- include hidden source fields
- let the same form component be reused in hero, middle CTA, and footer

SEO REQUIREMENTS
Implement strong on-page SEO for a landing page.
Include:
- title tag
- meta description
- Open Graph tags
- Twitter card tags
- canonical tag
- favicon support
- clean semantic headings
- structured data where useful
- alt text for images
- robots.txt
- sitemap.xml scaffold
- page speed optimization basics

Suggested page metadata direction:
Title:
Swolé Bears | Protein Gummy Bears for Active Lifestyles
Meta description:
Join the Swolé Bears waitlist for early access to protein gummy bears built for convenience, taste, and your active lifestyle.

ACCESSIBILITY REQUIREMENTS
Make the site accessible:
- semantic HTML
- sufficient contrast
- keyboard navigable
- proper labels
- aria attributes where appropriate
- visible focus states
- reduced motion respect
- form error accessibility

PERFORMANCE REQUIREMENTS
Optimize for speed:
- mobile-first responsive layout
- compressed image placeholders
- minimal JS
- no bloated dependencies
- lazy-load noncritical media
- clean CSS structure
- high Lighthouse-minded implementation

ANALYTICS / TRACKING REQUIREMENTS
Prepare hooks for:
- Google Analytics / GA4 placeholder
- Meta Pixel placeholder
- signup conversion event tracking
- CTA click tracking
- scroll-depth tracking placeholders

LEGAL / COMPLIANCE
Avoid disease or medical claims.
Avoid fake certifications.
Avoid unsupported nutrition specifics.
If any nutrition/statistical claims are uncertain, use placeholders.
Include privacy policy and terms placeholders.
Include email marketing consent language.

BUILD REQUIREMENTS
Generate the full implementation, not a mock description.
Create:
- Django project structure
- app structure
- models.py
- forms.py
- views.py
- urls.py
- template files
- partials/components where appropriate
- CSS setup
- JS file if needed
- environment variable example file
- Google Sheets integration service
- admin registration
- success/error handling
- migration-ready model definitions
- README with setup instructions
- deployment notes
- comments where secrets/config need to be added

DESIRED FILES
Please generate a complete working starter project with files such as:
- manage.py
- project settings files
- landing app
- templates/base.html
- templates/landing/home.html
- templates/partials/*
- static/css/*
- static/js/*
- services/google_sheets.py
- .env.example
- requirements.txt
- README.md

GOOGLE SHEETS INTEGRATION DETAILS
Use Google Sheets API with a service account.
Add clear setup notes for:
- enabling APIs
- creating service account
- sharing the sheet with the service account email
- setting spreadsheet ID and worksheet name in environment variables

If API append fails:
- still save lead in database
- log the exception safely
- show user a graceful success or partial-success flow
Do not expose secrets.

DYNAMIC BEHAVIOR TO INCLUDE
- rotating testimonial placeholder or subtle carousel if lightweight
- animated counters or waitlist momentum placeholder if tasteful
- sticky mobile signup CTA
- form submission without full page reload if simple to implement cleanly
- hidden UTM capture
- success state update after submit

COPY DELIVERABLES
Write all website copy directly in the templates.
The copy should be high-converting, original, and structured.
Use tasteful placeholder data where facts are not finalized.

PLACEHOLDER CONTENT TO INCLUDE
Include placeholders for:
- product renders
- founder photo
- nutrition values
- testimonial names
- launch timing
- social handles
- legal pages
- contact email

DO NOT
- do not build a full store
- do not overcomplicate backend architecture
- do not use childish design language
- do not use unverified claims as facts
- do not make it look generic or template-y
- do not make the page too text-heavy above the fold

OUTPUT FORMAT
Return the answer as a complete code project with all files clearly separated.
For each file, provide:
1. file path
2. full file contents

Also provide:
- a short explanation of the conversion strategy
- a short explanation of the technical architecture
- setup instructions
- how to deploy
- where to edit copy/images later

FINAL OPTIMIZATION GOAL
This site should feel like a premium prelaunch brand page that could realistically convert cold traffic from Instagram, TikTok, or paid ads into email subscribers.

The output should be polished enough that I can paste it into a project and run it with minimal changes.