#!/bin/bash
set -e
echo "Starting APK build environment setup..."

cd /home/antonio

if [ ! -d "/home/antonio/node-v22.2.0-linux-x64" ]; then
  echo "Installing Node.js 22..."
  wget -q https://nodejs.org/dist/v22.2.0/node-v22.2.0-linux-x64.tar.xz
  tar -xf node-v22.2.0-linux-x64.tar.xz
fi
export PATH="/home/antonio/node-v22.2.0-linux-x64/bin:$PATH"

if [ ! -d "/home/antonio/jdk-21.0.2" ]; then
  echo "Installing OpenJDK 21..."
  wget -q https://download.java.net/java/GA/jdk21.0.2/f2283984656d49d69e91c558476027ac/13/GPL/openjdk-21.0.2_linux-x64_bin.tar.gz
  tar -xzf openjdk-21.0.2_linux-x64_bin.tar.gz
fi
export JAVA_HOME="/home/antonio/jdk-21.0.2"
export PATH="$JAVA_HOME/bin:$PATH"

if [ ! -d "/home/antonio/android-sdk/cmdline-tools/latest" ]; then
  echo "Installing Android SDK..."
  mkdir -p /home/antonio/android-sdk/cmdline-tools
  cd /home/antonio/android-sdk/cmdline-tools
  rm -f *.zip.* && wget -q https://dl.google.com/android/repository/commandlinetools-linux-10406996_latest.zip -O cmdline.zip && python3 -m zipfile -e cmdline.zip .
  mv cmdline-tools latest
fi
export ANDROID_HOME="/home/antonio/android-sdk"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"
chmod +x /home/antonio/android-sdk/cmdline-tools/latest/bin/*

# Accept licenses and install SDK components
echo "Accepting licenses and downloading platforms..."
yes | sdkmanager --licenses > /dev/null
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" > /dev/null

# 4. Setup Capacitor Project
echo "Setting up Capacitor Project..."
cd "/home/antonio/Progetto streaming"
# Change name in package.json to something generic
sed -i 's/VivoPlayer/StreamPRO/g' index.html
sed -i 's/VivoPlayer/StreamPRO/g' package.json

# Install capacitor dependencies
npm install @capacitor/core @capacitor/cli @capacitor/android
npm run build

rm -rf android capacitor.config.json capacitor.config.ts
# Init Capacitor
yes "n" | npx cap init StreamPRO com.streampro.app --web-dir dist
yes "n" | npx cap add android

# 5. Build APK
echo "Building APK..."
cd android
./gradlew assembleDebug

echo "APK Built Successfully!"
cp app/build/outputs/apk/debug/app-debug.apk "/home/antonio/Progetto streaming/public/StreamPRO.apk"
echo "APK copied to public folder!"
