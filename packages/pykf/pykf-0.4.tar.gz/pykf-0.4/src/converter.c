/*********************************************************************

Japanese Kanji filter module
    Copyright (c) 2002, Atsuo Ishimoto.  All rights reserved. 

Permission to use, copy, modify, and distribute this software and its 
documentation for any purpose and without fee is hereby granted, provided that
the above copyright notice appear in all copies and that both that copyright 
notice and this permission notice appear in supporting documentation, and that
the name of Atsuo Ishimoto not be used in advertising or publicity pertaining 
to distribution of the software without specific, written prior permission. 

ATSUO ISHIMOTO DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, 
INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO
EVENT SHALL ATSUO ISHIMOTO BE LIABLE FOR ANY SPECIAL, INDIRECT OR 
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE. 

---------------------------------------------------------------------
This module is besed on kf.c written by Haruhiko Okumura.
    Copyright (c) 1995-2000 Haruhiko Okumura
    This file may be freely modified/redistributed.

Original kf.c:
    http://www.matsusaka-u.ac.jp/~okumura/kf.html

*********************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <string.h>
#include <assert.h>

#include "pykf.h"

#if defined(_MSC_VER)
#define LOCAL_INLINE __inline static
#endif

#if !defined(__cplusplus) && !defined(inline)
#ifdef __GNUC__
#define LOCAL_INLINE __inline static
#endif
#endif

#if !defined(LOCAL_INLINE)
#define LOCAL_INLINE static
#endif

#include "convert.h"




int guess(int imax, unsigned char buf[], int strict)
{
    int i, n;
    int ascii, euc, sjis, utf8, bad_euc, bad_sjis, bad_utf8;
    int jis, hankana;
    int sjis_error, euc_error, utf8_error;
    
    ascii = 1;
    bad_euc=euc=0; 
    bad_sjis=sjis=0;
    bad_utf8 = utf8=0;
    jis = 0;
    sjis_error = euc_error = utf8_error = 0;
    
    /* check BOM */
    if (imax >= 2) {
        if (buf[0] == 0xff && buf[1] == 0xfe) {
            return UTF16_LE;
        }
        else if (buf[0] == 0xfe && buf[1] == 0xff) {
            return UTF16_BE;
        }
    }
    if (imax >= 3 && !memcmp(buf, "\xef\xbb\xbf", 3)) {
        return UTF8;
    }

    // check SJIS
    hankana = 0;
    for (i = 0; i < imax; i++) {

        if (buf[i] >= 0x80) {
            ascii = 0;
        }

        if (buf[i] == 0x1b) {
            jis= 1;
        }
        
        if (buf[i] == 0x8e ) {
            // looks like euc.
            if (i + 2 < imax) {
                if (buf[i+2]==0x8e && ishankana(buf[i+1])) {
                    bad_sjis += 1;
                }
            }
        }

        if (ishankana(buf[i])) {
            sjis += 0x10/2-1;
            hankana++;
        }
        else {
            if (hankana == 1) {
                // single halfwidth-kana is bad sign.
                bad_sjis++;
            }
            hankana = 0;

            if (issjis1(buf[i])) {
                if (i+1 >= imax) {
                    if (strict) {
                        sjis_error = 1;
                        break;
                    }
                    bad_sjis+=0x100;
                }
                else if (issjis2(buf[i+1])) {
                    sjis += 0x10;
                    i++;
                }
                else {
                    if (strict) {
                        sjis_error = 1;
                        break;
                    }
                    bad_sjis += 0x100;
                }
            }
            else if (buf[i] >= 0x80) {
                if (strict) {
                    sjis_error = 1;
                    break;
                }
                bad_sjis += 0x100;          
            }
        }
    }

    if (ascii && jis) {
        return JIS;
    }

    if (ascii) {
        return ASCII;
    }

    // check EUC-JP
    hankana=0;
    for (i = 0; i < imax; i++) {
        if (buf[i] == 0x8e) {
            if (i+1 >= imax) {
                if (strict) {
                    euc_error = 1;
                    break;
                }
                bad_euc += 0x100;
            }
            else if (ishankana(buf[i+1])) {
                euc+=10; 
                i++;
                hankana++;
            }
            else {
                if (strict) {
                    euc_error = 1;
                    break;
                }
                bad_euc += 0x100;
            }
        }
        else {
            if (hankana == 1) {
                bad_euc++;
            }
            hankana = 0;
            if (iseuc(buf[i])) {
                if (i+1 >= imax) {
                    if (strict) {
                        euc_error = 1;
                        break;
                    }
                    bad_euc+=0x100;
                }
                else if (iseuc(buf[i+1])) {
                    i++;
                    euc+=0x10;
                }
                else {
                    if (strict) {
                        euc_error = 1;
                        break;
                    }
                    bad_euc+=0x100;
                }
            }
            else if (buf[i] == 0x8f) {
                if (i+2 >= imax) {
                    if (strict) {
                        euc_error = 1;
                        break;
                    }
                    bad_euc+=0x100;
                }
                else if (iseuc(buf[i+1]) && iseuc(buf[i+2])) {
                    i+=2;
                    euc+=0x10;
                }
                else {
                    if (strict) {
                        euc_error = 1;
                        break;
                    }
                    bad_euc+=100;
                }
            }
            else if (buf[i] >= 0x80) {
                if (strict) {
                    euc_error = 1;
                    break;
                }
                bad_euc+=0x100;
            }
        }
    }

    // check UTF-8
    for (i = 0; i < imax; i++) {
        int c_len;
        c_len = utf8_len(buf[i]);
        if (c_len) {
            if (i+c_len-1 >= imax) {
                if (strict) {
                    utf8_error = 1;
                    break;
                }
                bad_utf8 += 1000;
            }
            i++;
            for (n=0; n < c_len-1; n++) {
                if (!isutf8_trail(buf[i+n])) {
                    if (strict) {
                        utf8_error = 1;
                    }
                    else {
                        bad_utf8 += 1000;
                    }
                    break;
                }
            }

            if (utf8_error) {
                break;
            }

            if (n == (c_len-1)) {
                /* no error */
                utf8 += (int)(0x10 * c_len/2.0+1); /* prefer utf-8 over SJIS/EUC a bit....*/
                i += (c_len-2);
            }
        } else if (buf[i] >= 0x80) {
            if (strict) {
                utf8_error = 1;
                break;
            }
            bad_utf8 += 1000;
        }
    }
