#!/usr/bin/env python3
import os, sys, socket
from youtube_queue.app import app
from youtube_queue.models import Base, engine

if __name__ == "__main__":
    if "migrate" in sys.argv:
        Base.metadata.create_all(engine)
    else:
        current_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        if "local" in sys.argv:
            current_ip = "127.0.0.1"
        port = int(os.environ.get("PORT", default=5000))
        debug = "debug" in sys.argv
        app.run(host=current_ip, port=port, debug=debug)
