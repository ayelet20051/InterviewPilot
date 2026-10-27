
from uuid import uuid4

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

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
    ready_to_practice: bool = False


class PracticePlan(BaseModel):
    goal: str
    focus_areas: list[str] = Field(default_factory=list)
    first_question: str


class TurnResult(BaseModel):
    intent: str
    assessment: str = "not_applicable"
    feedback: str = ""
    learned: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    next_action: str
    response: str
    next_question: str = ""
    topic: str = ""


SYSTEM_PROMPT = """
את InterviewPilot, סוכנת AI אישית להכנה לראיונות עבודה בפיתוח תוכנה.

המטרה שלך היא לעזור למשתמשת להתכונן לראיון באופן אישי,
דינמי ומותאם לידע שלה.

קבלי החלטות לפי ההקשר המלא של השיחה, ולא לפי התאמה
לרשימה קבועה של משפטים.

בכל תור:
- הביני מה המשתמשת רוצה להשיג בהודעה הנוכחית.
- החליטי מה הפעולה המתאימה ביותר להמשך.
- התאימי את התוכן לרמת הידע, לתפקיד ולמטרת התרגול.
- אל תחזרי על שאלה שכבר נשאלה ללא צורך.
- עני על שאלה ישירה לפני שאת ממשיכה בתרגול.
- אם המשתמשת מבקשת לשנות נושא, החליפי נושא.
- אם היא מבקשת לחזור לנושא קודם, השתמשי בהיסטוריית השיחה.
- אם היא מבקשת הסבר, הסבירי בצורה ברורה ומעשית.
- אם היא אינה יודעת תשובה, עזרי לה ללמוד במקום להעניש אותה.
- אם התשובה שגויה או חלקית, הסבירי מה חסר והתאימי את הצעד הבא.
- אם היא מבקשת לסיים, סיימי בצורה מסודרת.
- אל תמציאי פרטים על המשתמשת או על דרישות המשרה.
- עני בעברית טבעית וברורה.
- הציגי לכל היותר שאלה אחת בכל תגובה.

השתמשי במידע שנאסף ובתשובות קודמות כדי להחליט
מה כדאי לעשות עכשיו.

response הוא התגובה המלאה למשתמשת.
next_question היא השאלה הלימודית הבאה, אם נדרשת.
אם אין צורך בשאלה נוספת, השאירי את next_question ריק.

הבחיני בין תשובה לשאלת ידע לבין בקשה לשנות את מהלך השיחה.
בקשת שינוי נושא אינה תשובה לשאלה הלימודית הקודמת.

ב-C#:
var נקבע בזמן קומפילציה.
dynamic מאפשר בדיקות טיפוסים בזמן ריצה.
"""


