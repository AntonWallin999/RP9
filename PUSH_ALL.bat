from pathlib import Path

content = r"""@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ======================================
REM PUSH_ALL.bat
REM Deterministic push using GitHub Desktop bundled git
REM Repository: F:\GitHub\RP9
REM ======================================

set "REPO_DIR=F:\GitHub\RP9"

echo.
echo ======================================
echo   GitHub PUSH_ALL - START
echo   Repo: %REPO_DIR%
echo ======================================
echo.

REM Verify repository directory exists
if not exist "%REPO_DIR%\" (
  echo ERROR: Repository directory does not exist:
  echo %REPO_DIR%
  goto END
)

REM Verify this is a Git repository
if not exist "%REPO_DIR%\.git\" (
  echo ERROR: No .git directory found in:
  echo %REPO_DIR%
  goto END
)

REM Enter repository directory
cd /d "%REPO_DIR%"
if errorlevel 1 (
  echo ERROR: Could not enter repository directory.
  goto END
)

REM Locate GitHub Desktop bundled git.exe
set "GIT_BASE=%LOCALAPPDATA%\GitHubDesktop"
set "GIT_EXE="

for /d %%D in ("%GIT_BASE%\app-*") do (
  if exist "%%D\resources\app\git\cmd\git.exe" (
    set "GIT_EXE=%%D\resources\app\git\cmd\git.exe"
  )
)

if not defined GIT_EXE (
  echo ERROR: Could not locate git.exe from GitHub Desktop.
  echo Expected under:
  echo %LOCALAPPDATA%\GitHubDesktop\app-*\resources\app\git\cmd\git.exe
  goto END
)

echo Using Git:
echo "%GIT_EXE%"
echo.

REM Verify git works
"%GIT_EXE%" --version
if errorlevel 1 (
  echo ERROR: git.exe failed to run.
  goto END
)

REM Show current status
echo.
echo --- CURRENT STATUS ---
"%GIT_EXE%" status
echo ----------------------
echo.

REM Add all changes
echo Adding all changes...
"%GIT_EXE%" add -A
if errorlevel 1 (
  echo ERROR: git add failed.
  goto END
)

REM Commit with timestamp; skipped automatically if no changes exist
set "COMMIT_MSG=Auto push %DATE% %TIME%"
echo Committing...
"%GIT_EXE%" commit -m "%COMMIT_MSG%" >nul 2>&1

REM Push to GitHub
echo Pushing to GitHub...
"%GIT_EXE%" push
if errorlevel 1 (
  echo ERROR: git push failed.
  goto END
)

echo.
echo SUCCESS: Push completed.
echo.

:END
echo ======================================
echo   GitHub PUSH_ALL - END
echo ======================================
pause
endlocal
"""

out = Path("/mnt/data/PUSH_ALL.bat")
out.write_text(content, encoding="utf-8", newline="\r\n")
print(f"Created: {out}")
