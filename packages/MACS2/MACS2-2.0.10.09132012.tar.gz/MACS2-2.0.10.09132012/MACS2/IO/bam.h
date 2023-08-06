/* Declarations for bam parser.

 */

#ifndef __BAM_H_
#define __BAM_H_

/* Store BAM references */
typedef struct _RLENGTH
{
  char ** refname; /* reference chromosome names */
  long ** reflength;

}



/* Store BAM record */
typedef struct _BAM
{
  char* chromosome;		/* chromosome name */
  long  startpos;		/* left position, 0-indexed */
  long  endpos;			/* right position, excluded */
  char* name;			/* name of the feature */
  int   score;			/* score is integar between 0 and 1000 */
  short strand;			/* stand can be 0 for plus */
  char* other;			/* other information after 6th column will be ignored.*/
} BED;

/* for store BED struct in a 1-direction chain */
typedef struct _BEDRecord
{
  BED *bed;
  struct _BEDRecord *next;
} BEDRecord;

/* parse a BED file */
BEDRecord* parse_file (FILE * fp);

/* parse BED records from text block 
   all stuff are in memory.
 */
BEDRecord* parse_text ( const char* text);
/* parse a single BED record */
BEDRecord* parse_record ( const char* text);

/* free fasta recordS */
void free_records ( BEDRecord* target_record);

/* create a fasta record */
BEDRecord* new_record (const char* chrom, const long startpos,
		       const long endpos, const chr* name, 
		       const int score, const short strand, 
		       const char* other );

/* write a record */
int write_record (FILE *fp, BEDRecord* fr);

/* write multiple records */
int write_records (FILE *fp, BEDRecord* fr);

#endif
