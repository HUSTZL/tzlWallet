###
 # @Author: Haofei Hou
 # @Date: 08-08-2022 16:01:07
 # @LastEditTime: 08-12-2022 10:46:21
 # @Contact: yuechuhaoxi020609@outlook.com
###
#docker rm -vf $(docker ps -aq) # not shut down the front web server

docker build -f dockerfiles/Dockerfile.normal -t psb_normal .

docker container run -p 80:8080 -it -v /home/ubuntu/Bill_Backend/test/:/app/test psb_normal
