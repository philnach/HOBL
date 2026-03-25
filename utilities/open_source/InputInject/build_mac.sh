#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

OUTDIR="Output"
# build InputInjector for macOS
dotnet publish -f net8.0-macos -r osx-arm64 -c Release -o $OUTDIR /p:OS=MACOS
# Extract package to ease install
rm -rf $OUTDIR/out
pkgutil --expand-full $OUTDIR/InputInject-1.0.pkg $OUTDIR/out
cp -r $OUTDIR/out/InputInject.pkg/Payload/InputInject.app/Contents/MonoBundle $OUTDIR/osx-arm64
rm -rf $OUTDIR/out
# Zip it
zip -j $OUTDIR/InputInject_osx-arm64.zip $OUTDIR/osx-arm64/*
rm -rf $OUTDIR/osx-arm64