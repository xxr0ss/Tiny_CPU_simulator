import sys
import sim

def usage():
    print("Usage: [python3] ./main.py [-d] progname")

def main():
    verbose = False
    debug = False
    argc = len(sys.argv)
    if (argc == 1):
        usage()
        exit()
    if (sys.argv[1][0] == '-'):
        if (argc == 2):
            usage()
            exit()
        filename = sys.argv[2]
        if (sys.argv[1][1] == 'v'):
            verbose = True
        elif (sys.argv[1][1] == 'd'):
            debug = True
            verbose = True
        else:
            usage()
            exit()
    else:
        verbose = 0
        filename = sys.argv[1]
    sim.verbose = verbose
    sim.debug = debug
    sim.run(filename)


if __name__ == '__main__':
    main()