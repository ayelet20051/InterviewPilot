
from typing import Literal, TypedDict, NotRequired
from uuid import uuid4

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

from storage import InterviewStorage
from tools import save_interview_record

load_dotenv()


class UserProfileUpdate(BaseModel):
    job_title: str = ""
    seniority: str = ""
    job_description: str = ""
    experience: str = ""
    technologies: list[str] = Field(default_factory=list)
    training_goal: str = ""
    clarification_needed: str = ""
    ready_to_practice: bool = False


class PracticePlan(BaseModel):
    goal: str
    focus_areas: list[str] = Field(default_factory=list)
    first_question: str


class CheckQuestion(BaseModel):
    question: str


class TurnResult(BaseModel):
    intent: Literal[
        "answer", "dont_know", "request_explanation",
        "process_question", "complaint", "new_topic",
        "clarification",
    ]
    assessment: Literal[
        "understood", "partial", "incorrect",
        "unclear", "not_applicable",
    ] = "not_applicable"
    feedback: str = ""
    learned: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    next_action: Literal[
        "advance", "deepen", "explain", "check_understanding",
        "clarify", "answer_process_question",
        "change_topic", "acknowledge_complaint",
    ]
    response: str
    next_question: str = ""
    topic: str = ""


class PracticeTurnState(TypedDict):
    question: str
    answer: str
    result: NotRequired[TurnResult]
    response: NotRequired[str]


SYSTEM_PROMPT = """
את InterviewPilot, סוכנת אישית להכנה לראיונות עבודה בפיתוח תוכנה.
עני בעברית ברורה וטבעית.
שאלי לכל היותר שאלה אחת בכל תגובה.
אל תמציאי מידע על המשתמשת או על דרישות התפקיד.
התאימי את הלמידה לפרופיל, לניסיון ולתשובות הקודמות.
עני לשאלה ישירה לפני המשך התרגול.
אם המשתמשת אינה יודעת, הסבירי את הרעיון ובדקי הבנה בשאלה ממוקדת.
אם התשובה חלקית או שגויה, הסבירי מה חסר או מה שגוי.
אל תתקדמי לנושא חדש לפני בדיקת הבנה לאחר הסבר.
אל תחזרי על שאלות שכבר נשאלו, אלא אם נדרשת בדיקה חוזרת.
העדיפי דוגמה מעשית על פני הגדרה בלבד.
ב-C#: var נקבע בזמן קומפילציה; dynamic מאפשר בדיקות בזמן ריצה.
response הוא הטקסט המלא שיוצג למשתמשת.
"""


PROFILE_PROMPT = """
חלצי פרטים מפורשים בלבד ושמרי פרטים קיימים שלא נסתרו.
אל תסיקי תפקיד או רמת ניסיון מתוך בקשה כללית.
"תכוון אותי לפי התפקיד" אינה שם תפקיד ואינה מספיקה להתחלת תרגול.
אם שם התפקיד אינו ברור, בקשי הבהרה אחת.
ready_to_practice יהיה True רק אם ידוע תפקיד או תחום ראיון מסוים.
"""


class InterviewAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model_name = model
        self.model = OpenAI(timeout=45, max_retries=2)
        self.storage = InterviewStorage()
        self.records = self.storage.load()

        self.session_id = None
        self.started = False
        self.stage = "setup"
        self.profile = {}
        self.training_goal = ""
        self.focus_areas = []
        self.conversation = []

        self.current_question = ""
        self.covered_questions = []
        self.covered_topics = []
        self.learned = []
        self.gaps = []

        self.practice_graph = self._build_practice_graph()

    def _build_practice_graph(self):
        graph = StateGraph(PracticeTurnState)
        graph.add_node("decide_turn", self._graph_decide_turn)
        graph.add_node("save_answer", self._graph_save_answer)
        graph.add_node("finish_turn", self._graph_finish_turn)
        graph.add_edge(START, "decide_turn")
        graph.add_conditional_edges(
            "decide_turn",
            self._route_after_decision,
            {"save_answer": "save_answer", "finish_turn": "finish_turn"},
        )
        graph.add_edge("save_answer", "finish_turn")
        graph.add_edge("finish_turn", END)
        return graph.compile()

    def _graph_decide_turn(self, state):
        return {"result": self._decide_turn(state["answer"])}

    def _route_after_decision(self, state):
        result = state.get("result")
        return (
            "save_answer"
            if result and result.intent == "answer"
            else "finish_turn"
        )

    def _graph_save_answer(self, state):
        self._save_answer(state["question"], state["answer"])
        return {}

    def _graph_finish_turn(self, state):
        result = state.get("result")
        if result is None:
            response = "לא הצלחתי לנתח את התשובה. נסי שוב."
        else:
            self._remember_result(result)
            response = self._execute_action(result)
        self._add_assistant_message(response)
        return {"response": response}

    def start(self):
        self.session_id = str(uuid4())
        self.started = True
        self.stage = "setup"
        self.profile = {
            "job_title": "",
            "seniority": "",
            "job_description": "",
            "experience": "",
            "technologies": [],
        }
        self.training_goal = ""
        self.focus_areas = []
        self.conversation = []
        self.current_question = ""
        self.covered_questions = []
        self.covered_topics = []
        self.learned = []
        self.gaps = []

        response = (
            "שלום! אני InterviewPilot. לאיזה תפקיד את מתכוננת? "
            "אם יש לך מודעת דרושים, אפשר לצרף את הפרטים החשובים."
        )
        self._add_assistant_message(response)
        return response

    @staticmethod
    def _normalize(text):
        return " ".join(text.strip().casefold().split()).rstrip("?!., ")

    def _add_user_message(self, text):
        self.conversation.append({"role": "user", "content": text})

    def _add_assistant_message(self, text):
        self.conversation.append({"role": "assistant", "content": text})

    def _profile_summary(self):
        return (
            f"תפקיד: {self.profile.get('job_title') or 'לא נמסר'}\n"
            f"רמת ניסיון: {self.profile.get('seniority') or 'לא נמסרה'}\n"
            f"תיאור משרה: {self.profile.get('job_description') or 'לא נמסר'}\n"
            f"ניסיון: {self.profile.get('experience') or 'לא נמסר'}\n"
            f"טכנולוגיות: {', '.join(self.profile.get('technologies', [])) or 'לא נמסרו'}\n"
            f"מטרת התרגול: {self.training_goal or 'לא נמסרה'}"
        )

    def _messages(self, instruction):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": "פרופיל:\n" + self._profile_summary()},
        ]
        messages.extend(self.conversation)
        messages.append({"role": "user", "content": instruction})
        return messages

    def _parse_model_output(self, schema, messages):
        result = self.model.responses.parse(
            model=self.model_name,
            input=messages,
            text_format=schema,
        )
        if result.output_parsed is None:
            raise RuntimeError("המודל לא החזיר תוצאה תקינה.")
        return result.output_parsed

    def _extract_profile(self, message):
        return self._parse_model_output(
            UserProfileUpdate,
            [
                {"role": "system", "content": PROFILE_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"פרופיל קיים:\n{self._profile_summary()}\n"
                        f"הודעה חדשה:\n{message}\n"
                        "חלצי פרטים מפורשים בלבד."
                    ),
                },
            ],
        )

    def _update_profile(self, update):
        for key in ("job_title", "seniority", "job_description", "experience"):
            value = getattr(update, key).strip()
            if value:
                self.profile[key] = value

        combined = self.profile.get("technologies", []) + update.technologies
        unique = []
        seen = set()
        for item in combined:
            item = item.strip()
            if item and item.casefold() not in seen:
                seen.add(item.casefold())
                unique.append(item)
        self.profile["technologies"] = unique

        if update.training_goal.strip():
            self.training_goal = update.training_goal.strip()

    def _has_specific_target(self):
        title = self._normalize(self.profile.get("job_title", ""))
        vague_titles = {
            "", "לא נמסר", "פיתוח", "פיתוח תוכנה",
            "הכנה לראיון", "הכנה לראיונות עבודה",
        }
        description = self._normalize(self.profile.get("job_description", ""))
        return title not in vague_titles or len(description) >= 30

    def _create_practice_plan(self):
        return self._parse_model_output(
            PracticePlan,
            self._messages(
                "בני תוכנית תרגול לתפקיד הנתון. "
                "התחשבי בניסיון ובטכנולוגיות. "
                f"אל תחזרי על השאלות האלה: {self.covered_questions}. "
                "החזירי מטרה, תחומי מיקוד ושאלה ראשונה אחת."
            ),
        )

    def _start_practice(self):
        plan = self._create_practice_plan()
        self.training_goal = plan.goal or self.training_goal
        self.focus_areas = plan.focus_areas
        self.stage = "practice"
        question = plan.first_question.strip()
        if not question:
            question = "מהו משתנה בתכנות?"
        self._remember_question(question)
        response = (
            f"מטרת התרגול: {self.training_goal}\n\n"
            f"השאלה הראשונה: {question}"
        )
        self._add_assistant_message(response)
        return response

    def _decide_turn(self, answer):
        return self._parse_model_output(
            TurnResult,
            self._messages(
                f"""
השאלה הנוכחית: {self.current_question}
תשובת המשתמשת: {answer}
תחומי מיקוד: {self.focus_areas}
ידע שהופגן: {self.learned}
פערים שזוהו: {self.gaps}
שאלות קודמות: {self.covered_questions}

העריכי את התשובה ובחרי פעולה אחת.
אם המשתמשת אינה יודעת או מבקשת הסבר, הסבירי את הנושא.
במצב כזה next_action צריך להיות check_understanding,
ו-next_question צריכה לבדוק את הרעיון שהוסבר.
אם התשובה נכונה, אפשר להתקדם או להעמיק.
אם התשובה חלקית או שגויה, הסבירי מה חסר ובדקי הבנה.
אם המשתמשת מבקשת המלצה, בחרי את הצעד הלימודי הבא והסבירי בקצרה למה.
החזירי תגובה בעברית ושאלה אחת לכל היותר.
"""
            ),
        )

    def _create_check_question(self, explanation):
        try:
            result = self._parse_model_output(
                CheckQuestion,
                self._messages(
                    f"""
ההסבר שניתן למשתמשת:
{explanation}

צור שאלה אחת קצרה שבודקת אם היא הבינה את הרעיון בהסבר.
אל תשאל "האם הבנת?".
בקש דוגמה, הסבר במילים שלה או יישום פשוט.
אל תחזור על שאלה שכבר נשאלה.
החזר שאלה אחת בלבד.
"""
                ),
            )
            question = result.question.strip()
            if question and self._normalize(question) not in {
                self._normalize(q) for q in self.covered_questions
            }:
                return question
        except Exception:
            pass

        return "אם יש משתנה בשם גיל שמכיל את הערך 25, מה התפקיד של המשתנה בתוכנית?"

    def _save_answer(self, question, answer):
        if not question.strip() or not answer.strip():
            return
        if not self.session_id:
            raise RuntimeError("לא נוצר מזהה לתרגול.")
        save_interview_record(question, answer, session_id=self.session_id)
        self.records = self.storage.load()

    def _remember_question(self, question):
        question = question.strip()
        if not question:
            return
        normalized = self._normalize(question)
        if normalized not in {
            self._normalize(q) for q in self.covered_questions
        }:
            self.covered_questions.append(question)
        self.current_question = question

    def _remember_result(self, result):
        for item in result.learned:
            if item.strip() and item.strip() not in self.learned:
                self.learned.append(item.strip())
        for item in result.gaps:
            if item.strip() and item.strip() not in self.gaps:
                self.gaps.append(item.strip())
        topic = result.topic.strip()
        if topic and topic not in self.covered_topics:
            self.covered_topics.append(topic)

    def _remove_generic_invitation(self, response):
        unwanted = (
            "האם יש משהו נוסף",
            "יש משהו נוסף שתרצי לדעת",
            "האם יש עוד משהו",
            "רוצה לדעת עוד",
            "אם יש לך שאלות נוספות",
        )
        lines = [
            line for line in response.splitlines()
            if not any(term in line for term in unwanted)
        ]
        return "\n".join(lines).strip()

    def _execute_action(self, result):
        response = self._remove_generic_invitation(result.response.strip())
        question = result.next_question.strip()
        must_check = (
            result.intent in {"dont_know", "request_explanation"}
            or result.next_action == "check_understanding"
        )

        if must_check:
            if not question:
                question = self._create_check_question(response)
            response = response.rstrip() + "\n\n" + question
            self._remember_question(question)
            return response

        question_actions = {
            "advance", "deepen", "clarify", "change_topic",
        }
        if result.next_action in question_actions:
            if not question:
                question = self._create_check_question(response)
            response = response.rstrip() + "\n\n" + question
            self._remember_question(question)

        return response

    def answer(self, answer):
        if not self.started:
            self.start()

        answer = answer.strip()
        if not answer:
            return "לא התקבלה הודעה. אפשר להמשיך כשאת מוכנה."

        normalized = self._normalize(answer)
        if normalized in {"סיום", "די", "עצור"}:
            self.stage = "finished"
            response = "התרגול הסתיים."
            self._add_user_message(answer)
            self._add_assistant_message(response)
            return response

        if self.stage == "finished":
            return "התרגול הסתיים. הפעילי מחדש כדי להתחיל תרגול חדש."

        if self.stage == "setup":
            self._add_user_message(answer)
            try:
                update = self._extract_profile(answer)
                self._update_profile(update)
            except Exception:
                response = (
                    "לא הצלחתי לעבד את הפרטים. "
                    "לאיזה תפקיד את מתכוננת?"
                )
                self._add_assistant_message(response)
                return response

            if update.ready_to_practice and self._has_specific_target():
                try:
                    return self._start_practice()
                except Exception:
                    response = "לא הצלחתי לבנות תוכנית כרגע. נסי שוב."
                    self._add_assistant_message(response)
                    return response

            response = update.clarification_needed.strip()
            if not response or self._has_specific_target():
                response = (
                    "מה בדיוק כולל תפקיד "
                    f"'{self.profile.get('job_title') or answer}'? "
                    "אם יש מודעת דרושים, אפשר לשלוח את עיקרי הדרישות."
                )
            self._add_assistant_message(response)
            return response

        if self.stage == "practice":
            previous_question = self.current_question
            self._add_user_message(answer)
            try:
                state = self.practice_graph.invoke({
                    "question": previous_question,
                    "answer": answer,
                })
                return state["response"]
            except Exception:
                response = (
                    "נתקלתי בבעיה בעיבוד התשובה. "
                    "נסי שוב. אם התקלה חוזרת, נבדוק את הודעת השגיאה."
                )
                self._add_assistant_message(response)
                return response

        return "לא הצלחתי לזהות את שלב התרגול. הפעילי מחדש את התוכנית."
