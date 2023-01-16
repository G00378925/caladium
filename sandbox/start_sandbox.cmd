@echo off
:caladium_sandbox_loop
"%ProgramFiles%\Racket\Racket.exe" main.rkt
goto caladium_sandbox_loop

