# EduCast AI - Knowledge Extraction & Podcast Generation

Transform any learning topic into engaging podcast conversations using AI.

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your API keys
cat > .env << EOF
VALYU_API_KEY=your_valyu_key
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
EOF

# 4. Start the server
./start.sh

# 5. Open frontend/index.html in your browser
```

**Need API keys?** See [Step 2: Get Your API Keys](#step-2-get-your-api-keys) below.

## Overview

EduCast AI allows users to describe what they want to learn, then automatically:
1. Extracts comprehensive knowledge from the internet (via Valyu.ai)
2. Generates engaging multi-speaker podcast scripts (via OpenAI)
3. Creates natural-sounding audio conversations (via ElevenLabs)
4. Delivers downloadable audio content for learning on-the-go

## Current Status

✅ **Phase 1: Knowledge Extraction** (COMPLETE)
- Valyu.ai integration for web knowledge extraction
- Structured data extraction from internet sources
- Query-based learning content generation

✅ **Phase 2: Podcast Generation** (COMPLETE)
- OpenAI integration for conversational script generation
- ElevenLabs integration for multi-voice audio
- Complete end-to-end pipeline
- Flask API backend
- React frontend UI

## Detailed Setup Instructions

### Step 1: Prerequisites

Make sure you have:
- **Python 3.8 or higher** (check with `python3 --version`)
- **pip** package manager
- **Three API keys** (see Step 2)

### Step 2: Get Your API Keys

You'll need three API keys to run the full application:

#### 1. Valyu.ai API Key (Required)
1. Visit [Valyu Platform](https://platform.valyu.ai/)
2. Sign up or log in
3. Navigate to [API Keys](https://platform.valyu.ai/user/account/apikeys)
4. Copy your API key
5. **Free tier includes**: $10 credits, over 1000 query retrievals, no credit card required

#### 2. OpenAI API Key (Required for Podcast Generation)
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Create a new API key and copy it
5. **Note**: Requires credits in your OpenAI account

#### 3. ElevenLabs API Key (Required for Audio Generation)
1. Visit [ElevenLabs](https://elevenlabs.io/)
2. Sign up or log in
3. Navigate to [API Keys](https://elevenlabs.io/app/settings/api-keys)
4. Copy your API key
5. **Free tier includes**: Limited characters per month

### Step 3: Clone and Setup

```bash
# Navigate to your project directory
cd educast-ai

# Create a virtual environment (recommended)
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Edit the `.env` file and add your API keys:

```bash
# Valyu.ai API Key - Required for knowledge extraction
VALYU_API_KEY=your_valyu_api_key_here

# OpenAI API Key - Required for podcast script generation
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs API Key - Required for audio generation
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Flask Configuration (optional)
FLASK_ENV=development
```

**Important**: Replace `your_*_api_key_here` with your actual API keys. Do not commit the `.env` file to version control!

### Step 5: Test the Setup

#### Option A: Quick Test (Knowledge Extraction Only)

Test if knowledge extraction works:

```bash
python knowledge_extraction.py
```

This will test knowledge extraction with a sample query about quantum computing.

#### Option B: Test API Endpoints

Test the API server:

```bash
python test_api.py
```

#### Option C: Full Application Test

Start the full application:

```bash
# Make start.sh executable (first time only)
chmod +x start.sh

# Start the application
./start.sh
```

Or manually:

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Start the Flask API server
python api.py
```

The server will start on `http://localhost:5001`

### Step 6: Open the Web Interface

1. Open `frontend/index.html` in your web browser
   - You can double-click the file, or
   - Right-click → Open With → Your Browser
   - Or use: `open frontend/index.html` (macOS) or `xdg-open frontend/index.html` (Linux)

2. The interface should connect to the API running on port 5001

### Step 7: Test the Full Workflow

1. **Enter a learning query** in the input field, e.g.:
   - "I want to learn about machine learning basics"
   - "Explain quantum computing"
   - "How do neural networks work?"

2. **Click "Extract Knowledge"** - This will:
   - Search the internet using Valyu.ai
   - Extract comprehensive knowledge
   - Display sources and content

