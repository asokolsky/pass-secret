# README

Here I look into different methods to pass parameters and secrets to an
application, application in a docker container, application container in a
docker compose environment.

Secrets, e.g. password, can be passed to a process via:

* command line - really a bad idea because anyone can read it!
* environment - better
* stdin - best

This will (hopefully) show how to use
[gomplate](https://github.com/hairyhenderson/gomplate)
to retrieve the secrets, e.g. from AWS Secret Manager, and pass these to an app
or container.

Road map:

* Start with [app/README.md](app/README.md) for a bare app case.
* Continue with [app/README-docker.md](app/README-docker.md) for a consideration
of passing parameters and secrets to an app in a container.
* Finally: [README-docker-compose.md](README-docker-compose.md) covers docker
compose case.
