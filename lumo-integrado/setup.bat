@echo off
echo === Lumo Setup ===
cd /d "%~dp0backend"
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo.
echo Pronto! Para rodar:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn main:app --reload
echo    Depois abra frontend\index.html no navegador
pause
