# -*- coding:cp932 -*-
from __future__ import nested_scopes

import unittest
from pykf import *

def readfile(fname):
    lines = [l for l in open(fname).readlines() if l[0:1] != '#']
    sjis = [int(l.split(",")[0], 16) for l in lines]
    sjis = "".join([chr(s >> 8)+chr(s & 0xff) for s in sjis])
    euc = [int(l.split(",")[1], 16) for l in lines]
    euc = "".join([chr(s >> 8)+chr(s & 0xff) for s in euc])
    
    return sjis, euc

class test_kf(unittest.TestCase):

    def readtbl(self, fname):
        f = open(fname)
        lines = [l for l in f.readlines() if l[0:1] != '#']
        sjis = [int(l.split(",")[0], 16) for l in lines]
        sjis = "".join([chr(s >> 8)+chr(s & 0xff) for s in sjis])
        euc = [int(l.split(",")[1], 16) for l in lines]
        euc = "".join([chr(s >> 8)+chr(s & 0xff) for s in euc])
        return sjis, euc
        
    def conv(self, sjis):
        euc1 = toeuc(sjis)
        jis1 = tojis(sjis)
        euc2 = toeuc(jis1)
        jis2 = tojis(euc1)
        sjis1 = tosjis(jis1)
        sjis2 = tosjis(euc1)

        for i in range(0, len(sjis), 2):
            s = sjis[i:i+2]
            e1 = sjis1[i:i+2]
            if s != e1:
                print "%s(%x%x) %s(%x%x)" % (s, ord(s[0]), ord(s[1]), e1, ord(e1[0]), ord(e1[1]))


        assert sjis==sjis1
        assert sjis1==sjis2
        assert (max(sjis) < '\x80') or sjis2 != euc1
        assert (max(sjis) < '\x80') or sjis2 != jis1
        assert euc1==euc2
        assert (max(sjis) < '\x80') or euc1 !=jis1
        assert jis1==jis2
        
        assert (max(sjis) < '\x80') or guess(sjis1) == SJIS
        assert (max(sjis) < '\x80') or guess(euc1) == EUC
        assert (max(sjis) < '\x80') or guess(jis1) == JIS


    def testBasic(self):
        sjis = open("./readme.sjis").read()
        self.conv(sjis)
    
    def testHankana(self):
        sjis = open("test/hankana.txt").read()
        self.conv(sjis)

    def testNEC(self):
        sjis, euc = self.readtbl("../misc/nectoeuc.txt")
        assert toeuc(sjis) == euc
        assert toeuc(tojis(sjis)) == euc
        assert tosjis(euc) == sjis
        
    def testNECIBM(self):
        sjis, euc = self.readtbl("../misc/necibmtoeuc.txt")
        assert toeuc(sjis) == euc
        assert toeuc(tojis(sjis)) == euc
        assert tosjis(euc) == sjis
        
    def testIBM(self):
        sjis, euc = self.readtbl("../misc/ibmtoeuc.txt")
        assert toeuc(sjis) == euc
        assert toeuc(tojis(sjis)) == euc
        assert tosjis(euc) != sjis
        assert unicode(tosjis(euc), "cp932") == unicode(sjis, "cp932")

    def testGaiji(self):
        sjis = "".join([chr(x)+chr(y) for x in range(0xf0, 0xfa) for y in range(0x40, 0x7e)])
        assert tosjis(toeuc(sjis)) == "\x81\xac" * (len(sjis)/2)
        assert tosjis(tojis(sjis)) == "\x81\xac" * (len(sjis)/2)
        
        sjis = "".join([chr(x)+chr(y) for x in range(0xf0, 0xfa) for y in range(0x80, 0xfd)])
        assert tosjis(toeuc(sjis)) == "\x81\xac" * (len(sjis)/2)
        assert tosjis(tojis(sjis)) == "\x81\xac" * (len(sjis)/2)
    
    def testUtf8(self):
        utf8 = "\xe3\x81\x82\xe3\x81\x84\xe3\x81\x86\xe3\x81\x88\xe3\x81\x8a"
        assert guess(utf8) == UTF8
        assert guess("\xef\xbb\xbf") == UTF8

    def testJisNormalize(self):
        sjis = "\x82\xa0"
        jis = tojis(sjis, SJIS)
        assert jis[-3:] == '\x1b(B'
        assert tosjis(jis, JIS) == sjis

        euc = toeuc("\x82\xa0", SJIS)
        jis = tojis(euc, EUC)
        assert jis[-3:] == '\x1b(B'
        assert toeuc(jis, JIS) == euc

