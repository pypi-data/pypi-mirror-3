import sys
from books import ubook


coding = sys.getfilesystemencoding()
if not len(sys.argv) == 3:
    print "Form: python ubook.py 'Title of Book', 'Book Author'"
    sys.exit(1)

print ubook(sys.argv[1].decode(coding), sys.argv[2].decode(coding))




