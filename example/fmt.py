#!/usr/bin/env python3

import sys

import jctlfmt
from jctlfmt import Prio


class Formatter(jctlfmt.BaseFormatter):
    def fmt(self, x: jctlfmt.Entry) -> str | None:
        if x.str_uip == 'kernel':
            if x.prio >= Prio.INFO:
                return self.fmt_none(x)
            elif x.prio == Prio.NOTICE and not x.msg.startswith('Linux version '):
                return self.fmt_none(x)

            if x.str_pm.startswith('<5>Linux version '):
                return self.fmt_nopid_msg(x, 'Linux version ...')

        elif x.str_ui == '(myapp.service) myapp':
            if x.prio >= Prio.INFO:
                return self.fmt_none(x)

            return self.fmt_nopid(x)

        return self.fmt_nopid_nomsg(x)


def main(argv: list[str] | None = None) -> int:
    return jctlfmt.exec(Formatter, argv)


if __name__ == '__main__':
    sys.exit(main())
