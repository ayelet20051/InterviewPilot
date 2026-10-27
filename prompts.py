



interview_records = []


def record_interview_progress(question, answer):
    """Save an interview question and the candidate's answer."""

    record = {
        "question": question,
        "answer": answer,
    }

    interview_records.append(record)

    return {
        "recorded": True,
        "total_answers": len(interview_records),
        "message": "התשובה נשמרה בהצלחה."
    }


TOOLS = [
    {
        "type": "function",
        "name": "record_interview_progress",
        "description": (
            "שומר את שאלת הראיון ואת תשובת המועמדת. "
            "יש להפעיל את הכלי לאחר קבלת תשובה."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "שאלת הראיון האחרונה"
                },
                "answer": {
                    "type": "string",
                    "description": "תשובת המועמדת"
                }
            },
            "required": ["question", "answer"],
            "additionalProperties": False
        },
        "strict": True
    }
]
