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
        length: str = "medium",
        voice_ids: Optional[List[str]] = None,
        characteristics: Optional[List[str]] = None
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
            speaker_config = self._get_speaker_config(num_speakers, style, voice_ids, characteristics)

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

    def _get_speaker_config(self, num_speakers: int, style: str, voice_ids: Optional[List[str]] = None, characteristics: Optional[List[str]] = None) -> List[Dict]:
        """
        Define speaker personalities based on style

        Args:
            num_speakers: Number of speakers (1-4 supported)
            style: Podcast style
            voice_ids: Optional list of ElevenLabs voice IDs to use. If provided, overrides default voices.

        Returns:
            List of speaker configurations
        """
        # Available ElevenLabs voices (premium voices)
        # You can get more voice IDs from: https://elevenlabs.io/app/voices
        available_voices = [
            "9BWtsMINqrJLrRacOk9x",  # Aria (female, expressive)
            "IKne3meq5aSn9XLyUdCD",  # Paul (male, friendly)
            "EXAVITQu4vr4xnSDxMaL",  # Bella (female, clear)
            "VR6AewLTigWG4xSOukaG",  # Arnold (male, deep)
            "ThT5KcBeYPX3keUQqHPh",  # Dorothy (female, warm)
            "XB0fDUnXU5powFXDhCwa",  # Charlotte (female, professional)
            "ErXwobaYiN019PkySvjV",  # Antoni (male, smooth)
            "MF3mGyEYCl7XYWbV9V6O",  # Elli (female, young)
        ]

        # Use provided voice IDs or default to first available voices
        if voice_ids:
            selected_voices = voice_ids[:num_speakers]
            # Pad with default voices if not enough provided
            while len(selected_voices) < num_speakers:
                selected_voices.append(available_voices[len(selected_voices) % len(available_voices)])
        else:
            selected_voices = available_voices[:num_speakers]

        # Limit to 4 speakers max for better quality
        num_speakers = min(num_speakers, 4)
        selected_voices = selected_voices[:num_speakers]

        # Characteristic to personality mapping
        characteristic_map = {
            'expert': ("Host/Expert", "Knowledgeable, enthusiastic, clear explainer"),
            'curious': ("Curious Learner", "Curious, asks great questions, relatable"),
            'analytical': ("Analyst", "Analytical, provides depth and context"),
            'practical': ("Practical Expert", "Experienced, shares practical insights"),
            'casual': ("Co-host", "Laid-back, conversational, storyteller"),
            'energetic': ("Co-host", "Energetic, witty, brings fun facts"),
            'friendly': ("Guest", "Friendly, engaging, relatable"),
            'humorous': ("Guest", "Humorous, light-hearted, entertaining"),
            'advocate': ("Advocate", "Analytical, presents one perspective"),
            'challenger': ("Challenger", "Critical thinker, questions assumptions"),
            'moderator': ("Moderator", "Balanced, facilitates discussion"),
            'data-driven': ("Analyst", "Data-driven, provides evidence")
        }

        # Default speaker names
        default_names = ["Alex", "Jordan", "Sam", "Riley"]

        configs = []
        for i in range(num_speakers):
            # Use custom characteristics if provided, otherwise use style defaults
            if characteristics and i < len(characteristics) and characteristics[i] in characteristic_map:
                char_value = characteristics[i]
                role, personality = characteristic_map[char_value]
                name = default_names[i]
            else:
                # Use style-based defaults
                if style == "educational":
                    speaker_names = ["Alex", "Jordan", "Sam", "Riley"]
                    speaker_roles = ["Host/Expert", "Curious Learner", "Co-host", "Guest Expert"]
                    personalities = [
                        "Knowledgeable, enthusiastic, clear explainer",
                        "Curious, asks great questions, relatable",
                        "Analytical, provides depth and context",
                        "Experienced, shares practical insights"
                    ]
                elif style == "casual":
                    speaker_names = ["Sam", "Riley", "Alex", "Jordan"]
                    speaker_roles = ["Co-host", "Co-host", "Guest", "Guest"]
                    personalities = [
                        "Laid-back, conversational, storyteller",
                        "Energetic, witty, brings fun facts",
                        "Friendly, engaging, relatable",
                        "Humorous, light-hearted, entertaining"
                    ]
                else:  # debate
                    speaker_names = ["Morgan", "Taylor", "Casey", "Jordan"]
                    speaker_roles = ["Advocate", "Challenger", "Moderator", "Analyst"]
                    personalities = [
                        "Analytical, presents one perspective",
                        "Critical thinker, questions assumptions",
                        "Balanced, facilitates discussion",
                        "Data-driven, provides evidence"
                    ]
                name = speaker_names[i] if i < len(speaker_names) else default_names[i]
                role = speaker_roles[i] if i < len(speaker_roles) else "Speaker"
                personality = personalities[i] if i < len(personalities) else "Engaging conversationalist"

            configs.append({
                "name": name,
                "role": role,
                "personality": personality,
                "voice_id": selected_voices[i]
            })

        return configs

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
