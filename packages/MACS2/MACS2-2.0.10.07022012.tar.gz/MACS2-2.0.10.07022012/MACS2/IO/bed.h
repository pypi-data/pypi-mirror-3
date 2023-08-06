/* Declarations for parsefasta.

   Copyright (C) Liu Tao

   This library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Library General Public License
   as published by the Free Software Foundation; either version 2 of
   the License, or (at your option) any later version.

   This library is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Library General Public License for more details.

   You should have received a copy of the GNU Library General Public
   License along with this library; see the file COPYING.LIB.  If not,
   write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
   Boston, MA 02111-1307, USA.  */

#ifndef __BED_H_
#define __BED_H_

/* Store BED record */
typedef struct _BED
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
