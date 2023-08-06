
def kill(files):
    for f in files:
        try:
            src = open(f, 'r')
        except IOError:
            print "FAIL: Can't open file %s" % f
        else:
            try:
                sink = open('deadbangs-%s' % f, 'w')
            except IOError:
                print "FAIL: Can't write file 'deadbangs-%s'" % f
                src.close()
            else:
                for line in src:
                    bang_split = line.split('!')
                    if (len(bang_split) > 1 and  # there is a bang
                        len(bang_split[0]) > 0): # there is content before it
                        sink.write(bang_split[0] + '\n')
                        sink.write("!" + "!".join(bang_split[1:]))
                    else:
                        sink.write(line)
                src.close()
                sink.close()
