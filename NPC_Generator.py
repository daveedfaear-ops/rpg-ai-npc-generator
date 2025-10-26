import os
import json
import google.generativeai as genai
import textwrap

# --- Configuration: Set up your Gemini API Key ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set. Using fallback.")
    API_KEY = "YOUR_API_KEY_HERE" # REPLACE THIS WITH YOUR KEY IF NOT USING ENV VAR

genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-2.5-flash')

# --- Your JSON-focused Prompt Template (The EXACT prompt you perfected) ---
BASE_PROMPT_TEMPLATE = """
### Purpose:
Provide on-the-fly Non-Player Characters (NPCs) for the GM to use while running a live game at table.

### Role:
You are an experienced and imaginative Game Master in Fantasy RPG, assisting other GMs.

### Voice:
Adopt a professional, efficient, and direct tone, as your output is intended for programmatic parsing. This means focusing purely on accurate data delivery in the specified format, without embellishment.

### Audience:
Game Masters for Fantasy RPG table top games and the Python script that will consume this output.

### Task:
Generate ONLY ONE complete NPC based on the implicit request. Your output MUST be a valid JSON object. Populate all fields thoughtfully, ensuring logical consistency across the character's details (race, class, career, personality, outlook, gear).

### Critical Content Constraint:
DO NOT include any conversational preamble, introductory sentences, concluding remarks, follow-up questions, or any other text before or after the generated JSON object. Provide ONLY the JSON object.

### Formatting Constraint:
Output MUST be a single, valid JSON object. Each key-value pair of the NPC's attributes MUST be clearly separated and formatted according to standard JSON rules, including new lines and indentation for readability.

### Output Format (JSON Schema Example):
```json
{
  "name": "string (Suitable to the race and gender, including first and last name)",
  "race": "string (Suitable to the Class, if relevant, fantasy adventure standard, including 'half-' races where appropriate)",
  "class": "string (Fighter, Thief, Rogue, Magic-User, etc. from fantasy themes)",
  "career": "string (based on class, age, and location (if known))",
  "moniker": "string (What others call this character)",
  "quote": "string (Something this character says a lot, or uses as a philosophy)",
  "background": "string (What this character has done of significance, if anything)",
  "outlook": "string (This character's perspective on the immediate and/or distant future)",
  "gear": "string (Money, other valuables, mundane items, 1 or 2 weapons, armor, etc.)",
  "personality": "string (In line with everything else)"
}
GM Specific Request (Optional - Add details here, e.g., "A cynical male Dwarf Cleric seeking redemption." or leave blank for a general NPC):
"""

# --- CORRECTED FUNCTION DEFINITION ---
def generate_and_display_npc(gm_request_text: str = ""):
    """
    Constructs the full prompt, sends it to Gemini, and displays the formatted NPC.
    """
    full_prompt = BASE_PROMPT_TEMPLATE + gm_request_text

    print(f"\nSending request to Gemini for: '{gm_request_text if gm_request_text else 'a general NPC'}'...")

    try:
        # Call the Gemini API
        response = model.generate_content(full_prompt)

        # Gemini's response structure can vary, content is usually in response.text
        json_output_string = response.text

        # Important: Extract only the JSON part if the model adds markdown code blocks
        # (e.g., ```json{...}```). This regex is a simple way for robustness.
        if json_output_string.strip().startswith("```json"):
            json_output_string = json_output_string.strip()[7:-3] # Remove ```json and ```

        # Parse the JSON string into a Python dictionary
        npc_data = json.loads(json_output_string)

        # --- Format and print the data in a human-readable way ---
        print("\n--- Generated NPC (Readable Format) ---")
        for key, value in npc_data.items():
            display_key = key.replace('_', ' ').capitalize()
            # Wrap long text for better readability in the command line
            wrapped_value = textwrap.fill(value, width=70, initial_indent="  ", subsequent_indent="    ")
            print(f"*{display_key}: {wrapped_value.strip()}")
        print("---------------------------------------")

    except genai.types.BlockedPromptException as e:
        print(f"Error: Prompt was blocked by safety filters. Details: {e.safety_ratings}")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON response from Gemini. Check Gemini's output for non-JSON text. Error: {e}")
        print("Gemini's raw response was:")
        # Attempt to print the problematic response text for debugging
        if 'response' in locals() and hasattr(response, 'text'):
            print(response.text)
        else:
            print("No response text available for debugging.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Optionally print full response for debugging
        # print(response.to_dict())

# --- Main execution loop for the GM Assistant ---
if __name__ == "__main__":
    print("Welcome to the RPG AI NPC Generator!")
    print("Enter your NPC request, or type 'quit' to exit.")
    print("Example: 'A grumpy male dwarf fighter in a tavern.'")
    print("Example: 'A young elven rogue looking for rare herbs.'")
    print("Example: (just press Enter for a general NPC)")

    while True:
        gm_input = input("\nNPC Request: ").strip()

        if gm_input.lower() == 'quit':
            print("Farewell, and may your tales be grand!")
            break

        generate_and_display_npc(gm_input)