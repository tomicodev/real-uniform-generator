@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Real Uniform Generator - Build and Blender 5.2 Test
echo ============================================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\build_and_test.ps1" %*
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo SUCCESS
    echo Install ZIP: %~dp0dist\real_uniform_generator-v0.2.0.zip
) else (
    echo FAILED - Exit code: %EXIT_CODE%
    echo Copy the complete error output when reporting the failure.
)
echo.
pause
exit /b %EXIT_CODE%
