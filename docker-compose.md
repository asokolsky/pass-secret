# App run via docker-compose

`compose.yaml` describes the services.

## Build it

```sh
sudo docker compose build
```

## Just run it

```
> sudo docker compose up
[+] Running 1/0
 ⠿ Container pass-secret-app-1  Recreated 0.1s
Attaching to pass-secret-app-1
pass-secret-app-1  | Failed to read from <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>: Expecting value: line 1 column 1 (char 0)
pass-secret-app-1  |  * Serving Flask app 'app'
pass-secret-app-1  |  * Debug mode: off
pass-secret-app-1  | WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
pass-secret-app-1  |  * Running on all addresses (0.0.0.0)
pass-secret-app-1  |  * Running on http://127.0.0.1:8888
pass-secret-app-1  |  * Running on http://172.18.0.2:8888
pass-secret-app-1  | Press CTRL+C to quit
```

Note: container fails to read secrets from `stdin` yet continues execution.

### Test it

In another shell:

```
> curl -q http://127.0.0.1:8888
hello from docker!
> curl -q http://127.0.0.1:8888/get-env
{
  "AP_FOO": "secret_not_really",
  "AP_BAR": "in_your_face"
}
> curl -q http://127.0.0.1:8888/get-secrets
{}
```

Note: no secrets were passed.

Note: environment was passed from `compose.yaml`.

## Run it passing the stdin to a container

This runs docker comose service `app` and passes to it secrets via `stdin`:

```
> cat ./app/secrets.json| sudo docker compose run -T -p '127.0.0.1:8888:8888' app
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8888
 * Running on http://172.18.0.2:8888
Press CTRL+C to quit
```
### Test it

In another shell:

'''
> curl -q http://127.0.0.1:8888
hello from docker!
> curl -q http://127.0.0.1:8888/get-env
{
  "AP_BAR": "in_your_face",
  "AP_FOO": "secret_not_really"
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
'''

## Run it passing the `secrets.json` to `docker compose` via stdin

Use `gomplate` to create a compose (with secrets) and pass it to
`docker compose` via stdin

```
> gomplate -d secrets=./app/secrets.json -f compose.gomplate| \
  sudo docker compose -f - up
[+] Running 1/1
 ⠿ Container pass-secret-app-1  Recreated 0.1s
Attaching to pass-secret-app-1
pass-secret-app-1  | Failed to read from <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>: Expecting value: line 1 column 1 (char 0)
pass-secret-app-1  |  * Serving Flask app 'app'
pass-secret-app-1  |  * Debug mode: off
pass-secret-app-1  | WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
pass-secret-app-1  |  * Running on all addresses (0.0.0.0)
pass-secret-app-1  |  * Running on http://127.0.0.1:8888
pass-secret-app-1  |  * Running on http://172.18.0.2:8888
pass-secret-app-1  | Press CTRL+C to quit
```

### Test it

In another shell:

'''
> curl -q http://127.0.0.1:8888
hello from docker!
> curl -q http://127.0.0.1:8888/get-env
{
  "AP_GRAULT": "true",
  "AP_FOO": "bar",
  "AP_BAZ": "1",
  "AP_QUX": "null",
  "AP_QUUX": "3.3"
}
> curl -q http://127.0.0.1:8888/get-secrets
{}
'''

## Run it passing the secrets from AWS SM to `docker compose` via stdin

Provided you stored the secrets in AWS SM under the key `pass-secret`:

```sh
aws secretsmanager create-secret \
    --name pass-secret \
    --description "Secrets for pass-secret repo" \
    --secret-string file:app/secrets.json
```
You can now retrieve the secrets and pass it directly to docker compose via
stdin using gomplate:

```
> gomplate -d 'secrets=aws+sm:pass-secret?type=application/json' -f compose.gomplate| \
   sudo docker compose -f - up
[+] Running 1/0
 ⠿ Container pass-secret-app-1  Recreated 0.0s
Attaching to pass-secret-app-1
pass-secret-app-1  | Failed to read from <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>: Expecting value: line 1 column 1 (char 0)
pass-secret-app-1  |  * Serving Flask app 'app'
pass-secret-app-1  |  * Debug mode: off
pass-secret-app-1  | WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
pass-secret-app-1  |  * Running on all addresses (0.0.0.0)
pass-secret-app-1  |  * Running on http://127.0.0.1:8888
pass-secret-app-1  |  * Running on http://172.18.0.2:8888
pass-secret-app-1  | Press CTRL+C to quit
```

Check the app:
```
> curl -q http://127.0.0.1:8888
hello from docker!
> curl -q http://127.0.0.1:8888/get-env
{
  "AP_FOO": "bar",
  "AP_BAZ": "1",
  "AP_QUX": "null",
  "AP_QUUX": "3.3",
  "AP_GRAULT": "true"
}
> curl -q http://127.0.0.1:8888/get-secrets
{}
```

## Conclusion

We demonstrated:
* how to use gomplate to retrieve secrets from AWS SM and to pass
these to docker container via stdin;
* how to use gomplate to retrieve secrets from AWS SM and to pass
these to docker compose environment.
