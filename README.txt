how to use:
    host: run server.py and wait, until client will connect
          by default, server is running on localhost:8084. You can
          change it by hardcoding ip:port in the source, or just
          pass it threw arguments --ip <ip> and/or --port <port>

    client: just run it and do not close console shell is working in
            you can hardcode ip:port of your server in the source, or
            pass it threw arguments --ip <ip> and/or --port <port>

    if you want just to test it, you can

requirements:
    python 3.6+
    tested for: linux

host commands:
    mk - create file (echo > filename.txt DOESN'T WORK (I don't know, why))
