@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo Real Uniform Generator v0.6.0 - Build and Blender Test
echo ============================================================
powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\build_and_test.ps1"
set EXIT_CODE=%ERRORLEVEL%
if not "%EXIT_CODE%"=="0" (
  echo.
  echo FAILED - Exit code: %EXIT_CODE%
  echo Copy the complete error output when reporting the failure.
) else (
  echo.
  echo SUCCESS
  echo Install: dist\real_uniform_generator-v0.6.0.zip
)
pause
exit /b %EXIT_CODE%
