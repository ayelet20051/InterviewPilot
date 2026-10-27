
import json
from pathlib import Path


class InterviewStorage:
    """אחראי לשמירת נתוני התרגול בקובץ."""

    def __init__(self, file_path="interview_history.json"):
        self.file_path = Path(__file__).resolve().parent / file_path
        print("נתיב קובץ השמירה:", self.file_path)

    def save(self, records):
        """שומר את רשומות התרגול לקובץ JSON."""

        try:
            with self.file_path.open("w", encoding="utf-8") as file:
                json.dump(
                    records,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            print(
                f"השמירה הצליחה. מספר הרשומות: {len(records)}"
            )

        except (OSError, TypeError, ValueError) as error:
            raise RuntimeError(
                f"לא ניתן לשמור את היסטוריית התרגול: {error}"
            ) from error

    def load(self):
        """טוען רשומות תרגול מקובץ JSON."""

        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                records = json.load(file)

        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"לא ניתן לטעון את היסטוריית התרגול: {error}"
            ) from error

        if not isinstance(records, list):
            raise ValueError(
                "קובץ היסטוריית התרגול חייב להכיל רשימה."
            )

        return records
