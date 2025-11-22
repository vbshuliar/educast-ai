"""
Script Generator Module
Converts extracted knowledge into engaging podcast dialogue using OpenAI
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ScriptGenerator:
    """
    Generates conversational podcast scripts from knowledge content using OpenAI
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ScriptGenerator

        Args:
            api_key: OpenAI API key. If not provided, will try to load from OPENAI_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please provide it or set OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=self.api_key)
        print("✓ OpenAI client initialized")

    def generate_dialogue_script(
        self,
        knowledge: str,
        topic: str,
        num_speakers: int = 2,
        style: str = "educational",
        length: str = "medium"
    ) -> Dict:
        """
        Generate a conversational podcast script from knowledge content

        Args:
            knowledge: The extracted knowledge content
            topic: The topic being discussed
            num_speakers: Number of speakers (2-3 recommended)
            style: Podcast style - "educational", "casual", "debate"
            length: Script length - "short" (~3-4min), "medium" (~7-10min), "detailed" (~12-15min)

        Returns:
            Dictionary containing:
                - success: Boolean
                - script: List of dialogue turns with speaker, text, and emotion
                - error: Error message if failed
        """
        print(f"\n🎬 Generating {length} {style} dialogue script...")
        print(f"   Topic: {topic}")
        print(f"   Speakers: {num_speakers}")

        try:
            # Define speaker personalities
            speaker_config = self._get_speaker_config(num_speakers, style)

            # Create system prompt
            system_prompt = self._create_system_prompt(speaker_config, style, length)

            # Create user prompt
            user_prompt = f"""
Topic: {topic}

Knowledge Content:
{knowledge}

Generate an engaging {length} podcast dialogue based on this content.
"""

            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )

            # Parse response
            import json
            script_data = json.loads(response.choices[0].message.content)

            print(f"✓ Generated script with {len(script_data.get('dialogue', []))} dialogue turns")

            return {
                'success': True,
                'script': script_data.get('dialogue', []),
                'metadata': {
                    'topic': topic,
                    'num_speakers': num_speakers,
                    'style': style,
                    'length': length,
                    'speaker_config': speaker_config
                }
            }

        except Exception as e:
            print(f"✗ Error generating script: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_speaker_config(self, num_speakers: int, style: str) -> List[Dict]:
        """
        Define speaker personalities based on style

        Returns:
            List of speaker configurations
        """
        if style == "educational":
            configs = [
                {
                    "name": "Alex",
                    "role": "Host/Expert",
                    "personality": "Knowledgeable, enthusiastic, clear explainer",
                    "voice_id": "9BWtsMINqrJLrRacOk9x"  # Aria (female, expressive)
                },
                {
                    "name": "Jordan",
                    "role": "Curious Learner",
                    "personality": "Curious, asks great questions, relatable",
                    "voice_id": "IKne3meq5aSn9XLyUdCD"  # Paul (male, friendly)
                }
            ]
        elif style == "casual":
            configs = [
                {
                    "name": "Sam",
                    "role": "Co-host",
                    "personality": "Laid-back, conversational, storyteller",
                    "voice_id": "9BWtsMINqrJLrRacOk9x"
                },
                {
                    "name": "Riley",
                    "role": "Co-host",
                    "personality": "Energetic, witty, brings fun facts",
                    "voice_id": "IKne3meq5aSn9XLyUdCD"
                }
            ]
        else:  # debate
            configs = [
                {
                    "name": "Morgan",
                    "role": "Advocate",
                    "personality": "Analytical, presents one perspective",
                    "voice_id": "9BWtsMINqrJLrRacOk9x"
                },
                {
                    "name": "Taylor",
                    "role": "Challenger",
                    "personality": "Critical thinker, questions assumptions",
                    "voice_id": "IKne3meq5aSn9XLyUdCD"
                }
            ]

        return configs[:num_speakers]

    def _create_system_prompt(self, speaker_config: List[Dict], style: str, length: str) -> str:
        """
        Create the system prompt for OpenAI
        """
        # Define target turn count based on length
        turn_targets = {
            "short": "8-12 dialogue turns (~3-4 minutes)",
            "medium": "15-20 dialogue turns (~7-10 minutes)",
            "detailed": "25-35 dialogue turns (~12-15 minutes)"
        }

        speakers_desc = "\n".join([
            f"- {s['name']} ({s['role']}): {s['personality']}"
            for s in speaker_config
        ])

        return f"""You are a professional podcast script writer. Create an engaging {style} podcast dialogue.

Speakers:
{speakers_desc}

Guidelines:
1. Target length: {turn_targets.get(length, turn_targets['medium'])}
2. Make it conversational and natural - use casual language, questions, acknowledgments
3. Include emotional cues in brackets: [enthusiastically], [curious], [thoughtfully], [excited], [chuckling]
4. Break down complex concepts into digestible pieces
5. Use examples and analogies when helpful
6. Maintain good pacing - alternate between speakers naturally
7. Add natural transitions and reactions
8. End with a clear conclusion or takeaway

Response Format (JSON):
{{
    "dialogue": [
        {{
            "speaker": "Alex",
            "text": "[enthusiastically] Welcome to today's episode! We're diving into...",
            "emotion": "enthusiastic"
        }},
        {{
            "speaker": "Jordan",
            "text": "[curious] That sounds fascinating! Can you explain...",
            "emotion": "curious"
        }}
    ]
}}

Make it engaging, educational, and fun!"""

    def format_for_elevenlabs(self, script: List[Dict], speaker_config: List[Dict]) -> List[Dict]:
        """
        Format script for ElevenLabs text-to-dialogue API

        Args:
            script: Generated dialogue script
            speaker_config: Speaker configuration with voice IDs

        Returns:
            List formatted for ElevenLabs API
        """
        # Create speaker name to voice_id mapping
        voice_map = {speaker['name']: speaker['voice_id'] for speaker in speaker_config}

        formatted = []
        for turn in script:
            speaker_name = turn.get('speaker')
            voice_id = voice_map.get(speaker_name, speaker_config[0]['voice_id'])

            formatted.append({
                "text": turn.get('text', ''),
                "voice_id": voice_id
            })

        return formatted


def main():
    """
    Test the script generator
    """
    print("=" * 60)
    print("Script Generator Test")
    print("=" * 60)

    try:
        generator = ScriptGenerator()
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return

    # Test with sample knowledge
    sample_knowledge = """
Quantum entanglement is a phenomenon where particles become correlated in such a way
that the quantum state of each particle cannot be described independently. When particles
are entangled, measurements on one particle instantly affect the other, regardless of distance.
This has applications in quantum computing for creating powerful quantum algorithms and
quantum cryptography for secure communication.
"""

    result = generator.generate_dialogue_script(
        knowledge=sample_knowledge,
        topic="Quantum Entanglement",
        num_speakers=2,
        style="educational",
        length="short"
    )

    if result['success']:
        print("\n" + "=" * 60)
        print("GENERATED SCRIPT")
        print("=" * 60)

        for i, turn in enumerate(result['script'], 1):
            print(f"\n{i}. {turn['speaker']}: {turn['text']}")

        print("\n" + "=" * 60)
        print(f"Total turns: {len(result['script'])}")
    else:
        print(f"\n❌ Failed: {result.get('error')}")


if __name__ == "__main__":
    main()
