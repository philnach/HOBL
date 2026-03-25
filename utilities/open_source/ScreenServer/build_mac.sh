#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

OUTDIR="Output"
rm -rf $OUTDIR
# build ScreenServer for macOS
dotnet publish -f net8.0-macos -r osx-arm64 -c Release -o $OUTDIR/ScreenServer_osx-arm64 /p:OS=MACOS
# Extract package to ease install
cd $OUTDIR/ScreenServer_osx-arm64
rm -rf out
pkgutil --expand-full ScreenServer-1.0.pkg out
cp -r out/ScreenServer.pkg/Payload/ScreenServer.app .
rm -rf out
# Zip it
zip -r ScreenServer_osx-arm64.zip ScreenServer.app
rm -rf ScreenServer.app
