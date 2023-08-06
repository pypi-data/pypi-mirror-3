#!/usr/bin/env python

       
class IntStr(object):
    def __init__(self, alphabet, sign_character=None):
        self.alphabet_reverse = dict((c, i) for (i, c) in enumerate(alphabet))
        self.alphabet = alphabet
        self.sign_character = sign_character

    def encode(self, n):
        if n < 0:
            return self.sign_character + self.encode(-n)
        base = len(self.alphabet)
        alphabet = self.alphabet
        s = []
        while True:
            n, r = divmod(n, base)
            s.append(alphabet[r])
            if n == 0: break
        return ''.join(reversed(s))

    def decode(self, s):
        if s[0] == self.sign_character:
            return -self.decode(s[1:])
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

    intstr = IntStr(ALPHABET,"$")

    s = intstr.encode(-1234567)
    print s 
    print intstr.decode(s)
