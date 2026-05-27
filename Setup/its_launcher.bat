@echo off
setlocal

set CMD=%1

REM if "%CMD%"=="itsbox://run-dashboard" (

    REM monitor server 실행
    wsl bash -ic "/home/smlee/Viewer/ITS/run_monitor_server.sh"
REM )

endlocal