/*
    printf("sjis_error:%d euc_error:%d, utf8_error:%d\n", sjis_error, euc_error, utf8_error);
    printf("sjis:%d euc:%d, utf8:%d\n", sjis, euc, utf8);
    printf("bad_sjis:%d bad_euc:%d, bad_utf8:%d\n", bad_sjis, bad_euc, bad_utf8);
*/

    if (sjis_error && euc_error && utf8_error) {
        return ERROR;
    }
    
    if (sjis_error) {
        if (euc_error) {
            return UTF8;
        }
        if (utf8_error) {
            return EUC;
        }
        if (euc-bad_euc > utf8-bad_utf8)
            return EUC;
        else if (euc-bad_euc < utf8-bad_utf8)
            return UTF8;
    }

    if (euc_error) {
        if (sjis_error) {
            return UTF8;
        }
        if (utf8_error) {
            return SJIS;
        }
        if (sjis-bad_sjis > utf8-bad_utf8)
            return SJIS;
        else if (sjis-bad_sjis < utf8-bad_utf8)
            return UTF8;
    }
    
    if (utf8_error) {
        if (sjis_error) {
            return EUC;
        }
        if (euc_error) {
            return SJIS;
        }
        if (sjis-bad_sjis > euc-bad_euc)
            return SJIS;
        else
            return EUC;
    }
    
    if (sjis-bad_sjis > euc-bad_euc) {
        if (sjis-bad_sjis > utf8-bad_utf8)
            return SJIS;
        else if (sjis-bad_sjis < utf8-bad_utf8)
            return UTF8;
    }

    if (sjis-bad_sjis < euc-bad_euc) {
        if (euc-bad_euc > utf8-bad_utf8)
            return EUC;
        else if (euc-bad_euc < utf8-bad_utf8)
            return UTF8;
    }
    return UNKNOWN;
}

LOCAL_INLINE
void jis_to_sjis2(unsigned char *ph, unsigned char *pl);

LOCAL_INLINE
int isjis0213(unsigned char h, unsigned char l) {
    unsigned int *p;
    unsigned int jis = (h << 8 | l) & 0xffff;

    for (p=tbl_jis0213; *(p+2) < jis; p+=2);

    if (*p <= jis && (jis < (p[0] + p[1]))) {
        return 1;
    }
    else {
        return 0;
    }
}


LOCAL_INLINE 
int mskanji_to_jis(unsigned char *ph, unsigned char *pl) {
    int *p;
    int sjis = (*ph << 8 | *pl) & 0xffff;

    if (isgaiji1(*ph)) {
        *ph = (CONV_FAILED >> 8) & 0xff;
        *pl = CONV_FAILED & 0xff;
        return 1;
    }
    
    for (p=tbl_sjis2jis; *p < sjis; p+=2);
    
    if (*p == sjis) {
        *ph = (*(p+1)) >> 8;
        *pl = (*(p+1)) & 0xff;
        return 1;
    }
    return 0;
}

