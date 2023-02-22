# App in a docker container

Consider passing parameters and secrets to a container running the
[app](README.md)).

## Build the app image

```sh
sudo docker build -t params-secret-test .
```

## Start the app container

Note the need for:

* passing the contents of `secrets.json` via `stdin`
* passing a secret via environment variable `AP_FOO`
* need for use of interactive mode
* need to map the network port

```
> cat secrets.json| sudo docker run -e AP_FOO=bar -p 8888:8888 -i params-secret-test
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8888
 * Running on http://172.17.0.2:8888
Press CTRL+C to quit
```

### Access the app in the container

In a separate shell:
```
> curl -q http://127.0.0.1:8888
hello from docker!
> curl -q http://127.0.0.1:8888/get-env
{
  "AP_FOO": "bar"
}
> curl -q http://127.0.0.1:8888/get-secrets
{
  "foo": "bar",
  "baz": 1,
  "qux": null,
  "quux": 3.3,
  "grault": true,
  "garply": [
    "waldo",
    "xyzzy",
    "thud"
  ],
  "corge": {
    "fred": 1,
    "plugh": false
  }
}
```

## Examine the Secrets Leakage

```
> ps ax|grep "docker run -e AP_FOO"
1264069 pts/6    S+     0:00 sudo docker run -e AP_FOO=bar -p 8888:8888 -i params-secret-test
1264070 pts/8    Ss+    0:00 sudo docker run -e AP_FOO=bar -p 8888:8888 -i params-secret-test
1264071 pts/8    Sl     0:00 docker run -e AP_FOO=bar -p 8888:8888 -i params-secret-test
1264936 pts/7    S+     0:00 grep docker run -e AP_FOO
```

Note that the need to explicitly set the environment for the container forces
it to be present on the command line which makes it unsuitable for passing
secrets.

## A better way to start the app container

If you store secrets in AWS...

```sh
aws secretsmanager create-secret \
    --name pass-secret \
    --description "Secrets for pass-secret repo" \
    --secret-string file:secrets.json
```

You can launch the container with secrets retrieved from AWS using gomplate:

```
cat secrets.gomplate | \
  gomplate -d 'secrets=aws+sm:pass-secret' | \
  sudo docker run -e AP_FOO=bar -p 8888:8888 -i params-secret-test

 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8888
 * Running on http://172.17.0.2:8888
Press CTRL+C to quit
```

Then in a separate shell:
```
> curl -q http://127.0.0.1:8888
hello from docker!
> curl -q http://127.0.0.1:8888/get-env
{
  "AP_FOO": "bar"
}
> curl -q http://127.0.0.1:8888/get-secrets
{
  "foo": "bar",
  "baz": 1,
  "qux": null,
  "quux": 3.3,
  "grault": true,
  "garply": [
    "waldo",
    "xyzzy",
    "thud"
  ],
  "corge": {
    "fred": 1,
    "plugh": false
  }
}
```
## Conclusion

By now we demonstrated that:

* you can pass secrets to a container using stdin
* use of AWS+SM allows for secrets consumption without touching the file system
* use of environment or command line will leak the secrets

## Use with docker-compose

See the [parent directory](../).
