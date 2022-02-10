python -m venv env
call .\env\Scripts\activate.bat
python -m pip install --upgrade pip
FOR /F %k in (requirements.txt) DO ( if NOT # == %k ( pip install %k ) )
python main.py
