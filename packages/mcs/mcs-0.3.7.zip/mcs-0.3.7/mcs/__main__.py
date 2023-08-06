#!/usr/bin/python
from . import Mcs


def main():
    mcs = Mcs()
    try:
        raise SystemExit(mcs.main())
    except KeyboardInterrupt:
        print "-- interrupted --"

if __name__ == "__main__":
    main()
