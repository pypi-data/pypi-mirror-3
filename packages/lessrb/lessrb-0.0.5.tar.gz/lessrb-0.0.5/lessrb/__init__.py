import os
import sys

def run():
    lessbin = os.path.join(os.path.dirname(__file__),
                           'rb', 'bin', 'lessc')
    if not os.access(lessbin, os.X_OK):
        os.chmod(lessbin, 0755)
    os.execv(lessbin, ['lessc'] + sys.argv[1:])

if __name__ == '__main__':
    run()
