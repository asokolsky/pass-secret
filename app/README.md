# README

This test app runs Flask and demonstrates passing parameters and secrets to a
process at launch:

* parameters are passed on the command line
* parameters may be passed via environment
* some secrets may be passed via stdin

Prototype: https://docs.docker.com/samples/flask/

## app CLI

```
> python3 app.py -h
usage: app.py [-h] [--hi HI] [--host HOST] [--port PORT] [secrets]

A Flask app with parameters and secrets passed to it. Some parameters can be
passed as command line options. Some parameters can be passed as environment
variables, e.g. AP_PARAM1. You can also pass a JSON with secretes via stdin.

positional arguments:
  secrets      JSON-formatted secrets to be passed for reveal at
               http://host:port/get-secrets

options:
  -h, --help   show this help message and exit
  --hi HI      Message to present at http://host:port/, defaults to "Hello world!"
  --host HOST  IP of the host, defaults to 0.0.0.0
  --port PORT  Port number, defaults to 8000

AP_* environment is revealed at http://host:port/get-env```
```

## Start the app

Start it and pass secrets:

* via environment - see environment variable `AP_FOO` being set
* via stdin - from file `secrets.json`:

```
> AP_FOO=bar python3 app.py --hi "Cruel cruel world" <secrets.json
 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://192.168.10.191:8000/ (Press CTRL+C to quit)
```

## Access the app

In a separate shell:
```
> curl http://127.0.0.1:8000/
Cruel cruel world
> curl http://127.0.0.1:8000/get-env
{
  "AP_FOO": "bar"
}
> curl http://127.0.0.1:8000/get-secrets
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

Start with identifying the pid of the app:
```
> ps ax|grep "python3 app"
1252123 pts/7    S+     0:00 python3 app.py --hi Cruel cruel world
1252602 pts/6    S+     0:00 grep python3 app
```

Note: our app pid is `1252123` and we can see it in `/proc`:

```
> ls -la /proc/1252123/cmdline
-r--r--r-- 1 alex alex 0 Feb 18 12:07 /proc/1252123/cmdline
> ls -la /proc/1252123/environ
-r-------- 1 alex alex 0 Feb 18 12:17 /proc/1252123/environ
```

Process command line can be read easily, hence is not suitable for passing the
secrets:

```
> cat /proc/1252123/cmdline | xargs -0
python3 app.py --hi Cruel cruel world
```

Process environment is more secure, although the owner can always get it:
```
> cat /proc/1252123/environ | xargs -0
GJS_DEBUG_TOPICS=JS ERROR;JS LOG LANGUAGE=en_US USER=alex....
```

Examine the process file descriptors:
```
> ls -l /proc/1252123/fd
total 0
lr-x------ 1 alex alex 64 Feb 18 12:44 0 -> /home/alex/Projects/pass-secret/app/secrets.json
lrwx------ 1 alex alex 64 Feb 18 12:44 1 -> /dev/pts/7
lrwx------ 1 alex alex 64 Feb 18 12:44 2 -> /dev/pts/7
lrwx------ 1 alex alex 64 Feb 18 12:44 3 -> 'socket:[15031007]'
```

Note: process stdin `/proc/1252123/fd/0` is as secure as
`/proc/1252123/environ`.  When stdin comes from a file others can easily see it:

```
> cat /proc/1252123/fd/0
{
    "foo": "bar",
    "baz": 1,
    "qux": null,
    "quux": 3.3,
    "grault": true,
    "garply": ["waldo", "xyzzy", "thud"],
    "corge": {
        "fred": 1,
        "plugh": false
    }
}
```

Launching the app like this makes a difference:
```
> cat secrets.json | AP_FOO=bar python3 app.py --hi "Cruel cruel world"
```

## Use gomplate with file data source

[gomplate](https://github.com/hairyhenderson/gomplate) lists among its
data sources "JSON (including EJSON - encrypted JSON), YAML, AWS EC2 metadata,
Hashicorp Consul and Hashicorp Vault".

For example, here we use `secrets.json` as a data source to fill in
`secrets.gomplate`:

'''
> cat secrets.gomplate | gomplate -d secrets=secrets.json
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

Let the gomplate fill the secrets (for now, coming from file data source) and
pass these to the app:

```sh
cat secrets.gomplate | \
  gomplate -d secrets=secrets.json | \
  AP_FOO=bar python3 app.py --hi "Cruel cruel world"
```

As you would expect:

```
> curl http://127.0.0.1:8000/
Cruel cruel world
> curl http://127.0.0.1:8000/get-env
{
  "AP_FOO": "bar"
}
> curl http://127.0.0.1:8000/get-secrets
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
## Use gomplate with AWS Secrets Manager as a data source

Store the secrets in AWS Secrets Manager under the key `pass-secret`:

```sh
aws secretsmanager create-secret \
    --name pass-secret \
    --description "Secrets for pass-secret repo" \
    --secret-string file:secrets.json
```

Launch the app like this:
```sh
cat secrets.gomplate | \
  gomplate -d 'secrets=aws+sm:pass-secret?type=application/json' | \
  AP_FOO=bar python3 app.py --hi "Cruel cruel world"
```

Then in another shell:
```console
> curl http://127.0.0.1:8000/
Cruel cruel world
> curl http://127.0.0.1:8000/get-env
{
  "AP_FOO": "bar"
}
> curl http://127.0.0.1:8000/get-secrets
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


### Examine secrets leakage

Find pid:
```
> ps ax|grep "python3 app"
1258961 pts/6    S+     0:00 python3 app.py --hi Cruel cruel world
1259415 pts/7    S+     0:00 grep python3 app
```

Process command line?
```
> ls -la /proc/1258961/cmdline
-r--r--r-- 1 alex alex 0 Feb 18 16:22 /proc/1258961/
```

Let's see it:
```
> cat /proc/1258961/cmdline| xargs -0
python3 app.py --hi Cruel cruel world
```
Let's see the process environment:
```
alex@latitude7490:~/Projects/pass-secret/app/ > cat /proc/1258961/environ | xargs -0
GJS_DEBUG_TOPICS=JS ERROR;JS LOG ...VSCODE_INJECTION=1 AP_FOO=bar
```

Let's see the process' stdin:
```
> ls -la /proc/1258961/fd/
total 0
dr-x------ 2 alex alex  0 Feb 18 16:28 .
dr-xr-xr-x 9 alex alex  0 Feb 18 16:22 ..
lr-x------ 1 alex alex 64 Feb 18 16:29 0 -> 'pipe:[15069457]'
lrwx------ 1 alex alex 64 Feb 18 16:29 1 -> /dev/pts/6
lrwx------ 1 alex alex 64 Feb 18 16:29 2 -> /dev/pts/6
lrwx------ 1 alex alex 64 Feb 18 16:29 3 -> 'socket:[15071306]'
```

Attempt to read it does not result in anything:
```
> cat /proc/1258961/fd/0
>
```

## Conclusion

* Passing the secrets via stdin works best
* Using gomplate isolates the application from concerns about secrets storage.

Using stdin to ingest the secrets retrieved by gomplate from a secure storage,
e.g. from AWS Secret Manager, is a recommended way to store and pass secrets to
an app.

Read more about the app use in a container: [docker.md](docker.md)