LOCAL_INLINE
void sjis_to_jis(unsigned char *ph, unsigned char *pl)
{
    if (*ph <= 0x9f) {
        if (*pl < 0x9f)
            *ph = (*ph << 1) - 0xe1;
        else
            *ph = (*ph << 1) - 0xe0;
    } else {
        if (*pl < 0x9f)  
            *ph = (*ph << 1) - 0x161;
        else
            *ph = (*ph << 1) - 0x160;
    }
    if (*pl < 0x7f) 
        *pl -= 0x1f;
    else if (*pl < 0x9f) 
        *pl -= 0x20;
    else
        *pl -= 0x7e;
}

LOCAL_INLINE
void sjis_to_jis2(unsigned char *ph, unsigned char *pl)
{
    if (mskanji_to_jis(ph, pl))
        return;
    else
        sjis_to_jis(ph, pl);
}


LOCAL_INLINE
void jis_to_sjis(unsigned char *ph, unsigned char *pl)
{
    if (*ph & 1) {
        if (*pl < 0x60) 
            *pl += 0x1f;
        else             
            *pl += 0x20;
    } else
        *pl += 0x7e;

    if (*ph < 0x5f)
        *ph = (*ph + 0xe1) >> 1;
    else
        *ph = (*ph + 0x161) >> 1;
}


LOCAL_INLINE 
int jis_to_mskanji(unsigned char *ph, unsigned char *pl) {
    int *p;
    int jis = (*ph << 8 | *pl) & 0xffff;

    for (p=tbl_jis2sjis; *p < jis; p+=2);
    
    if (*p == jis) {
        *ph = (*(p+1)) >> 8;
        *pl = (*(p+1)) & 0xff;
        return 1;
    }
    return 0;
}



LOCAL_INLINE
void jis_to_sjis2(unsigned char *ph, unsigned char *pl)
{
    if (jis_to_mskanji(ph, pl))
        return;
    else 
        jis_to_sjis(ph, pl);
}





