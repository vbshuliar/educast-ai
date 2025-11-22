"""
Flask API for EduCast AI Knowledge Extraction
Simple backend to serve the React frontend
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from .knowledge_extraction import KnowledgeExtractor
from .audio_generator import PodcastGenerator
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Get project root directory (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PODCASTS_DIR = os.path.join(PROJECT_ROOT, 'podcasts')

# Ensure podcasts directory exists
os.makedirs(PODCASTS_DIR, exist_ok=True)

# Initialize knowledge extractor
try:
    extractor = KnowledgeExtractor()
    print("✓ Knowledge Extractor initialized")
except Exception as e:
    print(f"✗ Failed to initialize extractor: {e}")
    extractor = None

# Initialize podcast generator
try:
    podcast_gen = PodcastGenerator()
    print("✓ Podcast Generator initialized")
except Exception as e:
    print(f"✗ Failed to initialize podcast generator: {e}")
    podcast_gen = None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'extractor_ready': extractor is not None,
        'podcast_gen_ready': podcast_gen is not None
    })


@app.route('/api/extract', methods=['POST'])
def extract_knowledge():
    """
    Extract knowledge based on user query

    Request body:
    {
        "query": "What I want to learn about"
    }

    Response:
    {
        "success": true/false,
        "query": "original query",
        "answer": "extracted knowledge",
        "sources": [...],
        "error": "error message if failed"
    }
    """
    try:
        # Get query from request
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'No query provided. Please send {"query": "your question"}'
            }), 400

        query = data['query'].strip()

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400

        if not extractor:
            return jsonify({
                'success': False,
                'error': 'Knowledge extractor not initialized. Check API key.'
            }), 500

        # Extract knowledge
        print(f"\n📥 Received query: {query}")
        result = extractor.extract_knowledge(query)

        if result['success']:
            print(f"✓ Successfully extracted {len(result['answer'])} characters")

            # Convert to JSON-serializable format
            json_result = {
                'success': True,
                'query': result['query'],
                'answer': result['answer'],
                'sources': result.get('sources', [])
            }
            return jsonify(json_result)
        else:
            print(f"✗ Extraction failed: {result.get('error', 'Unknown error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            })

    except Exception as e:
        print(f"✗ Error in extract endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/format-podcast', methods=['POST'])
def format_for_podcast():
    """
    Format extracted knowledge for podcast generation (future use)

    Request body:
    {
        "knowledge": {...}  # output from /api/extract
    }
    """
    try:
        data = request.get_json()

        if not data or 'knowledge' not in data:
            return jsonify({
                'success': False,
                'error': 'No knowledge data provided'
            }), 400

        if not extractor:
            return jsonify({
                'success': False,
                'error': 'Knowledge extractor not initialized'
            }), 500

        # Format for podcast
        podcast_data = extractor.format_for_podcast(data['knowledge'])

        return jsonify(podcast_data)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/generate-podcast', methods=['POST'])
def generate_podcast():
    """
    Generate complete podcast: Knowledge → Script → Audio

    Request body:
    {
        "query": "What to learn about",
        "style": "educational" | "casual" | "debate",  # optional
        "length": "short" | "medium" | "detailed",    # optional
        "num_speakers": 2                              # optional
    }

    Response:
    {
        "success": true/false,
        "audio_url": "/api/download/podcast.mp3",
        "script": [...],
        "metadata": {...},
        "error": "error message if failed"
    }
    """
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400

        query = data['query'].strip()
        style = data.get('style', 'educational')
        length = data.get('length', 'medium')
        num_speakers = data.get('num_speakers', 2)

        if not podcast_gen:
            return jsonify({
                'success': False,
                'error': 'Podcast generator not initialized. Check API keys.'
            }), 500

        print(f"\n🎙️ Full podcast generation requested")
        print(f"   Query: {query}")
        print(f"   Style: {style}, Length: {length}, Speakers: {num_speakers}")

        # Step 1: Extract knowledge
        print("\n📚 Step 1: Extracting knowledge...")
        knowledge_result = extractor.extract_knowledge(query)

        if not knowledge_result['success']:
            return jsonify({
                'success': False,
                'error': f"Knowledge extraction failed: {knowledge_result.get('error')}"
            }), 500

        # Step 2: Generate podcast
        print("\n🎬 Step 2: Generating podcast...")
        safe_filename = query[:50].replace(' ', '_').replace('/', '_')
        output_path = os.path.join(PODCASTS_DIR, f"{safe_filename}.mp3")
        podcast_result = podcast_gen.generate_podcast(
            knowledge=knowledge_result['answer'],
            topic=query,
            output_path=output_path,
            num_speakers=num_speakers,
            style=style,
            length=length
        )

        if not podcast_result['success']:
            return jsonify({
                'success': False,
                'error': podcast_result.get('error')
            }), 500

        # Success!
        print("✅ Podcast generated successfully!")

        # Read the audio file and convert to base64 for direct client download
        import base64
        with open(podcast_result['audio_path'], 'rb') as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode('utf-8')

        return jsonify({
            'success': True,
            'audio_data': audio_data,  # Base64 encoded audio
            'audio_filename': os.path.basename(podcast_result['audio_path']),
            'script': podcast_result['script'],
            'metadata': podcast_result['metadata']
        })

    except Exception as e:
        print(f"✗ Error in generate-podcast endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_podcast(filename):
    """
    Download generated podcast audio file
    """
    try:
        file_path = os.path.join(PODCASTS_DIR, filename)

        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        return send_file(
            file_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Download error: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("EduCast AI API Server")
    print("=" * 60)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"API Key configured: {'Yes' if os.getenv('VALYU_API_KEY') else 'No'}")
    print()

    # Run server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
