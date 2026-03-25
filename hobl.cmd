@echo off
pushd %~dp0
rem if downloads\python_embed\python.exe exists
if exist downloads\python_embed\python.exe (
    rem run hobl.py with downloads\python_embed\python.exe and all passed arguments
    downloads\python_embed\python.exe core\hobl.py %*
) else (
    rem run hobl.py with system python
    python core\hobl.py %*
)
