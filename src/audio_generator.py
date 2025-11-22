"""
Audio Generator Module
Converts dialogue scripts into multi-speaker podcast audio using ElevenLabs
"""

import os
from typing import Dict, List, Optional
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()


class AudioGenerator:
    """
    Generates multi-speaker podcast audio using ElevenLabs text-to-dialogue API
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AudioGenerator

        Args:
            api_key: ElevenLabs API key. If not provided, will try to load from ELEVENLABS_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')

        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key not found. Please provide it or set ELEVENLABS_API_KEY environment variable.\n"
                "Get your API key from: https://elevenlabs.io/app/settings/api-keys"
            )

        self.client = ElevenLabs(api_key=self.api_key)
        print("✓ ElevenLabs client initialized")

    def get_available_voices(self) -> Dict:
        """
        Get list of available ElevenLabs voices

        Returns:
            Dictionary with success status and list of voices
        """
        try:
            voices = self.client.voices.get_all()
            return {
                'success': True,
                'voices': [
                    {
                        'voice_id': voice.voice_id,
                        'name': voice.name,
                        'category': getattr(voice, 'category', 'premade'),
                        'description': getattr(voice, 'description', '')
                    }
                    for voice in voices.voices
                ]
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_podcast_audio(
        self,
        dialogue_script: List[Dict],
        output_path: str = "podcast.mp3"
    ) -> Dict:
        """
        Generate podcast audio from dialogue script

        Args:
            dialogue_script: List of dialogue turns with text and voice_id
                Format: [{"text": "...", "voice_id": "..."}, ...]
            output_path: Path where to save the generated audio

        Returns:
            Dictionary containing:
                - success: Boolean
                - audio_path: Path to generated audio file
                - duration: Approximate duration in seconds
                - error: Error message if failed
        """
        print(f"\n🎙️ Generating podcast audio...")
        print(f"   Dialogue turns: {len(dialogue_script)}")
        print(f"   Output: {output_path}")

        try:
            # Generate audio using text-to-dialogue API
            audio_generator = self.client.text_to_dialogue.convert(
                inputs=dialogue_script
            )

            # Save audio to file
            print("   Converting to audio...")

            # ElevenLabs returns an iterator of audio chunks
            # We need to collect them and save to file
            audio_chunks = []
            for chunk in audio_generator:
                audio_chunks.append(chunk)

            # Write to file
            with open(output_path, 'wb') as f:
                for chunk in audio_chunks:
                    f.write(chunk)

            # Get file size for approximate duration estimation
            file_size = os.path.getsize(output_path)
            # Rough estimate: ~1MB per minute for typical podcast audio
            estimated_duration = (file_size / 1024 / 1024) * 60

            print(f"✓ Audio generated successfully")
            print(f"   File: {output_path}")
            print(f"   Size: {file_size / 1024 / 1024:.2f} MB")
            print(f"   Estimated duration: ~{estimated_duration:.1f} seconds")

            return {
                'success': True,
                'audio_path': output_path,
                'file_size': file_size,
                'estimated_duration': estimated_duration
            }

        except Exception as e:
            print(f"✗ Error generating audio: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_simple_tts(
        self,
        text: str,
        voice_id: str = "9BWtsMINqrJLrRacOk9x",
        output_path: str = "speech.mp3"
    ) -> Dict:
        """
        Generate simple text-to-speech audio (single speaker)

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            output_path: Path where to save the audio

        Returns:
            Dictionary with success status and audio path
        """
        print(f"\n🔊 Generating speech...")

        try:
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2"
            )

            # Save audio
            audio_chunks = []
            for chunk in audio_generator:
                audio_chunks.append(chunk)

            with open(output_path, 'wb') as f:
                for chunk in audio_chunks:
                    f.write(chunk)

            print(f"✓ Speech generated: {output_path}")

            return {
                'success': True,
                'audio_path': output_path
            }

        except Exception as e:
            print(f"✗ Error generating speech: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class PodcastGenerator:
    """
    Complete podcast generation pipeline:
    Knowledge → Script → Audio
    """

    def __init__(self):
        """Initialize with all required generators"""
        from .script_generator import ScriptGenerator

        try:
            self.script_gen = ScriptGenerator()
            self.audio_gen = AudioGenerator()
            print("✓ Podcast Generator initialized")
        except ValueError as e:
            raise ValueError(f"Failed to initialize generators: {e}")

    def generate_podcast(
        self,
        knowledge: str,
        topic: str,
        output_path: str = "podcast.mp3",
        num_speakers: int = 2,
        style: str = "educational",
        length: str = "medium",
        voice_ids: Optional[List[str]] = None,
        characteristics: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate complete podcast from knowledge content

        Args:
            knowledge: Extracted knowledge content
            topic: Podcast topic
            output_path: Where to save the final audio
            num_speakers: Number of speakers
            style: Podcast style
            length: Podcast length

        Returns:
            Dictionary with results
        """
        print("\n" + "=" * 60)
        print("COMPLETE PODCAST GENERATION PIPELINE")
        print("=" * 60)

        # Step 1: Generate script
        print("\nStep 1: Generating dialogue script...")
        script_result = self.script_gen.generate_dialogue_script(
            knowledge=knowledge,
            topic=topic,
            num_speakers=num_speakers,
            style=style,
            length=length,
            voice_ids=voice_ids,
            characteristics=characteristics
        )

        if not script_result['success']:
            return {
                'success': False,
                'error': f"Script generation failed: {script_result.get('error')}"
            }

        # Step 2: Format for ElevenLabs
        print("\nStep 2: Formatting for ElevenLabs...")
        dialogue_script = self.script_gen.format_for_elevenlabs(
            script_result['script'],
            script_result['metadata']['speaker_config']
        )

        # Step 3: Generate audio
        print("\nStep 3: Generating audio...")
        audio_result = self.audio_gen.generate_podcast_audio(
            dialogue_script=dialogue_script,
            output_path=output_path
        )

        if not audio_result['success']:
            return {
                'success': False,
                'error': f"Audio generation failed: {audio_result.get('error')}"
            }

        # Success!
        print("\n" + "=" * 60)
        print("✅ PODCAST GENERATED SUCCESSFULLY!")
        print("=" * 60)

        return {
            'success': True,
            'audio_path': audio_result['audio_path'],
            'script': script_result['script'],
            'metadata': {
                **script_result['metadata'],
                'file_size': audio_result['file_size'],
                'estimated_duration': audio_result['estimated_duration']
            }
        }


def main():
    """
    Test the audio generator
    """
    print("=" * 60)
    print("Audio Generator Test")
    print("=" * 60)

    try:
        generator = AudioGenerator()
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return

    # Test with simple dialogue
    test_dialogue = [
        {
            "text": "[cheerfully] Welcome to KnowCast AI! Today we're testing our podcast generation.",
            "voice_id": "9BWtsMINqrJLrRacOk9x"
        },
        {
            "text": "[curious] This is amazing! How does it work?",
            "voice_id": "IKne3meq5aSn9XLyUdCD"
        },
        {
            "text": "[enthusiastically] We use AI to extract knowledge and generate natural conversations!",
            "voice_id": "9BWtsMINqrJLrRacOk9x"
        }
    ]

    result = generator.generate_podcast_audio(
        dialogue_script=test_dialogue,
        output_path="test_podcast.mp3"
    )

    if result['success']:
        print(f"\n✅ Test successful! Audio saved to: {result['audio_path']}")
    else:
        print(f"\n❌ Test failed: {result.get('error')}")


if __name__ == "__main__":
    main()
