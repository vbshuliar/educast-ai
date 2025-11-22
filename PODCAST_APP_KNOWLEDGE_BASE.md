# Podcast Generation App - Complete Knowledge Base

**Project Name:** EduCast AI (or your preferred name)
**Hackathon:** {Tech: Europe} London AI Hack
**Track:** AI Operating Partners for SMBs
**Build Time:** 8.5 hours total (3-4h build, 4-5h polish/demo)
**Builder:** Solo, Vibe Coding (Lovable + Claude)

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [Core Features](#core-features)
3. [Technical Architecture](#technical-architecture)
4. [File Upload & Parsing](#file-upload--parsing)
5. [Section Detection Strategy](#section-detection-strategy)
6. [Summary Generation](#summary-generation)
7. [Podcaster System](#podcaster-system)
8. [System Prompts (All Variants)](#system-prompts-all-variants)
9. [OpenAI Integration](#openai-integration)
10. [ElevenLabs Integration](#elevenlabs-integration)
11. [Audio Concatenation](#audio-concatenation)
12. [UI Specifications](#ui-specifications)
13. [State Management](#state-management)
14. [Error Handling](#error-handling)
15. [Demo Strategy](#demo-strategy)
16. [Pitch Script](#pitch-script)
17. [Testing Checklist](#testing-checklist)
18. [Fallback Plans](#fallback-plans)
19. [Post-Hackathon Roadmap](#post-hackathon-roadmap)

---

## Product Overview

### The Problem
Students and professionals struggle to digest lengthy educational materials (lecture slides, academic papers, technical reports). Reading is time-consuming and often happens when they can't (commuting, exercising, doing chores).

### The Solution
Transform any PDF document into engaging, multi-speaker podcast conversations. Users upload their materials, get AI-generated section summaries, customize the podcast style and length, then receive professional audio content they can learn from anywhere.

### Unique Value Propositions
1. **Multi-speaker format** - More engaging than single narrator (NotebookLM-style)
2. **Customizable depth** - Short refresh (3-4min), solid overview (7-10min), or deep dive (12-15min)
3. **Personality selection** - Choose from 5 distinct podcaster personalities or custom instructions
4. **Section-by-section control** - Generate only what you need, when you need it
5. **Educational quality** - Designed for learning, not just summarization

### Target Users
- University students preparing for exams
- Professionals doing continuous learning
- Researchers reviewing papers
- Training departments creating audio materials

---

## Core Features

### MVP (Must-Have for Demo)
1. ✅ PDF upload (max 50MB)
2. ✅ Automatic section detection with editable summaries
3. ✅ Length slider (Short/Medium/Detailed) per section
4. ✅ Podcaster selection (5 presets OR custom prompt)
5. ✅ Podcast script generation (OpenAI)
6. ✅ Multi-speaker audio generation (ElevenLabs)
7. ✅ Auto-download audio + script
8. ✅ Generate one section at a time
9. ✅ Error handling with popup messages

### Nice-to-Have (If Time Permits)
- Preview extracted text before section detection
- Regenerate with different settings
- Progress bar during generation
- Example template prompts for custom mode
- Share link for generated podcasts

### Post-Hackathon Features
- Multiple file format support (DOCX, PPTX)
- Batch generation (all sections at once)
- Voice cloning (use your own voice)
- Save projects for later
- Playlist mode (auto-play all sections)
- Export to podcast platforms
- Team collaboration features

---

## Technical Architecture

### Tech Stack
```
Frontend & Backend:
├── Lovable (React-based no-code platform)
│   ├── UI components
│   ├── State management
│   ├── API orchestration
│   └── File handling

APIs:
├── OpenAI API (GPT-4-turbo)
│   ├── Section detection
│   ├── Summary generation
│   └── Podcast script creation
│
└── ElevenLabs API
    ├── Text-to-speech generation
    └── Multi-voice support

Libraries (in Lovable):
└── PDF.js or similar for PDF parsing
```

### Data Flow
```
User uploads PDF
    ↓
Extract text (PDF.js)
    ↓
OpenAI: Detect sections + generate summaries
    ↓
Display editable section cards
    ↓
User selects podcasters, length, edits summaries
    ↓
User clicks "Generate Podcast"
    ↓
OpenAI: Create conversation script
    ↓
Parse script by speaker
    ↓
ElevenLabs: Generate audio for each speaker turn
    ↓
Concatenate audio files in order
    ↓
Auto-download combined audio.mp3 + script.txt
```

### API Rate Limits & Costs (Estimate)
**OpenAI (GPT-4-turbo):**
- Section detection: ~500 tokens per document
- Summary generation: ~200 tokens per section
- Script generation (Medium): ~1500 tokens output
- Cost per podcast: ~$0.05-0.15

**ElevenLabs:**
- ~1200 characters for 7-10 min podcast
- Generation time: 15-30 seconds
- Free tier: 10,000 characters/month
- Cost (paid): ~$0.30 per 1000 characters

**Total per medium podcast: ~$0.20-0.50**

---

## File Upload & Parsing

### File Requirements
- **Format:** PDF only (MVP)
- **Max size:** 50MB
- **Ideal size:** 2-30 pages for best results
- **Content type:** Text-based PDFs (not scanned images)

### PDF Parsing Strategy

**Library:** PDF.js (most reliable for Lovable)

**Implementation approach:**
```javascript
// Lovable component for file upload
const handleFileUpload = async (file) => {
  if (file.size > 50 * 1024 * 1024) {
    showError("File too large. Max 50MB");
    return;
  }
  
  if (file.type !== 'application/pdf') {
    showError("Please upload a PDF file");
    return;
  }
  
  setLoading(true);
  
  try {
    const text = await extractPDFText(file);
    
    if (text.length < 100) {
      showError("Could not extract text. Is this a scanned PDF?");
      return;
    }
    
    // Send to section detection
    await detectSections(text);
    
  } catch (error) {
    showError("Failed to parse PDF: " + error.message);
  } finally {
    setLoading(false);
  }
};
```

**Text Extraction:**
- Extract all text content from PDF
- Preserve basic structure (paragraphs, headings)
- Remove excessive whitespace
- Combine hyphenated words at line breaks
- Maximum extracted text: ~50,000 words (larger than this, warn user to upload specific sections)

**Edge Cases:**
- Scanned PDFs (no text layer) → Error: "Please upload a text-based PDF"
- Password-protected → Error: "Cannot read password-protected files"
- Corrupted files → Error: "File appears corrupted"
- Empty/minimal text → Error: "Not enough content to generate podcast"

---

## Section Detection Strategy

### Goal
Intelligently split documents into 2-8 logical sections based on content, not arbitrary page breaks.

### OpenAI Prompt for Section Detection

```
You are a document analyzer. Your task is to split educational content into logical sections.

RULES:
1. Create 2-8 sections (prefer 3-6)
2. Each section should be a coherent topic or concept
3. Base splits on:
   - Topic changes
   - Heading hierarchies
   - Conceptual boundaries
   - NOT just page length

4. Sections should be substantial (min 200 words ideally)
5. If two sections are very small (<150 words each), combine them with "&" in title

OUTPUT FORMAT (JSON only):
[
  {
    "title": "Section Title",
    "content": "Full text of this section",
    "summary": "2-3 sentence preview of what this section covers"
  },
  ...
]

CONTENT TO ANALYZE:
{extracted_pdf_text}

Generate the JSON now. No additional commentary.
```

### Post-Processing Section Detection

**Validation:**
```javascript
const validateSections = (sections) => {
  // Too few sections
  if (sections.length < 2) {
    // Attempt to split largest section
    return attemptManualSplit(sections);
  }
  
  // Too many sections (overwhelming)
  if (sections.length > 8) {
    return combineSmallerSections(sections, maxSections: 8);
  }
  
  // Very small sections
  sections = sections.map(section => {
    if (section.content.length < 150 && sections.length > 2) {
      // Mark for potential combination
      section.needsCombining = true;
    }
    return section;
  });
  
  return sections;
};
```

**Display to User:**
Each section shows:
- Title (editable)
- Summary (editable - 2-4 sentences)
- Content preview (first 200 chars, expandable)
- Word count indicator

**User can:**
- Edit title and summary before generation
- Manually combine sections (if provided in UI)
- Proceed with AI's section splits

---

## Summary Generation

### Purpose
Create concise, accurate summaries that serve as the foundation for podcast scripts. Quality summaries = quality podcasts.

### Initial Summary Generation (Automated)

**Already handled in section detection, but if regenerating:**

```
Create a 2-4 sentence summary of the following educational content.

REQUIREMENTS:
- Capture the main concept/thesis
- Mention 2-3 key points
- Written for someone unfamiliar with the topic
- Clear, accessible language
- No jargon without explanation

CONTENT:
{section_content}

Summary:
```

### Summary Quality Guidelines

**Good Summary Characteristics:**
✅ States the main concept clearly
✅ Includes specific details (not vague)
✅ Shows what someone will learn
✅ 50-100 words (2-4 sentences)
✅ Self-contained (doesn't assume prior sections)

**Example Good Summary:**
```
"This section explains quantum entanglement, where two particles 
remain connected regardless of distance. It covers the EPR paradox, 
Bell's theorem, and experimental verification. Students will understand 
how entanglement challenges classical physics and enables quantum computing."
```

**Bad Summary (too vague):**
```
"This section is about quantum physics concepts and their applications."
```

### User Summary Editing

**When user edits summary:**
- Auto-save changes (no manual save button)
- Show character count (aim for 50-100 words)
- Highlight if too short (<30 words) → "Consider adding more detail"
- Highlight if too long (>150 words) → "Summary might be too detailed"

**Chat Refinement (Future Feature):**
User can request changes:
- "Make it more technical"
- "Focus on the methodology section"
- "Explain it simpler"

System re-generates summary with OpenAI incorporating the request.

---

## Podcaster System

### The 5 Podcaster Personalities

Each podcaster has distinct:
- Teaching style
- Tone/vocabulary
- Strengths
- ElevenLabs voice assignment

---

### 😊 Alex - The Friendly Guide

**Personality:**
- Casual, warm, approachable
- Like a helpful peer explaining concepts
- Uses everyday analogies and relatable examples

**Teaching Style:**
- Asks clarifying questions
- Connects new concepts to familiar ideas
- "Think of it like..." / "You know how when you..."
- Breaks down complex ideas into simple parts

**Tone Markers:**
- Conversational interjections ("right?", "you see?")
- Enthusiastic but not over-the-top
- Occasionally self-deprecating humor

**Best For:**
- Making complex topics accessible
- First-time learners
- Building confidence

**ElevenLabs Voice:** `Adam` (warm, conversational male voice)

**Sample Dialogue:**
```
[Alex]: Okay, so quantum entanglement - I know it sounds scary, 
but think of it like this. You know how identical twins sometimes 
say they can feel what the other is experiencing? It's kind of like 
that, but for particles. They're connected in this weird way where 
measuring one instantly affects the other, no matter how far apart 
they are. Wild, right?
```

---

### 🤓 Jamie - The Analyst

**Personality:**
- Precise, detail-oriented, methodical
- Enjoys accuracy and thoroughness
- Structured thinker

**Teaching Style:**
- Step-by-step explanations
- Provides concrete examples with numbers/data
- "Let's break this down..." / "The key thing here is..."
- Clarifies terminology before proceeding

**Tone Markers:**
- Measured pace
- Uses transitional phrases ("First..., Second..., Finally...")
- Appreciates nuance ("It's not quite that simple because...")

**Best For:**
- Technical accuracy
- Exam preparation
- Understanding details and edge cases

**ElevenLabs Voice:** `Rachel` (clear, articulate female voice)

**Sample Dialogue:**
```
[Jamie]: Let me break down exactly what's happening with entanglement. 
When two particles become entangled, their quantum states become 
correlated. This means if you measure particle A and find it's 
spin-up, particle B will instantaneously be spin-down - even if 
they're light-years apart. The key thing to understand here is that 
no information actually travels between them. It's the correlation 
that was established when they first entangled.
```

---

### 🎯 Morgan - The Straight Shooter

**Personality:**
- Direct, energetic, no-nonsense
- Cuts through complexity to core insights
- Results-oriented

**Teaching Style:**
- Gets to the point quickly
- Summarizes key takeaways
- "Here's what matters..." / "Bottom line is..."
- Skips unnecessary context

**Tone Markers:**
- Punchy, shorter sentences
- Action-oriented language
- Impatient with fluff

**Best For:**
- Quick review
- Time-crunched learners
- Grasping main concepts fast

**ElevenLabs Voice:** `Domi` (energetic, assertive female voice)

**Sample Dialogue:**
```
[Morgan]: Alright, entanglement in 30 seconds. Two particles get 
linked. Measure one, you instantly know about the other - doesn't 
matter if it's across the room or across the galaxy. Why does this 
matter? Because it's the foundation of quantum computing and secure 
communication. That's it. That's entanglement.
```

---

### 🔬 Dr. Rivera - The Academic

**Personality:**
- Scholarly, thorough, scientific
- Respects intellectual rigor
- Comfortable with complexity

**Teaching Style:**
- Comprehensive explanations with context
- References research and evidence
- "Studies show..." / "It's important to note..."
- Addresses counterarguments and limitations

**Tone Markers:**
- Professional vocabulary
- Caveats and qualifications
- Historical/scientific context

**Best For:**
- Deep understanding
- Research preparation
- Graduate-level learning

**ElevenLabs Voice:** `Arnold` (authoritative, measured male voice)

**Sample Dialogue:**
```
[Dr. Rivera]: Quantum entanglement, first described by Einstein, 
Podolsky, and Rosen in their famous 1935 paper, represents one of 
the most counterintuitive predictions of quantum mechanics. The 
phenomenon occurs when particles interact in such a way that the 
quantum state of each particle cannot be described independently. 
Bell's theorem in 1964 and subsequent experiments by Aspect and 
others have confirmed that entanglement violates local realism, 
which has profound implications for our understanding of nature.
```

---

### 💡 Sam - The Creative

**Personality:**
- Enthusiastic, big-picture thinker, imaginative
- Sees patterns and connections
- Future-focused and visionary

**Teaching Style:**
- Connects ideas across domains
- Explores implications and applications
- "What if we..." / "This connects to..." / "Imagine..."
- Asks provocative questions

**Tone Markers:**
- Excited about possibilities
- Metaphorical language
- "Aha moment" realizations

**Best For:**
- Creative thinking
- Seeing practical applications
- Interdisciplinary connections

**ElevenLabs Voice:** `Bella` (upbeat, engaging female voice)

**Sample Dialogue:**
```
[Sam]: Here's what blows my mind about entanglement - it's basically 
nature's way of saying distance is an illusion! Think about what 
this means for the future. We're already using it to build quantum 
computers that could solve problems classical computers never could. 
Imagine unhackable communication networks, or teleporting quantum 
information across the world. This isn't science fiction anymore - 
startups are building this stuff right now!
```

---

### Podcaster Selection UI

**Mode 1: Visual Picker (Default)**

```
┌─────────────────────────────────────────────────┐
│ 🎙️ Choose Your Podcasters (Select 2-4)         │
├─────────────────────────────────────────────────┤
│                                                 │
│  ☑️ 😊 Alex - The Friendly Guide                │
│     Casual • Uses analogies • Approachable      │
│     Perfect for: First-time learning            │
│                                                 │
│  ☑️ 🤓 Jamie - The Analyst                      │
│     Precise • Methodical • Detail-oriented      │
│     Perfect for: Exam prep & accuracy           │
│                                                 │
│  ☐ 🎯 Morgan - The Straight Shooter             │
│     Direct • Efficient • No-nonsense            │
│     Perfect for: Quick review                   │
│                                                 │
│  ☐ 🔬 Dr. Rivera - The Academic                 │
│     Scholarly • Thorough • Research-focused     │
│     Perfect for: Deep understanding             │
│                                                 │
│  ☐ 💡 Sam - The Creative                        │
│     Enthusiastic • Big-picture • Innovative     │
│     Perfect for: Seeing applications            │
│                                                 │
│  ⚠️ Minimum 2, Maximum 4 speakers               │
└─────────────────────────────────────────────────┘

[⇄ Switch to Custom Instructions Mode]
```

**Mode 2: Custom Instructions**

```
┌─────────────────────────────────────────────────┐
│ ✍️ Custom Podcast Instructions                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  [Text area - user types custom prompt]        │
│                                                 │
│  ⚠️ BE SPECIFIC - AI follows literally          │
│                                                 │
│  💡 Example Prompts:                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • "Two students studying together - one       │
│     explains while the other asks questions"   │
│                                                 │
│  • "Interview format - curious host questions  │
│     expert guest"                               │
│                                                 │
│  • "Three perspectives: skeptic, enthusiast,   │
│     neutral moderator"                          │
│                                                 │
│  • "Very casual like friends at coffee shop,   │
│     with humor"                                 │
│                                                 │
│  • "Formal academic debate between two         │
│     professors"                                 │
│                                                 │
│  [Use Custom Instructions]                      │
└─────────────────────────────────────────────────┘

[⇄ Switch to Visual Picker]
```

### Default Behavior

**If user selects nothing:**
- Auto-select: Alex + Jamie (balanced: friendly + analytical)
- Show gentle notification: "Using Alex & Jamie as default hosts"

**Validation:**
- Minimum 2 podcasters (single speaker available in future)
- Maximum 4 podcasters (more becomes chaotic)
- If user tries 5+: "Too many speakers makes conversation hard to follow. Max 4 recommended."

### Recommended Combinations

**For different content types:**

1. **Alex + Jamie** (Default, Most Versatile)
   - Balanced: accessible yet thorough
   - Works for any topic

2. **Morgan + Dr. Rivera** (Time-Efficient Depth)
   - Quick but comprehensive
   - Good for busy professionals

3. **Alex + Sam** (Creative & Engaging)
   - Great for conceptual topics
   - Makes abstract ideas concrete

4. **Jamie + Dr. Rivera** (Academic Rigor)
   - Maximum accuracy and depth
   - Exam/research preparation

5. **Alex + Jamie + Morgan** (Balanced Trio)
   - Multiple perspectives
   - Dynamic conversation

---

## System Prompts (All Variants)

### Base Prompt Components

All prompts share these elements:
1. Role definition
2. Podcaster personalities (if visual picker used)
3. Length-specific structure
4. Dialogue rules
5. Educational techniques
6. Format requirements

### Integration Pattern

```
[BASE ROLE + PODCASTERS]
+
[LENGTH-SPECIFIC INSTRUCTIONS]
+
[CONTENT TO CONVERT]
```

---

### SHORT Podcast Prompt (3-4 minutes)

```
You are a podcast script generator creating educational content.

PODCASTERS INVOLVED:
{if visual picker:}
- Alex (Friendly Guide): Casual, uses analogies, warm and approachable
- Jamie (The Analyst): Precise, methodical, detail-oriented
{OR if custom prompt:}
CUSTOM INSTRUCTIONS: {user_custom_prompt}

PODCAST LENGTH: SHORT (3-4 minutes)

STYLE:
- Conversational and energetic
- Clear, concise explanations
- No fluff or lengthy introductions
- Fast-paced but not rushed

STRUCTURE:
1. Brief intro (10 seconds): "Hey, let's talk about [topic]"
2. Core concept explanation (1-2 minutes)
3. 2-3 key takeaways with minimal examples
4. Quick recap (10 seconds): "So remember: [main points]"

DIALOGUE RULES:
- Natural speech patterns with occasional "um", "you know", "right"
- Short exchanges (2-3 sentences max per speaker turn)
- Build on each other's points naturally
- No jargon without immediate, simple explanation
- Each speaker should have multiple turns (not long monologues)
- Maintain distinct personality voices

EDUCATIONAL APPROACH:
- State the concept clearly first
- Give ONE concrete example
- Focus on "what" and "why it matters"
- Skip detailed "how" unless critical

FORMAT:
[Speaker Name]: dialogue here
[Speaker Name]: dialogue here

TARGET: 400-500 words total dialogue

CONTENT TO CONVERT:
SECTION TITLE: {section_title}
SECTION SUMMARY: {user_edited_summary}

Generate the podcast script now. Start directly with dialogue - no preamble.
```

---

### MEDIUM Podcast Prompt (7-10 minutes)

```
You are a podcast script generator creating educational content.

PODCASTERS INVOLVED:
{if visual picker:}
- Alex (Friendly Guide): Casual, uses analogies, warm and approachable
- Jamie (The Analyst): Precise, methodical, detail-oriented
{OR if custom prompt:}
CUSTOM INSTRUCTIONS: {user_custom_prompt}

PODCAST LENGTH: MEDIUM (7-10 minutes)

STYLE:
- Conversational yet thorough
- Balance explanation with engagement
- Like two knowledgeable friends teaching each other
- Natural pacing with varied rhythm

STRUCTURE:
1. Warm intro (20 seconds): Hook + what we'll cover
2. Main concept deep-dive (3-4 minutes)
3. 4-6 key points with concrete examples (3-4 minutes)
4. Brief discussion/synthesis (1 minute)
5. Recap with actionable takeaways (30 seconds)

DIALOGUE RULES:
- Natural back-and-forth conversation (not lecture-style)
- Exchange length varies: 1-4 sentences per turn
- Use analogies and real-world examples liberally
- One speaker can challenge the other's explanations for clarity
- Ask "why does this matter?" or "how does this work?" questions
- Include mini-debates or "wait, so does that mean..." moments
- Occasional appropriate humor or relatable asides
- Vary sentence length for natural rhythm
- Each speaker should contribute roughly equally
- Maintain distinct personality voices throughout

EDUCATIONAL TECHNIQUES:
- State concept, then explain with example
- Use "think of it like..." analogies
- Address common misconceptions explicitly
- Connect to things learners already know
- Preview important points, then deliver, then review
- Build complexity gradually
- Include "aha moment" realizations

FORMAT:
[Speaker Name]: dialogue here
[Speaker Name]: dialogue here

TARGET: 900-1200 words total dialogue

CONTENT TO CONVERT:
SECTION TITLE: {section_title}
SECTION SUMMARY: {user_edited_summary}

Generate the podcast script now. Start directly with dialogue - no preamble.
```

---

### DETAILED Podcast Prompt (12-15 minutes)

```
You are a podcast script generator creating comprehensive educational content.

PODCASTERS INVOLVED:
{if visual picker:}
- Alex (Friendly Guide): Casual, uses analogies, warm and approachable
- Jamie (The Analyst): Precise, methodical, detail-oriented
{OR if custom prompt:}
CUSTOM INSTRUCTIONS: {user_custom_prompt}

PODCAST LENGTH: DETAILED (12-15 minutes)

STYLE:
- In-depth yet accessible
- Intellectually curious and exploratory
- Like a great office hours discussion or seminar
- Comfortable with complexity

STRUCTURE:
1. Engaging intro (30 seconds): Hook + clear roadmap
2. Foundation concepts (2-3 minutes): Build understanding from ground up
3. Core content with multiple angles (6-8 minutes): Main points, examples, edge cases, implications
4. Critical thinking segment (2-3 minutes): Applications, connections, deeper questions
5. Synthesis & comprehensive recap (1 minute): Big picture takeaways

DIALOGUE RULES:
- Longer, more nuanced exchanges (2-5 sentences per turn)
- Natural interruptions when excited: "Oh wait, that reminds me..."
- Build ideas progressively across multiple exchanges
- Circle back to earlier points with new context
- Include "aha moment" realizations
- Use storytelling for complex examples
- Comfortable with brief tangents if genuinely insightful
- Speakers can disagree constructively then reach understanding
- Show thinking process: "Hmm, let me think about that..."
- Maintain distinct personality voices throughout

EDUCATIONAL TECHNIQUES:
- Multiple examples showing different facets of same concept
- Counterexamples: "What if we tried X instead? Would it work?"
- Explicitly connect to related concepts from broader field
- Address "why should I care?" with real applications
- Anticipate student questions: "You might be wondering..."
- Compare and contrast different approaches/interpretations
- Discuss practical applications and implications
- Highlight common pitfalls or misconceptions
- Include historical context where relevant
- Different perspectives on the same concept
- Scaffolding: start simple, add layers of complexity

DEPTH MARKERS TO INCLUDE:
- Nuance: "It's not quite that simple because..."
- Edge cases: "But what happens when..."
- Limitations: "This approach works well for X, but struggles with Y"
- Advanced connections: "This relates to [other concept] in that..."
- Research context: "Studies have shown..." or "Current thinking is..."
- Debate points: "Some argue X, while others claim Y"

FORMAT:
[Speaker Name]: dialogue here
[Speaker Name]: dialogue here

TARGET: 1500-2000 words total dialogue

CONTENT TO CONVERT:
SECTION TITLE: {section_title}
SECTION SUMMARY: {user_edited_summary}

Generate the podcast script now. Start directly with dialogue - no preamble.
```

---

### Podcaster Personality Integration

When using **visual picker**, add these personality traits to system prompt:

```
SPEAKER PERSONALITIES:

Alex (Friendly Guide):
- Uses everyday language and relatable analogies
- Asks clarifying questions from learner perspective
- Phrases: "Think of it like...", "You know how...", "That's kind of like..."
- Warm, encouraging tone

Jamie (The Analyst):
- Precise, structured explanations
- Provides specific details and data
- Phrases: "Let's break this down...", "The key thing is...", "To be specific..."
- Measured, clear tone

Morgan (Straight Shooter):
- Direct, efficient communication
- Cuts to core insights quickly
- Phrases: "Bottom line is...", "Here's what matters...", "In simple terms..."
- Energetic, punchy tone

Dr. Rivera (The Academic):
- Scholarly, comprehensive approach
- References research and context
- Phrases: "Research shows...", "It's important to note...", "Historically..."
- Professional, authoritative tone

Sam (The Creative):
- Enthusiastic about connections and implications
- Big-picture thinking
- Phrases: "What if...", "Imagine...", "This connects to...", "The exciting thing is..."
- Upbeat, visionary tone
```

### Custom Prompt Integration

When user provides **custom instructions**, replace podcaster personalities with:

```
CUSTOM PODCAST SETUP:
{user_custom_prompt}

Follow these instructions carefully while maintaining educational quality and natural conversation flow.
```

---

### OpenAI API Configuration

**Model:** `gpt-4-turbo` (or `gpt-4-1106-preview`)

**Temperature by Length:**
- Short: `0.7` (focused, consistent)
- Medium: `0.8` (balanced creativity)
- Detailed: `0.9` (more exploratory, varied)

**Max Tokens:**
- Short: `800` tokens
- Medium: `2000` tokens
- Detailed: `3000` tokens

**Other Parameters:**
```json
{
  "model": "gpt-4-turbo",
  "temperature": 0.8,
  "max_tokens": 2000,
  "top_p": 1,
  "frequency_penalty": 0.3,
  "presence_penalty": 0.3
}
```

**Frequency/Presence Penalty Explanation:**
- Reduces repetitive phrasing
- Encourages varied vocabulary
- Makes dialogue sound more natural

---

## OpenAI Integration

### API Setup

**Endpoint:** `https://api.openai.com/v1/chat/completions`

**Authentication:**
```javascript
headers: {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${OPENAI_API_KEY}`
}
```

### Three Use Cases

#### 1. Section Detection

**Request:**
```javascript
const detectSections = async (pdfText) => {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: 'gpt-4-turbo',
      temperature: 0.5,
      messages: [
        {
          role: 'system',
          content: SECTION_DETECTION_PROMPT // See "Section Detection Strategy"
        },
        {
          role: 'user',
          content: pdfText
        }
      ],
      response_format: { type: "json_object" } // Force JSON response
    })
  });
  
  const data = await response.json();
  return JSON.parse(data.choices[0].message.content);
};
```

#### 2. Podcast Script Generation

**Request:**
```javascript
const generatePodcastScript = async (sectionTitle, summary, length, podcasters) => {
  // Build system prompt
  const systemPrompt = buildSystemPrompt(length, podcasters);
  
  const userPrompt = `
SECTION TITLE: ${sectionTitle}
SECTION SUMMARY: ${summary}
  `.trim();
  
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: 'gpt-4-turbo',
      temperature: getTemperature(length), // 0.7, 0.8, or 0.9
      max_tokens: getMaxTokens(length),    // 800, 2000, or 3000
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      frequency_penalty: 0.3,
      presence_penalty: 0.3
    })
  });
  
  const data = await response.json();
  return data.choices[0].message.content;
};
```

**Helper Functions:**
```javascript
const getTemperature = (length) => {
  const temps = {
    'short': 0.7,
    'medium': 0.8,
    'detailed': 0.9
  };
  return temps[length] || 0.8;
};

const getMaxTokens = (length) => {
  const tokens = {
    'short': 800,
    'medium': 2000,
    'detailed': 3000
  };
  return tokens[length] || 2000;
};

const buildSystemPrompt = (length, podcasters) => {
  // Get base prompt for length
  let prompt = BASE_PROMPTS[length]; // SHORT_PROMPT, MEDIUM_PROMPT, or DETAILED_PROMPT
  
  // Add podcaster personalities
  if (podcasters.mode === 'visual') {
    const personalities = podcasters.selected.map(name => 
      PODCASTER_PERSONALITIES[name]
    ).join('\n\n');
    
    prompt = prompt.replace('{podcaster_section}', personalities);
  } else {
    prompt = prompt.replace('{podcaster_section}', 
      `CUSTOM INSTRUCTIONS: ${podcasters.customPrompt}`
    );
  }
  
  return prompt;
};
```

### Error Handling

```javascript
const callOpenAI = async (payload) => {
  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      if (response.status === 429) {
        throw new Error('Rate limit exceeded. Please wait a moment and try again.');
      }
      
      if (response.status === 401) {
        throw new Error('Invalid API key. Please check your OpenAI configuration.');
      }
      
      if (response.status === 400) {
        throw new Error('Invalid request. ' + (error.error?.message || ''));
      }
      
      throw new Error('OpenAI API error: ' + (error.error?.message || 'Unknown error'));
    }
    
    const data = await response.json();
    
    if (!data.choices || !data.choices[0]) {
      throw new Error('Unexpected API response format');
    }
    
    return data.choices[0].message.content;
    
  } catch (error) {
    console.error('OpenAI API Error:', error);
    throw error;
  }
};
```

---

## ElevenLabs Integration

### API Setup

**Endpoint:** `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`

**Authentication:**
```javascript
headers: {
  'Accept': 'audio/mpeg',
  'Content-Type': 'application/json',
  'xi-api-key': `${ELEVENLABS_API_KEY}`
}
```

### Voice Mapping

```javascript
const VOICE_IDS = {
  'Alex': '21m00Tcm4TlvDq8ikWAM',      // Adam - warm male
  'Jamie': '21m00Tcm4TlvDq8ikWAM',     // Rachel - clear female  
  'Morgan': 'AZnzlk1XvdvUeBnXmlld',    // Domi - energetic female
  'Dr. Rivera': 'VR6AewLTigWG4xSOukaG', // Arnold - authoritative male
  'Sam': 'EXAVITQu4vr4xnSDxMaL'        // Bella - upbeat female
};

// Note: Replace with actual ElevenLabs voice IDs from your account
// These are example IDs - verify correct voices in ElevenLabs dashboard
```

### Text-to-Speech Generation

**Single Speaker Turn:**
```javascript
const generateAudio = async (text, voiceId) => {
  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
    {
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': process.env.ELEVENLABS_API_KEY
      },
      body: JSON.stringify({
        text: text,
        model_id: 'eleven_monolingual_v1',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75
        }
      })
    }
  );
  
  if (!response.ok) {
    throw new Error(`ElevenLabs API error: ${response.status}`);
  }
  
  const audioBlob = await response.blob();
  return audioBlob;
};
```

**Voice Settings Explanation:**
- `stability: 0.5` - Moderate variation (more expressive)
- `similarity_boost: 0.75` - High fidelity to voice model
- Adjust for different effects (higher stability = more consistent, less expressive)

### Script Parsing

**Parse podcast script into speaker turns:**
```javascript
const parseScript = (script) => {
  // Script format: [Speaker Name]: dialogue
  const lines = script.split('\n').filter(line => line.trim());
  
  const turns = [];
  
  for (const line of lines) {
    const match = line.match(/^\[(.+?)\]:\s*(.+)$/);
    
    if (match) {
      const [_, speaker, dialogue] = match;
      turns.push({
        speaker: speaker.trim(),
        text: dialogue.trim()
      });
    }
  }
  
  return turns;
};

// Example output:
// [
//   { speaker: 'Alex', text: 'Hey, let's talk about quantum physics today.' },
//   { speaker: 'Jamie', text: 'Great topic! Where should we start?' },
//   ...
// ]
```

### Generate All Audio Segments

```javascript
const generatePodcastAudio = async (script, podcasters) => {
  const turns = parseScript(script);
  const audioSegments = [];
  
  for (const turn of turns) {
    // Get voice ID for this speaker
    const voiceId = VOICE_IDS[turn.speaker];
    
    if (!voiceId) {
      console.warn(`No voice mapping for speaker: ${turn.speaker}`);
      continue;
    }
    
    // Generate audio for this turn
    try {
      const audioBlob = await generateAudio(turn.text, voiceId);
      
      audioSegments.push({
        speaker: turn.speaker,
        text: turn.text,
        audio: audioBlob,
        duration: estimateDuration(turn.text) // rough estimate
      });
      
      // Small delay to avoid rate limits
      await new Promise(resolve => setTimeout(resolve, 100));
      
    } catch (error) {
      console.error(`Failed to generate audio for ${turn.speaker}:`, error);
      throw error;
    }
  }
  
  return audioSegments;
};

const estimateDuration = (text) => {
  // Rough estimate: ~150 words per minute
  const words = text.split(/\s+/).length;
  return (words / 150) * 60; // seconds
};
```

### Error Handling

```javascript
const callElevenLabs = async (text, voiceId) => {
  try {
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
      {
        method: 'POST',
        headers: {
          'Accept': 'audio/mpeg',
          'Content-Type': 'application/json',
          'xi-api-key': process.env.ELEVENLABS_API_KEY
        },
        body: JSON.stringify({
          text: text,
          model_id: 'eleven_monolingual_v1',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75
          }
        })
      }
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      
      if (response.status === 401) {
        throw new Error('Invalid ElevenLabs API key');
      }
      
      if (response.status === 429) {
        throw new Error('ElevenLabs rate limit exceeded. Please wait and try again.');
      }
      
      if (response.status === 400) {
        throw new Error('Invalid request to ElevenLabs: ' + errorText);
      }
      
      throw new Error(`ElevenLabs error (${response.status}): ${errorText}`);
    }
    
    return await response.blob();
    
  } catch (error) {
    console.error('ElevenLabs Error:', error);
    throw error;
  }
};
```

---

## Audio Concatenation

### The Challenge

ElevenLabs generates individual audio files per API call. We need to:
1. Generate multiple audio segments (one per speaker turn)
2. Concatenate them in order
3. Create a single downloadable MP3

### Approach Options

#### Option A: Client-Side Concatenation (Recommended for Lovable)

**Pros:**
- No backend needed
- Works in Lovable environment
- User's browser does the work

**Cons:**
- Limited browser compatibility (modern browsers only)
- More complex client code

**Implementation:**

```javascript
// Using Web Audio API
const concatenateAudio = async (audioSegments) => {
  // Create audio context
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  
  // Decode all audio blobs to audio buffers
  const audioBuffers = [];
  
  for (const segment of audioSegments) {
    const arrayBuffer = await segment.audio.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    audioBuffers.push(audioBuffer);
  }
  
  // Calculate total length
  const totalLength = audioBuffers.reduce((sum, buffer) => sum + buffer.length, 0);
  
  // Create combined buffer
  const combinedBuffer = audioContext.createBuffer(
    audioBuffers[0].numberOfChannels,
    totalLength,
    audioBuffers[0].sampleRate
  );
  
  // Copy all segments into combined buffer
  let offset = 0;
  for (const buffer of audioBuffers) {
    for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
      const channelData = buffer.getChannelData(channel);
      combinedBuffer.copyToChannel(channelData, channel, offset);
    }
    offset += buffer.length;
  }
  
  // Convert to WAV blob (or use library to convert to MP3)
  const wavBlob = await audioBufferToWavBlob(combinedBuffer);
  
  return wavBlob;
};

// Helper: Convert AudioBuffer to WAV Blob
const audioBufferToWavBlob = (audioBuffer) => {
  const numberOfChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;
  
  const bytesPerSample = bitDepth / 8;
  const blockAlign = numberOfChannels * bytesPerSample;
  
  const data = [];
  for (let channel = 0; channel < numberOfChannels; channel++) {
    data.push(audioBuffer.getChannelData(channel));
  }
  
  const length = audioBuffer.length * numberOfChannels * bytesPerSample;
  const buffer = new ArrayBuffer(44 + length);
  const view = new DataView(buffer);
  
  // Write WAV header
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + length, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true); // fmt chunk size
  view.setUint16(20, format, true);
  view.setUint16(22, numberOfChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);
  writeString(view, 36, 'data');
  view.setUint32(40, length, true);
  
  // Write audio data
  let offset = 44;
  for (let i = 0; i < audioBuffer.length; i++) {
    for (let channel = 0; channel < numberOfChannels; channel++) {
      const sample = Math.max(-1, Math.min(1, data[channel][i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
      offset += 2;
    }
  }
  
  return new Blob([buffer], { type: 'audio/wav' });
};

const writeString = (view, offset, string) => {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
};
```

**Simpler Alternative: Use lamejs for MP3**

```javascript
// Include lamejs library in Lovable
// Then:
const concatenateToMP3 = async (audioSegments) => {
  const audioContext = new AudioContext();
  
  // Decode all segments
  const buffers = await Promise.all(
    audioSegments.map(async (seg) => {
      const arrayBuffer = await seg.audio.arrayBuffer();
      return await audioContext.decodeAudioData(arrayBuffer);
    })
  );
  
  // Concatenate samples
  const totalLength = buffers.reduce((sum, b) => sum + b.length, 0);
  const sampleRate = buffers[0].sampleRate;
  
  const combined = new Float32Array(totalLength);
  let offset = 0;
  
  for (const buffer of buffers) {
    const channelData = buffer.getChannelData(0); // mono or left channel
    combined.set(channelData, offset);
    offset += buffer.length;
  }
  
  // Convert to MP3 using lamejs
  const mp3encoder = new lamejs.Mp3Encoder(1, sampleRate, 128);
  const mp3Data = [];
  
  const sampleBlockSize = 1152;
  for (let i = 0; i < combined.length; i += sampleBlockSize) {
    const sampleChunk = combined.subarray(i, i + sampleBlockSize);
    const mp3buf = mp3encoder.encodeBuffer(convertFloat32ToInt16(sampleChunk));
    if (mp3buf.length > 0) {
      mp3Data.push(mp3buf);
    }
  }
  
  const mp3buf = mp3encoder.flush();
  if (mp3buf.length > 0) {
    mp3Data.push(mp3buf);
  }
  
  const blob = new Blob(mp3Data, { type: 'audio/mp3' });
  return blob;
};

const convertFloat32ToInt16 = (buffer) => {
  const l = buffer.length;
  const buf = new Int16Array(l);
  for (let i = 0; i < l; i++) {
    buf[i] = Math.min(1, buffer[i]) * 0x7FFF;
  }
  return buf;
};
```

#### Option B: Backend Service

If client-side is too complex, use simple backend:

```javascript
// Send all audio segments to backend
const concatenateOnServer = async (audioSegments) => {
  const formData = new FormData();
  
  audioSegments.forEach((segment, index) => {
    formData.append(`audio_${index}`, segment.audio, `segment_${index}.mp3`);
  });
  
  const response = await fetch('/api/concatenate-audio', {
    method: 'POST',
    body: formData
  });
  
  return await response.blob();
};
```

**Backend (Python Flask example):**
```python
from flask import Flask, request, send_file
from pydub import AudioSegment
import io

@app.route('/api/concatenate-audio', methods=['POST'])
def concatenate_audio():
    segments = []
    
    # Get all uploaded segments
    for key in sorted(request.files.keys()):
        audio_file = request.files[key]
        segment = AudioSegment.from_mp3(audio_file)
        segments.append(segment)
    
    # Concatenate
    combined = segments[0]
    for segment in segments[1:]:
        combined += segment
    
    # Export to bytes
    output = io.BytesIO()
    combined.export(output, format='mp3')
    output.seek(0)
    
    return send_file(output, mimetype='audio/mp3')
```

### Recommended Approach for Hackathon

**Use Option A (client-side) with WAV format:**
- Simpler than MP3 encoding
- Works in all modern browsers
- No backend needed
- Users can convert to MP3 themselves if needed

**OR use Option B if:**
- Lovable environment restricts audio manipulation
- You're comfortable spinning up quick backend
- Want guaranteed MP3 output

### Optimizations

**Reduce API Calls:**
- Combine consecutive turns by same speaker into one API call
- Example: If Alex has 3 turns in a row, combine before sending to ElevenLabs

```javascript
const optimizeTurns = (turns) => {
  const optimized = [];
  let current = null;
  
  for (const turn of turns) {
    if (current && current.speaker === turn.speaker) {
      // Same speaker - combine
      current.text += ' ' + turn.text;
    } else {
      // New speaker - save previous and start new
      if (current) optimized.push(current);
      current = { speaker: turn.speaker, text: turn.text };
    }
  }
  
  if (current) optimized.push(current);
  
  return optimized;
};
```

**Progress Tracking:**
```javascript
const generateWithProgress = async (turns, onProgress) => {
  const total = turns.length;
  const segments = [];
  
  for (let i = 0; i < turns.length; i++) {
    const audio = await generateAudio(turns[i].text, VOICE_IDS[turns[i].speaker]);
    segments.push({ ...turns[i], audio });
    
    onProgress((i + 1) / total * 100);
  }
  
  return segments;
};

// Usage:
generateWithProgress(turns, (percent) => {
  updateUI(`Generating audio: ${Math.round(percent)}%`);
});
```

---

## UI Specifications

### Complete User Flow

```
┌─────────────────────────────────────────┐
│ 1. LANDING / UPLOAD                     │
├─────────────────────────────────────────┤
│                                         │
│  🎙️ EduCast AI                          │
│  Transform Your PDFs into Podcasts      │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │                                 │  │
│  │   📁 Drop PDF here              │  │
│  │   or click to browse            │  │
│  │                                 │  │
│  │   Max 50MB • Text-based only    │  │
│  └─────────────────────────────────┘  │
│                                         │
│  ✨ Example: Upload lecture slides,    │
│     get 3 podcast episodes in minutes  │
└─────────────────────────────────────────┘

                    ↓
                    
┌─────────────────────────────────────────┐
│ 2. PROCESSING                           │
├─────────────────────────────────────────┤
│                                         │
│  ⏳ Analyzing your document...          │
│                                         │
│  [████████░░] 80%                       │
│                                         │
│  Extracting text and detecting sections │
└─────────────────────────────────────────┘

                    ↓

┌─────────────────────────────────────────┐
│ 3. SECTION OVERVIEW                     │
├─────────────────────────────────────────┤
│                                         │
│  📚 Found 4 sections in your document   │
│                                         │
│  [📄 Edit all sections below, then      │
│   generate podcasts individually]       │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ SECTION 1: Introduction to Quantum      │
│            Mechanics                     │
├─────────────────────────────────────────┤
│                                         │
│ ✏️ Summary (editable):                  │
│ ┌─────────────────────────────────────┐│
│ │ This section introduces fundamental ││
│ │ concepts of quantum mechanics,      ││
│ │ including wave-particle duality... ││
│ └─────────────────────────────────────┘│
│ 87 words • [Preview full text ▼]       │
│                                         │
│ 🎙️ Podcasters:                          │
│ ┌─────────────────────────────────────┐│
│ │ [😊 Alex] [🤓 Jamie] [+ Add more]   ││
│ └─────────────────────────────────────┘│
│ [⇄ Switch to custom instructions]      │
│                                         │
│ 📏 Length:                              │
│ ●━━━━━━━ Short (3-4 min)               │
│ ━━●━━━━━ Medium (7-10 min)             │
│ ━━━━━━● Detailed (12-15 min)           │
│                                         │
│        [🎙️ Generate Podcast]            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ SECTION 2: Wave Functions               │
├─────────────────────────────────────────┤
│ [Similar layout...]                     │
└─────────────────────────────────────────┘

                    ↓ (after clicking Generate)

┌─────────────────────────────────────────┐
│ SECTION 1: Introduction to Quantum      │
│            Mechanics                     │
├─────────────────────────────────────────┤
│                                         │
│ ⏳ Generating your podcast...           │
│                                         │
│ ✓ Creating conversation script...      │
│ ✓ Generating Alex's voice...           │
│ ⏳ Generating Jamie's voice... 60%      │
│ ⏺️ Combining audio...                   │
│                                         │
│ Estimated time: ~20 seconds             │
└─────────────────────────────────────────┘

                    ↓

┌─────────────────────────────────────────┐
│ SECTION 1: Introduction to Quantum      │
│            Mechanics                     │
├─────────────────────────────────────────┤
│                                         │
│ ✅ Podcast Ready! (7:42)                │
│                                         │
│ 🔊 [▶️ ━━━━━━━━━━━━━━ 0:00 / 7:42]    │
│                                         │
│ 📥 Downloaded: podcast.mp3 & script.txt│
│                                         │
│ 💬 Conversation Preview:                │
│ ┌─────────────────────────────────────┐│
│ │ [Alex]: Hey Jamie, ready to dive   ││
│ │ into quantum mechanics?            ││
│ │                                    ││
│ │ [Jamie]: Absolutely! Let's start   ││
│ │ with the basics...                 ││
│ │                                    ││
│ │ [View full script ▼]               ││
│ └─────────────────────────────────────┘│
│                                         │
│ [🔄 Regenerate] [⚙️ Different settings] │
└─────────────────────────────────────────┘
```

### Component Specifications

#### File Upload Component

**States:**
- `idle` - Waiting for file
- `uploading` - File being processed
- `error` - Invalid file
- `success` - File accepted

**Validation:**
```javascript
const validateFile = (file) => {
  if (file.size > 50 * 1024 * 1024) {
    return { valid: false, error: 'File too large (max 50MB)' };
  }
  
  if (file.type !== 'application/pdf') {
    return { valid: false, error: 'Only PDF files supported' };
  }
  
  return { valid: true };
};
```

**UI Feedback:**
- Drag-over state: Highlight drop zone
- Processing: Show spinner + "Extracting text..."
- Error: Red border + error message
- Success: Green checkmark + "Processing document..."

#### Section Card Component

**Props:**
```javascript
{
  id: string,
  title: string,
  summary: string,
  wordCount: number,
  fullContent: string (optional, for preview),
  selectedPodcasters: array,
  length: 'short' | 'medium' | 'detailed',
  status: 'editing' | 'generating' | 'complete' | 'error',
  audioUrl: string (if complete),
  script: string (if complete)
}
```

**States:**
- `editing` - User can edit, not generated yet
- `generating` - Podcast being created
- `complete` - Podcast ready
- `error` - Generation failed

**Editable Fields:**
- Title (inline edit)
- Summary (textarea, auto-expanding)

**Controls:**
- Podcaster selector
- Length slider
- Generate button (disabled during generation)

#### Podcaster Selector Component

**Two modes (toggle):**

1. **Visual Picker:**
   - 5 checkboxes with emoji + name + description
   - Default: Alex + Jamie pre-selected
   - Min 2, Max 4 validation
   - Warning if >3 selected

2. **Custom Prompt:**
   - Text area
   - Placeholder with examples
   - Warning about being specific
   - Character counter

**Toggle Logic:**
- Switching modes saves current selection
- Can switch back without losing data
- Default to Visual Picker on load

#### Length Slider Component

**Options:**
- Short (3-4 min)
- Medium (7-10 min)
- Detailed (12-15 min)

**Visual:**
```
Short     Medium    Detailed
  ●━━━━━━━━━━━━━━━
  
Casual    Thorough  Comprehensive
review    learning  deep-dive
```

**Default:** Medium

#### Audio Player Component

**Features:**
- Play/pause
- Scrub timeline
- Volume control
- Playback speed (1x, 1.25x, 1.5x)
- Time display (current / total)

**Auto-behavior:**
- Auto-play on generation complete (optional)
- Remember playback position

#### Progress Indicator Component

**During generation, show:**
1. Creating conversation script... ✓
2. Generating [Speaker 1] voice... ⏳ 60%
3. Generating [Speaker 2] voice... ⏺️
4. Combining audio... ⏺️

**States:**
- ⏺️ Waiting
- ⏳ In progress (with %)
- ✓ Complete
- ❌ Failed

---

## State Management

### Global State Structure

```javascript
const AppState = {
  // File handling
  uploadedFile: File | null,
  extractedText: string | null,
  
  // Sections
  sections: [
    {
      id: string,
      title: string,
      summary: string,
      content: string,
      wordCount: number,
      
      // Customization
      selectedPodcasters: {
        mode: 'visual' | 'custom',
        selected: ['Alex', 'Jamie'] | null,
        customPrompt: string | null
      },
      length: 'short' | 'medium' | 'detailed',
      
      // Generation status
      status: 'editing' | 'generating' | 'complete' | 'error',
      error: string | null,
      
      // Results
      script: string | null,
      audioUrl: string | null,
      scriptUrl: string | null,
      
      // Progress tracking
      generationProgress: {
        step: string,
        percent: number
      } | null
    }
  ],
  
  // UI state
  activeSection: string | null,
  showPodcasterModal: boolean,
  errors: []
};
```

### State Updates

**File Upload:**
```javascript
setState({
  uploadedFile: file,
  extractedText: null,
  sections: []
});
```

**Section Detection Complete:**
```javascript
setState({
  extractedText: fullText,
  sections: detectedSections.map(s => ({
    id: generateId(),
    ...s,
    selectedPodcasters: {
      mode: 'visual',
      selected: ['Alex', 'Jamie'],
      customPrompt: null
    },
    length: 'medium',
    status: 'editing',
    error: null,
    script: null,
    audioUrl: null,
    scriptUrl: null,
    generationProgress: null
  }))
});
```

**Start Generation:**
```javascript
updateSection(sectionId, {
  status: 'generating',
  error: null,
  generationProgress: {
    step: 'Creating script...',
    percent: 0
  }
});
```

**Update Progress:**
```javascript
updateSection(sectionId, {
  generationProgress: {
    step: 'Generating Alex voice...',
    percent: 40
  }
});
```

**Generation Complete:**
```javascript
updateSection(sectionId, {
  status: 'complete',
  script: generatedScript,
  audioUrl: audioBlob,
  scriptUrl: scriptBlob,
  generationProgress: null
});

// Trigger auto-download
downloadFile(audioBlob, 'podcast.mp3');
downloadFile(scriptBlob, 'script.txt');
```

**Generation Error:**
```javascript
updateSection(sectionId, {
  status: 'error',
  error: 'Failed to generate audio: Rate limit exceeded',
  generationProgress: null
});
```

### Local Storage Persistence (Optional)

Save state to allow users to refresh without losing work:

```javascript
// Save on every state change
useEffect(() => {
  localStorage.setItem('educast_state', JSON.stringify(state));
}, [state]);

// Load on mount
useEffect(() => {
  const saved = localStorage.getItem('educast_state');
  if (saved) {
    setState(JSON.parse(saved));
  }
}, []);
```

**What to save:**
- Sections (summaries, settings)
- NOT audio files (too large)
- NOT extracted text (can re-extract)

---

## Error Handling

### Error Categories

#### 1. File Upload Errors

**File too large:**
```
❌ File exceeds 50MB limit
💡 Try uploading specific sections or a smaller document
```

**Wrong file type:**
```
❌ Please upload a PDF file
💡 Currently only PDF format is supported
```

**Scanned PDF (no text):**
```
❌ Cannot extract text from this PDF
💡 This appears to be a scanned document. Please upload a text-based PDF
```

**Corrupted file:**
```
❌ File appears corrupted or invalid
💡 Try re-exporting your PDF and uploading again
```

#### 2. OpenAI Errors

**Rate limit:**
```
❌ Too many requests. Please wait a moment.
💡 Try again in 30 seconds
[Retry button available after countdown]
```

**Invalid API key:**
```
❌ Authentication failed
💡 Please check your API configuration
[This should not happen in production - log for debugging]
```

**Content policy violation:**
```
❌ Content cannot be processed
💡 The document may contain inappropriate content
```

**Timeout:**
```
❌ Request timed out
💡 Your document might be too complex. Try shorter sections.
[Retry button]
```

#### 3. ElevenLabs Errors

**Rate limit:**
```
❌ Voice generation limit reached
💡 Please wait a few minutes before generating more podcasts
[Show retry after timer]
```

**Invalid voice:**
```
❌ Voice generation failed
💡 Try selecting different podcasters
[This is a bug - log for fixing]
```

**Text too long:**
```
❌ Script too long for voice generation
💡 Try using 'Short' or 'Medium' length instead
```

#### 4. Audio Processing Errors

**Concatenation failed:**
```
❌ Failed to combine audio segments
💡 Please try generating again
[Retry button]
```

**Browser incompatibility:**
```
❌ Your browser doesn't support audio processing
💡 Please use Chrome, Firefox, or Edge
```

### Error Display Pattern

**Toast Notifications (temporary):**
```javascript
showToast({
  type: 'error' | 'warning' | 'success',
  message: string,
  duration: 3000-5000ms,
  action: { label: 'Retry', onClick: retryFunction } // optional
});
```

**Inline Errors (persistent):**
- Show on the specific section card
- Red border + error icon
- Error message + helpful tip
- Retry button if applicable

**Modal Errors (blocking):**
- For critical failures (API key issues, etc.)
- Requires acknowledgment
- May prevent further use until resolved

### Error Recovery

**Auto-retry logic:**
```javascript
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Exponential backoff: 2s, 4s, 8s
      const delay = Math.pow(2, i + 1) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};

// Usage:
try {
  const result = await retryWithBackoff(() => callOpenAI(prompt));
} catch (error) {
  showError('Failed after 3 attempts: ' + error.message);
}
```

**Graceful degradation:**
- If audio concatenation fails → Provide individual audio files
- If ElevenLabs fails → Provide script only, suggest trying again
- If section detection fails → Allow manual section input

### Error Logging

**For debugging (production):**
```javascript
const logError = (context, error) => {
  console.error(`[${context}]`, error);
  
  // Send to error tracking service (optional)
  // trackError({ context, error, user, timestamp });
};

// Usage:
try {
  await generatePodcast(section);
} catch (error) {
  logError('podcast_generation', {
    sectionId: section.id,
    error: error.message,
    stack: error.stack
  });
  
  showUserError('Failed to generate podcast. Please try again.');
}
```

---

## Demo Strategy

### Pre-Demo Preparation

**1. Test Files Ready:**
- **Short doc** (3 pages): Quick demo, ~2 min generation
- **Medium doc** (10 pages): Shows section detection
- **Long doc** (30+ pages): Shows smart splitting

**2. Pre-Generated Backup:**
- Have 1-2 podcasts already generated
- In case live generation fails
- Can show "here's one I made earlier"

**3. API Keys Verified:**
- Test OpenAI key 1 hour before
- Test ElevenLabs key 1 hour before
- Have backup keys ready

**4. Browser Setup:**
- Clear cache
- Close other tabs (performance)
- Test audio playback
- Check download folder permissions

### Demo Flow (90 seconds)

**Opening (10s):**
```
"Ever struggle to find time to read long documents? 
What if you could learn while commuting, exercising, 
or doing chores? Let me show you EduCast AI."
```

**Upload (5s):**
```
[Drag PDF]
"Upload any PDF - lecture slides, research papers, reports..."
```

**Section Detection (10s):**
```
[Shows 4 sections appearing]
"AI automatically splits it into logical sections with summaries.
You can edit these summaries to focus on what matters to you."
```

**Customization (15s):**
```
[Click on Section 2]
"Choose your podcasters - want it casual and friendly?
Select Alex and Jamie."

[Adjust slider]
"Pick how deep you want to go - short refresh, 
solid overview, or comprehensive deep-dive."
```

**Generation (20s):**
```
[Click Generate]
"Now watch the magic..."

[Show progress]
"Creating conversation script...
Generating Alex's voice...
Generating Jamie's voice...
Combining audio..."

[Audio ready]
"And done! Professional podcast in 20 seconds."
```

**Playback (20s):**
```
[Play audio clip - 15 seconds]
[Alex]: "Hey Jamie, let's talk about quantum entanglement..."
[Jamie]: "Great topic! So imagine two particles..."

"Hear that? Natural conversation, multiple speakers,
actually educational."
```

**Value Prop (10s):**
```
"Your document downloads as audio + transcript automatically.
Learn anywhere, anytime. Turn hours of reading into 
podcast episodes you can consume on the go."
```

### What to Emphasize

**Technical Innovation:**
- Multi-speaker generation (NotebookLM-style)
- Smart section detection
- Customizable depth and style

**User Value:**
- Time-saving for students/professionals
- Accessibility (learning while mobile)
- Control over output

**Polish:**
- Smooth UI
- Instant downloads
- Error handling

### Backup Plans

**If live generation fails:**
```
"Let me show you one I prepared earlier - 
the generation usually takes 20 seconds, 
but here's the result..."
[Play pre-generated podcast]
```

**If audio won't play:**
```
"The audio has been downloaded - you can see 
the script here showing the natural conversation 
between Alex and Jamie..."
[Show script preview]
```

**If upload fails:**
```
"While that's processing, let me show you 
an example with a document I uploaded earlier..."
```

### Handling Questions

**"How accurate is the content?"**
```
"It's based on GPT-4 and trained on vast educational materials.
You can always edit the summaries before generation to ensure
accuracy, and you have the transcript to verify."
```

**"What file types?"**
```
"PDFs for now - that's most academic and professional content.
Post-hackathon we're adding Word, PowerPoint, and more."
```

**"Can I use my own voice?"**
```
"Great question! ElevenLabs supports voice cloning - 
that's on our roadmap. For now, 5 professional voices 
to choose from."
```

**"How much does it cost?"**
```
"About $0.20-0.50 per podcast episode. For SMBs creating
training materials, that's 100x cheaper than hiring 
voice actors and editors."
```

**"How long are podcasts?"**
```
"You control it - 3-4 minutes for quick reviews, up to 
15 minutes for comprehensive learning. The slider adjusts
the depth automatically."
```

---

## Pitch Script

### 30-Second Elevator Pitch

```
"Students and professionals waste hours reading documents they 
could learn from while commuting or exercising. EduCast AI 
transforms any PDF into engaging, multi-speaker podcast conversations. 

Upload your lecture slides, get intelligent section summaries, 
customize the style and depth, and receive professional audio 
content in minutes. It's NotebookLM meets Spotify for education - 
making learning accessible anywhere, anytime."
```

### 2-Minute Pitch

**Problem (20s):**
```
"There's a massive gap in how we consume educational content. 
Research papers, lecture slides, technical reports - they're all 
locked in text format that demands our visual attention. 

Students preparing for exams, professionals doing continuous learning, 
researchers reviewing papers - they're all time-constrained. They want 
to learn during their commute, while exercising, doing chores - but 
they can't. Reading requires dedicated focus time they don't have."
```

**Solution (40s):**
```
"EduCast AI solves this with AI-powered podcast generation. 

Here's how it works: Upload any PDF. Our AI analyzes it and splits 
it into logical sections with summaries you can edit. Choose your 
podcast style - want it casual and friendly? Technical and precise? 
Quick overview or deep dive? 

We then generate a natural conversation between multiple AI voices - 
like NotebookLM's viral podcast feature, but with full control over 
depth, style, and focus. In 20 seconds, you get professional audio 
and a transcript, auto-downloaded and ready to go.

The result? Learn anywhere. A 50-page paper becomes three podcast 
episodes you can consume while commuting."
```

**Market Opportunity (30s):**
```
"The global e-learning market is $400B and growing. Audio learning 
specifically is exploding - podcast consumption is up 45% since 2020.

Our target customers:
- Universities creating accessible course materials
- Corporate training departments 
- Professional education platforms
- Individual students and lifelong learners

We're leveraging APIs that cost pennies per generation, making this 
scalable from day one."
```

**Traction / Demo (20s):**
```
"We built this in 8.5 hours using OpenAI for intelligent summarization 
and ElevenLabs for voice generation. The tech works - I can show you 
a live demo right now."

[Quick demo if time permits]
```

**Ask (10s):**
```
"We're looking for early design partners in education and corporate 
training. If you know anyone who creates learning materials at scale, 
I'd love an introduction."
```

### Key Messages to Hit

**Uniqueness:**
- Multi-speaker format (more engaging than single narrator)
- Customizable depth (not just generic summaries)
- Section-by-section control (targeted learning)

**Business Model (if asked):**
- B2B SaaS: $50-500/month for institutions
- API costs: ~$0.30 per podcast
- Gross margins: 80%+

**Competitive Advantage:**
- NotebookLM: Only does full-doc, no customization
- Traditional audiobooks: Expensive production, inflexible
- TTS tools: Single voice, not conversational

**Vision:**
- Short-term: Best tool for converting docs to podcasts
- Medium-term: Learning platform with spaced repetition
- Long-term: Personalized AI tutor for every subject

---

## Testing Checklist

### Pre-Demo Testing (1 hour before)

**File Upload:**
- [ ] PDF under 5MB works
- [ ] PDF at 30MB works
- [ ] PDF over 50MB shows error
- [ ] Non-PDF file shows error
- [ ] Drag-and-drop works
- [ ] Click to browse works

**Text Extraction:**
- [ ] Simple PDF extracts correctly
- [ ] Multi-column PDF extracts correctly
- [ ] PDF with images extracts text
- [ ] Scanned PDF shows appropriate error

**Section Detection:**
- [ ] 10-page doc creates 3-5 sections
- [ ] 30-page doc creates appropriate sections
- [ ] Very short doc (2 pages) handles gracefully
- [ ] Sections have reasonable summaries
- [ ] Section titles are descriptive

**Customization:**
- [ ] Can edit section titles
- [ ] Can edit summaries
- [ ] Summary character count updates
- [ ] Podcaster selector shows all 5 options
- [ ] Can select 2-4 podcasters
- [ ] Warning shows if <2 or >4 selected
- [ ] Can toggle to custom prompt mode
- [ ] Custom prompt saves when switching modes
- [ ] Length slider works for all positions
- [ ] Visual feedback on slider position

**Podcast Generation:**
- [ ] Generate button disabled during processing
- [ ] Progress indicator shows each step
- [ ] Progress percentages update
- [ ] Script appears when ready
- [ ] Audio player appears when ready
- [ ] Audio plays correctly
- [ ] Can pause/resume audio
- [ ] Can scrub timeline
- [ ] Volume control works
- [ ] Playback speed selector works

**Downloads:**
- [ ] Audio file downloads automatically
- [ ] Script file downloads automatically
- [ ] Files have correct format (MP3, TXT)
- [ ] File names are reasonable
- [ ] Can re-download if needed

**Error Handling:**
- [ ] OpenAI rate limit shows proper error
- [ ] ElevenLabs rate limit shows proper error
- [ ] Network error shows retry option
- [ ] Invalid API key shows helpful message
- [ ] Retry button works

**Multi-Section:**
- [ ] Can customize different sections differently
- [ ] Generating one section doesn't block UI
- [ ] Can view one section while another generates
- [ ] Multiple completed podcasts display correctly

### Edge Cases to Test

**Unusual Documents:**
- [ ] Document with only 1 section detected
- [ ] Document with 10+ sections detected
- [ ] Document in non-English (should still work)
- [ ] Document with lots of math symbols
- [ ] Document with tables and figures

**Unusual Selections:**
- [ ] Single podcaster (if allowed)
- [ ] 4 podcasters (maximum)
- [ ] All custom prompt mode
- [ ] Very long custom prompt (500+ chars)
- [ ] Switching between Short/Med/Detailed quickly

**Stress Testing:**
- [ ] Generate 3 sections in rapid succession
- [ ] Very long summary (500+ words)
- [ ] Very short summary (10 words)
- [ ] Maximum length podcast (15 min)
- [ ] Back button during generation
- [ ] Refresh page during generation

---

## Fallback Plans

### If Running Out of Time

**Priority 1 (Must Have):**
- File upload + text extraction
- Section detection (even if manual)
- Single podcast generation (even just one length)
- Basic audio playback
- Download functionality

**Priority 2 (Should Have):**
- Length slider (Short/Med/Detailed)
- 2 podcasters (Alex + Jamie)
- Edit summaries
- Progress indicator

**Priority 3 (Nice to Have):**
- All 5 podcasters
- Custom prompt mode
- Multiple sections
- Audio player controls
- Polished UI

**Absolute Minimum Viable Demo:**
```
1. Upload PDF
2. Shows one big summary (no sections)
3. Click "Generate Podcast"
4. Get one audio file with 2 speakers
5. Can play and download

This alone shows the core value.
```

### If Technical Blockers

**If audio concatenation is too hard:**
- Provide separate audio files per speaker
- User clicks through manually
- Still impressive, just different UX

**If ElevenLabs is problematic:**
- Use only 1-2 voices (simpler)
- Or generate script only, claim "audio in progress"
- Show script with "Imagine this as audio..."

**If OpenAI rate limits:**
- Use GPT-3.5-turbo (cheaper, faster)
- Shorter prompts
- Pre-generate some demos

**If file parsing is buggy:**
- Start with plain text input (copy-paste)
- "PDF upload coming soon"
- Still shows the core value

### If Demo Day Issues

**No internet:**
- Have pre-generated podcasts ready
- Show offline version of UI
- Walk through with screenshots

**APIs down:**
- Pre-recorded demo video
- Presentation slides with mockups
- Focus on vision and market opportunity

**Browser issues:**
- Have backup browser open
- Test on organizer's laptop beforehand
- Mobile fallback (if applicable)

**Time cut short:**
- Start with problem statement
- Show pre-made podcast playing
- Skip to value prop
- "Happy to show full demo after"

---

## Post-Hackathon Roadmap

### Immediate Improvements (Week 1)

**Technical:**
- Support DOCX, PPTX formats
- Improve section detection accuracy
- Better audio concatenation (reliable MP3 output)
- Progress bar with time estimates

**UX:**
- Batch generation (all sections at once)
- Preview full extracted text
- Undo/redo for edits
- Keyboard shortcuts

**Polish:**
- Better error messages
- Loading animations
- Responsive mobile design
- Dark mode

### Short-Term Features (Month 1)

**Core Features:**
- Voice cloning (use your own voice)
- Save projects for later
- Share generated podcasts via link
- Playlist mode (auto-play all sections)
- Export to podcast platforms (RSS feed)

**Quality:**
- Better speaker turn optimization (fewer API calls)
- Background music options
- Adjustable speaking speed per speaker
- Pause lengths between segments

**Education-Specific:**
- Quiz generation based on content
- Flashcard export
- Spaced repetition integration
- Chapter markers in audio

### Medium-Term (Quarter 1)

**Product:**
- Team collaboration (share projects)
- Organization accounts (multiple users)
- Template prompts library
- Custom brand voices for companies
- Analytics (listen time, completion rates)

**Integrations:**
- Google Drive / Dropbox import
- Notion integration
- Learning Management Systems (Canvas, Moodle)
- Slack bot for instant generation

**Business:**
- Pricing tiers (Free, Pro, Enterprise)
- Usage analytics
- Payment integration
- Customer dashboard

### Long-Term Vision (Year 1)

**Platform Evolution:**
- Full learning platform with courses
- AI tutor mode (answer questions about content)
- Interactive transcripts (click to jump)
- Video + slides → podcast
- Multi-language support

**Advanced AI:**
- Custom fine-tuned models for domains
- Adaptive difficulty (adjust based on learner)
- Debate mode (explore controversies)
- Research synthesis (combine multiple papers)

**Market Expansion:**
- B2B SaaS for corporate training
- White-label for universities
- API for developers
- Mobile apps (iOS, Android)

---

## Appendix: Quick Reference

### API Endpoints

**OpenAI:**
```
POST https://api.openai.com/v1/chat/completions
Header: Authorization: Bearer {key}
Model: gpt-4-turbo
```

**ElevenLabs:**
```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
Header: xi-api-key: {key}
Model: eleven_monolingual_v1
```

### Voice IDs (Example - Verify in Dashboard)

```javascript
{
  'Alex': '21m00Tcm4TlvDq8ikWAM',     // Adam
  'Jamie': 'EXAVITQu4vr4xnSDxMaL',    // Rachel
  'Morgan': 'AZnzlk1XvdvUeBnXmlld',   // Domi
  'Dr. Rivera': 'VR6AewLTigWG4xSOukaG', // Arnold
  'Sam': 'pNInz6obpgDQGcFmaJgB'       // Bella
}
```

### File Limits

- Max size: 50MB
- Format: PDF (text-based)
- Ideal: 2-30 pages
- Sections: 2-8 recommended

### Generation Times

- Script: 5-15 seconds
- Audio (Short): 10-15 seconds
- Audio (Medium): 20-30 seconds
- Audio (Detailed): 30-60 seconds
- Total: ~30-90 seconds per podcast

### Cost Estimates

- OpenAI (Medium podcast): ~$0.10
- ElevenLabs (Medium podcast): ~$0.30
- Total per generation: ~$0.40
- Monthly with 100 podcasts: ~$40 in API costs

---

## Final Notes

### Success Criteria

**Minimum Success:**
- Upload PDF → Get audio podcast
- At least 2 different speakers
- Download works
- Live demo works

**Good Success:**
- All customization options work
- Multiple sections
- Clean UI
- Positive judge feedback

**Great Success:**
- Flawless demo
- Judges want to use it
- Conversation about next steps
- Prize consideration

### Remember

1. **Focus on the demo** - The live demonstration is everything
2. **Keep it simple** - Better to have one thing work perfectly than three things work poorly
3. **Tell the story** - Connect problem → solution → value
4. **Be confident** - You built something real in 8.5 hours
5. **Have fun** - This is impressive work, enjoy showing it off!

---

**Good luck with your hackathon! You've got this! 🚀**

---

*Last Updated: Pre-Hackathon*
*Version: 1.0*
*Status: Ready to Build*
