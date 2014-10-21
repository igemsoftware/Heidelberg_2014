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

int DeleteDirectory(char *lpszDir, int noRecycleBin)
{
	int len = strlen(lpszDir);
	char *pszFrom = (char *)malloc(len + 2);
	strcpy(pszFrom, lpszDir);
	pszFrom[len] = 0;
	pszFrom[len + 1] = 0;

	SHFILEOPSTRUCT fileop;
	fileop.hwnd = NULL;    // no status display
	fileop.wFunc = FO_DELETE;  // delete operation
	fileop.pFrom = pszFrom;  // source file name as double null terminated string
	fileop.pTo = NULL;    // no destination needed
	fileop.fFlags = FOF_NOCONFIRMATION | FOF_SILENT;  // do not prompt the user

	if (!noRecycleBin)
		fileop.fFlags |= FOF_ALLOWUNDO;

	fileop.fAnyOperationsAborted = FALSE;
	fileop.lpszProgressTitle = NULL;
	fileop.hNameMappings = NULL;

	int ret = SHFileOperation(&fileop);
	free(pszFrom);
	return (ret == 0);
}