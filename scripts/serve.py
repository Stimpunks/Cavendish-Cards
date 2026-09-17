#!/usr/bin/env python3
"""Serve web/ for local preview, from any Python on the machine.

    python3 scripts/serve.py [port]        # port, else $PORT, else 8000

This exists because `python3 -m http.server --directory web` has a landmine in
it: that module's __main__ block evaluates `os.getcwd()` while building its
argument parser, before it has looked at a single argument, so it dies wherever
that call is refused rather than wherever the working directory is actually
needed. Nothing here touches the working directory at all -- the root comes
from this file's own location, and the handler is handed that root explicitly,
which is also what stops SimpleHTTPRequestHandler falling back to os.getcwd().

That does NOT make any interpreter work under the Claude Code preview launcher,
and .claude/launch.json still pins /opt/homebrew/bin/python3 for a separate
reason. Apple's /usr/bin/python3 (the Xcode shim) cannot read files under
~/Documents when the launcher starts it: it fails with `can't open file ...
Operation not permitted` on this script, by relative path and by absolute path
alike, before any of the above runs. That is a TCC decision about which binary
is asking, not something a script can route around. From an ordinary shell the
same interpreter serves this fine.

Two things this adds over the stdlib default, both to make the local site
behave a little more like the deployed one: the media types netlify.toml pins
by hand, and no-store on everything so a rebuild shows up on reload instead of
serving yesterday's cards.json out of the browser cache.

What it cannot do is apply the security headers. Those come from netlify.toml
and are absent locally -- see web/README.md for what that hides, because it has
already hidden one shipped bug.
"""

import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# abspath() only consults the working directory for a relative path, and the
# main script's __file__ is absolute on every Python this repo supports.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, os.pardir, "web"))


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/markdown; charset=utf-8",
        ".webmanifest": "application/manifest+json",
        ".svg": "image/svg+xml",
        ".woff2": "font/woff2",
    }

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        # One line per request, without the date stamp the default prepends.
        sys.stderr.write("%s\n" % (fmt % args))


def main():
    # An argument wins; then $PORT, which is how the Claude Code preview
    # launcher hands over a free port when 8000 is already taken by another
    # session's server; then the old default. Nothing here needs a fixed port
    # -- it serves static files, with no callback, webhook, or allowed origin
    # pointing at it -- so .claude/launch.json sets autoPort and passes none.
    port = 8000
    source = None
    if len(sys.argv) > 1:
        port, source = sys.argv[1], "argument"
    elif os.environ.get("PORT"):
        port, source = os.environ["PORT"], "$PORT"
    if source is not None:
        try:
            port = int(port)
        except ValueError:
            sys.exit(f"Not a port number ({source}): {port!r}")

    if not os.path.isdir(ROOT):
        sys.exit(f"No {ROOT}. Run `python3 scripts/build-site.py` first.")
    if not os.path.exists(os.path.join(ROOT, "cards.json")):
        print("  ! web/cards.json is missing -- the deck will load empty.\n"
              "    Run `python3 scripts/build-site.py` to generate it.",
              file=sys.stderr)

    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=ROOT))
    print(f"Serving {ROOT} at http://127.0.0.1:{port}/  (ctrl-c to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
