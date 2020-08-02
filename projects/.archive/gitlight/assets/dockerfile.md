Uploading to Docker
===================

We use a custom image to control what's available during testing.

Build/Release
-------------

Prep:

-   Open [Play w/ Docker](https://labs.play-with-docker.com/)
-   Add new instance
-   Connect via ssh
-   Copy assets/dockerfile -> host:Dockerfile

Build Image:

    docker build ./

This will show something like:

    Successfully built cbbedc85134f
                       ^-- <image-id>

Deploy:

    docker login --username=<username>
    docker tag <image-id> gitlight/deb-testing-py3
    docker push gitlight/deb-testing-py3

Hurray, a new version of ``gitlight/deb-testing-py3`` has
been uploaded to Docker Hub!
