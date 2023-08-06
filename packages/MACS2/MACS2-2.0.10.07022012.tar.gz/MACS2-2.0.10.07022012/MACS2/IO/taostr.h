#ifndef __TAOIO_H_
#define __TAOIO_H_

#define BUFFERSIZE 1000

/* read lines from file handle one per read  */
char * readline (FILE *fp);

/* read text from file handle til the char per read.  */
char * readtil (FILE *fp, char c);

/* split string into pieces using delimitation characters in
   `delimit', store the number of pieces in *num.
   Note that the original string s is changed during operation.
 */
char ** splitstr (char *s, int *num, char *delimit);

/* int to string */
char * int2str ( const int a );

#endif
