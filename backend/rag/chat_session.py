from typing import List, Tuple
from rag.question_gen import generate_conversational_question, is_user_ready_to_start, generate_feedback_from_history
from rag.question_gen import QuestionSelector
from rag.vectorstore import QuestionVectorStore


class ChatSession:
    """
    Manages a single interview session state.
    """

    def __init__(self, skills: List[str], vector_store: QuestionVectorStore, job_title: str = ""):
        selector = QuestionSelector(vector_store)
        self.job_title = job_title
        self.questions = selector.select_relevant_questions(skills, job_title=job_title)
        self.current_index = 0
        self.followup_done = False
        self.chat_history: List[Tuple[str, str]] = []
        self.last_question = ""
        self.last_answer = ""
        self.total_turns = 0  # base + follow-up questions together
        self.MAX_TURNS = 6  # adjust this as needed

    def get_next_prompt(self, user_input: str = "") -> str | list[str] | dict:
        """
        Interview loop: greeting → readiness → question + follow-up (capped at MAX_TURNS).
        """

        if not self.questions:
            return "No questions available."

        # Early exit if we're done
        if self.total_turns >= self.MAX_TURNS:
            return {
                "message": "Interview complete.",
                "summary": self.generate_summary()
            }
        # Greeting
        if self.current_index == 0 and not self.followup_done and not self.chat_history and not user_input:
            return (
                "Hi! I’m your AI Interviewer. I’ll ask you a few technical questions based on your resume. "
                "Let me know once you’re ready."
            )

        # Waiting for user to say "ready"
        if self.current_index == 0 and not self.followup_done and not self.chat_history and user_input:
            if is_user_ready_to_start(user_input):
                base_q, _ = self.questions[0]
                self.last_question = base_q
                self.followup_done = True
                self.total_turns += 1
                return ["Great! Let’s get started.", generate_conversational_question(base_question=base_q, job_title=self.job_title)]
            else:
                return "No worries — just let me know when you’re ready to begin."

        # Store last answer
        if self.last_question and user_input:
            self.chat_history.append((self.last_question, user_input))
            self.last_answer = user_input

        # Follow-up — check before sending
        if self.followup_done:
            if self.total_turns >= self.MAX_TURNS:
                return {
                    "message": "Interview complete.",
                    "summary": self.generate_summary()
                }
            followup = generate_conversational_question(self.last_question, self.last_answer, self.job_title)
            self.followup_done = False
            self.current_index += 1
            self.total_turns += 1
            return followup

        # Base question — check before sending
        if self.current_index < len(self.questions):
            if self.total_turns + 1 > self.MAX_TURNS:  # +1 for follow-up
                return {
                    "message": "Interview complete.",
                    "summary": self.generate_summary()
                }
            base_q, _ = self.questions[self.current_index]
            self.last_question = base_q
            self.followup_done = True
            self.total_turns += 1
            return generate_conversational_question(base_q, job_title=self.job_title)

        # Fallback
        return {
            "message": "Interview complete.",
            "summary": self.generate_summary()
        }

    def generate_summary(self) -> dict:
        """
        Generates a basic summary report of the interview.
        """
        asked_skills = list({tag for _, meta in self.questions for tag in meta.get("tags", [])})
        total_turns = self.total_turns
        base_qs = total_turns // 2
        followups = total_turns - base_qs

        # feedback = (
        #     "You demonstrated good understanding of most topics. "
        #     "Consider expanding more on advanced topics."
        # )
        # feedback = generate_feedback_via_llm(self.chat_history, asked_skills)
        feedback_obj  = generate_feedback_from_history(self.chat_history)

        return {
            "total_questions": base_qs,
            "followups": followups,
            "skills": asked_skills,
            "feedback": feedback_obj.get("feedback", ""),
            "score": feedback_obj.get("score", 0),
            "category_scores": feedback_obj.get("categories", {})
        }

    def is_finished(self) -> bool:
        return self.current_index >= len(self.questions)
    
    