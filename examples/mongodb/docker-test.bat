@echo off

docker build . -t migrate-anything-docker-test
docker run --rm --name ma-mongo -d migrate-anything-docker-test
docker exec ma-mongo sh /test/test-in-docker.sh
docker exec ma-mongo kill 1
