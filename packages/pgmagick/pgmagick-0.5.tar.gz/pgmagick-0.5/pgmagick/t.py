import sys

for line in open(sys.argv[1]):
    line = line.strip()
    print line, "Class"
    print "-" * (len(line) + 6)
    print ".. autoclass::", line
    print "   :members:"
    print "   :inherited-members:"
    print ""
