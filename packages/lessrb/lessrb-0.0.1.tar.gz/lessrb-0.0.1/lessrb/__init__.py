import os
import sys

def run():
    lessbin = os.path.join(os.path.dirname(__file__),
                           '..', 'rb', 'bin', 'lessc')
    os.execv(lessbin, ['lessc'] + sys.argv[1:])

if __name__ == '__main__':
    run()
