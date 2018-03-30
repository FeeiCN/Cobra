# -*- coding: utf-8 -*-

"""
    log
    ~~~

    Implements color logger

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
import sys
import re
import subprocess
import logging
import cloghandler

# stream handle
#
# Copyright (C) 2010-2012 Vinay Sajip. All rights reserved. Licensed under the new BSD license.
#
logger = logging.getLogger('CobraLog')
log_path = 'logs'
if os.path.isdir(log_path) is not True:
    os.mkdir(log_path, 0o755)
logfile = os.path.join(log_path, 'cobra.log')
fh_format = logging.Formatter("[%(asctime)s] %(levelname)s [%(lineno)s] %(message)s")
sh_format = logging.Formatter("\r[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

UNICODE_ENCODING = "utf8"

try:
    mswindows = subprocess.mswindows
except AttributeError as e:
    mswindows = False


def single_time_warn_message(message):  # Cross-linked function
    sys.stdout.write(message)
    sys.stdout.write("\n")
    sys.stdout.flush()


def stdout_encode(data):
    try:
        data = data or ""

        # Reference: http://bugs.python.org/issue1602
        if mswindows:
            output = data.encode(sys.stdout.encoding, "replace")

            if '?' in output and '?' not in data:
                warn = "cannot properly display Unicode characters "
                warn += "inside Windows OS command prompt "
                warn += "(http://bugs.python.org/issue1602). All "
                warn += "unhandled occurances will result in "
                warn += "replacement with '?' character. Please, find "
                warn += "proper character representation inside "
                warn += "corresponding output files. "
                single_time_warn_message(warn)

            ret = output
        else:
            ret = data.encode(sys.stdout.encoding)
    except Exception as e:
        ret = data.encode(UNICODE_ENCODING) if isinstance(data, unicode) else data

    return ret


if mswindows:
    import ctypes
    import ctypes.wintypes

    # Reference: https://gist.github.com/vsajip/758430
    #            https://github.com/ipython/ipython/issues/4252
    #            https://msdn.microsoft.com/en-us/library/windows/desktop/ms686047%28v=vs.85%29.aspx
    ctypes.windll.kernel32.SetConsoleTextAttribute.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.WORD]
    ctypes.windll.kernel32.SetConsoleTextAttribute.restype = ctypes.wintypes.BOOL


class ColorizingStreamHandler(logging.StreamHandler):
    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    # levels to (background, foreground, bold/intense)
    level_map = {
        logging.DEBUG: (None, 'blue', False),
        logging.INFO: (None, 'green', False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', False)
    }
    csi = '\x1b['
    reset = '\x1b[0m'
    disable_coloring = False

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty() and not self.disable_coloring

    def emit(self, record):
        try:
            message = stdout_encode(self.format(record))
            stream = self.stream

            if not self.is_tty:
                if message and message[0] == "\r":
                    message = message[1:]
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))

            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except IOError:
            pass
        except Exception as e:
            self.handleError(record)

    if not mswindows:
        def output_colorized(self, message):
            self.stream.write(message.decode('utf-8'))
    else:
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,  # black
            1: 0x04,  # red
            2: 0x02,  # green
            3: 0x06,  # yellow
            4: 0x01,  # blue
            5: 0x05,  # magenta
            6: 0x03,  # cyan
            7: 0x07,  # white
        }

        def output_colorized(self, message):
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)

            if fd is not None:
                fd = fd()

                if fd in (1, 2):  # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)

            while parts:
                text = parts.pop(0)

                if text:
                    write(text)

                if parts:
                    params = parts.pop(0)

                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0

                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08  # foreground intensity on
                            elif p == 0:  # reset to default color
                                color = 0x07
                            else:
                                pass  # error condition ignored

                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        if record.levelno in self.level_map and self.is_tty:
            bg, fg, bold = self.level_map[record.levelno]
            params = []

            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))

            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))

            if bold:
                params.append('1')

            if params and message:
                if message.lstrip() != message:
                    prefix = re.search(r"\s+", message).group(0)
                    message = message[len(prefix):]
                else:
                    prefix = ""

                message = "%s%s" % (prefix, ''.join((self.csi, ';'.join(params),
                                                     'm', message, self.reset)))

        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        return self.colorize(message, record)


try:
    sh = ColorizingStreamHandler(sys.stdout)
except ImportError:
    sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(sh_format)
logger.addHandler(sh)

# file handle
fh = cloghandler.ConcurrentRotatingFileHandler(logfile, maxBytes=(1048576 * 5), backupCount=7)
fh.setFormatter(fh_format)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.setLevel(logging.INFO)
