#!/usr/bin/env python

       
class IntStr(object):
    def __init__(self, alphabet):
        self.alphabet_reverse = dict((c, i) for (i, c) in enumerate(alphabet))
        self.alphabet = alphabet

    def encode(self, n):
        base = len(self.alphabet)
        alphabet = self.alphabet
        s = []
        while True:
            n, r = divmod(n, base)
            s.append(alphabet[r])
            if n == 0: break
        return ''.join(reversed(s))

    def decode(self, s):
        base = len(self.alphabet)
        alphabet_reverse = self.alphabet_reverse
        n = 0
        for c in s:
            n = n * base + alphabet_reverse[c]
        return n

if __name__ == '__main__':
    import string

    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
               string.digits + '-_'

    intstr = IntStr(ALPHABET)

    s = intstr.encode(1234567)
    print s 
    print intstr.decode(s)
    from model._db import mc

    ALPHABET = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'

    x = IntStr(ALPHABET)
    num_encode = x.encode
    num_decode = x.decode
    for i in range(10000):
        mc.set(num_encode(i),i)
        print num_decode(num_encode(i))

    for i in range(10000):
        if type(mc.get(num_encode(i))) != int:
            print i
    for i in range(10000):
        mc.delete(num_encode(i))
    for i in range(10000):
        if mc.get(num_encode(i)) is not None:
            print i


