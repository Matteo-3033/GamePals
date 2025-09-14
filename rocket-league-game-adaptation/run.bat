@echo off

echo Starting the GamePals framework with the provided arguments...
if "%2"=="" (
    call python main.py -gc configs/game.toml -agc configs/agents.toml -asc %1
) else (
    call python main.py -gc configs/game.toml -agc configs/agents.toml -asc %1 -o %2
)

if errorlevel 1 (
    echo An error occurred while running the GamePals framework.
    exit /b 1
)
