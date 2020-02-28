# -*- coding: utf-8 -*-
"""Freenet proxy."""

import os
import subprocess
import sys
import time
import urllib.parse
import warnings

import stem

import darc.typing as typing
from darc.error import FreenetBootstrapFailed, render_error

# bootstrap wait
BS_WAIT = float(os.getenv('FREENET_BS_WAIT', '10'))

# Freenet port
FREENET_PORT = os.getenv('FREENET_PORT', '8888')

# Freenet bootstrap retry
FREENET_RETRY = int(os.getenv('FREENET_RETRY', '3'))

# Freenet project path
FREENET_PATH = os.getenv('FREENET_PATH', '/usr/local/src/freenet')

# Freenet bootstrapped flag
_FREENET_BS_FLAG = False
# Freenet daemon process
_FREENET_PROC = None


def _freenet_bootstrap():
    """Freenet bootstrap."""
    global _FREENET_BS_FLAG, _FREENET_PROC

    # launch Freenet process
    args = ['su', '-', 'darc', os.path.join(FREENET_PATH, 'run.sh'), 'start']
    _FREENET_PROC = subprocess.Popen(args)
    time.sleep(BS_WAIT)

    # _FREENET_PROC = subprocess.Popen(
    #     args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    # )

    # stdout, stderr = _FREENET_PROC.communicate(timeout=BS_WAIT)
    # if DEBUG:
    #     print(render_error(stdout, stem.util.term.Color.BLUE))  # pylint: disable=no-member
    # print(render_error(stderr, stem.util.term.Color.RED))  # pylint: disable=no-member

    returncode = _FREENET_PROC.returncode
    if returncode is not None and returncode != 0:
        raise subprocess.CalledProcessError(returncode, args,
                                            _FREENET_PROC.stdout,
                                            _FREENET_PROC.stderr)

    # update flag
    _FREENET_BS_FLAG = True


def freenet_bootstrap():
    """Bootstrap wrapper for Freenet."""
    # don't re-bootstrap
    if _FREENET_BS_FLAG:
        return

    print(stem.util.term.format('Bootstrapping Freenet proxy...',
                                stem.util.term.Color.BLUE))  # pylint: disable=no-member
    for _ in range(FREENET_RETRY+1):
        try:
            _freenet_bootstrap()
            break
        except Exception as error:
            warning = warnings.formatwarning(error, FreenetBootstrapFailed, __file__, 64, 'freenet_bootstrap()')
            print(render_error(warning, stem.util.term.Color.YELLOW), end='', file=sys.stderr)  # pylint: disable=no-member


def has_freenet(link_pool: typing.Set[str]) -> bool:
    """Check if contain Freenet links."""
    for link in link_pool:
        # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
        parse = urllib.parse.urlparse(link)

        if parse.netloc in (f'127.0.0.1:{FREENET_PORT}', f'localhost:{FREENET_PORT}'):
            return True
    return False