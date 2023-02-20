# gomplate with AWS+SM data source

Have your gomplate
[set-up](https://asokolsky.github.io/apps/gomplate.html)

Verify it:

```
> echo 'foo={{ (ds "secrets").foo }}' | \
    gomplate -d secrets=app/secrets.json
foo=bar
```

Have your AWS CLI
[set-up](https://asokolsky.github.io/aws/cli.html#install).

Then...

## Publish the secrets

```sh
aws secretsmanager create-secret \
    --name pass-secret \
    --description "Secrets for pass-secret repo" \
    --secret-string file://app/secrets.json
```

## Verify the secret

Retrieve the secret you just stored (assumes you have `jq` installed):
```sh
aws secretsmanager get-secret-value --secret-id pass-secret| \
    jq ".SecretString"
```

## Use AWS Secrets Manager Secrets with gomplate

By now AWS SM secret `pass-secret` is ready for consumption by gomplate:

```sh
echo 'foo={{ (ds "secrets").foo }}' | \
    gomplate -d 'secrets=aws+sm:pass-secret?type=application/json'
```
