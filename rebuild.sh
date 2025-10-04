#!/bin/bash
# rebuild.sh - Rebuild Docker images with new enhancements
echo "🔨 Rebuilding Docker images..."
docker-compose build --no-cache
echo "✅ Build complete!"
