@echo off
echo Building ClipYTwo executable...
echo.

REM Check if virtual environment exists and activate it
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found!
    echo It is recommended to create one with: python -m venv venv
    echo Continuing without virtual environment...
    echo.
)

REM Install dependencies if needed
echo Installing/updating dependencies...
pip install -r requirements.txt
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM Build executable using pyinstaller
echo Building executable with PyInstaller...
pyinstaller --clean ClipYTwo.spec

echo.
if exist dist\ClipYTwo.exe (
    echo SUCCESS! Build complete!
    echo Executable location: dist\ClipYTwo.exe
) else (
    echo ERROR: Build failed! Check the output above for errors.
)
echo.
pause

