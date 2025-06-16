@echo off
echo 🔄 Usuwanie starych buildów...
rmdir /s /q build
rmdir /s /q dist
del /q spedycja_gui.spec

echo 🚀 Budowanie nowego .exe...
pyinstaller --onefile --noconsole spedycja_gui.py

echo ✅ Gotowe! Nowy plik znajduje się w folderze "dist"
pause
