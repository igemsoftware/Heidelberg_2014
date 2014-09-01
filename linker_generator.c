
#if __STDC_VERSION__ >= 199901L
#define _XOPEN_SOURCE 600
#else
#define _XOPEN_SOURCE 500
#endif /* __STDC_VERSION__ */

#include "Python.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/rsa.h>
#include <openssl/engine.h>
#include <openssl/bn.h>
#include <openssl/err.h>

/* BOINC */
#include <boinc_api.h>
#include <boinc_zip.h>

#include "linker_generator.h"
#include "config.h"

#ifdef __linux
#include "linux_functions.h"
#define DIR_SLASH "/"
#elif _WIN32
#include "windows_functions.h"
#pragma comment(lib, "crypt32.lib") 
#define DIR_SLASH "\\"
#endif

#define RESOURCES_ZIP "linkergen_res.zip"
#define STDERR_FILE "stderr.txt"
#define STDOUT_FILE STDERR_FILE

#define DEBUG

int fileExists(char* name) {
  struct stat buf;
  return (stat(name, &buf) == 0) ? TRUE : FALSE;
}


void print_error(char *place, char *msg, char *param){
	if(param != NULL)
		fprintf(stderr, "ERROR[%-12.12s]: %s %s\n", place, msg, param);
	else
		fprintf(stderr, "ERROR[%-12.12s]: %s\n", place, msg);
}


char *strnchr(char *str, size_t len, int character) {
    char *end = str + len;
    char c = (char)character;
    do {
        if (*str == c) {
            return str;
        }
    } while (++str <= end);
    return NULL;
}

int unzip_resources(char *basedir) {
	char unzip_file[MAX_PATH] = {0};
	char unzip_lock_started[MAX_PATH] = {0};
	char unzip_lock_finished[MAX_PATH] = {0};
	char working_dir[MAX_PATH] = {0};
    int rc;
    FILE *lockfile;
    //unzFile uf;

    /* Check if other process is already extracting */
    strncpy(unzip_lock_started, basedir, MAX_PATH);
	strncat(unzip_lock_started, DIR_SLASH "unzip_started", MAX_PATH - (strlen(basedir) + 1));
    
    strncpy(unzip_lock_finished, basedir, MAX_PATH);
	strncat(unzip_lock_finished, DIR_SLASH "unzip_finished", MAX_PATH - (strlen(basedir) + 1));

    if(!fileExists(unzip_lock_finished)) {
    	if(createFailIfExists(unzip_lock_started) < 0){	// Lockfile exists --> other process extracting
    		/* Wait max 5 minutes for process to finish */
    		printf("Other process allready extracting...\n");
    		boinc_temporary_exit_wrapper(20, "Other process allready extracting\n", FALSE);
    		return -1; 
    	}
    	else {								// Lockfile does not exist --> extract data
    		boinc_resolve_filename(RESOURCES_ZIP, unzip_file, MAX_PATH);
    		#ifdef DEBUG
			printf("No process extracting yet. Extracting %s...\n", unzip_file);
        	#endif
        	if(fileExists(unzip_file)) {
				/*
				//Alternative implementation
				#ifdef USEWIN32IOAPI
					zlib_filefunc64_def ffunc;
				#endif
				#ifdef USEWIN32IOAPI
					fill_win32_filefunc64A(&ffunc);
					uf = unzOpen2_64(unzip_file,&ffunc);
				#else
					uf = unzOpen64(unzip_file);
				#endif
				
				if(getcwd(working_dir, MAX_PATH) == NULL)
					printf("Warning: Unable to save working dir!\n");

				#ifdef _WIN32
					if (_chdir(basedir))
				#else
					if (chdir(basedir))
				#endif
        		{
          		printf("Error changing into %s, aborting\n", basedir);
          		return(-1);
        		}

           		rc = do_extract(uf, 0, 1, '\0');
				*/
				rc = boinc_zip(UNZIP_IT, unzip_file, basedir);
				#ifdef DEBUG
				printf("Unzip routine returned %i\n", rc);
				#endif
				lockfile = fopen(unzip_lock_finished, "w");
				fclose(lockfile);

				return rc;
        	}
			else {
				printf("%s does not exist. Aborting...\n", unzip_file);
				remove(unzip_lock_started);
				return -1;
	        }
    	}
    }
    else
    	return 0;
}


