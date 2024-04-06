import os

video_dir = "/root/src"
for i, file in enumerate(os.listdir(video_dir)):
    if os.path.isfile(os.path.join(video_dir, file)):
        os.system(f"VID={i} REDIS_PORT=1000{i} screen -d -m python3 /root/starwit-fork/tools/echo-parser.py")
        print(f"VID={i} REDIS_PORT=1000{i} screen -d -m python3 /root/starwit-fork/tools/echo-parser.py")