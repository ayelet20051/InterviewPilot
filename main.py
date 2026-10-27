
from agent import InterviewAgent


def main():
    print("ברוכה הבאה ל-InterviewPilot!")
    print("כתבי 'סיום' כדי לסיים את התרגול.")

    try:
        agent = InterviewAgent()
        ai_message = agent.start()
        print("\nInterviewPilot:", ai_message)

        while True:
            answer = input("\nהתשובה שלך: ").strip()

            if answer.lower() == "סיום":
                print("\nהתרגול הסתיים.")
                break

            if not answer:
                print("לא הוזנה תשובה. נסי שוב.")
                continue

            try:
                ai_message = agent.answer(answer)
                print("\nInterviewPilot:", ai_message)

            except Exception as error:
                print(f"\nשגיאה בהפעלת הסוכן: {error}")
                break

    except Exception as error:
        print(f"\nשגיאה בהפעלת InterviewPilot: {error}")


if __name__ == "__main__":
    main()