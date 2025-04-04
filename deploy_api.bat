@echo off
echo Building the Docker image...
docker build -t side-stacker-app .

echo Tagging the Docker image...
docker tag side-stacker-app:latest nikitalokhmachev/side-stacker-app:latest

echo Pushing the Docker image to the repository...
docker push nikitalokhmachev/side-stacker-app:latest

echo Done.
pause
