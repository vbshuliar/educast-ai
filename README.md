# EduCast AI 🎙️

Transform any learning topic into engaging podcast conversations using AI.

## Quick Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add API Keys

Create a `.env` file in the project root:

```bash
VALYU_API_KEY=your_valyu_key_here
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### 3. Run the Application

```bash
./scripts/start.sh
```

Or manually:
```bash
source venv/bin/activate
python -m src.api
```

### 4. Open the Web Interface

Open `frontend/index.html` in your browser.

## How It Works

1. **Enter a learning query** (e.g., "I want to learn about machine learning")
2. **Click "Extract Knowledge"** - Searches the internet and extracts comprehensive information
3. **Click "Generate Podcast"** - Creates a multi-speaker audio conversation

## Project Structure

```
educast-ai/
├── src/              # Main application code
├── tests/            # Test files
├── scripts/          # Utility scripts
├── frontend/         # Web interface
└── podcasts/         # Generated audio files
```

## API Endpoints

- `GET /api/health` - Check API status
- `POST /api/extract` - Extract knowledge from query
- `POST /api/generate-podcast` - Generate complete podcast

## Testing

```bash
# Test knowledge extraction
python -m src.knowledge_extraction

# Test API
python tests/test_api.py
```

## Troubleshooting

**Module not found?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Port 5001 already in use?**
```bash
lsof -i :5001  # Find process
# Kill it or change port in src/api.py
```

**API key errors?**
- Make sure `.env` file exists in project root
- No quotes around keys: `KEY=value` not `KEY="value"`
- No spaces around `=`

---

**Built for learners everywhere** 🚀