3. **Click "Generate Podcast"** - This will:
   - Generate a conversational script using OpenAI
   - Create multi-speaker audio using ElevenLabs
   - Download the podcast automatically
   - Display the audio player

## Testing Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with all three API keys
- [ ] Knowledge extraction test passes (`python knowledge_extraction.py`)
- [ ] API server starts without errors (`python api.py`)
- [ ] Frontend opens in browser (`frontend/index.html`)
- [ ] Can extract knowledge from a query
- [ ] Can generate and download a podcast

## Usage

### Web Interface (Recommended)

The easiest way to use EduCast AI is through the web interface:

1. **Start the API server:**
   ```bash
   ./start.sh
   ```
   Or manually:
   ```bash
   source venv/bin/activate
   python api.py
   ```

2. **Open the frontend:**
   - Open `frontend/index.html` in your browser
   - The interface will connect to `http://localhost:5001`

3. **Use the interface:**
   - Enter what you want to learn
   - Click "Extract Knowledge" to get information
   - Click "Generate Podcast" to create audio

### Command Line Testing

#### Test Knowledge Extraction Only

```bash
python knowledge_extraction.py
```

This tests knowledge extraction with a sample query and displays:
- Extracted knowledge content
- Source citations
- Podcast-ready formatted data

#### Test API Endpoints

```bash
python test_api.py
```

### Python API Usage

You can also use the modules directly in Python:

```python
from knowledge_extraction import KnowledgeExtractor
from audio_generator import PodcastGenerator

# Initialize
extractor = KnowledgeExtractor()
podcast_gen = PodcastGenerator()

# Extract knowledge
query = "I want to learn about machine learning basics"
knowledge = extractor.extract_knowledge(query)

if knowledge['success']:
    # Generate podcast
    result = podcast_gen.generate_podcast(
        knowledge=knowledge['answer'],
        topic=query,
        output_path="my_podcast.mp3",
        num_speakers=2,
        style="educational",
        length="medium"
    )
    
    if result['success']:
        print(f"Podcast saved to: {result['audio_path']}")
```

## API Endpoints

The Flask API provides the following endpoints:

- `GET /api/health` - Check API status and component readiness
- `POST /api/extract` - Extract knowledge from a query
  ```json
  {
    "query": "What you want to learn"
  }
  ```
- `POST /api/generate-podcast` - Generate complete podcast
  ```json
  {
    "query": "What you want to learn",
    "style": "educational" | "casual" | "debate",
    "length": "short" | "medium" | "detailed",
    "num_speakers": 2
  }
  ```
- `GET /api/download/<filename>` - Download generated podcast

## API Reference

### `KnowledgeExtractor`

Main class for extracting knowledge from the internet.

#### Methods

**`extract_knowledge(query, search_depth="comprehensive")`**
- Extracts comprehensive knowledge based on user query
- **Parameters:**
  - `query` (str): What the user wants to learn
  - `search_depth` (str): "quick", "standard", or "comprehensive"
- **Returns:** Dictionary with extracted knowledge and sources

**`search_with_details(query, max_results=20, relevance_threshold=0.4)`**
- Performs detailed search with structured results
- **Parameters:**
  - `query` (str): Search query
  - `max_results` (int): Maximum number of results
  - `relevance_threshold` (float): Minimum relevance score (0-1)
- **Returns:** Dictionary with detailed search results

**`format_for_podcast(knowledge_data)`**
- Formats extracted knowledge for podcast script generation
- **Parameters:**
  - `knowledge_data` (dict): Output from extract_knowledge()
- **Returns:** Formatted dictionary ready for podcast generation

## Response Format

### Successful Knowledge Extraction

```json
{
  "success": true,
  "query": "I want to learn about quantum computing",
  "answer": "Comprehensive explanation of quantum computing...",
  "sources": [
    {
      "title": "Source Title",
      "url": "https://example.com",
      "source": "Web",
      "relevance_score": 0.95
    }
  ],
  "raw_response": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "query": "original query",
  "error": "Error description"
}
```

## Project Structure

