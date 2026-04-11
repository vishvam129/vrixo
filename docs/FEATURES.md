# Vrixo — Master Feature Specification

The complete list of features for Vrixo, compiled from research across Remini, PhotoRoom, Picsart, Canva, Fotor, Remove.bg, Lensa, Pixlr, YouCam, Topaz, HeadshotPro, Cleanup.pictures, PicWish, Hotpot.ai, VSCO, Facetune, Adobe Express, and Photo AI — plus standard SaaS, infrastructure, compliance, mobile, business, testing, and growth requirements.

**Total: ~1,235 features across 12 sections** (audited v2 with gap analysis).

---

## Table of Contents

1. [AI Photo Features (Core Product)](#1-ai-photo-features-core-product)
2. [User-Facing Platform (SaaS Layer)](#2-user-facing-platform-saas-layer)
3. [Admin / Backend](#3-admin--backend)
4. [Growth / Marketing](#4-growth--marketing)
5. [Infrastructure / DevOps](#5-infrastructure--devops)
6. [Security / Privacy / Compliance](#6-security--privacy--compliance)
7. [Mobile App (React Native)](#7-mobile-app-react-native)
8. [Business / Revenue](#8-business--revenue)
9. [Quality / Testing](#9-quality--testing)
10. [Nice-to-have / Competitive Edge](#10-nice-to-have--competitive-edge)
11. [Audit Additions (v2 — Gaps Filled)](#11-audit-additions-v2--gaps-filled)
12. [Audit Notes — Duplicates & Scope Issues](#12-audit-notes--duplicates--scope-issues)
13. [MVP Priority Cut](#mvp-priority-cut)

---

## 1. AI Photo Features (Core Product)

### 1.1 Enhancement & Quality
1. AI Image Upscale 2x
2. AI Image Upscale 4x
3. AI Image Upscale 6x
4. AI Image Upscale 8x
5. AI Image Upscale to 4K
6. AI Image Upscale to 8K
7. Face-optimized upscale / Recover Faces
8. Low-light photo enhancement
9. AI Denoise / Noise removal
10. AI Sharpen (standard mode)
11. Motion blur removal / Unblur
12. Lens blur / defocus correction
13. Camera shake correction
14. Super Focus / Focus recovery
15. Auto exposure fix
16. Auto contrast adjustment
17. Auto white balance
18. Auto color correction
19. Auto brightness adjustment
20. Auto saturation enhancement
21. Dehaze
22. HDR effect / HDR boost
23. Auto-enhance one-click
24. Smart HDR merge
25. Detail recovery / Texture enhancement
26. Pixelated image recovery
27. Low-resolution image fix
28. Portrait-optimized enhancer
29. Anime-optimized enhancer
30. Text-in-image enhancer / Preserve Text
31. Product photo enhancer
32. Graphic image enhancer
33. Wonder mode (all-in-one denoise+sharpen+upscale)

### 1.2 Restoration (Old / Damaged)
34. Old photo restoration
35. Scratch removal
36. Dust & scratch removal
37. Crease removal
38. Water stain removal
39. Yellow-edge / fade repair
40. Tear / rip repair
41. Faded color recovery
42. Face detail recovery in old photos
43. Multi-level damage restoration modes
44. Black-and-white colorization
45. Sepia-to-color conversion
46. Custom colorization with AI prompt
47. Scanned photo cleanup
48. Print-to-digital restoration

### 1.3 Background Operations
49. One-click background removal
50. Transparent PNG export
51. High-res background removal up to 50MP
52. Background removal for people
53. Background removal for products
54. Background removal for animals
55. Background removal for cars/vehicles
56. Background removal for graphics/logos
57. Hair-detail preserving removal
58. Edge refinement brush
59. Manual background erase tool
60. AI background replacement from library
61. AI background generator from text prompt
62. Studio-style backgrounds
63. Nature backgrounds
64. Solid color background
65. Gradient background
66. Blurred background / Bokeh
67. Portrait blur / Depth-of-field
68. Background shadow generation
69. Realistic cast shadows
70. Reflection generation
71. Region-of-interest background selection
72. Batch background removal
73. Background for e-commerce
74. Scene replacement with prompt

### 1.4 Face Editing
75. AI face enhancer / Face restore
76. Face retouch
77. Skin smoothing
78. Blemish / pimple removal
79. Wrinkle removal
80. Dark circle removal
81. Spot removal
82. Teeth whitening
83. Eye brightening
84. Eye enlargement
85. Eye color change
86. Red-eye removal
87. Face slim / Face Shaper
88. Jawline reshape
89. Cheekbone highlight
90. Nose reshape
91. Lip reshape / enhancement
92. Chin adjustment
93. Forehead adjustment
94. Face symmetry correction
95. AI makeup (full look)
96. Lipstick application
97. Foundation
98. Blush
99. Eyeshadow
100. Eyeliner
101. Mascara / lashes
102. Contour & highlight
103. Eyebrow shaping
104. Virtual makeover presets (day, glam, bridal)
105. AI hairstyle change (60+ styles)
106. Hair color change
107. Hair volume adjust
108. Bangs / fringe try-on
109. Beard add/remove/style
110. Moustache style
111. Face age progression
112. Face age regression (make younger)
113. Baby face filter
114. AI gender swap
115. AI ethnicity change (consent-gated)
116. Face swap between photos
117. Multi-face swap in group photos
118. Face expression change (smile, frown)
119. Smile Editor
120. Eyes-open fix (closed-eye correction)
121. Look direction / gaze adjustment
122. Face healing tool
123. Concealer tool
124. Matte finish / oil removal
125. Neck smoothing
126. Double chin reduction

### 1.5 Object Operations
127. AI object removal
128. AI person removal
129. Text / watermark removal
130. Logo removal
131. Healing brush
132. Magic eraser
133. Generative fill
134. AI Replace / swap object
135. AI inpainting with prompt
136. AI outpainting / Magic Expand
137. Image extend beyond borders
138. Smart resize with AI fill
139. Object move / relocate
140. Object duplicate / clone
141. Object resize in place
142. Object rotate in place
143. Power retouch brush sizing
144. Object replace with text prompt
145. AI add object to scene
146. Distraction removal
147. Crowd / bystander removal
148. Unwanted element detection (auto)

### 1.6 Style / Artistic
149. AI anime filter
150. Manga style
151. Oil painting effect
152. Watercolor effect
153. Pencil sketch
154. Charcoal sketch
155. Cartoon effect
156. Pop art / Warhol style
157. Van Gogh style
158. Chinese painting style
159. Pixel art
160. 3D render effect
161. Disney Pixar style
162. Cyberpunk style
163. Vintage / retro filter
164. Film grain emulation
165. Kodachrome preset
166. Kodak Portra preset
167. Fuji Velvia preset
168. Fuji / Kodak / Agfa / Ilford film presets
169. 200+ custom preset library
170. Creator-made presets
171. HSL adjustment
172. Custom LUT upload
173. Filter intensity slider
174. Duotone / Tritone
175. Split-tone effect
176. Cross-processing
177. Glitch effect
178. Polaroid frame
179. Vignette
180. Light leak overlay
181. Bokeh overlay
182. Dust / grain overlay
183. Instagram-style filter pack
184. Moody / Noir filter
185. Warm / cool tone preset

### 1.7 Generation (Text-to-Image / Avatars)
186. Text-to-image generator
187. Image-to-image generation
188. Prompt library / suggestions
189. Negative prompt support
190. AI avatar generator from selfies
191. 120+ avatar styles
192. Themed avatar packs (sci-fi, anime, business)
193. AI professional headshot generator
194. 50+ headshots per session
195. Custom background for headshots
196. Custom clothing for headshots
197. Team headshot packages
198. Remix headshot (keep outfit/BG, new pose)
199. AI photo pack themes (Quiet Luxury, Photography, etc.)
200. Personal AI model training
201. Fast training (under 1 minute)
202. Avatar aging (progression from baby to elder)
203. AI sticker generator
204. AI logo generator
205. AI pattern generator
206. AI wallpaper generator
207. Multi-image grid generation (4, 9, 16 variants)
208. Seed control for reproducibility
209. Aspect ratio presets (1:1, 16:9, 9:16, 4:5)
210. Model version selector (SDXL, Flux, proprietary)

### 1.8 Passport / ID Photos
211. Passport photo maker with country presets (130+ countries)
212. India passport (35x45mm)
213. US passport (2x2 inch)
214. Schengen visa (35x45mm)
215. UK passport
216. Canada passport
217. China visa / ID
218. Australia passport
219. UAE / Gulf region IDs
220. Custom size entry
221. AI face crop / center / alignment
222. Auto head-size compliance
223. Auto eye-line positioning
224. White background auto-generation
225. Blue background auto-generation
226. Red / custom color background for IDs
227. Clothing change for formal attire
228. Expression compliance check (neutral, eyes open)
229. Glasses detection / removal warning
230. Shadow removal for ID compliance
231. DPI auto-set (300/600 DPI)
232. Print sheet layout (4x6 with multiple copies)
233. Official standards validator
234. Driving license photo
235. Student ID photo
236. Employee ID photo
237. Visa photo (all major visa types)

### 1.9 Compositing
238. Merge two photos / couple merger
239. AI baby generator (future baby from 2 parents)
240. Baby gender selection
241. Baby resemblance slider (dad % / mom %)
242. Baby age/expression variants
243. Pregnancy photo filter
244. AI group photo merger - best faces from multiple shots
245. Multi-shot face blending (fix closed eyes)
246. Photo collage maker
247. Photomontage / double exposure
248. Add self to any scene (place in location)
249. Product into lifestyle scene
250. Virtual models / try-on clothes
251. Outfit swap
252. Specific color change (clothing, hair, background)

### 1.10 Lighting / Relight
253. AI relight with custom direction
254. Studio lighting preset
255. Natural daylight preset
256. Sunset / golden hour preset
257. Moody dramatic lighting
258. Rembrandt lighting pattern
259. Butterfly lighting pattern
260. Split lighting pattern
261. Soft box simulation
262. Ring light simulation
263. Shadow direction adjustment
264. Color temperature adjustment
265. Light intensity slider
266. Ambient occlusion fix
267. Auto studio-quality lighting
268. Highlight / shadow recovery

### 1.11 Compression / Resize / Format
269. Image compression (lossless)
270. Image compression (lossy with quality slider)
271. Resize by pixels
272. Resize by percentage
273. Resize for social (Instagram, FB, Twitter, LinkedIn, TikTok)
274. Smart crop (AI subject-aware)
275. Aspect ratio presets
276. Format conversion (JPG to PNG)
277. PNG to JPG
278. HEIC to JPG
279. WebP conversion
280. AVIF conversion
281. TIFF support
282. RAW file support
283. SVG export (for graphics)
284. PDF export
285. GIF creation
286. Metadata stripping (privacy)
287. EXIF preservation option
288. Color profile conversion (sRGB, Adobe RGB)

### 1.12 Batch Operations
289. Batch enhance
290. Batch background removal
291. Batch upscale
292. Batch resize
293. Batch format conversion
294. Batch watermark add/remove
295. Batch rename
296. Batch filter application
297. Apply same settings to 50 images
298. Batch download as ZIP
299. Batch tagging
300. Queue prioritization for batch jobs

### 1.13 Video Features (Photo-to-Video)
301. Photo-to-video animation
302. AI talking avatar
303. Lip-sync with script
304. Motion capture / Mocap transfer
305. Cinemagraph creation
306. Camera pan / zoom animation
307. Parallax 3D effect
308. Short clip enhancement
309. Video upscaling
310. Video denoise
311. Video relight
312. Video background removal
313. Face retouch in video
314. Video to GIF
315. Slideshow video generator

### 1.14 Language / Accessibility on AI
316. Multi-language prompt input (45+ languages)
317. Prompt translation
318. Voice-to-prompt input
319. Text-in-image translator
320. Natural language edit commands

---

## 2. User-Facing Platform (SaaS Layer)

### 2.1 Authentication
321. Email + password signup
322. Email verification (magic link)
323. Google OAuth login
324. Apple Sign-in
325. Facebook login
326. Phone / OTP login (SMS)
327. WhatsApp OTP login (India)
328. Magic link passwordless login
329. Biometric login (mobile)
330. Remember device option
331. Single sign-on (SSO) for enterprise
332. Guest mode (limited preview)

### 2.2 User Profile
333. Profile avatar upload
334. Display name
335. Email change (with verification)
336. Password change
337. Username / handle
338. Bio / description
339. Country / region setting
340. Language preference
341. Timezone setting
342. Link social accounts
343. Account deletion (GDPR right to be forgotten)
344. Data export / download my data
345. Usage statistics visible to user

### 2.3 Billing & Subscriptions
346. Free tier with daily/weekly limits
347. Pro monthly subscription
348. Pro annual subscription (discounted)
349. Credits system (pay per use)
350. One-time credit pack purchase
351. Credit rollover rules
352. Trial period (7-day free trial)
353. Student discount tier
354. Family / team plan (multi-seat)
355. Enterprise / custom plan
356. API / developer plan
357. Regional pricing (India vs Global - INR vs USD)
358. Currency selector
359. Downgrade flow with feedback
360. Cancel subscription flow
361. Pause subscription
362. Win-back / retention offer on cancel
363. Invoice history / download PDF
364. GST / tax display (India compliance)
365. Receipt email automation
366. Subscription auto-renew toggle
367. Renewal reminder emails
368. Payment method management
369. Multiple payment methods per account

### 2.4 Payment Processing
370. Stripe integration (global)
371. Razorpay integration (India)
372. Credit / debit cards
373. UPI (India)
374. Net banking (India)
375. PayPal
376. Apple Pay
377. Google Pay
378. Wallets (Paytm, PhonePe)
379. eMandate (recurring India)
380. International cards (92 currencies via Razorpay)
381. 3DS / SCA compliance
382. PCI-DSS compliance
383. Refund initiation via support
384. Chargeback handling
385. Failed payment retry logic
386. Dunning emails

### 2.5 History / Library
387. Edit history timeline
388. All past results grid view
389. Favorites / star items
390. Folder organization
391. Tags / labels
392. Search my edits
393. Filter by feature used
394. Filter by date
395. Sort by newest / oldest / most used
396. Bulk delete
397. Trash / 30-day restore
398. Storage quota indicator
399. Original + edited side-by-side view
400. Re-edit from history
401. Version history per image
402. Share a folder

### 2.6 Sharing
403. Direct download (PNG, JPG, WebP)
404. Download with transparent background
405. Download in original resolution
406. Download with custom watermark
407. Shareable public link
408. Private link with expiry
409. Password-protected link
410. QR code for share
411. Share to Instagram
412. Share to Facebook
413. Share to X / Twitter
414. Share to WhatsApp
415. Share to LinkedIn
416. Share to Pinterest
417. Share to TikTok
418. Share to Reddit
419. Share to email
420. Copy to clipboard
421. Embed code
422. Watermark toggle (free tier forced)
423. Remove watermark (paid)
424. Custom watermark upload

### 2.7 Referral / Affiliate
425. Referral code per user
426. Referral reward (credits both sides)
427. Referral leaderboard
428. Affiliate program signup
429. Affiliate dashboard with earnings
430. Affiliate unique URL
431. Commission tracking
432. Payout threshold
433. Payout method (Wise, bank, PayPal)

### 2.8 Notifications
434. Transactional emails (welcome, receipt)
435. Marketing emails (opt-in)
436. Job-complete email (long renders)
437. In-app notification bell
438. Push notifications (web)
439. Push notifications (mobile)
440. Notification preferences page
441. Unsubscribe links in all emails
442. Weekly digest email
443. Re-engagement email
444. Birthday / anniversary email
445. Feature announcement email

### 2.9 Settings / Preferences
446. Theme selector (light / dark / auto)
447. Language selector (i18n)
448. Quality preference (fast / balanced / best)
449. Auto-save originals toggle
450. Default export format
451. Default export quality
452. NSFW filter toggle
453. Auto-delete uploads toggle
454. Auto-download results toggle
455. Keyboard shortcuts editor
456. Notification preferences granular
457. Privacy controls
458. Face recognition consent toggle
459. AI training opt-in/out

### 2.10 Dark Mode & Theme
460. Dark mode (system + manual)
461. Light mode
462. High-contrast mode
463. Custom accent color (Pro)

### 2.11 Internationalization
464. English (default)
465. Hindi
466. Spanish
467. French
468. German
469. Portuguese (Brazil)
470. Japanese
471. Korean
472. Mandarin Chinese
473. Arabic (RTL support)
474. Russian
475. Indonesian
476. Vietnamese
477. Turkish
478. Tamil / Telugu / Bengali (India regional)
479. Auto-detect from browser
480. Currency auto-switch by locale
481. Date / time format per locale

### 2.12 Accessibility (WCAG 2.1 AA)
482. Screen reader support / ARIA labels
483. Keyboard navigation full
484. Focus indicators visible
485. Alt text for all images
486. Color contrast compliance
487. Text resize up to 200%
488. Reduced motion mode
489. Captions for video tutorials
490. Voice commands (optional)

### 2.13 Help / Support
491. FAQ / knowledge base
492. Searchable help center
493. In-app live chat (Intercom / Crisp)
494. Email support ticket
495. WhatsApp support (India)
496. Video tutorials library
497. Feature-specific tooltips
498. Interactive product tours
499. Community forum / Discord
500. Submit bug report with screenshot
501. Feature request voting board
502. Status page (uptime)
503. Contact form

### 2.14 Onboarding
504. Welcome screen / splash
505. Interactive tutorial
506. First-edit guided flow
507. Feature highlights modal
508. Sample images to try
509. "Try before sign up" mode
510. Progress checklist for first week
511. Tooltips on hover
512. Empty state CTAs
513. Personalized feature recommendations

### 2.15 States & Errors
514. Skeleton loading screens
515. Progress bar for long jobs
516. Queue position indicator
517. ETA for job completion
518. Empty state illustrations (no history)
519. 404 error page with search
520. 500 error page with retry
521. Maintenance mode page
522. Offline indicator (mobile)
523. Upload failed recovery
524. Retry mechanism on failure
525. Friendly error messages (no stack traces)

---

## 3. Admin / Backend

### 3.1 User Management
526. User search (email, ID, phone)
527. User profile view (admin)
528. Suspend user
529. Ban user (permanent)
530. Delete user (GDPR erase)
531. Refund user
532. Gift credits
533. Change user tier
534. View user usage logs
535. Impersonate user (with audit)
536. Reset user password
537. Unlock locked account
538. Verify email manually

### 3.2 Content Moderation
539. NSFW detection pipeline (auto)
540. CSAM detection (PhotoDNA / Thorn)
541. Flagged content queue
542. Manual review interface
543. User report button
544. Auto-ban on CSAM detection
545. Deepfake detection
546. Celebrity / public figure filter
547. Copyright / IP detection
548. Watermark detection on uploads
549. Moderator roles
550. Appeal process workflow

### 3.3 Analytics Dashboard
551. DAU / MAU / WAU
552. Retention cohorts
553. Churn rate
554. MRR / ARR
555. LTV / CAC
556. Conversion funnel (visitor → signup → paid)
557. Feature usage breakdown
558. Credit consumption per feature
559. Revenue by plan
560. Revenue by country
561. Top users by spend
562. Support ticket volume
563. Model inference costs per feature
564. Job success / failure rates
565. P95 / P99 latency
566. Signups over time
567. A/B test results viewer
568. Custom dashboards

### 3.4 A/B Testing & Experiments
569. Feature flag system (LaunchDarkly / GrowthBook / PostHog)
570. Percentage rollouts
571. User segment targeting
572. Experiment management
573. Variant creation
574. Statistical significance calculator
575. Multi-armed bandit testing
576. Gradual rollout / canary

### 3.5 Rate Limiting & Quotas
577. Per-user rate limits
578. Per-IP rate limits
579. Per-API-key limits
580. Burst limits
581. Daily quota by tier
582. Credit deduction logic
583. Overage billing
584. Grace period on limit exceed

### 3.6 Queue Management
585. Job queue dashboard (BullMQ / Celery)
586. Retry failed jobs
587. Kill running jobs
588. Priority queues (paid > free)
589. Dead letter queue
590. Job timeout enforcement
591. Worker scaling controls
592. GPU pool management

### 3.7 Model Management
593. Model version registry
594. A/B test model versions
595. Roll back model deployment
596. Model cost tracking
597. Model latency tracking
598. Hot-swap models
599. Custom model upload (enterprise)
600. Model fine-tuning interface

### 3.8 Monitoring & Alerts
601. Sentry error tracking
602. Datadog / New Relic APM
603. Uptime monitoring (UptimeRobot)
604. PagerDuty on-call alerts
605. Slack alerts for critical issues
606. Database slow query alerts
607. Cost anomaly alerts
608. Fraud detection alerts

### 3.9 Audit & Compliance
609. Audit log (all admin actions)
610. Immutable log storage
611. Log retention policy
612. Export audit log
613. GDPR data request workflow
614. DPDP data request workflow
615. DSR (Data Subject Request) handler

### 3.10 Admin Roles & Tools
616. Super admin role
617. Support admin role
618. Moderator role
619. Finance admin role
620. Read-only analyst role
621. Role permissions matrix
622. Admin 2FA mandatory
623. Customer support CRM integration (Zendesk / Intercom)
624. Refund tool with reason codes
625. Coupon generation tool
626. Broadcast message tool (send to all users)

---

## 4. Growth / Marketing

### 4.1 SEO & Content
627. Landing page per feature (/background-remover, /upscale, /passport)
628. Schema.org markup
629. Sitemap XML auto-gen
630. Robots.txt
631. Open Graph tags
632. Twitter card tags
633. Canonical URLs
634. Hreflang for multi-language SEO
635. Page speed optimized (Core Web Vitals)
636. Image alt tags
637. Internal linking strategy
638. Breadcrumbs
639. FAQ schema for rich snippets

### 4.2 Showcase / Social Proof
640. Public gallery of user creations (opt-in)
641. Before/after slider on landing
642. Video demos per feature
643. Customer testimonials
644. Trustpilot / G2 embed
645. Rating widget
646. User count / photos processed counter
647. Case studies
648. Featured creators
649. Influencer collaborations page

### 4.3 Blog & Content Marketing
650. Blog with CMS
651. Category / tag system
652. Author pages
653. Related posts
654. Email subscribe form
655. RSS feed
656. Comments (optional)
657. Social share buttons
658. Reading time estimate
659. Table of contents auto-gen

### 4.4 Launch Assets
660. Product Hunt launch page
661. Press kit (logos, screenshots)
662. Media kit PDF
663. Brand guidelines page
664. Roadmap public page
665. Changelog page
666. What's new modal

### 4.5 Viral / Referral
667. Share-to-earn credits
668. "Share your result" prompt after edit
669. Invite friends modal
670. Referral leaderboards
671. Social media auto-caption
672. Auto-generated share image with watermark
673. "Edited with Vrixo" badge (free tier)

### 4.6 Email Marketing
674. Welcome email series (5 emails)
675. Onboarding drip campaign
676. Feature announcement broadcast
677. Retention email (inactive 7 days)
678. Win-back email (inactive 30 days)
679. Abandoned cart email
680. Birthday email
681. Re-engagement with exclusive credits
682. Newsletter
683. Segmentation (by tier, usage, country)
684. A/B test subject lines
685. Customer.io / Mailchimp / Resend integration

### 4.7 Promo & Coupons
686. Coupon code generation
687. Percentage discount codes
688. Fixed amount codes
689. Free trial extension codes
690. First-purchase discount
691. Limited-time flash sale
692. Seasonal promotions (Diwali, Christmas)
693. Bundle pricing
694. Upsell modals

### 4.8 API & Integrations
695. Public REST API
696. API documentation (Swagger / Redoc)
697. API key management
698. Webhooks on events
699. Rate-limited free tier API
700. SDK: Python
701. SDK: JavaScript / Node
702. SDK: PHP
703. SDK: Ruby
704. SDK: Go
705. Postman collection
706. Zapier integration
707. Make.com (Integromat) integration
708. n8n integration
709. Figma plugin
710. Shopify app
711. WordPress plugin
712. Chrome extension
713. Canva app / plugin
714. Slack bot
715. Discord bot
716. Notion integration
717. Airtable integration

---

## 5. Infrastructure / DevOps

### 5.1 Frontend Delivery
718. CDN (Cloudflare / Fastly)
719. Edge caching rules
720. Asset minification
721. Brotli compression
722. Image CDN with on-the-fly transforms
723. Static site for marketing (Next.js SSG)
724. ISR for dynamic marketing pages
725. Service Worker for PWA

### 5.2 Caching
726. Redis for session cache
727. Redis for job metadata
728. CDN edge cache for API responses
729. Memcached option
730. Stale-while-revalidate strategy
731. Cache invalidation API

### 5.3 Job Processing
732. BullMQ (Node) or Celery (Python)
733. GPU worker pool
734. CPU worker pool
735. Priority queues
736. Job status API
737. Progress streaming (SSE / WebSocket)
738. Scheduled / cron jobs
739. Retry with exponential backoff
740. Dead letter queue

### 5.4 Storage
741. Cloudflare R2 (primary - cheap egress)
742. AWS S3 (secondary / backup)
743. Presigned upload URLs
744. Multi-part upload for large files
745. Automatic lifecycle rules (auto-delete)
746. Object versioning
747. Cold storage for old results
748. Regional buckets for data residency

### 5.5 Database
749. PostgreSQL primary
750. Read replicas
751. Connection pooling (PgBouncer)
752. Logical replication
753. Automated backups (daily + PITR)
754. Point-in-time recovery
755. Redis for hot data
756. ClickHouse for analytics
757. Vector DB for embeddings (Pinecone / pgvector)

### 5.6 Auth & Security
758. JWT tokens with short TTL
759. Refresh tokens with rotation
760. Session invalidation on logout
761. CSRF protection
762. CORS configuration
763. SQL injection prevention (parameterized queries)
764. XSS protection (CSP headers)
765. Content Security Policy
766. HSTS enforcement
767. Secure cookies (httpOnly, SameSite)
768. Rate limiting (per-IP, per-user)
769. Cloudflare DDoS protection
770. WAF (Web Application Firewall)
771. Bot detection
772. reCAPTCHA on signup
773. Anomaly detection
774. Secret scanning (GitHub)

### 5.7 Monitoring & Observability
775. Sentry (errors)
776. Datadog / Grafana (metrics)
777. Loki / ELK (logs)
778. OpenTelemetry traces
779. Custom metric dashboards
780. Synthetic monitoring
781. Real user monitoring (RUM)
782. Health check endpoints (/healthz, /readyz)
783. Liveness probe for Kubernetes
784. Readiness probe

### 5.8 Analytics Platform
785. PostHog (product analytics)
786. Plausible (privacy-first web analytics)
787. Mixpanel (alternative)
788. Google Analytics 4 (optional)
789. Event tracking taxonomy
790. Funnel analysis
791. Session replay (PostHog)

### 5.9 CI/CD & DevOps
792. GitHub Actions pipelines
793. Automated tests on PR
794. Automated Docker build
795. Preview deployments per PR
796. Staging environment
797. Production environment
798. Blue-green deployment
799. Canary deployment
800. Feature flag rollout
801. Rollback automation
802. Database migration pipeline
803. Automated changelog from PRs

### 5.10 Containerization & Orchestration
804. Dockerfile per service
805. Docker Compose for local dev
806. Kubernetes or ECS in prod
807. Horizontal Pod Autoscaler
808. Cluster autoscaling
809. Helm charts
810. Ingress with TLS
811. Service mesh (Istio / Linkerd optional)

### 5.11 Backup / DR
812. Daily automated DB backups
813. Weekly full backup to offsite
814. Cross-region replication
815. Disaster recovery runbook
816. RTO / RPO defined
817. Backup restoration drills (quarterly)
818. Object storage versioning

### 5.12 SSL / Network
819. HTTPS enforced (Let's Encrypt / managed cert)
820. TLS 1.3
821. HTTP/2 and HTTP/3
822. Certificate auto-renewal
823. Wildcard subdomain cert
824. Private VPC
825. NAT gateway
826. Bastion host for SSH

### 5.13 Environment & Secrets
827. .env per environment
828. AWS Secrets Manager / HashiCorp Vault
829. Env variable validation at startup
830. Config drift detection
831. Ephemeral credentials
832. Key rotation policy

### 5.14 API Architecture
833. API versioning (/v1, /v2)
834. Deprecation notices
835. GraphQL optional layer
836. Rate limit headers
837. Idempotency keys for mutations
838. Pagination standard (cursor-based)
839. OpenAPI spec
840. API gateway

### 5.15 Scaling & Cost
841. Auto-scaling policies
842. Spot / preemptible GPU instances
843. Cost dashboard per service
844. Idle resource cleanup
845. CDN bandwidth monitoring
846. Right-sizing automation
847. Reserved instance planning

---

## 6. Security / Privacy / Compliance

### 6.1 Legal Documents
848. Terms of Service
849. Privacy Policy (GDPR compliant)
850. DPDP-compliant privacy notice (India)
851. Cookie Policy
852. Acceptable Use Policy
853. Content Guidelines
854. Refund Policy
855. DMCA Policy + notice form
856. Data Processing Addendum (DPA) for B2B
857. Sub-processor list
858. EULA

### 6.2 Consent & Cookies
859. Cookie consent banner (GDPR)
860. Granular consent (analytics, marketing, necessary)
861. Consent version tracking
862. Re-consent when policy changes
863. Consent manager for DPDP (India)
864. Face biometric consent (explicit opt-in)
865. AI training consent toggle
866. Marketing consent separate

### 6.3 Data Protection
867. Encryption at rest (AES-256)
868. Encryption in transit (TLS)
869. Database field-level encryption for PII
870. Key management (KMS)
871. Pseudonymization
872. Data minimization
873. Purpose limitation
874. Retention policies (auto-delete uploads 24h)
875. Auto-delete results (configurable 7-30 days)
876. Permanent delete on account erase

### 6.4 Account Security
877. 2FA via TOTP (Authenticator app)
878. 2FA via SMS
879. 2FA via email code
880. Backup codes
881. Login alerts (new device)
882. Active sessions view
883. Remote logout (all devices)
884. Suspicious login challenge
885. Password strength meter
886. Password breach check (HaveIBeenPwned)
887. Password reset via email
888. Password reset via phone OTP
889. Account recovery questions (optional)

### 6.5 Compliance Certifications
890. SOC 2 Type II (roadmap)
891. ISO 27001 (roadmap)
892. GDPR compliance
893. DPDP Act 2023 compliance (India)
894. CCPA compliance (California)
895. COPPA (no under-13)
896. Age gate at signup (13+ or 18+ for face)
897. Age verification for avatar / face features

### 6.6 Safety & Abuse
898. NSFW upload blocking
899. CSAM scanning (mandatory)
900. Hash-based known-bad matching
901. Watermark on all free-tier exports
902. C2PA content credentials (provenance)
903. Deepfake disclosure label
904. Non-consensual imagery prevention
905. Reporting mechanism for victims
906. Law enforcement request policy
907. Transparency report (annual)
908. 72-hour breach notification workflow

### 6.7 Right to be Forgotten
909. Account deletion flow (soft then hard)
910. 30-day grace period for restore
911. Hard delete after grace
912. Confirmation email for deletion
913. Purge from backups within 90 days
914. Third-party data purge coordination

---

## 7. Mobile App (React Native)

### 7.1 Native Capabilities
915. Native camera integration
916. Photo library picker
917. Multi-select picker
918. Drag-and-drop upload
919. Clipboard paste
920. Share sheet "Open in Vrixo"
921. Save to Photos / Files
922. Export to third-party apps

### 7.2 Offline / Sync
923. Offline queue (edits resumed when online)
924. Cached results
925. Background upload
926. Download manager
927. Local draft storage

### 7.3 Notifications
928. Push notifications (APNs / FCM)
929. Deep links from notification
930. Silent push for sync

### 7.4 Monetization
931. In-App Purchase (iOS StoreKit)
932. In-App Purchase (Google Play Billing)
933. Server-side receipt verification
934. Subscription restoration
935. Promo codes (App Store)

### 7.5 Auth
936. Sign in with Apple (mandatory iOS)
937. Google Sign-In
938. Biometric login (Face ID / Touch ID / fingerprint)
939. Auto-login on app open

### 7.6 Deep Linking
940. Universal Links (iOS)
941. App Links (Android)
942. Branch.io / Firebase Dynamic Links
943. Referral deep links
944. Share link opens app

### 7.7 Platform Features
945. Widgets (iOS / Android)
946. Shortcut / Siri integration
947. App Clip / Instant App preview
948. Live Activities (iOS)
949. Picture-in-picture (video)
950. Haptic feedback
951. Dark mode follow system
952. Dynamic type support
953. Landscape / portrait rotation
954. Tablet / foldable optimized

---

## 8. Business / Revenue

### 8.1 Pricing Tiers
955. Free tier (daily limit, watermark, low-res)
956. Pro tier monthly
957. Pro tier annual (2 months free)
958. Pro+ tier (more credits + advanced features)
959. Credit packs (100, 500, 1000, 5000)
960. Enterprise custom
961. API usage-based plan
962. Lifetime deal (early adopter)

### 8.2 Credit System
963. Credit ledger per user
964. Credit cost per feature (published)
965. Credit estimate before running
966. Credit top-up auto-purchase
967. Credit expiry rules
968. Credit gifts from referrals
969. Credit rollover for Pro subscribers
970. Bonus credits on first purchase

### 8.3 Regional & Tax
971. INR pricing for India
972. USD for global
973. Local currency for EU, UK, AU, CA, SG, UAE
974. Purchasing power parity pricing
975. GST invoice for India (18%)
976. VAT for EU
977. Sales tax for US states
978. Tax ID collection for B2B
979. Reverse charge mechanism
980. TDS handling (India)

### 8.4 Trials & Retention
981. 7-day free trial
982. Credit card required / not required variants
983. Trial reminder emails
984. Trial extension for engagement
985. Post-trial downgrade to free
986. Winback offer (50% off 3 months)
987. Pause instead of cancel
988. Exit survey on cancel
989. Reactivation incentive

### 8.5 Revenue Features
990. Gift cards
991. Gift subscription
992. Corporate / team billing
993. PO-based invoicing
994. Loyalty points program
995. Tier upgrade rewards
996. Milestone rewards (100 edits badge)

---

## 9. Quality / Testing

### 9.1 Automated Tests
997. Unit tests (Jest / Vitest / Pytest)
998. Integration tests
999. API contract tests
1000. E2E tests (Playwright)
1001. Visual regression tests (Chromatic / Percy)
1002. Accessibility tests (axe-core)
1003. Load testing (k6 / Locust)
1004. Stress testing
1005. Chaos engineering (Gremlin)
1006. Security testing (OWASP ZAP)
1007. Dependency vulnerability scan (Snyk / Dependabot)
1008. Secret scanning in CI

### 9.2 Model / AI Quality
1009. Model accuracy benchmarks
1010. Golden dataset for regression
1011. Output quality A/B tests
1012. Human-in-the-loop evaluation
1013. Bias / fairness audits
1014. Hallucination detection
1015. Prompt injection tests

### 9.3 User Testing
1016. Beta program signup
1017. Private beta feature flag
1018. Feedback widget in beta
1019. NPS surveys
1020. CSAT surveys
1021. In-app micro-surveys
1022. User interview scheduler

---

## 10. Nice-to-have / Competitive Edge

### 10.1 AI Assistant
1023. Natural language edit assistant (chat interface)
1024. Voice-command editing
1025. Suggestion engine ("try these edits")
1026. Auto-edit recipes from prompt
1027. Style transfer from reference image
1028. "Make this like [celebrity photo]" style match

### 10.2 Community
1029. Public profile page
1030. Follow / followers
1031. Likes / comments on shared works
1032. Remix another user's edit
1033. Preset marketplace (user-made)
1034. Prompt marketplace
1035. Weekly challenges / contests
1036. Prize pool for contest winners
1037. Creator program with revenue share
1038. Verified creator badge

### 10.3 Developer Ecosystem
1039. Public API with free tier
1040. SDK libraries (Python, JS, PHP, Go, Ruby)
1041. Webhook events
1042. OAuth for third-party apps
1043. Partner integration program
1044. App directory

### 10.4 Workflow / Productivity
1045. Batch API for bulk processing
1046. Automations / recipes (if-this-then-that style)
1047. Scheduled edits
1048. Template library
1049. Brand kit (colors, logos, fonts)
1050. Team collaboration (share workspace)
1051. Real-time co-editing (stretch)
1052. Comments on projects
1053. Approval workflows

### 10.5 Differentiators (India-first)
1054. India-first regional pricing
1055. Regional language UI (Hindi, Tamil, Telugu, Bengali)
1056. WhatsApp bot for editing
1057. Telegram bot for editing
1058. Astrology / festival photo themes (Diwali, Holi frames)
1059. Wedding photography pack (Indian market)
1060. Matrimony profile photo optimizer
1061. LinkedIn photo optimizer
1062. Instagram reel cover creator
1063. Thumbnail generator for YouTube
1064. Offline desktop app (Windows / Mac / Linux)
1065. GPU-accelerated local mode (privacy)

---

## 11. Audit Additions (v2 — Gaps Filled)

After reviewing the initial 1,065 features, I identified ~170 important features missing from v1. These are features that virtually every competitor has but were not in the original list. They are grouped by the category they belong to.

### 11.1 Basic Photo Editing Tools (missed in v1)
These are fundamental editor features — surprising they weren't in v1.

1066. Crop tool with freeform drag
1067. Crop with aspect ratio presets (1:1, 4:3, 16:9, 9:16, 3:2)
1068. Crop with rule-of-thirds grid overlay
1069. Crop with golden ratio grid overlay
1070. Rotate 90° clockwise / counter-clockwise
1071. Rotate by custom angle (slider)
1072. Flip horizontal / mirror image
1073. Flip vertical
1074. Auto-straighten (horizon detection)
1075. Manual straighten tool
1076. Perspective correction / keystone fix
1077. Barrel distortion fix
1078. Pincushion distortion fix
1079. Chromatic aberration removal
1080. Lens profile correction (by camera/lens model)
1081. Unlimited undo / redo stack
1082. Edit history panel
1083. Before/after toggle (hold to preview)
1084. Side-by-side before/after view
1085. Split-screen compare
1086. Zoom in / out with scroll
1087. Pan canvas (space + drag)
1088. Fit to screen / 100% / fit width
1089. Reset all edits button
1090. Quick preview mode

### 11.2 Pro Color Tools (missed in v1)
Professional editors have these — VSCO, Lightroom, Pixlr all do.

1091. Histogram display (live)
1092. Curves adjustment (RGB composite)
1093. Curves adjustment per channel (R, G, B)
1094. Levels adjustment
1095. Selective color adjustment
1096. HSL per-color adjustment (Hue, Saturation, Lightness)
1097. Gradient map
1098. Channel mixer
1099. Posterize effect
1100. Solarize effect
1101. Threshold black-and-white
1102. Color picker / eyedropper tool
1103. Color palette extractor from image
1104. Custom color wheel
1105. Color match between photos

### 11.3 Selection & Masking Tools (missed in v1)
Any serious editor has these — especially important for localized edits.

1106. Rectangular marquee selection
1107. Elliptical marquee selection
1108. Lasso (freeform) selection
1109. Polygon lasso selection
1110. Magnetic lasso (edge-aware)
1111. Magic wand selection (color similarity)
1112. Quick-select brush
1113. Select subject automatically (AI)
1114. Select sky automatically
1115. Select background automatically
1116. Invert selection
1117. Add to / subtract from selection
1118. Refine edge tool
1119. Feather selection
1120. Expand / contract selection
1121. Layer mask
1122. Clipping mask
1123. Alpha channel editing

### 11.4 Layers & Non-Destructive Editing (missed in v1)
Pro photo editors need layers — surprising omission in v1.

1124. Multi-layer support
1125. Layer visibility toggle
1126. Layer opacity slider
1127. Blend modes (Normal, Multiply, Screen, Overlay, Soft Light, etc.)
1128. Layer groups / folders
1129. Layer drag to reorder
1130. Layer effects (drop shadow, glow, stroke, bevel)
1131. Adjustment layers (non-destructive color edits)
1132. Smart objects
1133. Layer merging / flattening
1134. Layer duplication
1135. Fill / stroke layer

### 11.5 Text & Typography (missed in v1)
Every social photo editor has text tools.

1136. Add text to image
1137. Google Fonts integration (1000+ fonts)
1138. Custom font upload (TTF, OTF)
1139. Text color picker
1140. Text shadow
1141. Text outline / stroke
1142. Text gradient fill
1143. Text background
1144. Curved text / text on path
1145. Vertical text
1146. Rich text editor (bold, italic, underline)
1147. Letter spacing (kerning)
1148. Line spacing (leading)
1149. Text alignment (left, center, right, justify)
1150. Handwriting font pack
1151. Script font pack
1152. Emoji support in text
1153. Localized fonts (Devanagari, Tamil, Arabic, etc.)
1154. Text-on-image templates

### 11.6 Shapes, Stickers, Overlays (missed in v1)
1155. Shape library (rectangle, circle, triangle, polygon, star, heart)
1156. Line tool
1157. Arrow tool
1158. Speech bubble / thought bubble
1159. Callout shapes
1160. Icon library (Feather, Material, etc.)
1161. SVG import
1162. Custom shape upload
1163. Sticker library (thousands)
1164. Emoji sticker picker
1165. Animated GIF stickers
1166. Seasonal sticker packs (Diwali, Holi, Christmas, Eid)
1167. Brand / meme sticker packs
1168. Frame library (polaroid, cinema, vintage)
1169. Border with adjustable color / width
1170. Rounded corners
1171. Drop shadow effect on image

### 11.7 Image Analysis & OCR (missed in v1)
These are huge for user value — OCR alone is a killer feature.

1172. OCR — extract text from image (multi-language)
1173. Text-in-image translation (live)
1174. QR code detection and decoding
1175. Barcode detection and decoding
1176. Face detection with count overlay
1177. Object detection with labels
1178. Scene classification (indoor, outdoor, portrait, etc.)
1179. Auto alt-text generation (accessibility)
1180. Image description generation (AI caption)
1181. Reverse image search (find source online)
1182. Similar image finder within library
1183. Duplicate image detector
1184. Dominant color extraction
1185. Composition analysis (rule of thirds, leading lines)

### 11.8 Smart Library & Search (missed in v1)
Users accumulate thousands of edits — they need search.

1186. Face grouping (cluster photos by person)
1187. Automatic album creation
1188. Semantic search ("photos of dogs", "beach photos")
1189. Search by color dominance
1190. Search by date range
1191. Search by GPS location
1192. Search by emotion / mood detection
1193. Search by people (after face grouping)
1194. Auto-tagging with AI labels
1195. Smart albums (rule-based)
1196. Year-in-review / memories
1197. On-this-day feature
1198. Recently used filters
1199. Favorite filters bookmark
1200. Recent prompts history

### 11.9 EXIF & Metadata (missed in v1)
1201. EXIF viewer (camera, date, settings)
1202. EXIF editor
1203. GPS coordinates viewer / editor
1204. Strip all EXIF on export (privacy)
1205. Copyright metadata embed
1206. IPTC metadata support
1207. XMP metadata support
1208. Author / photographer metadata

### 11.10 Additional Social Sharing (missed in v1)
1209. Share to Threads (Meta)
1210. Share to Snapchat
1211. Share to Telegram
1212. Share to Bluesky
1213. Share to Mastodon
1214. Share to Weibo (China market)
1215. Share to Line (Japan market)
1216. Share to KakaoTalk (Korea)
1217. Share to VK (Russia)

### 11.11 Additional Payment Methods (missed in v1)
1218. BNPL — Klarna
1219. BNPL — Affirm
1220. BNPL — Afterpay
1221. Brazilian Pix
1222. Chinese Alipay
1223. Chinese WeChat Pay
1224. Japanese Line Pay
1225. SEPA Direct Debit (EU)
1226. Cryptocurrency (Bitcoin, ETH, USDT) — optional

### 11.12 Additional Regional Compliance (missed in v1)
1227. LGPD compliance (Brazil)
1228. POPIA compliance (South Africa)
1229. APPI compliance (Japan)
1230. PIPEDA compliance (Canada)
1231. PIPA compliance (South Korea)
1232. PDPL compliance (Saudi Arabia)
1233. PDPA compliance (Singapore)
1234. PDPA compliance (Thailand)
1235. Australia Privacy Act compliance

### 11.13 Additional Admin / Support Tools (missed in v1)
1236. Bulk user actions (tag, suspend, email)
1237. User segment builder
1238. Custom user properties / attributes
1239. Email template editor
1240. In-app announcement editor
1241. System-wide banner for incidents
1242. Coupon bulk generator
1243. CSV export of users / revenue / usage
1244. Role-based admin permissions matrix UI
1245. Admin activity timeline per user

### 11.14 Additional Infrastructure (missed in v1)
1246. Circuit breakers (Hystrix-style)
1247. Graceful degradation fallbacks
1248. Image optimization service (imgproxy / imgix)
1249. Feature flag framework (GrowthBook / Unleash)
1250. Event streaming (Kafka — for enterprise analytics)
1251. Time-series metrics DB (Prometheus / InfluxDB)
1252. Distributed tracing (Jaeger / Tempo)
1253. Chaos testing infrastructure
1254. Blue-green database migrations

### 11.15 Additional Mobile Features (missed in v1)
1255. Apple Pencil support (iPad)
1256. Stylus support (Android tablets)
1257. iPad Pro optimized layout
1258. Android tablet optimized layout
1259. Foldable phone adaptive layout
1260. Siri Shortcuts integration
1261. Google Assistant actions
1262. Android home screen widget
1263. iOS lock screen widget
1264. Apple Watch companion (simple actions)
1265. Background task processing
1266. Keychain / Keystore secure storage

### 11.16 Infrastructure Details I Forgot (missed in v1)
1267. WebSocket for real-time job progress
1268. Server-Sent Events (SSE) alternative
1269. gRPC for internal service comms
1270. Protocol buffer schemas
1271. Database indexing strategy docs
1272. Query performance budget

---

## 12. Audit Notes — Duplicates & Scope Issues

### 12.1 Potential Duplicates / Overlaps to Merge

These features in v1 overlap significantly and should be considered as one with variants:

- **#68 "Background shadow generation" ≈ #69 "Realistic cast shadows"**
  → Merge as one feature: "AI shadow generation (drop shadow + cast shadow modes)"

- **#131 "Healing brush" ≈ #122 "Face healing tool"**
  → These are similar but face healing is face-specific — keep separate but cross-reference

- **#186 "Text-to-image generator" + #188 "Prompt library" + #189 "Negative prompt" + #208 "Seed control"**
  → These are all aspects of one feature (T2I generator with full controls), but splitting them out is useful for scoping

- **#276–#280 "Format conversion" (JPG→PNG, PNG→JPG, HEIC, WebP, AVIF)**
  → Better framed as one feature: "Universal format converter supporting JPG, PNG, HEIC, WebP, AVIF, TIFF, BMP, GIF"

- **#23 "Auto-enhance one-click" ≈ #33 "Wonder mode"**
  → Both are "one-click magic enhance" — same feature, different branding

- **#346 "Free tier" + #955–#958 "Tier pricing"**
  → These reference the same thing across different categories (platform vs business), which is fine

### 12.2 Features That Might Be Out of Scope for Early Stages

Not wrong, but you should NOT build these until you have paying users:

- **#1051 Real-time co-editing** (extremely complex, low demand for photo editing)
- **#304 Motion capture / Mocap transfer** (video feature — out of scope for photo MVP)
- **#811 Service mesh (Istio/Linkerd)** (overkill until you have 50+ microservices)
- **#814 Cross-region replication** (overkill for early stages — single region is fine)
- **#807 Kubernetes HPA** (start with simpler hosting like Render / Railway)
- **#575 Multi-armed bandit testing** (overkill — simple A/B is enough initially)
- **#948 Live Activities (iOS)** (low ROI for photo editor)
- **#599 Custom model upload (enterprise)** (wait until enterprise plan exists)
- **#800–803 Blue-green / Canary / Rollback automation** (great goals, but start with simple deploys)
- **#890 SOC 2 Type II** (needed for B2B enterprise sales — wait ~1 year)
- **#891 ISO 27001** (same as above)

### 12.3 Features Missing From v1 That Are Worth Adding (Already Added in §11)

These were the important gaps I caught in this audit:
- Basic editing tools (crop, rotate, undo/redo, histogram) — in every editor
- Text & typography tools — 90% of users want text on photos
- OCR — huge value, low effort
- Layers & masks — needed for pro users
- Face grouping & smart library — Remini and Apple Photos have this
- Regional compliance (LGPD, APPI, etc.) — needed for global launch
- Alternative payment methods (BNPL, regional) — needed for conversion

### 12.4 Things That Look Wrong / Need Clarification

- **#304 Motion capture / Mocap transfer** — this is really a video feature. Should move to Category 1.13 "Video Features" or remove from 1.9 Compositing.
- **#201 Fast training (under 1 minute)** — this is a *claim* not a feature. Remove or rephrase as "Fast training pipeline (target: sub-minute turnaround)".
- **#289 "Batch enhance"** and **#290 "Batch background removal"** etc. — these are really the SAME underlying feature (batch processor) applied to different AI models. One feature, many handlers.
- **#232 "Print sheet layout (4x6 with multiple copies)"** — this is a print feature; might be better grouped with an "Export & Print" sub-category we don't currently have.

### 12.5 Summary

**Audit verdict:**
- ✅ **Added:** ~170 features (mostly basic editing, text, OCR, regional compliance, payments)
- ⚠️ **Duplicates flagged:** ~8 features that overlap and could be merged
- 🚫 **Out-of-scope for MVP:** ~11 features to defer until later
- ❓ **Needs clarification:** ~4 features that are mislabeled or are claims rather than features

**New total: ~1,235 features** (up from 1,065, minus ~8 possible merges = net ~1,227 actionable).

---

## MVP Priority Cut

**Don't build all 1,065 at once.** Start with this priority cut:

### Phase 1 — MVP (Weeks 1-8)
Features needed to launch a usable product:

**AI Features (start with these 5):**
- #49 One-click background removal
- #1 AI upscale 2x/4x
- #75 AI face enhance
- #34 Old photo restoration
- #127 AI object removal

**Platform basics:**
- #321 Email + password signup
- #346 Free tier with limits
- #403 Download result
- #422 Watermark for free tier
- #504 Welcome screen
- #514 Loading states
- #848 Terms of Service
- #849 Privacy Policy

**Infrastructure:**
- #718 CDN (Cloudflare)
- #741 Cloudflare R2 storage
- #749 PostgreSQL
- #775 Sentry error tracking
- #819 HTTPS enforced
- #874 Auto-delete uploads 24h

### Phase 2 — Paid Launch (Weeks 9-16)
- Payments (Razorpay + Stripe)
- Credit system
- Pro subscription tier
- History / library
- Referral program
- Email marketing
- Analytics (PostHog)
- Content moderation (NSFW filter)

### Phase 3 — Growth (Months 5-6)
- SEO landing pages per feature
- Blog
- Social sharing
- More AI features (colorize, object removal, headshots)
- Internationalization (Hindi first)

### Phase 4 — Scale (Months 7-12)
- Mobile app (React Native)
- Admin dashboard
- Advanced AI features (avatars, passport, compositing)
- Community features
- API for developers

---

## Sources

Competitor research compiled from:
- [Remini](https://remini.ai/)
- [PhotoRoom](https://www.photoroom.com/)
- [Picsart](https://picsart.com/ai-tools/)
- [Canva Magic Studio](https://www.canva.com/magic/)
- [Fotor](https://www.fotor.com/ai-photo-editor/)
- [Remove.bg](https://www.remove.bg/api)
- [Lensa](https://lensa.app/)
- [Pixlr](https://pixlr.com/tools/photo-editor/)
- [YouCam Perfect](https://www.perfectcorp.com/consumer/apps/ymk)
- [Topaz Photo AI](https://www.topazlabs.com/topaz-photo)
- [HeadshotPro](https://www.headshotpro.com/)
- [Cleanup.pictures](https://cleanup.pictures/)
- [PicWish](https://picwish.com/photo-enhancer)
- [Hotpot.ai](https://hotpot.ai/tools)
- [VSCO](https://www.vsco.co/features/photo-filters)
- [Facetune](https://www.facetuneapp.com/features/ai-photo-editor)
- [Adobe Express](https://www.adobe.com/express/ai)
- [Photo AI](https://photoai.com/)
