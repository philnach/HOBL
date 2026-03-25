@echo off
pushd %~dp0
if exist ..\python_embed\python.exe (
    ..\python_embed\python.exe ScenarioMaker.pyw %*
) else (
    python ScenarioMaker.pyw %*
)
