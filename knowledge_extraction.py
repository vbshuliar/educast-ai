"""
Knowledge Extraction Module using Valyu.ai
This module handles extracting knowledge from the internet based on user queries.
"""

import os
import sys
import json
from typing import Dict, List, Optional

# Check and import dependencies
try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: python-dotenv not installed")
    print("   Install with: pip3 install python-dotenv")
    sys.exit(1)

try:
    from valyu import Valyu
except ImportError:
    print("❌ Error: valyu SDK not installed")
    print("   Install with: pip3 install valyu")
    sys.exit(1)

# Load environment variables
load_dotenv()


class KnowledgeExtractor:
    """
    Handles knowledge extraction from the internet using Valyu.ai DeepSearch API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the KnowledgeExtractor.

        Args:
            api_key: Valyu.ai API key. If not provided, will try to load from VALYU_API_KEY env variable.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv('VALYU_API_KEY')

        if not self.api_key:
            raise ValueError(
                "Valyu API key not found. Please provide it as an argument or set VALYU_API_KEY environment variable.\n"
                "Get your API key from: https://platform.valyu.ai/user/account/apikeys"
            )

        # Initialize Valyu SDK
        self.valyu = Valyu(api_key=self.api_key)
        print("✓ Valyu.ai SDK initialized successfully")

    def extract_knowledge(
        self,
        query: str,
        search_depth: str = "comprehensive"
    ) -> Dict:
        """
        Extract knowledge from the internet based on the user's learning query.

        Args:
            query: What the user wants to learn (e.g., "I want to learn about quantum computing")
            search_depth: Level of detail - "quick", "standard", or "comprehensive"

        Returns:
            Dictionary containing:
                - success: Boolean indicating if extraction was successful
                - query: Original query
                - answer: AI-generated comprehensive answer
                - sources: List of source information (if available)
                - error: Error message (if failed)
        """
        print(f"\n🔍 Extracting knowledge for: '{query}'")
        print(f"   Search depth: {search_depth}")

        try:
            # Use the answer() method for AI-powered comprehensive responses
            response = self.valyu.answer(query=query)

            # Check if response is successful
            if response and hasattr(response, 'success') and response.success:
                print("✓ Knowledge extracted successfully")

                result = {
                    'success': True,
                    'query': query,
                    'answer': response.contents if hasattr(response, 'contents') else '',
                    'raw_response': response,
                    'sources': self._extract_sources(response)
                }

                return result
            elif response and hasattr(response, 'error') and response.error:
                print(f"✗ API Error: {response.error}")
                return {
                    'success': False,
                    'query': query,
                    'error': f'API Error: {response.error}',
                    'raw_response': response
                }
            else:
                print("✗ No content received from Valyu.ai")
                print(f"   Debug - Full response: {response}")
                return {
                    'success': False,
                    'query': query,
                    'error': 'No content received from Valyu.ai',
                    'raw_response': response
                }

        except Exception as e:
            print(f"✗ Error during knowledge extraction: {str(e)}")
            return {
                'success': False,
                'query': query,
                'error': str(e)
            }

    def search_with_details(
        self,
        query: str,
        max_results: int = 20,
        relevance_threshold: float = 0.4
    ) -> Dict:
        """
        Perform detailed search with structured results.
        Useful for getting specific sources and citations.

        Args:
            query: Search query
            max_results: Maximum number of results to return
            relevance_threshold: Minimum relevance score (0-1)

        Returns:
            Dictionary with search results including URLs, titles, and content
        """
        print(f"\n🔍 Searching with details for: '{query}'")

        try:
            response = self.valyu.search(
                query,
                max_num_results=max_results,
                relevance_threshold=relevance_threshold
            )

            if response and response.get('success'):
                print(f"✓ Found {len(response.get('results', []))} results")
                return {
                    'success': True,
                    'query': query,
                    'results': response.get('results', []),
                    'tx_id': response.get('tx_id')
                }
            else:
                print("✗ Search failed")
                return {
                    'success': False,
                    'query': query,
                    'error': 'Search failed',
                    'raw_response': response
                }

        except Exception as e:
            print(f"✗ Error during search: {str(e)}")
            return {
                'success': False,
                'query': query,
                'error': str(e)
            }

    def _extract_sources(self, response) -> List[Dict]:
        """
        Extract source information from Valyu response.

        Args:
            response: Raw response from Valyu.ai (response object)

        Returns:
            List of source dictionaries
        """
        sources = []

        # Check if search_results are available in the response (from answer() method)
        if hasattr(response, 'search_results') and response.search_results:
            for result in response.search_results:
                source = {
                    'title': result.get('title', 'Unknown') if isinstance(result, dict) else getattr(result, 'title', 'Unknown'),
                    'url': result.get('url', '') if isinstance(result, dict) else getattr(result, 'url', ''),
                    'source': result.get('source', 'Web') if isinstance(result, dict) else getattr(result, 'source', 'Web'),
                    'relevance_score': result.get('relevance_score', 0) if isinstance(result, dict) else getattr(result, 'relevance_score', 0)
                }
                sources.append(source)

        return sources

    def format_for_podcast(self, knowledge_data: Dict) -> Dict:
        """
        Format extracted knowledge for podcast generation.

        Args:
            knowledge_data: Output from extract_knowledge()

        Returns:
            Formatted dictionary ready for podcast script generation
        """
        if not knowledge_data.get('success'):
            return {
                'success': False,
                'error': knowledge_data.get('error', 'Knowledge extraction failed')
            }

        return {
            'success': True,
            'topic': knowledge_data['query'],
            'content': knowledge_data['answer'],
            'sources': knowledge_data.get('sources', []),
            'metadata': {
                'original_query': knowledge_data['query'],
                'extraction_method': 'valyu_ai_answer'
            }
        }


def main():
    """
    Example usage of the KnowledgeExtractor.
    """
    print("=" * 60)
    print("EduCast AI - Knowledge Extraction Test")
    print("=" * 60)

    # Initialize extractor
    try:
        extractor = KnowledgeExtractor()
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return
    except ImportError as e:
        print(f"\n❌ Error: {e}")
        return

    # Example query
    example_query = "I want to learn about quantum entanglement and its applications in quantum computing"

    print(f"\nExample Query: {example_query}")
    print("-" * 60)

    # Extract knowledge
    knowledge = extractor.extract_knowledge(example_query)

    # Display results
    if knowledge['success']:
        print("\n" + "=" * 60)
        print("EXTRACTED KNOWLEDGE")
        print("=" * 60)
        print(f"\n{knowledge['answer'][:500]}...")  # First 500 chars

        if knowledge.get('sources'):
            print("\n" + "=" * 60)
            print("SOURCES")
            print("=" * 60)
            for i, source in enumerate(knowledge['sources'][:5], 1):  # First 5 sources
                print(f"\n{i}. {source['title']}")
                print(f"   URL: {source['url']}")
                print(f"   Relevance: {source.get('relevance_score', 'N/A')}")

        # Format for podcast
        podcast_data = extractor.format_for_podcast(knowledge)

        print("\n" + "=" * 60)
        print("PODCAST-READY DATA")
        print("=" * 60)
        print(json.dumps({
            'topic': podcast_data['topic'],
            'content_length': len(podcast_data['content']),
            'num_sources': len(podcast_data.get('sources', []))
        }, indent=2))

    else:
        print("\n" + "=" * 60)
        print("ERROR")
        print("=" * 60)
        print(f"❌ {knowledge.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
