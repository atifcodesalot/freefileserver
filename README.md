# FreeFileServer

## What is FreeFileServer?
FreeFileServer is an extremely simplistic HTTP file server written in Python. It enables to share a directory on your browser over any network via [HTTP](https://en.wikipedia.org/wiki/HTTP). It was written from scratch with zero AI. Uses no external dependencies.


## Usage
clone this repo:

```
git clone https://github.com/atifcodesalot/freefileserver
```

Go to the project directory:

```
cd freefileserver
```

Finally run the package:

```
python3 -m freefileserver [file-path]
```

## HTTPS
To run your server with HTTPS, first you need to provide your TLS private key and certificate in te project directory as two files:
`key.pem` and `cert.pem`. Then run the package with the `--secure` flag.


## Example usage:

```
python3 -m freefileserver --secure C:\
```
This shares your entire C: directory with `HTTPS`.


```
python3 -m freefileserver .
```

This serves the current (project) directory with plain `HTTP`.






