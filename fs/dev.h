/* Block layer abstraction */

int dev_init(); /* Returns -1 on failure */
int dev_size(); /* Size of each block */
int dev_count(); /* Number of blocks */
int dev_read(int id, unsigned char* buf); /* Returns -1 on failure */
int dev_write(int id, unsigned char* buf); /* Returns -1 on failure */