class test_zerolen(unittest.TestCase):
    def test_zerolen(self):
        src = ""
        assert tosjis(src) == ""
        assert toeuc(src) == ""
        assert tojis(src) == ""

        assert tosjis(src, EUC) == ""
        assert tosjis(src, JIS) == ""
        assert tosjis("\x1b(I", JIS) == ""
        assert toeuc(src, SJIS) == ""
        assert toeuc(src, JIS) == ""
        assert toeuc("\x1b(I", JIS) == ""
        assert tojis(src, SJIS) == ""
        assert tojis(src, EUC) == ""

class test_split(unittest.TestCase):
    def test_split(self):
        ascii = "abcdefg"
        sjis = "abc\x82\xa0\x82\xa1\x82\xa2\xb1\xb2\xb3abc\x82\xa0"

        assert "".join(split(ascii)) == ascii
        assert "".join(split(sjis)) == sjis
        assert "".join(split(toeuc(sjis))) == toeuc(sjis)
        assert "".join(split(tojis(sjis))) == tojis(sjis)


class test_tohalf(unittest.TestCase):
    sjis = 'abc\x83A\x83C\x83E\x83G\x83I\x83K\x83M\x83O\x83Q\x83S\x82`\x82a\x82b'
    sjis_half = 'abc\xb1\xb2\xb3\xb4\xb5\xb6\xde\xb7\xde\xb8\xde\xb9\xde\xba\xde\x82`\x82a\x82b'
    all_half = '\xa1\xa2\xa3\xa4\xa5\xa7\xb1\xa8\xb2\xa9\xb3\xaa\xb4\xab\xb5\xb6\xb6\xde\xb7\xb7\xde\xb8\xb8\xde\xb9\xb9\xde\xba\xba\xde\xbb\xbb\xde\xbc\xbc\xde\xbd\xbd\xde\xbe\xbe\xde\xbf\xbf\xde\xc0\xc0\xde\xc1\xc1\xde\xaf\xc2\xc2\xde\xc3\xc3\xde\xc4\xc4\xde\xc5\xc6\xc7\xc8\xc9\xca\xca\xde\xca\xdf\xcb\xcb\xde\xcb\xdf\xcc\xcc\xde\xcc\xdf\xcd\xcd\xde\xcd\xdf\xce\xce\xde\xce\xdf\xcf\xd0\xd1\xd2\xd3\xac\xd4\xad\xd5\xae\xd6\xd7\xd8\xd9\xda\xdb\x83\x8e\xdc\x83\x90\x83\x91\xa6\xdd\xb3\xde\x83\x95\xb0'
    all_full = "\x81B\x81u\x81v\x81A\x81E\x83@\x83A\x83B\x83C\x83D\x83E\x83F\x83G\x83H\x83I\x83J\x83K\x83L\x83M\x83N\x83O\x83P\x83Q\x83R\x83S\x83T\x83U\x83V\x83W\x83X\x83Y\x83Z\x83[\x83\\\x83]\x83^\x83_\x83`\x83a\x83b\x83c\x83d\x83e\x83f\x83g\x83h\x83i\x83j\x83k\x83l\x83m\x83n\x83o\x83p\x83q\x83r\x83s\x83t\x83u\x83v\x83w\x83x\x83y\x83z\x83{\x83|\x83}\x83~\x83\x80\x83\x81\x83\x82\x83\x83\x83\x84\x83\x85\x83\x86\x83\x87\x83\x88\x83\x89\x83\x8a\x83\x8b\x83\x8c\x83\x8d\x83\x8e\x83\x8f\x83\x90\x83\x91\x83\x92\x83\x93\x83\x94\x83\x95\x81["

    def test_sjis(self):
        assert tohalf_kana(self.sjis, SJIS) == self.sjis_half
        assert tohalf_kana(self.all_full, SJIS) == self.all_half
        
    def test_euc(self):
        e = toeuc(self.sjis, SJIS)
        assert tohalf_kana(e, EUC) == toeuc(self.sjis_half, SJIS)

        e = toeuc(self.all_full, SJIS)
        assert tohalf_kana(e, EUC) == toeuc(self.all_half, SJIS)


