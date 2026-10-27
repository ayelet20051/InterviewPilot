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

צרו קובץ `.env` בתיקיית הפרויקט הראשית והגדירו בו את מפתח ה־API של OpenAI, תחת שם המשתנה שבו משתמש הקוד.

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
