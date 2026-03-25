@echo off
REM Copyright (c) Microsoft. All rights reserved.
REM Licensed under the MIT license. See LICENSE file in the project root for full license information.

REM build InputInjector for macOS
dotnet publish -f net8.0-windows -r win-x64 -c Release -o Output\InputInject_win-x64 /p:OS=WINDOWS
dotnet publish -f net8.0-windows -r win-arm64 -c Release -o Output\InputInject_win-arm64 /p:OS=WINDOWS
cd Output
tar.exe -a -cf InputInject_win-x64.zip -C InputInject_win-x64 *
rd /s /q InputInject_win-x64
tar.exe -a -cf InputInject_win-arm64.zip -C InputInject_win-arm64 *
rd /s /q InputInject_win-arm64