```
educast-ai/
├── api.py                    # Flask API server
├── knowledge_extraction.py   # Valyu.ai knowledge extraction
├── script_generator.py       # OpenAI script generation
├── audio_generator.py        # ElevenLabs audio generation
├── requirements.txt          # Python dependencies
├── start.sh                  # Startup script
├── .env                      # Your API keys (create this, gitignored)
├── frontend/
│   └── index.html           # React web interface
├── podcasts/                 # Generated podcast files (auto-created)
├── test_api.py              # API testing script
├── test_imports.py           # Dependency testing
├── test_valyu_search.py      # Valyu testing
├── README.md                # This file
└── PODCAST_APP_KNOWLEDGE_BASE.md  # Original project documentation
```

## Features

### Current Features
- ✅ Internet knowledge extraction (Valyu.ai)
- ✅ AI-powered script generation (OpenAI GPT-4)
- ✅ Multi-speaker audio generation (ElevenLabs)
- ✅ Web interface with real-time updates
- ✅ Automatic podcast download
- ✅ Source citations and references
- ✅ Multiple podcast styles (educational, casual, debate)
- ✅ Adjustable length (short, medium, detailed)

### Future Enhancements
- [ ] Multiple podcaster personality options
- [ ] Section-based generation for long topics
- [ ] Audio player with advanced controls
- [ ] Save and manage podcast library
- [ ] Export to podcast platforms (RSS feed)
- [ ] Voice cloning support
- [ ] Background music options

## Troubleshooting

### Common Issues

#### "Module not found" or Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### "API key not found" Error

1. **Check `.env` file exists:**
   ```bash
   ls -la .env
   ```

2. **Verify API keys are set:**
   ```bash
   # Should show your keys (be careful not to commit this!)
   cat .env
   ```

3. **Make sure keys are formatted correctly:**
   ```bash
   VALYU_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ELEVENLABS_API_KEY=your_key_here
   ```
   - No quotes around the key
   - No spaces around the `=`
   - Key starts immediately after `=`

#### "Failed to connect to API" in Frontend

1. **Check if API server is running:**
   ```bash
   # Should show process on port 5001
   lsof -i :5001
   ```

2. **Verify the port matches:**
   - API runs on port 5001 (check `api.py`)
   - Frontend connects to `http://localhost:5001` (check `frontend/index.html`)

3. **Check CORS is enabled:**
   - Make sure `flask-cors` is installed
   - Verify `CORS(app)` is in `api.py`

#### "No content received" from Valyu

- Check your Valyu API key is valid
- Verify you have remaining credits on Valyu.ai
- Try a simpler query first
- Check the API logs in the terminal

#### "OpenAI API Error"

- Verify your OpenAI API key is correct
- Check you have credits in your OpenAI account
- Try a shorter query or reduce `length` parameter
- Check rate limits in OpenAI dashboard

#### "ElevenLabs API Error"

- Verify your ElevenLabs API key is correct
- Check your character quota hasn't been exceeded
- Try generating a shorter podcast (`length: "short"`)
- Verify the voice IDs in `script_generator.py` are valid

#### Podcast Directory Issues

The `podcasts/` directory is created automatically. If you see file errors:

```bash
# Manually create the directory
mkdir -p podcasts

# Check permissions
ls -la podcasts
```

#### Port Already in Use

If port 5001 is already in use:

```bash
# Find what's using the port
lsof -i :5001

# Kill the process or change the port in api.py
```

#### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

If you're still stuck:

1. **Check the logs:**
   - API server logs appear in the terminal
   - Check `api.log` for detailed error messages

2. **Test components individually:**
   ```bash
   # Test knowledge extraction
   python knowledge_extraction.py
   
   # Test script generation
   python script_generator.py
   
   # Test audio generation
   python audio_generator.py
   ```

3. **Verify API keys work:**
   - Test each API key independently
   - Check API dashboards for usage/errors

4. **Check dependencies:**
   ```bash
   pip list | grep -E "valyu|openai|elevenlabs|flask"
   ```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions:
- Open a GitHub issue
- Check [Valyu.ai Documentation](https://docs.valyu.ai/)

---

Built with ❤️ for learners everywhere
