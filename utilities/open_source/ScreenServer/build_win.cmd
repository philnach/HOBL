@echo off
REM Copyright (c) Microsoft. All rights reserved.
REM Licensed under the MIT license. See LICENSE file in the project root for full license information.

REM build ScreenServer for windows
dotnet publish -f net8.0-windows -r win-x64 -c Release -o Output\ScreenServer_win-x64 /p:OS=WINDOWS
dotnet publish -f net8.0-windows -r win-arm64 -c Release -o Output\ScreenServer_win-arm64 /p:OS=WINDOWS
cd Output
tar.exe -a -cf ScreenServer_win-x64.zip -C ScreenServer_win-x64 *
rd /s /q ScreenServer_win-x64
tar.exe -a -cf ScreenServer_win-arm64.zip -C ScreenServer_win-arm64 *
rd /s /q ScreenServer_win-arm64
