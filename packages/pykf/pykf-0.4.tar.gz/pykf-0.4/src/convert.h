#define isjis(c) (((c)>=0x21 && (c)<=0x7e))
#define iseuc(c) (((c)>=0xa1 && (c)<=0xfe))

#define isgaiji1(c) ((c)>=0xf0 && (c)<=0xf9)
#define isibmgaiji1(c) ((c)>=0xfa && (c)<=0xfc)
#define issjis1(c) (((c)>=0x81 && (c)<=0x9f) || ((c)>=0xe0 && (c)<=0xef) || isgaiji1(c) || isibmgaiji1(c))
#define issjis2(c) ((c)>=0x40 && (c)<=0xfc && (c)!=0x7f)

#define ishankana(c) ((c)>=0xa0 && (c)<=0xdf)

#define isutf8_2byte(c) (0xc0<=c && c <= 0xdf)
#define isutf8_3byte(c) (0xe0<=c && c <= 0xef)
#define isutf8_4byte(c) (0xf0<=c && c <= 0xf7)
#define isutf8_5byte(c) (0xf8<=c && c <= 0xfb)
#define isutf8_6byte(c) (0xfc<=c && c <= 0xfd)
#define isutf8_trail(c) (0x80<=c && c <= 0xbf)

#define utf8_len(c) (isutf8_2byte(c)?2:isutf8_3byte(c)?3:isutf8_4byte(c)?4:isutf8_5byte(c)?5:isutf8_6byte(c)?6:0)
#define CONV_FAILED 0x222e
