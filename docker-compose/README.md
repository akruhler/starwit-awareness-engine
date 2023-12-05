# Docker-Compose Version Of The Vision Pipeline
This repository aims at replicating the Helm/Kubernetes-based vision pipeline for local development as closely as possible. It might not always be up-to-date...

## Documentation
A longer explanation of the architecture and the technical setup can be found in `../doc/README.md`.

## How-To Run
All relevant components (Redis and Postgres) have healthchecks in place, s.t. `docker compose up` should "just work".\
For a working (basic) pipeline you need (at least) the following components running (which is what `docker compose up` will give you):
- redis
- video-source-py
- object-detector
- object-tracker
- streaming-server

In order to have more control you might want to start all components separately (e.g. in tmux panes).
For the video source you either need to have a video stream readily available (and configure its uri accordingly) or you can use the streaming-server compose service, which will play a video file on demand (that you have to mount!).\
**Caution:** Do not try to mount the video file directly to the video source. This is currently not supported as the video source relies on the source to pace itself, the video source will read frames as fast as possible!

If you have a Nvidia GPU in your system, you can try changing the `device` on object-detector and -tracker from `cpu` to `cuda`. No guarantees whether that will work!

## Visual Pipeline Introspection
The `../tools/watch.py` script can be used to visually look into the data flows within the pipeline. See more detailed description it its readme.