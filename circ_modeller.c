#if __STDC_VERSION__ >= 199901L
#define _XOPEN_SOURCE 600
#else
#define _XOPEN_SOURCE 500
#endif /* __STDC_VERSION__ */

#include <glib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <modeller.h>

/* Linux */
#include <libgen.h>
#include <unistd.h>

/* BOINC */
#include <boinc_zip.h>
#include <boinc_api.h>


/* Example of using Modeller from a C program. This simply reads in a PDB
 * file, prints out some data from that file, and then writes out a new
 * file in MMCIF format.
 *
 * To compile, use (where XXX is your Modeller version):
 * gcc -Wall -o c-example c-example.c `modXXX --cflags --libs` \
 *     `pkg-config --cflags --libs glib-2.0`
 * (If you use a compiler other than gcc, or a non-Unix system, you may need
 * to run 'modXXX --cflags --libs' manually and construct suitable compiler
 * options by hand.)
 *
 * To run, you must ensure that the Modeller dynamic libraries are in your
 * search path. This can be done on most systems by adding the directory
 * reported by 'modXXX --libs' to the LD_LIBRARY_PATH environment variable.
 * (On Mac, set DYLD_LIBRARY_PATH instead. On Windows, PATH. On AIX, LIBPATH.)
 *
 * You must also ensure that Modeller knows where it was installed,
 * and what the license key is. You can either do this by setting the
 * MODINSTALLXXX and KEY_MODELLERXXX environment variables accordingly, or
 * by calling the mod_install_dir_set() and mod_license_key_set() functions
 * before you call mod_start(). For example, if Modeller is installed in
 * /lib/modeller on a 32-bit Linux system, the following would work from the
 * command line (all on one line), where KEY is your license key:
 *     KEY_MODELLERXXX=KEY MODINSTALLXXX=/lib/modeller/
 *     LD_LIBRARY_PATH=/lib/modeller/lib/i386-intel8 ./c-example
 */

#define getExecPath getExecPath_l
#define checkFileExists fileExists
#define createFailIfExists createFailIfExists_l
#define DEBUG
#define MAX_PATH 2048
#define RESOURCES_ZIP MODELLER_RES_ZIP

int getExecPath_l(char *path, size_t len){
	if (readlink("/proc/self/exe", path, len) != -1) {
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

int unzip(char *basedir) {
	char unzip_file[MAX_PATH] = {0};
	char unzip_lock_started[MAX_PATH] = {0};
	char unzip_lock_finished[MAX_PATH] = {0};
    int rc;

    /* Check if other process is already extracting */
    strncpy(unzip_lock_started, basedir, MAX_PATH);
    strncat(unzip_lock_started, "/unzip_started", MAX_PATH-(strlen(basedir)+1))
    
    strncpy(unzip_lock_finished, basedir, MAX_PATH);
    strncat(unzip_lock_finished, "/unzip_finished", MAX_PATH-(strlen(basedir)+1))

    if(!checkFileExists(unzip_lock_finished)) {
    	if(createFailIfExists(unzip_lock_started) < 0){	// Lockfile exists --> other process extracting
    		/* Wait max 5 minutes for process to finish */
    		int i;
    		for(i = 0; i < 100; i++){
    			sleep(3);
    			if(checkFileExists(unzip_lock_finished))
    				return UNZIP_ALREADY_DONE;
    		}
    		printf("Other process taking to long to exit.")
    		return -1; 
    	}
    	else {								// Lockfile does not exist --> extract data
    		boinc_resolve_filename(RESOURCES_ZIP, unzip_file, MAX_PATH);
    		#ifdef DEBUG
			printf("No process extracting yet. Extracting %s...\n", unzip_file);
        	#endif
        	if(checkFileExists(unzip_file)) {
				rc = boinc_zip(UNZIP_IT, unzip_file, basedir);
				#ifdef DEBUG
				printf("boinc_zip(UNZIP_IT, %s, \"%s\") returned %i\n",unzip_file, basedir, rc);
				#endif
				return rc;
        	}
			else {
				printf("%s does not exist. Aborting...\n", unzip_file);
				return -1;
	        }
    	}
    }
    else
    	return UNZIP_ALREADY_DONE

        

}

void simple_crypt(char *array, int array_size)
{
    int i;
    char secret[] = { 22, 53, 44, 71, 66, 177, 253, 122, 33, 78, 167, 180 };
    for(i = 0; i < array_size; i++)
        array[i] ^= secret[i];
}

/* Exit, reporting the Modeller error, iff one occurred. */
void handle_error(int ierr)
{
  if (ierr != 0) {
    GError *err = mod_error_get();
    fprintf(stderr, "Modeller error: %s\n", err->message);
    g_error_free(err);
    exit(1);
  }
}

int main(void)
{
	char modeller_path[FILENAME_MAX];
	char libs_path[FILENAME_MAX];
	char licence[] = {91, 122, 104, 2, 14, -8, -81, 59, 111, 4, -30, 0};

	struct mod_libraries *libs;
	struct mod_model *mdl;
	struct mod_io_data *io;
	struct mod_file *fh;
	int ierr, *sel1, nsel1;

	
	getExecPath(modeller_path, FILENAME_MAX);

	
	/* Set Modeller environment variables correctly */
	strncpy(libs_path, modeller_path, FILENAME_MAX);
	strncat(libs_path, "/libs.lib", FILENAME_MAX-strlen(libs_path));
	setenv("LIBS_LIB9v14", libs_path, 1);
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
	fh = mod_file_open("2nbt.pdb", "r");
	if (fh) {
		mod_model_read(mdl, io, libs, fh, "PDB", "FIRST:@LAST:  ", 7, &ierr);
		mod_file_close(fh, &ierr);
	} else {
		ierr = 1;
	}
	handle_error(ierr);
	printf("Model of %s solved at resolution %f, rfactor %f\n", mdl->seq.name,
	     mdl->seq.resol, mdl->seq.rfactr);
	fh = mod_file_open("new.cif", "w");
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

	mod_end();
	return 0;
}
