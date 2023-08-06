#include "_lcs.h"

#include <string.h>
#include <stdlib.h>
#include <limits.h>

#include <stdio.h>



// Allocate a band allowing to align sequences of length : 'length'

column_t* allocateColumn(int length,column_t *column, bool mode8bits)
{
	int size;
	bool newc = false;

			// The band length should be equal to the length
			// of the sequence + 7 for taking into account its
			// shape

	size = (length+1) * ((mode8bits) ? sizeof(int8_t):sizeof(int16_t));


			// If the pointer to the old column is NULL we allocate
			// a new column

	if (column==NULL)
	{

		column = malloc(sizeof(column_t));
		if (!column)
			return NULL;

		column->size = 0;
		column->data.shrt=NULL;
		column->score.shrt=NULL;
		newc = true;
	}

			// Otherwise we check if its size is sufficient
			// or if it should be extend

	if (size > column->size)
	{
		int16_t *old = column->data.shrt;
		int16_t *olds= column->score.shrt;

		column->data.shrt = malloc(size);
		column->score.shrt= malloc(size);

		if (!column->data.shrt || !column->score.shrt)
		{
			column->data.shrt = old;
			column->score.shrt= olds;

			if (newc)
			{
				free(column);
				column=NULL;
				return NULL;
			}
			return NULL;
		}
		else
			column->size = size;
	}

	return column;
}

void freeColumn(column_p column)
{
	if (column)
	{
		if (column->data.shrt)
			free(column->data.shrt);

		if (column->score.shrt)
			free(column->score.shrt);

		free(column);
	}
}

int fastLCSScore(const char* seq1, const char* seq2,column_pp column,int32_t* lpath)
{
	return fastLCSScore16(seq1,seq2,column,lpath);
}

