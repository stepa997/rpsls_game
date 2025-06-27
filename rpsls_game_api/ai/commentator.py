# ai/commentator.py
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


def generate_comment(player_move: str, computer_move: str, result: str) -> str:
    prompt = f"""
        You are a witty and concise game commentator.
        This was a Rock-Paper-Scissors-Lizard-Spock match.
        Player picked: {player_move}, Computer picked: {computer_move}. Result: {result}.
        Write a short and punchy one-line reaction (max 10 words):
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=0.8,
        max_tokens=30,
    )
    return response.choices[0].message.content.strip()
