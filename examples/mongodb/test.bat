@echo off

echo Running migrations
echo.

migrate-anything migrations
if ERRORLEVEL 1 GOTO ERROR


echo.
echo Adding new migration
echo.

copy migrations\01-test.py migrations\02-test.py
migrate-anything migrations
if ERRORLEVEL 1 GOTO ERROR

echo.
echo Undoing old migration
echo.

del migrations\02-test.py
del migrations\*.pyc

migrate-anything migrations
if ERRORLEVEL 1 GOTO ERROR
if exist test-file.txt (
    echo Undo did not work.
    GOTO :ERROR
)

GOTO :CLEANUP

:ERROR
echo Error during test
goto :EOF

:CLEANUP
