@echo off
echo Starting Redis with Docker...
docker run -p 6379:6379 --name redis -d redis:7-alpine

echo Redis started on port 6379
echo To stop Redis: docker stop redis
echo To remove Redis container: docker rm redis

