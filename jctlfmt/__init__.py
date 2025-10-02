#!/usr/bin/env python3

import argparse
import json
import sys

from datetime import datetime as dt
from enum import IntEnum
from typing import TextIO


class Prio(IntEnum):
    '''
    Represents the priority of a journal message
    '''
    EMERG = 0
    ALERT = 1
    CRIT = 2
    ERR = 3
    WARNING = 4
    NOTICE = 5
    INFO = 6
    DEBUG = 7


class Entry:
    '''
    Represents a parsed journal message. The constructor takes a journal
    message in JSON format as parameter
    '''

    def __init__(self, line: str) -> None:
        self.line = line
        'Original line in JSON format'

        raw = json.loads(line)

        # For more info about the systemd journal JSON format, see
        # https://www.freedesktop.org/software/systemd/man/systemd.journal-fields.html

        self.datetime = dt.fromtimestamp(int(raw.get(
            '_SOURCE_REALTIME_TIMESTAMP',
            raw['__REALTIME_TIMESTAMP']
        )[:-6]))
        'Date and time of the journal message'

        self.hostname: str = raw['_HOSTNAME']
        'Name of the host that generated the journal message'

        self.unit: str = raw.get('_SYSTEMD_UNIT', '')
        'Systemd unit name'

        self.ident: str = raw.get('SYSLOG_IDENTIFIER', '')
        'Syslog identifier'

        self.pid: str = raw.get('_PID', '')
        'Process ID'

        self.prio = int(raw.get('PRIORITY', -1))
        'Priority of the message (as `int`)'

        self.msg: str = (
            bytes(raw['MESSAGE']).decode() if isinstance(raw['MESSAGE'], list)
            else raw['MESSAGE']
        ).strip()
        'Message text'

    @property
    def str_ui(self) -> str:
        '''
        Returns `(unit) ident` omitting the empty parts
        '''
        if self.unit == '':
            return self.ident
        elif self.ident == '':
            return f'({self.unit})'
        else:
            return f'({self.unit}) {self.ident}'

    @property
    def str_uip(self) -> str:
        '''
        Returns `(unit) ident[pid]` omitting the empty parts
        '''
        if self.pid == '':
            return self.str_ui
        else:
            return f'{self.str_ui}[{self.pid}]'

    @property
    def str_pm(self) -> str:
        '''
        Returns `<prio>msg` with prio as int (e.g. `<6>Hello world`)
        '''
        return f'<{self.prio}>{self.msg}'


class BaseFormatter:
    '''
    Base class for formatters
    '''

    def __init__(self, en_filt: bool = True, en_sens: bool = True) -> None:
        self.en_filt = en_filt
        'Whether or not to enable filtering'

        self.en_sens = en_sens
        'Whether or not to enable sensitive mode'

    def fmt_full(self, x: Entry) -> str:
        '''
        Gets the full representation of the entry `x`
        '''
        return f'{x.datetime} {x.hostname} {x.str_uip}: {x.str_pm}'

    def fmt_nopid(self, x: Entry) -> str:
        '''
        Gets the representation of the entry `x` omitting the pid if sensitive
        mode is enabled, or the full representation if sensitive mode is
        disabled
        '''
        if not self.en_sens:
            return self.fmt_full(x)
        return f'{x.datetime} {x.hostname} {x.str_ui}: {x.str_pm}'

    def fmt_nopid_msg(self, x: Entry, msg: str) -> str:
        '''
        Gets the representation of the entry `x` omitting the pid and using the
        custom message `msg` if sensitive mode is enabled, or the full
        representation if sensitive mode is disabled
        '''
        if not self.en_sens:
            return self.fmt_full(x)
        return f'{x.datetime} {x.hostname} {x.str_ui}: <{x.prio}>{msg}'

    def fmt_nopid_nomsg(self, x: Entry) -> str:
        '''
        Gets the representation of the entry `x` omitting pid and message if
        sensitive mode is enabled, or the full representation if sensitive mode
        is disabled
        '''
        if not self.en_sens:
            return self.fmt_full(x)
        return f'{x.datetime} {x.hostname} {x.str_ui}: <{x.prio}>'

    def fmt_unknown(self, x: Entry) -> str:
        '''
        Invokes `self.fmt_nopid_msg` with custom message `???` (three
        question marks)
        '''
        return self.fmt_nopid_msg(x, '???')

    def fmt_none(self, x: Entry) -> str | None:
        '''
        Returns `None` if filtering is enabled, or `self.fmt_nopid_nomsg(x)` if
        filtering is disabled
        '''
        if self.en_filt:
            return None
        return self.fmt_nopid_nomsg(x)

    def fmt(self, x: Entry) -> str | None:
        '''
        Like `self.fmt_nopid_nomsg` but filters lines with
        `prio == Prio.DEBUG`. This method is meant to be overridden by a
        derived class
        '''
        if x.prio == Prio.DEBUG:
            return self.fmt_none(x)
        return self.fmt_nopid_nomsg(x)


def exec(class_fmtr, argv=None,
         file_in: TextIO = sys.stdin, file_out: TextIO = sys.stdout) -> int:
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--no-filter', action='store_true',
                        help='Disable filtering')
    parser.add_argument('-s', '--no-sensitive', action='store_true',
                        help='Disable sensitive mode')
    parser.add_argument('-j', '--json-output', action='store_true',
                        help='JSON output mode')

    args = parser.parse_args(argv[1:])

    fmtr = class_fmtr(not args.no_filter, not args.no_sensitive)

    for line in file_in:
        text = fmtr.fmt(Entry(line))

        if args.json_output:
            json.dump(text, file_out)
            print(file=file_out)
            file_out.flush()
        else:
            if text is not None:
                print(text, file=file_out)
                file_out.flush()

    return 0
