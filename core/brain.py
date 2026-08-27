import os
import json
import requests
from config import GEMINI_API_KEY, GEMINI_MODEL, USER_NAME, ASSISTANT_NAME
from core.tools import JARVIS_TOOL_FUNCTIONS, JARVIS_TOOL_DECLARATIONS

SYSTEM_INSTRUCTION = f"""You are {ASSISTANT_NAME}, an advanced, intelligent, and courteous AI assistant inspired by Tony Stark's JARVIS.
You assist {USER_NAME} with controlling their computer, executing tasks, retrieving information, and managing their system.
Guidelines:
1. Tone: Professional, courteous, efficient, slightly witty, and cinematic (e.g., "Right away, sir", "All systems nominal, sir", "Task completed").
2. Tool Usage: Always use the appropriate tool when {USER_NAME} asks to open/close apps, check hardware health, adjust volume, take screenshots, play songs on YouTube, search Google, or lock the computer.
3. Brevity: Keep verbal responses concise and natural (1-3 sentences), since your response will be spoken aloud via text-to-speech.
"""

class JarvisBrain:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL
        self.history = []

    def set_api_key(self, key: str):
        self.api_key = key.strip()

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE")

    def _call_gemini_api(self, contents: list, tools: list = None) -> dict:
        """Direct REST call to Google Gemini generateContent endpoint with tools support."""
        if not self.is_configured():
            raise ValueError("Gemini API key is not configured. Please add your key to .env or in the HUD.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 800
            }
        }

        if tools:
            # Convert declarations to Gemini API format
            gemini_tools = [{"function_declarations": tools}]
            payload["tools"] = gemini_tools

        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
        if response.status_code != 200:
            error_data = response.json().get("error", {})
            error_msg = error_data.get("message", response.text)
            raise RuntimeError(f"Cloud AI Error ({response.status_code}): {error_msg}")

        return response.json()

    def process_command(self, user_text: str, on_action_callback=None) -> str:
        """
        Sends user command to the Cloud Brain, executes any tool calls locally,
        and returns the final verbal response.
        """
        if not self.is_configured():
            return "Please provide your Gemini API key in the configuration file or HUD settings to activate my cloud brain, sir."

        # Add user message to contents
        contents = list(self.history)
        contents.append({
            "role": "user",
            "parts": [{"text": user_text}]
        })

        try:
            # Step 1: Initial call to Gemini with tools
            response_json = self._call_gemini_api(contents, tools=JARVIS_TOOL_DECLARATIONS)
            candidates = response_json.get("candidates", [])
            if not candidates:
                return "I received an empty transmission from the cloud brain, sir."

            first_candidate = candidates[0]
            content = first_candidate.get("content", {})
            parts = content.get("parts", [])

            # Check if Gemini decided to call a function
            function_calls = [p.get("functionCall") for p in parts if "functionCall" in p]

            if function_calls:
                # Add model's tool call turn to contents
                contents.append(content)
                
                tool_response_parts = []
                for fc in function_calls:
                    fn_name = fc.get("name")
                    fn_args = fc.get("args", {})
                    
                    if on_action_callback:
                        try:
                            on_action_callback(f"Executing: {fn_name}({json.dumps(fn_args)})")
                        except Exception:
                            pass

                    # Execute the local tool
                    if fn_name in JARVIS_TOOL_FUNCTIONS:
                        func = JARVIS_TOOL_FUNCTIONS[fn_name]
                        try:
                            result = func(**fn_args)
                        except Exception as e:
                            result = f"Error executing tool: {str(e)}"
                    else:
                        result = f"Unknown tool: {fn_name}"

                    tool_response_parts.append({
                        "functionResponse": {
                            "name": fn_name,
                            "response": {"result": result}
                        }
                    })

                # Step 2: Send tool output back to model for final spoken response
                contents.append({
                    "role": "user",
                    "parts": tool_response_parts
                })

                final_response_json = self._call_gemini_api(contents)
                final_parts = final_response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                final_text = "".join([p.get("text", "") for p in final_parts]).strip()
                
                # Keep short history for context (up to last 10 exchanges)
                self.history = contents[-10:]
                return final_text if final_text else "Task executed successfully, sir."

            else:
                # Normal conversational response
                text_response = "".join([p.get("text", "") for p in parts]).strip()
                contents.append(content)
                self.history = contents[-10:]
                return text_response or "Understood, sir."

        except Exception as e:
            return f"Encountered an issue processing your request: {str(e)}"

# Global Brain Instance
jarvis_brain = JarvisBrain()
