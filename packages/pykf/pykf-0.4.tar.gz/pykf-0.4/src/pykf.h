

/* kanji conversion tables */
extern unsigned int tbl_jis0213[];
extern int tbl_sjis2jis[];
extern int tbl_jis2sjis[];


/* Japanese character encodings */
enum {ERROR=-1, UNKNOWN=0, ASCII=1, SJIS=2, EUC=3, JIS=4, UTF8=5, UTF16_LE=7, UTF16_BE=8};

int guess(int imax, unsigned char buf[], int strict);
int sjistojis(int len, unsigned char *buf, unsigned char **ret, int *retlen, int jis0208);
int euctojis(int len, unsigned char *buf, unsigned char **ret, int *retlen, int jis0208);
int sjistoeuc(int len, unsigned char *buf, unsigned char **ret, int *retlen);
int jistoeuc(int len, unsigned char *buf, unsigned char **ret, int *retlen);
int jistosjis(int len, unsigned char *buf, unsigned char **ret, int *retlen);
int euctosjis(int len, unsigned char *buf, unsigned char **ret, int *retlen);

int sjistohankana(int len, unsigned char *buf, unsigned char **ret, int *retlen);
int euctohankana(int len, unsigned char *buf, unsigned char **ret, int *retlen);
int sjistofullkana(int len, unsigned char *buf, unsigned char **ret, int *retlen);
int euctofullkana(int len, unsigned char *buf, unsigned char **ret, int *retlen);


