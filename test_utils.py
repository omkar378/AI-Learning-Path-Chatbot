print("Starting test")

from google import genai
print("Gemini import OK")

from googleapiclient.discovery import build
print("YouTube import OK")

from prompt import user_goal_prompt
print("Prompt import OK")

from utils import generate_learning_path
print("Utils import OK")