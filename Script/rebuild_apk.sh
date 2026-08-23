#!/bin/bash
set -e
cd "/home/antonio/Progetto streaming"
export JAVA_HOME="/home/antonio/jdk-21.0.2"
export PATH="$JAVA_HOME/bin:/home/antonio/node-v22.2.0-linux-x64/bin:$PATH"
export ANDROID_HOME="/home/antonio/android-sdk"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"

yes "n" | npx cap sync

cd android
./gradlew assembleDebug
cp app/build/outputs/apk/debug/app-debug.apk "/home/antonio/Progetto streaming/public/StreamPRO.apk"
