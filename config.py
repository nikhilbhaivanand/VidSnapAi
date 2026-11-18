import os

# Put your key in an environment variable instead of in the code:
#   export ELEVENLABS_API_KEY="your_new_key"      (Windows: set ELEVENLABS_API_KEY=your_new_key)
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
