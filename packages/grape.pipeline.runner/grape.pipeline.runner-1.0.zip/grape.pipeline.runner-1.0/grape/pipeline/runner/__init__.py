"""
Runs Grape pipelines.
"""
import sys
import argparse
import logging

from grape.pipeline.runner.runner import Runner


def main():
    print "start"
    desc = 'Runs configured Grape pipelines'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--version', action='store_true',
                      default=False, help='Displays version and exits.')

    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    runner = Runner()
    runner.start()
    runner.stop()
    sys.exit(0)


if __name__ == '__main__':
    main()
