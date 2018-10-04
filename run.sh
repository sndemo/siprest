./build.sh
docker run --rm -it -p 8080:8080 --name siprest --network sndemo sndemo/siprest
