import elevenlabs
import inspect

print("Dir(elevenlabs):")
print(dir(elevenlabs))

try:
    from elevenlabs import ElevenLabs
    print("\nElevenLabs class found directly.")
except ImportError:
    print("\nElevenLabs class NOT found directly.")

try:
    from elevenlabs.client import ElevenLabs
    print("ElevenLabs class found in .client")
except ImportError:
    print("ElevenLabs class NOT found in .client")
