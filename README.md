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

## Screenshots

<img width="1405" height="1021" alt="צילום מסך 2026-10-27 115053" src="https://github.com/user-attachments/assets/4274d003-2247-45a2-ab0d-4da736f0175b" />
<img width="1402" height="1006" alt="צילום מסך 2026-10-27 115038" src="https://github.com/user-attachments/assets/7b6c4bad-5d56-4b32-adb6-30c17b102a33" />
<img width="1408" height="1028" alt="צילום מסך 2026-10-27 115011" src="https://github.com/user-attachments/assets/cb77818f-0b74-495f-9086-43737613df77" />
<img width="945" height="578" alt="צילום מסך 2026-10-27 115140" src="https://github.com/user-attachments/assets/39b87cd1-6485-4af4-9c70-e82615283ae3" />
<img width="1408" height="1023" alt="צילום מסך 2026-10-27 115124" src="https://github.com/user-attachments/assets/956ec5f9-0d2c-4807-becf-4dd48c8e3157" />
<img width="1403" height="1025" alt="צילום מסך 2026-10-27 114957" src="https://github.com/user-attachments/assets/b4f30660-b94d-4609-a421-ac78bebcb529" />
<img width="1406" height="1016" alt="צילום מסך 2026-10-27 114942" src="https://github.com/user-attachments/assets/4ce7e598-4023-4519-85e0-d339bc756935" />



