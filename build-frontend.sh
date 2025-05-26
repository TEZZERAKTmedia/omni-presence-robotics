#!/bin/bash
echo "🔧 Installing frontend deps and building dist..."
cd Frontend
rm -rf node_modules dist package-lock.json
npm install --omit=optional
npm run build
cd ..
