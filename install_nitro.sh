#!/bin/bash

echo "Downloading and extracting Nitro binary from Docker image..."

# Docker 이미지를 통해 바이너리 추출
docker create --name temp-nitro offchainlabs/nitro-node:v3.2.1-d81324d
docker cp temp-nitro:/usr/local/bin/nitro ./nitro
docker rm temp-nitro

chmod +x ./nitro
echo "Nitro binary has been successfully extracted to ./nitro"
