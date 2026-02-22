from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import json

# ✅ This must come first
app = FastAPI()

# Define the game state schema
class GameState(BaseModel):
    player_health: int
    hiding: bool
    sprinting: bool
    distance: float

@app.post("/decide")
def decide(state: GameState):
    # Build a prompt that forces the AI to output JSON
    prompt = f"""
Player health: {state.player_health}
Hiding: {state.hiding}
Sprinting: {state.sprinting}
Distance: {state.distance}

Respond ONLY in JSON with this format:
{{
  "fog": <number between 0 and 1>,
  "aggression": <number between 0 and 1>,
  "lights": "flicker"/"off"/"bright"
}}
Do NOT include any other text outside the JSON.
"""

    # Call Ollama LLaMA3 AI
    result = subprocess.run(
        ["ollama", "run", "llama3", prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",   # fixes Unicode errors on Windows
        errors="ignore"     # ignore any weird characters
    )

    # Debug: print what AI actually returned
    print("AI raw output:", result.stdout)

    # Try to parse JSON from AI
    try:
        decision_json = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Fallback in case AI didn't give valid JSON
        decision_json = {"fog": 0.5, "aggression": 0.7, "lights": "flicker"}

    return {"decision": decision_json}