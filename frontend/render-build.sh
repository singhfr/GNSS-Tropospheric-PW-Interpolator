#!/bin/bash

# Render.com build script for the frontend

echo "🚀 Starting frontend build for Render..."

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the Next.js application
echo "🔨 Building Next.js application..."
npm run build

echo "✅ Build completed successfully!"