void call_python(char *ProgramName, char *modeller_path, char *modeller_licence) {
	PyObject *module, *modeller_init, *calc;
	//char pythonhome[2*MAX_PATH] = { 0 };
	char **argv;
	
	// Reserve space for resolved filenames
	char *resolved_files[5];
	char file1[MAX_PATH] = { 0 };
	char file2[MAX_PATH] = { 0 };
	char file3[MAX_PATH] = { 0 };
	char file4[MAX_PATH] = { 0 };
	resolved_files[0] = file1;
	resolved_files[1] = file2;
	resolved_files[2] = file3;
	resolved_files[3] = file4;

	argv = &ProgramName;
	// Prevent import of site.py
	Py_NoSiteFlag = 1;

	Py_SetProgramName(ProgramName);

	Py_SetPythonHome(modeller_path);
	//Py_InitializeEx(0);
	Py_Initialize();
	PySys_SetPath(modeller_path);
	
	// Setup Python sys path to include modeller Module
	PySys_SetArgv(1, argv);

	module = PyImport_ImportModule("construct_circ_protein");
	if(module == NULL){
		PyObject *ptype, *pvalue, *ptraceback;
		PyErr_Fetch(&ptype, &pvalue, &ptraceback);
		//pvalue contains error message
		//ptraceback contains stack snapshot and many other information
		//(see python traceback structure)

		//Get error message
		char *pStrErrorMessage = PyString_AsString(pvalue);
		printf("Error importing Module:\n%s\n", pStrErrorMessage);
		//PyErr_Print();
		return;
	}

	modeller_init = PyObject_GetAttrString(module, "modeller_init");
	if(modeller_init == NULL){
		printf("Error getting Attribute modeller_init\n");
		PyErr_Print();
		return;
	}
	PyObject_CallFunction(modeller_init, "ss", modeller_path, modeller_licence);

	calc = PyObject_GetAttrString(module, "calc");
	if(calc == NULL){
		printf("Error getting Attribute calc.\n");
		PyErr_Print();
		return;
	}

	for (int i = 0; i < 3; i++){
		boinc_resolve_filename(used_filenames[i], resolved_files[i], MAX_PATH);
	}

	boinc_resolve_filename("output.pdb", resolved_files[3], MAX_PATH);

	PyObject_CallFunction(calc, "ssss", resolved_files[0], resolved_files[1], resolved_files[2], resolved_files[3]);
	
	PyObject *exception = PyErr_Occurred();
	if (exception != NULL){
		PyObject *ptype, *pvalue, *ptraceback;
		int errorcode;
		errorcode = PyErr_ExceptionMatches(exception);
		PyErr_Fetch(&ptype, &pvalue, &ptraceback);
		printf("Errorcode: %i\n%s\nTraceback:\n%s\n", errorcode, PyString_AsString(pvalue), PyString_AsString(ptraceback));
	}


	Py_Finalize();
}

int main(int argc, char **argv)
{
	char modeller_path[MAX_PATH] = {0};
	char libs_path[MAX_PATH] = {0};
	char licence[] = {91, 122, 104, 2, 14, -8, -81, 59, 111, 4, -30, 0};
	char exec_path[MAX_PATH] = { 0 };

/*
	struct mod_libraries *libs;
	struct mod_model *mdl;
	struct mod_io_data *io;
	struct mod_file *fh;
	int ierr, *sel1, nsel1, rc;
	char file_resolve[MAX_PATH];
*/
	int rc;
	boinc_init();
	
	#ifdef DEBUG
	//freopen(STDERR_FILE,"a",stdout); // also redirect stdout to stderr
	#endif

	getExecPath(modeller_path, MAX_PATH, 1);
	getExecPath(exec_path, MAX_PATH, 0);

	rc = unzip_resources(modeller_path); // Extract modeller resource files if not existent
	if(rc < 0){
		printf("Temporary exiting...\n");
		boinc_temporary_exit_wrapper(20, "Something went wrong while extracting!\n", FALSE);
	}

	if(check_file_signings((const char **)used_filenames))
		{print_error("main", "verifying files failed!", NULL); boinc_finish(-1);}

	/* Set Modeller environment variables correctly */
	strncpy(libs_path, modeller_path, MAX_PATH);
	strncat(libs_path, DIR_SLASH "libs.lib", MAX_PATH - strlen(libs_path));
	#ifdef __linux
	setenv("LIBS_LIB9v14", libs_path, 1);
	setenv("PYTHONPATH", "", 1);
	#elif _WIN32
	_putenv_s("LIBS_LIB9v14", libs_path);
	_putenv_s("PYTHONPATH", "");
	#endif


	
	#ifdef DEBUG
		printf("Setting Modeller install dir: \"%s\"\nSetting path to libs file: \"%s\"\n", modeller_path, libs_path);
	#endif

	

	/* Install encrypted licence */
	simple_crypt(licence, strlen(licence));

	call_python(exec_path, modeller_path, licence);

	boinc_finish(0);
	return -1;
}
