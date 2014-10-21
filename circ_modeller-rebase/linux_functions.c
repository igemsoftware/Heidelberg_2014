#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h> 
#include <fcntl.h>
#include <errno.h>
#include <libgen.h>
#include <unistd.h>
#include "circ_modeller.h"
//#include <glib.h>

int getExecPath_l(char *path, size_t len, int get_dirname){
	if (readlink("/proc/self/exe", path, len) != -1) {
        if(get_dirname)
            dirname(path); 
        return TRUE;
    }
    else
    	return FALSE;
}

int createFailIfExists_l(char *file){
	int fd;
	fd = open(file, O_CREAT|O_EXCL|O_RDWR, S_IRUSR|S_IWUSR);
    if (fd == -1 || errno == EEXIST)
    	return -1;	// File exists
    else {
    	close(fd);
    	return 0;	// File created
    }
}