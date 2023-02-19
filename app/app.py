from flask import Flask
import argparse
import sys
import json
import os
from typing import Any, Dict

app = Flask(__name__)

hi = 'Hello world!'

secrets:Dict[str, Any] = {}

@app.route('/')
def hello() -> str:
	return f'{hi}\n'

@app.route('/get-env')
def get_env() -> str:
    ap_env:Dict[str, Any] = {}
    for key, value in os.environ.items():
        if key.startswith('AP_'):
            ap_env[key] = value
    return json.dumps(ap_env, indent=2) + "\n"

@app.route('/get-secrets')
def get_secrets():
	return json.dumps(secrets, indent=2) + "\n"

def run() -> None:
    """
    Parse command line and then reads secret message from stdin,
    run flask.
    Never returns
    """
    #
    # Prepare CLI parser
    #
    parser = argparse.ArgumentParser(
        description = '''A Flask app with parameters and secrets passed to it.
Some parameters can be passed as command line options.
Some parameters can be passed as environment variables, e.g. AP_PARAM1.
You can also pass a JSON with secretes via stdin.''',
        epilog = 'AP_* environment is revealed at http://host:port/get-env')

    global hi
    parser.add_argument(
        '--hi', type=str, default=hi,
        help=f'Message to present at http://host:port/, defaults to "{hi}"')
    parser.add_argument(
        '--host', type=str, default='0.0.0.0',
        help='IP of the host, defaults to 0.0.0.0')
    parser.add_argument(
        '--port', type=int, default=8000, help='Port number, defaults to 8000')
    parser.add_argument(
        'secrets', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
        help='''JSON-formatted secrets to be passed for reveal at
http://host:port/get-secrets''')
    #
    # Parse CLI
    #
    args = parser.parse_args()
    #
    # Consume message hi from CLI
    #
    hi = args.hi
    #
    # Consume JSON of secrets from stdin
    #
    global secrets
    try:
        #with open(args.secrets) as json_data:
        secrets = json.load(args.secrets)
    except json.decoder.JSONDecodeError as err:
        print(f"Failed to read from {args.secrets}:", err)
        secrets = {}
    #
    # Never ending loop serving HTTP requests
    #
    app.run(host=args.host, port=args.port)
    return

if __name__ == '__main__':
    run()