int sjistojis(int len, unsigned char *buf, unsigned char **ret, int *retlen, int j0208)
{
    unsigned char c, d;
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;
    enum {NORMAL, KANJI, HANKANA, JIS0213} mode = NORMAL;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }


    for (pos = 0; pos < len; pos++) {
        tmplen = 0;
        if (issjis1(buf[pos]) && (pos + 1 < len) && issjis2(buf[pos+1])) {
            c = buf[pos];
            d = buf[pos+1];
            pos += 1;
            sjis_to_jis2(&c, &d);

            if (j0208 || !isjis0213(c, d)) {
                if (mode != KANJI) {
                    mode = KANJI;
                    tmp[tmplen++] = 0x1b;
                    tmp[tmplen++] = '$';
                    tmp[tmplen++] = 'B';
                }
            }
            else {
                if (mode != JIS0213) {
                    mode = JIS0213;
                    tmp[tmplen++] = 0x1b;
                    tmp[tmplen++] = '$';
                    tmp[tmplen++] = '(';
                    tmp[tmplen++] = 'O';
                }
            }
            tmp[tmplen++] = c;
            tmp[tmplen++] = d;
        } else if (ishankana(buf[pos])) {
            if (mode != HANKANA) {
                mode = HANKANA;
                tmp[tmplen++] = 0x1b;
                tmp[tmplen++] = '(';
                tmp[tmplen++] = 'I';
            }
            tmp[tmplen++] = buf[pos] & 0x7f;
        } else {
            if (mode != NORMAL) {
                mode = NORMAL;
                tmp[tmplen++] = 0x1b;
                tmp[tmplen++] = '(';
                tmp[tmplen++] = 'B';
            }
            tmp[tmplen++] = buf[pos];
        }

        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    if (mode != NORMAL) {
        if (retpos + 3 > *retlen) {
            *retlen = retpos + 3;
            newbuf = realloc(*ret, *retlen);
            if (!newbuf) {
                free(*ret);
                return 0;
            }
            *ret = newbuf;
        }
        *(*ret + retpos) = 0x1b;
        *(*ret + retpos+1) = '(';
        *(*ret + retpos+2) = 'B';
        retpos += 3;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;
    return 1;
}

int euctojis(int len, unsigned char *buf, unsigned char **ret, int *retlen, int j0208)
{
    unsigned char c, d;
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;
    enum {NORMAL, KANJI, HANKANA, JIS0213} mode = NORMAL;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen = 0;
        if (iseuc(buf[pos]) && (pos + 1 < len) && iseuc(buf[pos+1])) {
            c = buf[pos]  & 0x7f;
            d = buf[pos+1]  & 0x7f;
            pos += 1;

            if (j0208 || !isjis0213(c, d)) {
                if (mode != KANJI) {
                    mode = KANJI;
                    tmp[tmplen++] = 0x1b;
                    tmp[tmplen++] = '$';
                    tmp[tmplen++] = 'B';
                }
            }
            else {
                if (mode != JIS0213) {
                    mode = JIS0213;
                    tmp[tmplen++] = 0x1b;
                    tmp[tmplen++] = '$';
                    tmp[tmplen++] = '(';
                    tmp[tmplen++] = 'O';
                }
            }
            tmp[tmplen++] = c;  
            tmp[tmplen++] = d;
        } else if ((buf[pos] == 0x8e) && (pos + 1 < len) && ishankana(buf[pos+1])) {


            if (mode != HANKANA) {
                mode = HANKANA;
                tmp[tmplen++] = 0x1b;
                tmp[tmplen++] = '(';
                tmp[tmplen++] = 'I';
            }
            tmp[tmplen++] = buf[pos+1] & 0x7f;
            pos += 1;

        } else {
            if (mode != NORMAL) {
                mode = NORMAL;
                tmp[tmplen++] = 0x1b;
                tmp[tmplen++] = '(';
                tmp[tmplen++] = 'B';
            }
            tmp[tmplen++] = buf[pos];
        }

        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }
    
    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    if (mode != NORMAL) {
        if (retpos + 3 > *retlen) {
            *retlen = retpos + 3;
            newbuf = realloc(*ret, *retlen);
            if (!newbuf) {
                free(*ret);
                return 0;
            }
            *ret = newbuf;
        }
        *(*ret + retpos) = 0x1b;
        *(*ret + retpos+1) = '(';
        *(*ret + retpos+2) = 'B';
        retpos += 3;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;
    return 1;
}


int sjistoeuc(int len, unsigned char *buf, unsigned char **ret, int *retlen)
{
    unsigned char c, d;
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen=0;
        
        if (issjis1(buf[pos]) && (pos + 1 < len) && issjis2(buf[pos+1])) {
            c = buf[pos];
            d = buf[pos+1];
            pos += 1;
            
            sjis_to_jis2(&c, &d);
            tmp[tmplen++] = c | 0x80;
            tmp[tmplen++] = d | 0x80;
        } else if (ishankana(buf[pos])) {
            tmp[tmplen++] = '\x8e';
            tmp[tmplen++] = buf[pos];
        } else {
            tmp[tmplen++] = buf[pos];
        }

        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;

    return 1;
}

int jistoeuc(int len, unsigned char *buf, unsigned char **ret, int *retlen)
{
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;

    enum {NORMAL, KANJI, HANKANA} mode = NORMAL;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen=0;
        
        if ((pos + 2 < len) && 
            (!memcmp(buf+pos, "\x1b$@", 3) || 
             !memcmp(buf+pos, "\x1b$B", 3))) {

            mode = KANJI;
            pos += 2;
        }
        else if ((pos + 3 < len) && !memcmp(buf+pos, "\x1b$(O", 4)) {
            mode = KANJI;
            pos += 3;
        }
        else if ((pos + 2 < len) && 
                (!memcmp(buf+pos, "\x1b(B", 3) || 
                 !memcmp(buf+pos, "\x1b(J", 3))) {

            mode = NORMAL;
            pos += 2;
        }
        else if ((pos + 2 < len) && !memcmp(buf+pos, "\x1b(I", 3)) {
            mode = HANKANA;
            pos += 2;
        }
        else if (buf[pos] == '\x0e') {
            mode = HANKANA;
        }
        else if (buf[pos] == '\x0f') {
            mode = NORMAL;
        }
        else if (mode == KANJI && isjis(buf[pos]) && (pos+1 < len) && isjis(buf[pos+1])) {
            tmp[tmplen++] = buf[pos] | 0x80;
            tmp[tmplen++] = buf[pos+1] | 0x80;
            pos++;
        } else if (mode == HANKANA && buf[pos] >= 0x20 && buf[pos] <= 0x5f) {
            tmp[tmplen++] = '\x8e';
            tmp[tmplen++] = buf[pos] | 0x80;
        } else {
            tmp[tmplen++] = buf[pos];
        }
        
        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;
    return 1;
}


int jistosjis(int len, unsigned char *buf, unsigned char **ret, int *retlen)
{
    unsigned char c, d;
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;

    enum {NORMAL, KANJI, HANKANA} mode = NORMAL;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen=0;
        
        if ((pos + 2 < len) && 
            (!memcmp(buf+pos, "\x1b$@", 3) || 
             !memcmp(buf+pos, "\x1b$B", 3))) {

            mode = KANJI;
            pos += 2;
        }
        else if ((pos + 3 < len) && !memcmp(buf+pos, "\x1b$(O", 4)) {
            mode = KANJI;
            pos += 3;
        }
        else if ((pos + 2 < len) && 
                (!memcmp(buf+pos, "\x1b(B", 3) || 
                 !memcmp(buf+pos, "\x1b(J", 3))) {

            mode = NORMAL;
            pos += 2;
        }
        else if ((pos + 2 < len) && !memcmp(buf+pos, "\x1b(I", 3)) {
            mode = HANKANA;
            pos += 2;
        }
        else if (buf[pos] == '\x0e') {
            mode = HANKANA;
        }
        else if (buf[pos] == '\x0f') {
            mode = NORMAL;
        }
        else if (mode == KANJI && isjis(buf[pos]) && (pos+1 < len) && isjis(buf[pos+1])) {
            c = buf[pos];
            d = buf[pos+1];
            pos++;

            jis_to_sjis2(&c, &d);
            tmp[tmplen++] = c;
            tmp[tmplen++] = d;
        } else if (mode == HANKANA && buf[pos] >= 0x20 && buf[pos] <= 0x5f) {
            tmp[tmplen++] = buf[pos] | 0x80;
        } else {
            tmp[tmplen++] = buf[pos];
        }
        
        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;
    return 1;
}

int euctosjis(int len, unsigned char *buf, unsigned char **ret, int *retlen)
{
    unsigned char c, d;
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen=0;
        
        if (iseuc(buf[pos]) && (pos + 1 < len) && iseuc(buf[pos+1])) {
            c = buf[pos] & 0x7f;
            d = buf[pos+1] & 0x7f;
            pos += 1;
            
            jis_to_sjis2(&c, &d);
            tmp[tmplen++] = c;
            tmp[tmplen++] = d;
        } else if ((buf[pos] == 0x8e) && (pos + 1 < len) && ishankana(buf[pos+1])) {
            tmp[tmplen++] = buf[pos+1];
            pos++;
        } else {
            tmp[tmplen++] = buf[pos];
        }

        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;
    return 1;
}

static const char *s_h_kana[] = {
"\xdd", "\xdc", "\xdb", "\xda", "\xd9", "\xd8", "\xd7", "\xd6", "\xd5", "\xd4",
"\xd3", "\xd2", "\xd1", "\xd0", "\xcf", "\xce\xdf", "\xce\xde", "\xce", "\xcd\xdf",
"\xcd\xde", "\xcd", "\xcc\xdf", "\xcc\xde", "\xcc", "\xcb\xdf", "\xcb\xde",
"\xcb", "\xca\xdf", "\xca\xde", "\xca", "\xc9", "\xc8", "\xc7", "\xc6", "\xc5",
"\xc4\xde", "\xc4", "\xc3\xde", "\xc3", "\xc2\xde", "\xc2", "\xc1\xde", "\xc1",
"\xc0\xde", "\xc0", "\xbf\xde", "\xbf", "\xbe\xde", "\xbe", "\xbd\xde", "\xbd",
"\xbc\xde", "\xbc", "\xbb\xde", "\xbb", "\xba\xde", "\xba", "\xb9\xde", "\xb9",
"\xb8\xde", "\xb8", "\xb7\xde", "\xb7", "\xb6\xde", "\xb6", "\xb5", "\xb4", "\xb3\xde", 
"\xb3", "\xb2", "\xb1", "\xb0", "\xaf", "\xae", "\xad", "\xac", "\xab",
"\xaa", "\xa9", "\xa8", "\xa7", "\xa6", "\xa5", "\xa4", "\xa3", "\xa2", "\xa1", NULL};

static const unsigned char **h_kana = (const unsigned char **)s_h_kana;

static const char *s_euc_h_kana[] = {
"\x8e\xdd", "\x8e\xdc", "\x8e\xdb", "\x8e\xda", "\x8e\xd9", "\x8e\xd8", "\x8e\xd7", "\x8e\xd6", "\x8e\xd5", "\x8e\xd4",
"\x8e\xd3", "\x8e\xd2", "\x8e\xd1", "\x8e\xd0", "\x8e\xcf", "\x8e\xce\x8e\xdf", "\x8e\xce\x8e\xde", "\x8e\xce", "\x8e\xcd\x8e\xdf",
"\x8e\xcd\x8e\xde", "\x8e\xcd", "\x8e\xcc\x8e\xdf", "\x8e\xcc\x8e\xde", "\x8e\xcc", "\x8e\xcb\x8e\xdf", "\x8e\xcb\x8e\xde",
"\x8e\xcb", "\x8e\xca\x8e\xdf", "\x8e\xca\x8e\xde", "\x8e\xca", "\x8e\xc9", "\x8e\xc8", "\x8e\xc7", "\x8e\xc6", "\x8e\xc5",
"\x8e\xc4\x8e\xde", "\x8e\xc4", "\x8e\xc3\x8e\xde", "\x8e\xc3", "\x8e\xc2\x8e\xde", "\x8e\xc2", "\x8e\xc1\x8e\xde", "\x8e\xc1",
"\x8e\xc0\x8e\xde", "\x8e\xc0", "\x8e\xbf\x8e\xde", "\x8e\xbf", "\x8e\xbe\x8e\xde", "\x8e\xbe", "\x8e\xbd\x8e\xde", "\x8e\xbd",
"\x8e\xbc\x8e\xde", "\x8e\xbc", "\x8e\xbb\x8e\xde", "\x8e\xbb", "\x8e\xba\x8e\xde", "\x8e\xba", "\x8e\xb9\x8e\xde", "\x8e\xb9",
"\x8e\xb8\x8e\xde", "\x8e\xb8", "\x8e\xb7\x8e\xde", "\x8e\xb7", "\x8e\xb6\x8e\xde", "\x8e\xb6", "\x8e\xb5", "\x8e\xb4", "\x8e\xb3\x8e\xde", 
"\x8e\xb3", "\x8e\xb2", "\x8e\xb1", "\x8e\xb0", "\x8e\xaf", "\x8e\xae", "\x8e\xad", "\x8e\xac", "\x8e\xab",
"\x8e\xaa", "\x8e\xa9", "\x8e\xa8", "\x8e\xa7", "\x8e\xa6", "\x8e\xa5", "\x8e\xa4", "\x8e\xa3", "\x8e\xa2", "\x8e\xa1", NULL};

static const unsigned char **euc_h_kana = (const unsigned char **)s_euc_h_kana;



static const char *s_sjis_f_kana[] = {
 "\x83\x93", "\x83\x8f", "\x83\x8d", "\x83\x8c", "\x83\x8b", "\x83\x8a", 
 "\x83\x89", "\x83\x88", "\x83\x86", "\x83\x84", "\x83\x82", "\x83\x81", 
 "\x83\x80", "\x83\x7e", "\x83\x7d", "\x83\x7c", "\x83\x7b", "\x83\x7a", 
 "\x83\x79", "\x83\x78", "\x83\x77", "\x83\x76", "\x83\x75", "\x83\x74", 
 "\x83\x73", "\x83\x72", "\x83\x71", "\x83\x70", "\x83\x6f", "\x83\x6e", 
 "\x83\x6d", "\x83\x6c", "\x83\x6b", "\x83\x6a", "\x83\x69", "\x83\x68", 
 "\x83\x67", "\x83\x66", "\x83\x65", "\x83\x64", "\x83\x63", "\x83\x61", 
 "\x83\x60", "\x83\x5f", "\x83\x5e", "\x83\x5d", "\x83\x5c", "\x83\x5b", 
 "\x83\x5a", "\x83\x59", "\x83\x58", "\x83\x57", "\x83\x56", "\x83\x55", 
 "\x83\x54", "\x83\x53", "\x83\x52", "\x83\x51", "\x83\x50", "\x83\x4f", 
 "\x83\x4e", "\x83\x4d", "\x83\x4c", "\x83\x4b", "\x83\x4a", "\x83\x49", 
 "\x83\x47", "\x83\x94", "\x83\x45", "\x83\x43", "\x83\x41", "\x81\x5b", 
 "\x83\x62", "\x83\x87", "\x83\x85", "\x83\x83", "\x83\x48", "\x83\x46", 
 "\x83\x44", "\x83\x42", "\x83\x40", "\x83\x92", "\x81\x45", "\x81\x41", 
 "\x81\x76", "\x81\x75", "\x81\x42", NULL};

static const unsigned char **sjis_f_kana = (const unsigned char **)s_sjis_f_kana;


static const char *s_euc_f_kana[] = {
 "\xa5\xf3", "\xa5\xef", "\xa5\xed", "\xa5\xec", "\xa5\xeb", "\xa5\xea", 
 "\xa5\xe9", "\xa5\xe8", "\xa5\xe6", "\xa5\xe4", "\xa5\xe2", "\xa5\xe1", 
 "\xa5\xe0", "\xa5\xdf", "\xa5\xde", "\xa5\xdd", "\xa5\xdc", "\xa5\xdb", 
 "\xa5\xda", "\xa5\xd9", "\xa5\xd8", "\xa5\xd7", "\xa5\xd6", "\xa5\xd5", 
 "\xa5\xd4", "\xa5\xd3", "\xa5\xd2", "\xa5\xd1", "\xa5\xd0", "\xa5\xcf", 
 "\xa5\xce", "\xa5\xcd", "\xa5\xcc", "\xa5\xcb", "\xa5\xca", "\xa5\xc9", 
 "\xa5\xc8", "\xa5\xc7", "\xa5\xc6", "\xa5\xc5", "\xa5\xc4", "\xa5\xc2", 
 "\xa5\xc1", "\xa5\xc0", "\xa5\xbf", "\xa5\xbe", "\xa5\xbd", "\xa5\xbc", 
 "\xa5\xbb", "\xa5\xba", "\xa5\xb9", "\xa5\xb8", "\xa5\xb7", "\xa5\xb6", 
 "\xa5\xb5", "\xa5\xb4", "\xa5\xb3", "\xa5\xb2", "\xa5\xb1", "\xa5\xb0", 
 "\xa5\xaf", "\xa5\xae", "\xa5\xad", "\xa5\xac", "\xa5\xab", "\xa5\xaa", 
 "\xa5\xa8", "\xa5\xf4", "\xa5\xa6", "\xa5\xa4", "\xa5\xa2", "\xa1\xbc", 
 "\xa5\xc3", "\xa5\xe7", "\xa5\xe5", "\xa5\xe3", "\xa5\xa9", "\xa5\xa7", 
 "\xa5\xa5", "\xa5\xa3", "\xa5\xa1", "\xa5\xf2", "\xa1\xa6", "\xa1\xa2", 
 "\xa1\xd7", "\xa1\xd6", "\xa1\xa3", NULL};

static const unsigned char **euc_f_kana = (const unsigned char **)s_euc_f_kana;

int sjistohankana(int len, unsigned char *buf, unsigned char **ret, int *retlen) {
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;
    int i;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen=0;
        
        if (issjis1(buf[pos]) && (pos + 1 < len) && issjis2(buf[pos+1])) {
            for (i = 0; sjis_f_kana[i]; i++) {
                if (buf[pos] == sjis_f_kana[i][0] && buf[pos+1] == sjis_f_kana[i][1]) {
                    tmp[tmplen++] = h_kana[i][0];
                    if (h_kana[i][1]) {
                        tmp[tmplen++] = h_kana[i][1];
                    }
                    break;
                }
            }
            if (!sjis_f_kana[i]) {
                tmp[tmplen++] = buf[pos];
                tmp[tmplen++] = buf[pos+1];
            }

            pos++;
        } else {
            tmp[tmplen++] = buf[pos];
        }

        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;

    return 1;
}


int sjistofullkana(int len, unsigned char *buf, unsigned char **ret, int *retlen) {
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;
    int i, j;
    
    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen=0;
        
        if (ishankana(buf[pos])) {
            for (i = 0; h_kana[i]; i++) {
                for (j = 0; h_kana[i][j] && buf[pos+j]; j++) {
                    if (h_kana[i][j] != buf[pos+j]) {
                        break;
                    }
                }
                if (!h_kana[i][j]) {
                    const unsigned char *p;
                    for (p = sjis_f_kana[i]; *p; p++) {
                            tmp[tmplen++] = *p;
                    }
                    pos += j-1;
                    break;
                }
            }

            if (!h_kana[i]) {
                tmp[tmplen++] = buf[pos];
            }
        }
        else if (issjis1(buf[pos]) && (pos + 1 < len) && issjis2(buf[pos+1])) {
            tmp[tmplen++] = buf[pos];
            tmp[tmplen++] = buf[pos+1];
            pos += 1;
        } else {
            tmp[tmplen++] = buf[pos];
        }

        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;

    return 1;
}

int euctohankana(int len, unsigned char *buf, unsigned char **ret, int *retlen) {
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;
    int i;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen=0;
        
        if (iseuc(buf[pos]) && (pos + 1 < len) && iseuc(buf[pos+1])) {
            for (i = 0; euc_f_kana[i]; i++) {
                if (buf[pos] == euc_f_kana[i][0] && buf[pos+1] == euc_f_kana[i][1]) {
                    tmp[tmplen++] = '\x8e';
                    tmp[tmplen++] = h_kana[i][0];
                    if (h_kana[i][1]) {
                        tmp[tmplen++] = '\x8e';
                        tmp[tmplen++] = h_kana[i][1];
                    }
                    break;
                }
            }
            if (!euc_f_kana[i]) {
                tmp[tmplen++] = buf[pos];
                tmp[tmplen++] = buf[pos+1];
            }
            pos++;
        }
        else if ((buf[pos] == 0x8e) && (pos + 1 < len) && ishankana(buf[pos+1])) {
            tmp[tmplen++] = buf[pos];
            tmp[tmplen++] = buf[pos+1];
            pos++;
        } else {
            tmp[tmplen++] = buf[pos];
        }

        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;

    return 1;
}


int euctofullkana(int len, unsigned char *buf, unsigned char **ret, int *retlen) {
    int pos, tmplen, retpos=0;
    char tmp[10];
    unsigned char *newbuf;
    int i, j;

    if (!len) {
        *retlen = 0;
        return 1;
    }

    *retlen = len;
    *ret = malloc(*retlen);
    if (!*ret) {
        return 0;
    }

    for (pos = 0; pos < len; pos++) {
        tmplen=0;
        
        if ((buf[pos] == 0x8e) && (pos + 1 < len) && ishankana(buf[pos+1])) {
            for (i = 0; euc_h_kana[i]; i++) {
                for (j = 0; euc_h_kana[i][j] && buf[pos+j]; j++) {
                    if (euc_h_kana[i][j] != buf[pos+j]) {
                        break;
                    }
                }
                if (!euc_h_kana[i][j]) {
                    const unsigned char *p;
                    for (p = euc_f_kana[i]; *p; p++) {
                            tmp[tmplen++] = *p;
                    }
                    pos += j-1;
                    break;
                }
            }

            if (!h_kana[i]) {
                tmp[tmplen++] = buf[pos];
            }
        }
        else if (iseuc(buf[pos]) && (pos + 1 < len) && iseuc(buf[pos+1])) {
            tmp[tmplen++] = buf[pos];
            tmp[tmplen++] = buf[pos+1];
            pos += 1;
        } else {
            tmp[tmplen++] = buf[pos];
        }

        if (tmplen) {
            if (retpos + tmplen > *retlen) {
                *retlen = *retlen + len / 2 + 16;
                newbuf = realloc(*ret, *retlen);
                if (!newbuf) {
                    free(*ret);
                    return 0;
                }
                *ret = newbuf;
            }
            memcpy(*ret+retpos, tmp, tmplen);
            retpos += tmplen;
        }
    }

    if (!retpos) {
        *retlen = 0;
        free(*ret);
        return 1;
    }

    newbuf = realloc(*ret, retpos);
    if (!newbuf) {
        free(*ret);
        return 0;
    }
    *ret = newbuf;
    *retlen = retpos;

    return 1;
}


#ifdef PYKF_MAIN


void main() {
/*
    
    char *ret, *ret2, *ret3, *ret4, *ret5, *ret6, *ret7, *ret8;
    int retlen, retlen2, retlen3, retlen4, retlen5, retlen6, retlen7, retlen8;
    char *s1 = "\x82\xa0\xb1\x88\x9f\x61\x82\xa2\xb2\x8b\x8f\x62\x82\xa4\xb3\x89\x4b\x63\x82\xa6\xb4\x93\xbe\x64\x82\xa8\xb5\x94\xf6\x6f";
    char *s2 = "アイウエオ";
    char *gaiji = "\xf0\x40";
    char *s3 = "あいうえお\x81";
    char *s4 = "ｱｲｳｴｵｶ";
    char *s5 = "アイ";
    int guessed;

    guess(strlen(s1), s1, 1);
    sjistohankana(strlen(s2), s2, &ret7, &retlen7);


    sjistojis(strlen(s1), s1, &ret, &retlen);
    jistoeuc(retlen, ret, &ret2, &retlen2);
    guess(retlen2, ret2, 1);

    euctosjis(retlen2, ret2, &ret3, &retlen3);
    assert(strncmp(s1, ret3, strlen(s1))==0);

    euctojis(retlen2, ret2, &ret4, &retlen4);
    assert(strncmp(ret, ret4, retlen)==0);

    sjistoeuc(strlen(s1), s1, &ret5, &retlen5);
    assert(strncmp(ret2, ret5, strlen(ret2))==0);

    jistosjis(retlen4, ret4, &ret6, &retlen6);
    assert(strncmp(s1, ret6, strlen(s1))==0);

    sjistoeuc(strlen(gaiji), gaiji, &ret7, &retlen7);

    sjistojis(strlen(s5), s5, &ret8, &retlen8);

    guessed = guess(strlen(s3), s3, 1);
    assert(guessed == ERROR);

    guessed = guess(strlen(s3), s3, 0);
    assert(guessed == SJIS);

    guessed = guess(strlen(s4), s4, 0);


*/
    char *s = "㈱";
    char *ret;
    int retlen;

    sjistojis(strlen(s), s, &ret, &retlen, 0);

}

#endif
