#if __STDC_VERSION__ >= 199901L
#define _XOPEN_SOURCE 600
#else
#define _XOPEN_SOURCE 500
#endif /* __STDC_VERSION__ */

#include <glib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#include <modeller.h>

/* BOINC */
#include <boinc_api.h>
#include <boinc_zip.h>

#include "circ_modeller.h"
#include "config.h"

#ifdef __linux
#include "linux_functions.h"
#elif _WIN32
#include "windows_functions.h"
#endif

#define RESOURCES_ZIP "modeller_res.zip"
#define STDERR_FILE "stderr.txt"
#define STDOUT_FILE STDERR_FILE

#define DEBUG

int fileExists(char* name) {
  struct stat buf;
  return (stat(name, &buf) == 0) ? TRUE : FALSE;
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
    strncat(unzip_lock_started, "/unzip_started", MAX_PATH-(strlen(basedir)+1));
    
    strncpy(unzip_lock_finished, basedir, MAX_PATH);
    strncat(unzip_lock_finished, "/unzip_finished", MAX_PATH-(strlen(basedir)+1));

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
				/*#ifdef USEWIN32IOAPI
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

void simple_crypt(char *array, int array_size)
{
    int i;
    char secret[] = { 22, 53, 44, 71, 66, 177, 253, 122, 33, 78, 167, 180 };
    for(i = 0; i < array_size; i++)
        array[i] ^= secret[i];
}

/* Exit, reporting the Modeller error, if one occurred. */
void handle_error(int ierr)
{
  if (ierr != 0) {
    GError *err = mod_error_get();
    fprintf(stderr, "Modeller error: %s\n", err->message);
    g_error_free(err);
    boinc_finish(1);
  }
}

int main(void)
{
	char modeller_path[MAX_PATH];
	char libs_path[MAX_PATH];
	char licence[] = {91, 122, 104, 2, 14, -8, -81, 59, 111, 4, -30, 0};

	struct mod_libraries *libs;
	struct mod_model *mdl;
	struct mod_io_data *io;
	struct mod_file *fh;
	int ierr, *sel1, nsel1, rc;
	char file_resolve[MAX_PATH];

	boinc_init();
	
	#ifdef DEBUG
	//freopen(STDERR_FILE,"a",stdout); // also redirect stdout to stderr
	#endif

	getExecPath(modeller_path, MAX_PATH);

	rc = unzip_resources(modeller_path); // Extract modeller resource files if not existent
	if(rc < 0){
		printf("Temporary exiting...\n");
		boinc_temporary_exit_wrapper(20, "Something went wrong while extracting!\n", FALSE);
	}


	/* Set Modeller environment variables correctly */
	strncpy(libs_path, modeller_path, MAX_PATH);
	strncat(libs_path, "/libs.lib", MAX_PATH-strlen(libs_path));
	#ifdef __linux
	setenv("LIBS_LIB9v14", libs_path, 1);
	#elif _WIN32
	_putenv_s("LIBS_LIB9v14", libs_path);
	#endif
	
	#ifdef DEBUG
		printf("Setting Modeller install dir: \"%s\"\nSetting path to libs file: \"%s\"\n", modeller_path, libs_path);
	#endif

	mod_install_dir_set(modeller_path);

	/* Install encrypted licence */
	simple_crypt(licence, strlen(licence));
	mod_license_key_set(licence);

	mod_start(&ierr);
	handle_error(ierr);
	mod_header_write();

	mod_log_set(2, 1);
	libs = mod_libraries_new(NULL);
	fh = mod_file_open("${LIB}/restyp.lib", "r");
	if (fh) {
		mod_libraries_read_libs(libs, fh, &ierr);
		mod_file_close(fh, &ierr);
	} else {
		ierr = 1;
	}
	handle_error(ierr);
	mod_libraries_rand_seed_set(libs, -8123);

	mdl = mod_model_new(NULL);
	io = mod_io_data_new();
	boinc_resolve_filename("pdb_file", file_resolve, MAX_PATH);
	fh = mod_file_open(file_resolve, "r");
	if (fh) {
		mod_model_read(mdl, io, libs, fh, "PDB", "FIRST:@LAST:  ", 7, &ierr);
		mod_file_close(fh, &ierr);
	} else {
		ierr = 1;
	}
	handle_error(ierr);
	printf("Model of %s solved at resolution %f, rfactor %f\n", mdl->seq.name,
	     mdl->seq.resol, mdl->seq.rfactr);
	boinc_resolve_filename("output", file_resolve, MAX_PATH);
	fh = mod_file_open(file_resolve, "w");
	if (fh) {
		mod_selection_all(mdl, &sel1, &nsel1);
		mod_model_write(mdl, libs, sel1, nsel1, fh, "MMCIF", 0, 1, "", &ierr);
		g_free(sel1);
		mod_file_close(fh, &ierr);
	} else {
		ierr = 1;
	}
	handle_error(ierr);
	mod_libraries_free(libs);
	mod_model_free(mdl);
	mod_io_data_free(io);
	//mod_end();
	boinc_finish(0);
	return -1;
}
