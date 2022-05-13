cd ../../
docker build -t pocket_blockchain -f ./docker_build/pocket_blockchain/Dockerfile .
docker run --name pocket_blockchain -d -p 5001:5001 pocket_blockchain