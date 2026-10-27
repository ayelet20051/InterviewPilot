
from storage import InterviewStorage

storage = InterviewStorage()


def save_interview_record(
    question: str,
    answer: str,
    session_id: str | None = None,
) -> str:
    question = question.strip()
    answer = answer.strip()

    if not question or not answer:
        raise ValueError("לא ניתן לשמור שאלה או תשובה ריקות.")

    record = {
        "question": question,
        "answer": answer,
    }

    # רשומות חדשות יקושרו לתרגול שלהן.
    # רשומות ישנות ללא session_id נשארות ללא שינוי.
    if session_id:
        record["session_id"] = session_id

    interview_records = storage.load()

    if record in interview_records:
        return (
            "התשובה כבר נשמרה. "
            f"מספר הרשומות: {len(interview_records)}"
        )

    interview_records.append(record)

    try:
        storage.save(interview_records)
    except Exception as error:
        raise RuntimeError("שמירת התשובה נכשלה.") from error

    return (
        "התשובה נשמרה בהצלחה. "
        f"מספר הרשומות: {len(interview_records)}"
    )
