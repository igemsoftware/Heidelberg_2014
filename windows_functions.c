#include <stdlib.h>
#include <stdio.h>
#include <windows.h>

int getExecPath_w(char *path, size_t len, int get_dirname){
	if (GetModuleFileName(NULL, path, len) != 0) {
		if (get_dirname){
			char *end = strrchr(path, '\\');
			if (end != NULL)
				*end = 0;
		}
        return 1;
    }
    else
    	return 0;
}

int createFailIfExists_w(char *file){
	HANDLE handle;
	handle = CreateFile(file, GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
	if(handle == INVALID_HANDLE_VALUE)
		return -1;	// File exists
	else{
		CloseHandle(handle);
		return 0;	// Files does not exist
	}
}