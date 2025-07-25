from typing import List, Tuple
from rag.vectorstore import QuestionVectorStore
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# Load OpenAI key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class QuestionSelector:
    """
    Generates interview questions based on resume-extracted skills using FAISS.
    """

    def __init__(self, vector_store: QuestionVectorStore):
        self.vector_store = vector_store

    def select_relevant_questions(self, skills: List[str], top_k_per_skill: int = 2) -> List[Tuple[str, dict]]:
        """
        Retrieves top-k FAISS matches per skill and deduplicates them.

        Args:
            skills (List[str]): List of resume keywords or skills.
            top_k_per_skill (int): Number of questions to fetch per skill.

        Returns:
            List of (question, metadata) tuples.
        """
        seen = set()
        shortlisted = []

        for skill in skills:
            matches = self.vector_store.search(skill, k=top_k_per_skill)
            for question, metadata in matches:
                if question not in seen:
                    seen.add(question)
                    shortlisted.append((question, metadata))

        return shortlisted[:10]  # Limit to 10 questions max


def generate_conversational_prompt(base_question: str, prev_answer: str = "") -> str:
    """
    Builds a prompt to turn a base question into a conversational or follow-up version.

    Args:
        base_question (str): The original static technical question.
        prev_answer (str): Optional candidate answer to generate follow-up.

    Returns:
        str: Prompt string for the LLM.
    """
    if prev_answer:
        return (
            f"You are an AI interviewer. The candidate answered: '{prev_answer}'. "
            f"Ask a logical follow-up question based on this answer."
        )
    else:
        return (
            f"Rephrase the following technical interview question into a more conversational, friendly tone:\n"
            f"'{base_question}'"
        )

# def generate_conversational_question(base_question: str, prev_answer: str = "") -> str:
#     """
#     Uses OpenAI's chat model to convert a question into a conversational or follow-up style.

#     Args:
#         base_question (str): The original technical question.
#         prev_answer (str): Optional previous candidate answer.

#     Returns:
#         str: Conversational version of the question.
#     """
#     prompt = generate_conversational_prompt(base_question, prev_answer)
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.5,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print("OpenAI API error:", e)
#         return base_question

def generate_conversational_question(base_question: str, user_answer: str = "") -> str:
    """
    Uses OpenAI's chat model to convert a base technical question into:
    - A friendly style if no answer is given
    - A follow-up question if a candidate answer is provided
    """
    if not user_answer:
        prompt = f"Rephrase the following technical interview question into a more conversational, friendly tone:\n'{base_question}'"
        messages = [{"role": "user", "content": prompt}]
    else:
        system_msg = (
            "You are a senior technical interviewer evaluating a software engineering candidate.\n"
            f"You just asked them: \"{base_question}\"\n"
            f"The candidate answered: \"{user_answer}\"\n\n"
            "Your job is to ask a thoughtful follow-up question. Focus on:\n"
            "- Depth (ask for examples, use cases, edge cases, etc.)\n"
            "- Clarity (probe vague or generic responses)\n"
            "- Real-world relevance (tie it to industry patterns or practical tasks)\n\n"
            "You should not repeat the base question. Do not praise or critique the answer — just follow up with a new, intelligent question.\n"
            "Your response should be 1–2 sentences maximum."
        )
        user_msg = {
            "role": "user",
            "content": (
                f"The candidate answered: \"{user_answer}\" to the question \"{base_question}\". "
                "Ask a logical, thoughtful follow-up question as a senior technical interviewer."
            )
        }
        messages = [{"role": "system", "content": system_msg}, user_msg]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI API error:", e)
        return base_question if not user_answer else f"Can you elaborate more on your answer about: {base_question}?"

def is_user_ready_to_start(user_input: str) -> bool:
    """
    Uses OpenAI to determine if a user's response implies readiness to begin the interview.

    Args:
        user_input (str): The user's response to the AI's greeting.

    Returns:
        bool: True if the response signals readiness, False otherwise.
    """
    prompt = (
        f"The AI interviewer greeted the candidate and asked them to reply when ready to begin. "
        f"The candidate replied with: '{user_input}'. "
        "Does this response indicate the candidate is ready to start the interview? "
        "Just reply with 'true' or 'false'."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return "true" in response.choices[0].message.content.lower()
    except Exception as e:
        print("OpenAI API error during readiness check:", e)
        return False

def generate_feedback_from_history(chat_history) -> str:
    """
    Uses OpenAI to generate personalized feedback based on the chat history.
    """
    from openai import OpenAI
    client = OpenAI()
    print(f"Chat history for feedback:\n {chat_history}\n\n")
    transcript = "\n".join([f"Q: {q}\nA: {a}" for q, a in chat_history])
    print(f"Transcript for feedback:\n {transcript}\n\n")
    
    prompt = (
        "You are a senior technical interviewer evaluating a mock technical interview.\n\n"
        f"Transcript:\n{transcript}\n\n"
        "Please evaluate the candidate's performance based only on the actual answers.\n"
        "Do NOT assume correctness — treat vague, incorrect, or nonsensical answers as poor performance.\n"
        "Be fair but critical.\n\n"
        "1. Strengths: What did the candidate do well?\n"
        "2. Weaknesses: Where did they struggle or provide incorrect/vague answers?\n"
        "3. Communication: How clearly and confidently did they explain their answers?\n"
        "4. Score: Give a score out of 5 for overall technical performance. Use decimal points if needed.\n\n"
        "Respond in this JSON format:\n"
        "{\n"
        '  "feedback": "<summary>",\n'
        '  "score": <number between 0 and 5>\n'
        "}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        output = response.choices[0].message.content.strip()
        return json.loads(output)
    except Exception as e:
        print("OpenAI feedback generation failed:", e)
        return "Feedback could not be generated due to an internal error."

# def generate_feedback_via_llm(chat_history, skills):
#     """
#     Uses LLM to generate a summary feedback based on the chat and skills.
#     """
#     history_text = "\n".join(
#         [f"Q: {q}\nA: {a}" for q, a in chat_history]
#     )
#     prompt = f"""
#     You are an AI interviewer reviewing a candidate's technical interview. The transcript contains both the AI's questions and the candidate's responses.

#     Your task is to give an honest, critical evaluation of the candidate's knowledge and communication. If the answers are vague, irrelevant, or incorrect, say so. If the candidate uses unclear abbreviations or meaningless inputs like 'abc', 'cde', or 'idk', treat them as weak responses.

#     Skills being assessed: {", ".join(skills)}

#     Transcript:
#     {history_text}

#     Write 3–5 sentences summarizing their performance. Start with strengths (if any), but do not hesitate to highlight lack of depth, confusion, or poor explanation.

#     Feedback:
#     """


#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.6,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print("LLM feedback generation error:", e)
#         return "Feedback not available at the moment."

