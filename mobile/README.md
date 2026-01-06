# Mobile Companion App

This directory contains the React Native mobile application for the EVENT system. It allows field operators to receive alerts, view the mission map, and track real-time detections.

## Features

- **Authentication**: secure login with JWT.
- **Alert Feed**: View real-time security alerts.
- **Live Map**: Interactive map showing UAV position and detection zones.
- **Settings**: Connection and profile management.

## Prerequisites

- Node.js (v18+)
- npm or yarn

## Installation

```bash
cd mobile
npm install
```

## Configuration

 The API URL is currently configured in `src/api/client.js`.
- Android Emulator: `http://10.0.2.2:8000/api`
- iOS Simulator / Web: `http://localhost:8000/api`

## Running the App

Start the development server:

```bash
npx expo start
```

- Press `a` for Android Emulator.
- Press `i` for iOS Simulator (macOS only).
- Press `w` for Web preview.

## Building for Web

To verify the build or deploy as a PWA:

```bash
npx expo export --platform web
```