class test_tofull(unittest.TestCase):
    sjis = 'abc\x83A\x83C\x83E\x83G\x83I\x83K\x83M\x83O\x83Q\x83S\x82`\x82a\x82b'
    sjis_half = 'abc\xb1\xb2\xb3\xb4\xb5\xb6\xde\xb7\xde\xb8\xde\xb9\xde\xba\xde\x82`\x82a\x82b'
    all_half = '\xa1\xa2\xa3\xa4\xa5\xa7\xb1\xa8\xb2\xa9\xb3\xaa\xb4\xab\xb5\xb6\xb6\xde\xb7\xb7\xde\xb8\xb8\xde\xb9\xb9\xde\xba\xba\xde\xbb\xbb\xde\xbc\xbc\xde\xbd\xbd\xde\xbe\xbe\xde\xbf\xbf\xde\xc0\xc0\xde\xc1\xc1\xde\xaf\xc2\xc2\xde\xc3\xc3\xde\xc4\xc4\xde\xc5\xc6\xc7\xc8\xc9\xca\xca\xde\xca\xdf\xcb\xcb\xde\xcb\xdf\xcc\xcc\xde\xcc\xdf\xcd\xcd\xde\xcd\xdf\xce\xce\xde\xce\xdf\xcf\xd0\xd1\xd2\xd3\xac\xd4\xad\xd5\xae\xd6\xd7\xd8\xd9\xda\xdb\x83\x8e\xdc\x83\x90\x83\x91\xa6\xdd\xb3\xde\x83\x95\xb0'
    all_full = "\x81B\x81u\x81v\x81A\x81E\x83@\x83A\x83B\x83C\x83D\x83E\x83F\x83G\x83H\x83I\x83J\x83K\x83L\x83M\x83N\x83O\x83P\x83Q\x83R\x83S\x83T\x83U\x83V\x83W\x83X\x83Y\x83Z\x83[\x83\\\x83]\x83^\x83_\x83`\x83a\x83b\x83c\x83d\x83e\x83f\x83g\x83h\x83i\x83j\x83k\x83l\x83m\x83n\x83o\x83p\x83q\x83r\x83s\x83t\x83u\x83v\x83w\x83x\x83y\x83z\x83{\x83|\x83}\x83~\x83\x80\x83\x81\x83\x82\x83\x83\x83\x84\x83\x85\x83\x86\x83\x87\x83\x88\x83\x89\x83\x8a\x83\x8b\x83\x8c\x83\x8d\x83\x8e\x83\x8f\x83\x90\x83\x91\x83\x92\x83\x93\x83\x94\x83\x95\x81["

    def test_sjis(self):
#        print tofull_kana(self.sjis_half, SJIS)
        assert tofull_kana(self.sjis_half, SJIS) == self.sjis
        assert tofull_kana(self.all_half, SJIS) == self.all_full

    def test_euc(self):
        e = toeuc(self.sjis_half, SJIS)
        assert tofull_kana(e, EUC) == toeuc(self.sjis, SJIS)

        e = toeuc(self.all_half, SJIS)
        assert tofull_kana(e, EUC) == toeuc(self.all_full, SJIS)
        
class test_strict(unittest.TestCase):
    def test_sjis(self):
        s1 = "あいうえお"
        assert guess(s1, True) == SJIS
        assert guess(s1, False) == SJIS
        s2 = "あいうえおかきくけこ"*1000 + "\xf0\x01"
        assert guess(s2, False) == SJIS
        assert guess(s2, True) == ERROR
        
    def test_euc(self):
        s1 = toeuc("あいうえお", SJIS)
        assert guess(s1, True) == EUC
        assert guess(s1, False) == EUC
        s2 = toeuc("あいうえおかきくけこ"*1000 + "\xf0\x01", SJIS)
        assert guess(s2, False) == EUC
        assert guess(s2, True) == ERROR
        
    def test_jis(self):
        s1 = tojis("あいうえお", SJIS)
        assert guess(s1, True) == JIS
        assert guess(s1, False) == JIS
        s2 = tojis("あいうえおかきくけこ" + "\xf0\x01", SJIS)
        assert guess(s2, False) == UNKNOWN
        assert guess(s2, True) == ERROR
        
    def test_flag(self):
        setstrict(True)
        assert getstrict()
        
        setstrict(False)
        assert not getstrict()

        s2 = "あいうえおかきくけこ"*1000 + "\xf0\x01"
        assert guess(s2) == SJIS
        setstrict(True)
        assert guess(s2) == ERROR
        setstrict(False)


class test_j0208(unittest.TestCase):
    def test_sjis(self):
        s1 = "㈱"

        assert tojis(s1, SJIS, j0208=False) == '\x1b$(O-j\x1b(B'
        assert tojis(s1, SJIS, j0208=True) == '\x1b$B-j\x1b(B'
        
        assert tosjis(tojis(s1, SJIS, j0208=False)) == s1
        assert tosjis(tojis(s1, SJIS, j0208=True)) == s1

if __name__ == '__main__':
    unittest.main()


