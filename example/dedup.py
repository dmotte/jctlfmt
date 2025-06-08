#!/usr/bin/env python3

import re
import sys

import jctlfmt


def main():
    seen = []

    for line in sys.stdin:
        x = jctlfmt.Entry(line)

        if re.fullmatch(r'^session-[0-9]+\.scope$', x.unit):
            uniqstr = f'(session-123.scope) {x.ident}: {x.str_pm}'
        else:
            uniqstr = f'{x.str_ui}: {x.str_pm}'

        if uniqstr not in seen:
            seen.append(uniqstr)
            sys.stdout.write(line)

    return 0


if __name__ == '__main__':
    sys.exit(main())
