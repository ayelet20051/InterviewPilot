# InterviewPilot

## תיאור הפרויקט

InterviewPilot הוא סוכן AI המסייע למועמדים להתכונן לראיונות עבודה בתחום התוכנה והפיתוח באמצעות תרגול אישי ואינטראקטיבי.

## הבעיה שהפרויקט פותר

מועמדים בתחילת דרכם המקצועית מתקשים לזהות אילו נושאים עליהם ללמוד, כיצד לענות על שאלות מקצועיות וכיצד לזהות פערי ידע.

## הפתרון

InterviewPilot מנהל תהליך תרגול מותאם אישית. הסוכן אוסף מידע על התפקיד, על הידע של המשתמש ועל מטרת התרגול, מציג שאלות מקצועיות ומחליט כיצד להמשיך בהתאם לתשובות המתקבלות.

במהלך התרגול הסוכן משתמש במודל שפה של OpenAI כדי לנתח את המידע ולבחור את הצעד הבא. הוא נעזר בכלי לשמירת שאלות ותשובות בהיסטוריית התרגול, ומתייחס למידע שנאסף כדי להתאים את המשך התהליך.

## אופן פעולת הסוכן

1. איסוף מידע על התפקיד ועל מטרת התרגול.
2. ניתוח המידע באמצעות מודל שפה של OpenAI.
3. בחירת הצעד הבא בהתאם למטרה ולתשובות המשתמש.
4. שימוש בכלי לשמירת שאלות ותשובות בהיסטוריית התרגול.
5. התאמת המשך התרגול למידע שנאסף.
6. סיום התהליך כאשר המשתמש מסיים את התרגול או כאשר נדרש לעצור.

## טכנולוגיות

- Python
- OpenAI API
- FastAPI
- React
- Vite
- JSON לשמירת היסטוריית התרגול

## התקנה והפעלה

### דרישות מקדימות

- Python 3.11
- Node.js ו־npm
- מפתח API של OpenAI

### 1. התקנת תלויות ה־Backend

מתיקיית הפרויקט הראשית, הפעילו את הסביבה הווירטואלית:

```powershell
.\venv\Scripts\Activate.ps1
```

לאחר מכן התקינו את התלויות:

```powershell
python -m pip install -r requirements.txt
```

### 2. הגדרת מפתח API

צרו קובץ בשם `.env` בתיקיית הפרויקט הראשית והגדירו בו את מפתח ה־API של OpenAI, בהתאם לשם משתנה הסביבה שבו משתמש הקוד.

אין לפרסם את המפתח או להעלות את קובץ `.env` ל־GitHub.

### 3. הפעלת השרת

מתיקיית הפרויקט הראשית, הפעילו:

```powershell
python -m uvicorn server:app --host 127.0.0.1 --port 8765
```

בדיקת זמינות השרת:

http://127.0.0.1:8765/api/health

תיעוד ה־API:

http://127.0.0.1:8765/docs

### 4. התקנת והפעלת ה־Frontend

פתחו טרמינל נוסף ב־PyCharm והיכנסו לתיקיית `frontend`:

```powershell
cd frontend
```

התקינו את התלויות:

```powershell
npm install
```

הפעילו את סביבת הפיתוח:

```powershell
npm run dev
```

פתחו בדפדפן את כתובת ה־Local שמוצגת בטרמינל של Vite.

## Screenshots

### צילום מסך 1

![InterviewPilot - Screenshot 1](https://github.com/user-attachments/assets/4274d003-2247-45a2-ab0d-4da736f0175b)

### צילום מסך 2

![InterviewPilot - Screenshot 2](https://github.com/user-attachments/assets/7b6c4bad-5d56-4b32-adb6-30c17b102a33)

### צילום מסך 3

![InterviewPilot - Screenshot 3](https://github.com/user-attachments/assets/cb77818f-0b74-495f-9086-43737613df77)

### צילום מסך 4

![InterviewPilot - Screenshot 4](https://github.com/user-attachments/assets/39b87cd1-6485-4af4-9c70-e82615283ae3)

### צילום מסך 5

![InterviewPilot - Screenshot 5](https://github.com/user-attachments/assets/956ec5f9-0d2c-4807-becf-4dd48c8e3157)

### צילום מסך 6

![InterviewPilot - Screenshot 6](https://github.com/user-attachments/assets/b4f30660-b94d-4609-a421-ac78bebcb529)

### צילום מסך 7

![InterviewPilot - Screenshot 7](https://github.com/user-attachments/assets/4ce7e598-4023-4519-85e0-d339bc756935)

## אבטחה

אין להעלות ל־GitHub מפתחות API, קובצי `.env` או מידע אישי מתוך היסטוריית התרגול.