PROFILE_PROMPT = """
חלצי מהודעת המשתמשת פרטים מפורשים על ההכנה לראיון.

שמרי פרטים קיימים שלא נסתרו.
אל תמציאי תפקיד, ניסיון או טכנולוגיות.

זהי, כשנמסרו:
- שם התפקיד או תחום התפקיד.
- רמת הניסיון.
- תיאור המשרה.
- ניסיון קודם.
- טכנולוגיות.
- מטרת התרגול.

הבחיני בין מידע שחסר לבין מידע שהמשתמשת אמרה שאינו ידוע.
אם יש מספיק מידע להתחלת תרגול ממוקד, ready_to_practice יהיה True.
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
            "שלום! אני InterviewPilot. "
            "לאיזה תפקיד את מתכוננת? "
            "אפשר לציין גם רמת ניסיון וטכנולוגיות רלוונטיות."
        )

        self._add_assistant_message(response)
        return response

    @staticmethod
    def _normalize(text):
        return " ".join(
            text.strip().casefold().split()
        ).rstrip("?!., ")

    def _add_user_message(self, text):
        self.conversation.append({
            "role": "user",
            "content": text,
        })

    def _add_assistant_message(self, text):
        self.conversation.append({
            "role": "assistant",
            "content": text,
        })

    def _profile_summary(self):
        return (
            f"תפקיד: {self.profile.get('job_title') or 'לא נמסר'}\n"
            f"רמת ניסיון: {self.profile.get('seniority') or 'לא נמסרה'}\n"
            f"תיאור משרה: "
            f"{self.profile.get('job_description') or 'לא נמסר'}\n"
            f"ניסיון: {self.profile.get('experience') or 'לא נמסר'}\n"
            f"טכנולוגיות: "
            f"{', '.join(self.profile.get('technologies', [])) or 'לא נמסרו'}\n"
            f"מטרת התרגול: {self.training_goal or 'לא נמסרה'}"
        )

    def _messages(self, instruction):
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "system",
                "content": (
                    "זהו מצב התרגול הנוכחי:\n"
                    f"שלב: {self.stage}\n"
                    f"פרופיל:\n{self._profile_summary()}\n"
                    f"מטרת התרגול: {self.training_goal}\n"
                    f"תחומי מיקוד: {self.focus_areas}\n"
                    f"שאלה נוכחית: {self.current_question}\n"
                    f"שאלות שכבר נשאלו: {self.covered_questions}\n"
                    f"נושאים שכבר נלמדו: {self.covered_topics}\n"
                    f"ידע שהופגן: {self.learned}\n"
                    f"פערים שזוהו: {self.gaps}"
                ),
            },
        ]

        messages.extend(self.conversation)

        messages.append({
            "role": "user",
            "content": instruction,
        })

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
                {
                    "role": "system",
                    "content": PROFILE_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        f"פרופיל קיים:\n{self._profile_summary()}\n"
                        f"הודעה חדשה:\n{message}\n"
                        "חלצי את הפרטים מההודעה ועדכני את הפרופיל."
                    ),
                },
            ],
        )

    def _update_profile(self, update):
        for key in (
            "job_title",
            "seniority",
            "job_description",
            "experience",
        ):
            value = getattr(update, key).strip()

            if value:
                self.profile[key] = value

        existing = self.profile.get("technologies", [])
        combined = existing + update.technologies

        unique = []
        seen = set()

        for item in combined:
            item = item.strip()
            normalized = item.casefold()

            if item and normalized not in seen:
                seen.add(normalized)
                unique.append(item)

        self.profile["technologies"] = unique

        if update.training_goal.strip():
            self.training_goal = update.training_goal.strip()

    def _has_specific_target(self):
        title = self._normalize(
            self.profile.get("job_title", "")
        )

        vague_titles = {
            "",
            "לא נמסר",
            "פיתוח",
            "פיתוח תוכנה",
            "הכנה לראיון",
            "הכנה לראיונות עבודה",
        }

        description = self._normalize(
            self.profile.get("job_description", "")
        )

        technologies = self.profile.get("technologies", [])

        goal = self._normalize(self.training_goal)

        frontend_terms = (
            "צד לקוח",
            "frontend",
            "front-end",
            "פרונט",
        )

        has_frontend_focus = any(
            term in goal or term in description
            for term in frontend_terms
        )

        return (
            title not in vague_titles
            or len(description) >= 30
            or bool(technologies)
            or has_frontend_focus
        )

    def _create_practice_plan(self):
        return self._parse_model_output(
            PracticePlan,
            self._messages(
                "בני תוכנית תרגול אישית על סמך פרופיל המשתמשת "
                "והיסטוריית השיחה. בחרי תחומי מיקוד מתאימים "
                "ושאלה ראשונה אחת. אל תחזרי על שאלה שכבר נשאלה. "
                "אל תבקשי שוב פרטים שכבר נמסרו."
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
ההודעה האחרונה של המשתמשת:
{answer}

החליטי מה נכון לעשות עכשיו לפי ההקשר המלא.

החזירי:
- intent: סוג הכוונה של המשתמשת.
- assessment: הערכת תשובה, אם ניתנה תשובת ידע.
- feedback: משוב לימודי, אם מתאים.
- learned: ידע שהמשתמשת הפגינה.
- gaps: פערי ידע שהתגלו.
- next_action: הפעולה הבאה.
- response: התגובה המלאה למשתמשת.
- next_question: שאלה הבאה, רק אם נדרשת.
- topic: הנושא הרלוונטי.

בחרי את הפעולה בעצמך לפי ההקשר.
אל תתייחסי לכל הודעה כאילו היא תשובה לשאלת הידע.
אם המשתמשת מבקשת שינוי נושא, החליפי נושא.
אם היא מבקשת לחזור לנושא קודם, השתמשי בהיסטוריית השיחה.
אם היא מבקשת סיום, סכמי את ההתקדמות וסיימי.
אם היא מבקשת הסבר, הסבירי לפני שתמשיכי.
אם היא עונה על שאלה, העריכי את התשובה והתאימי את ההמשך.

next_question צריכה להתאים להחלטה שלך.
אל תשתמשי בשאלת בדיקת הבנה כללית כשאין לכך הצדקה.
אל תחזרי על שאלה שכבר נשאלה אלא אם יש לכך סיבה.
"""
            ),
        )

    def _save_answer(self, question, answer):
        if not question.strip() or not answer.strip():
            return

        if not self.session_id:
            raise RuntimeError("לא נוצר מזהה לתרגול.")

        save_interview_record(
            question,
            answer,
            session_id=self.session_id,
        )

        self.records = self.storage.load()

    def _remember_question(self, question):
        question = question.strip()

        if not question:
            return

        normalized = self._normalize(question)
        existing = {
            self._normalize(item)
            for item in self.covered_questions
        }

        if normalized not in existing:
            self.covered_questions.append(question)

        self.current_question = question

    def _remember_result(self, result):
        for item in result.learned:
            item = item.strip()

            if item and item not in self.learned:
                self.learned.append(item)

        for item in result.gaps:
            item = item.strip()

            if item and item not in self.gaps:
                self.gaps.append(item)

        topic = result.topic.strip()

        if topic and topic not in self.covered_topics:
            self.covered_topics.append(topic)

    def _execute_action(self, result, previous_question, answer):
        action = result.next_action.strip().casefold()
        intent = result.intent.strip().casefold()

        response = result.response.strip()
        next_question = result.next_question.strip()

        if intent == "finish" or action == "finish":
            self.stage = "finished"
            return response or self._create_summary()

        # שומרים תשובת ידע, אך לא שומרים בקשת שינוי נושא
        # כאילו הייתה תשובה לשאלת הראיון.
        if intent == "answer" and previous_question:
            self._save_answer(previous_question, answer)

        self._remember_result(result)

        if action in {"change_topic", "advance", "deepen", "clarify"}:
            if next_question:
                self._remember_question(next_question)

                if next_question.casefold() not in response.casefold():
                    response = (
                        response.rstrip()
                        + "\n\n"
                        + next_question
                    )

        elif action in {"explain", "check_understanding"}:
            if next_question:
                self._remember_question(next_question)

                if next_question.casefold() not in response.casefold():
                    response = (
                        response.rstrip()
                        + "\n\n"
                        + next_question
                    )

        # אם המודל לא בחר שאלה חדשה, לא ממציאים אחת
        # ולא מחזירים את המשתמשת אוטומטית לנושא הקודם.
        return response or "נמשיך בהתאם למה שתרצי לתרגל."

    def _create_summary(self):
        try:
            result = self.model.responses.create(
                model=self.model_name,
                input=self._messages(
                    "סכמי את התרגול בעברית. התייחסי לנושאים שנלמדו, "
                    "לידע שהופגן ולפערים שזוהו. הציעי צעד המשך אחד. "
                    "אל תמציאי הישגים שלא הופיעו בשיחה."
                ),
            )

            text = (result.output_text or "").strip()

            if text:
                return "סיכום התרגול\n\n" + text

        except Exception:
            pass

        learned = ", ".join(self.learned) or "עדיין לא תועד ידע מסוים"
        gaps = ", ".join(self.gaps) or "עדיין לא זוהו פערים מסוימים"

        return (
            "סיכום התרגול\n\n"
            f"נושאים וידע שהופגנו: {learned}\n"
            f"נושאים שכדאי לחזק: {gaps}"
        )

    def answer(self, answer):
        if not self.started:
            self.start()

        answer = answer.strip()

        if not answer:
            return "לא התקבלה הודעה. אפשר להמשיך כשאת מוכנה."

        normalized = self._normalize(answer)

        if normalized in {"סיום", "די", "עצור", "סיימתי"}:
            self._add_user_message(answer)
            response = self._create_summary()
            self.stage = "finished"
            self._add_assistant_message(response)
            return response

        if self.stage == "finished":
            return "התרגול הסתיים. הפעילי מחדש כדי להתחיל תרגול חדש."

        self._add_user_message(answer)

        if self.stage == "setup":
            try:
                update = self._extract_profile(answer)
                self._update_profile(update)

            except Exception:
                response = (
                    "לא הצלחתי לעבד את הפרטים כרגע. "
                    "אפשר לנסח בקצרה לאיזה תפקיד את מתכוננת?"
                )
                self._add_assistant_message(response)
                return response

            if update.ready_to_practice or self._has_specific_target():
                try:
                    return self._start_practice()

                except Exception:
                    response = (
                        "לא הצלחתי לבנות תוכנית תרגול כרגע. "
                        "נסי שוב."
                    )
                    self._add_assistant_message(response)
                    return response

            # ה-AI מחליט איזה פרט חיוני חסר, במקום
            # לשאול תמיד את אותה שאלת הבהרה.
            try:
                result = self._parse_model_output(
                    TurnResult,
                    self._messages(
                        "אנחנו בשלב איסוף פרטי התפקיד. "
                        "על סמך הפרופיל והשיחה, החליטי אם יש מספיק "
                        "מידע להתחלת תרגול ממוקד. אם כן, החזירי "
                        "תגובה שמאשרת את הכיוון ומסמנת שהשלב הבא "
                        "הוא התחלת התרגול. אם חסר מידע חיוני, "
                        "שאלי שאלה ממוקדת אחת בלבד. "
                        "אל תחזרי על שאלה שכבר נענתה."
                    ),
                )

                if self._has_specific_target():
                    return self._start_practice()

                response = result.response.strip()

                if not response:
                    response = (
                        "באיזה תחום בפיתוח תרצי להתמקד, "
                        "ואילו טכנולוגיות רלוונטיות לתפקיד?"
                    )

            except Exception:
                response = (
                    "באיזה תחום בפיתוח תרצי להתמקד, "
                    "ואילו טכנולוגיות רלוונטיות לתפקיד?"
                )

            self._add_assistant_message(response)
            return response

        if self.stage == "practice":
            previous_question = self.current_question

            try:
                result = self._decide_turn(answer)

                response = self._execute_action(
                    result,
                    previous_question,
                    answer,
                )

                self._add_assistant_message(response)
                return response

            except Exception:
                response = (
                    "נתקלתי בבעיה בעיבוד התשובה. "
                    "נסי שוב. אם התקלה חוזרת, נבדוק את הודעת השגיאה."
                )
                self._add_assistant_message(response)
                return response

        return "לא הצלחתי לזהות את שלב התרגול. הפעילי מחדש את התוכנית."
