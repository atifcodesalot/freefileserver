# FreeFileServer

## What is FreeFileServer?
FreeFileServer is an extremely simplistic HTTP file server written in Python. It enables to share a directory on your browser over any network via [HTTP](https://en.wikipedia.org/wiki/HTTP). It was written from scratch with zero AI.

No external dependencies.


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


## Example usage:

```
python3 -m freefileserver .
```

This serves the current (project) directory.
