# Desktop GUI Application

Consist of two programs: a **client program** calld `lux.py` and a **server program** called `luxserver.py`.
The `lux.py` program has a **graphical user interface** and communicates over a network with the `luxserver.py` program.

## The `lux.py` Program

When executed with `-h` as a command-line argument, the `lux.py` displays a help message that describes the program's behavior:

```
$ python lux.py -h
usage: lux.py [-h] host port

Client for the YUAG application

positional arguments:
  host        the host on which the server is running
  port        the port at which the server is listening

optional arguments:
  -h, --help  show this help message and exit
```

`lux.py` accepts exactly two command-line arguments. The first must be the **host**: the IP address or domain name of the computer on which your `luxserver.py` is running.
The second must be the number of the port at which `luxserver.py` is listening.

---

## The `luxserver.py` Program

When executed with `-h` as a command-line argument, the `luxserver.py` program displays the following help message that describes the program's behavior:

```
$ python luxserver.py -h
usage: luxserver.py [-h] port

Server for the YUAG application

positional arguments:
  port        the port at which the server should listen

optional arguments:
  -h, --help  show this help message and exit
```

`luxserver.py` accepts a single command-line argument.
That argument must be the number of the **port** on which the program will listen for connections.
