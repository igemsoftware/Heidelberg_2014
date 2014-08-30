
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

#include "circ_modeller.h"
#include "config.h"

#ifdef __linux
#include "linux_functions.h"
#define DIR_SLASH "/"
#elif _WIN32
#include "windows_functions.h"
#pragma comment(lib, "crypt32.lib") 
#define DIR_SLASH "\\"
#endif

#define RESOURCES_ZIP "modeller_res.zip"
#define STDERR_FILE "stderr.txt"
#define STDOUT_FILE STDERR_FILE
#define SIGNATURES_FILE "signatures"
#define OUTPUT_FILE "output.pdb"
#define MAX_LINESIZE 500
#define MAX_SIG_SIZE 500

//#define DEBUG

int fileExists(char* name) {
  struct stat buf;
  return (stat(name, &buf) == 0) ? TRUE : FALSE;
}

const char *used_filenames[] = {
								"construct_circ_protein.pyd",
								"configfile.csv", 
								"atomfile.pdb",
								"inputsequencefile.ali",
								"\0"
								};
// TODO change to stderr
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

const unsigned char public_key_modulus[] = 	{
	0xc3, 0x9f, 0xd8, 0x18, 0x5c, 0x93, 0xfe, 0x08, 0x91, 0x60, 0x43, 0xf6, 0x42, 0x98, 0x0e, 0x64,
	0x90, 0xc8, 0xbc, 0x67, 0x34, 0x09, 0xcc, 0x82, 0xc6, 0x92, 0x16, 0x16, 0x08, 0x67, 0xde, 0xde,
	0x14, 0x38, 0x3f, 0x0d, 0x08, 0x6e, 0x4d, 0x46, 0x6b, 0x95, 0xe8, 0xec, 0xec, 0x34, 0x83, 0x09,
	0xc5, 0xe9, 0x0e, 0x8e, 0xb6, 0xa6, 0x9e, 0xdb, 0x3b, 0x60, 0x7e, 0xdd, 0x15, 0x2d, 0x21, 0x02,
	0x1a, 0x0d, 0xb6, 0x83, 0xf4, 0xb8, 0x02, 0x41, 0xea, 0x5f, 0x5e, 0x25, 0x32, 0x2b, 0xeb, 0x23,
	0xc2, 0x37, 0xac, 0xd1, 0x35, 0xc0, 0x18, 0xcd, 0x45, 0x17, 0x50, 0xa1, 0xd4, 0x4a, 0x38, 0xe6,
	0xfa, 0x6e, 0x73, 0x03, 0x36, 0x55, 0xd9, 0x8f, 0xcd, 0xe0, 0x20, 0xe6, 0x41, 0x64, 0x93, 0x68,
	0xce, 0xff, 0xdc, 0xf1, 0x74, 0xc6, 0xf9, 0x39, 0xeb, 0x8a, 0xec, 0x2a, 0xdf, 0x5f, 0x14, 0x45,
	0x7e, 0xb0, 0xa1, 0xea, 0x0c, 0xf4, 0xc5, 0xbc, 0x53, 0xa1, 0xa1, 0xb0, 0x57, 0x0a, 0x78, 0xca,
	0x08, 0xa0, 0xa0, 0x22, 0x13, 0x51, 0x66, 0xcf, 0x53, 0x10, 0x1c, 0x1b, 0x9c, 0x08, 0x33, 0xc9,
	0xed, 0x86, 0x40, 0xcb, 0x03, 0x76, 0xdd, 0x18, 0x5f, 0xc0, 0x9a, 0x3c, 0x12, 0x2d, 0x19, 0x4c,
	0x89, 0x17, 0xbe, 0xc8, 0x83, 0x93, 0xf4, 0x5c, 0x5d, 0x84, 0x1d, 0x18, 0x6b, 0xab, 0xb2, 0x91,
	0xba, 0xca, 0xc9, 0x51, 0xe7, 0xd3, 0xd5, 0x5a, 0x13, 0x0b, 0x9f, 0x27, 0xd1, 0xe1, 0x06, 0x3e,
	0xd1, 0xa6, 0x17, 0x3e, 0x77, 0x59, 0xb9, 0x9f, 0xff, 0x6d, 0x76, 0xf3, 0x9a, 0x77, 0x54, 0xd4,
	0x4c, 0xf3, 0x44, 0x5d, 0xa0, 0x2a, 0xd7, 0x18, 0x88, 0x00, 0x7b, 0xb7, 0xaf, 0x3a, 0x02, 0x4f,
	0x33, 0x11, 0x31, 0x3c, 0x68, 0xde, 0x6f, 0x0b, 0xac, 0x26, 0x46, 0x6f, 0xca, 0xcb, 0x1a, 0xed
	};

const unsigned char public_key_exponent[] = {0x01, 0x00, 0x01};


int build_public_key(EVP_PKEY *public_key){
	RSA *rsa_public_key;

	rsa_public_key = RSA_new(); //DONOT FREE!, we are using the PKEY_assign_RSA function
	// Fill RSA strukture with data
	BN_free(rsa_public_key->n);
	if(NULL == (rsa_public_key->n = BN_bin2bn(public_key_modulus, sizeof(public_key_modulus)/sizeof(public_key_modulus[0]), NULL)))
		{print_error("build_pub_key", "converting modulus to bn", NULL); goto error;}

	BN_free(rsa_public_key->e);
	if(NULL == (rsa_public_key->e = BN_bin2bn(public_key_exponent, sizeof(public_key_exponent)/sizeof(public_key_exponent[0]), NULL)))
		{print_error("build_pub_key", "converting exponent to bn", NULL); goto error;}
	
	if(!EVP_PKEY_assign_RSA(public_key, rsa_public_key)) //Key gets freed when PKEY gets freed
		{print_error("build_pub_key", "EVP_PKEY_assign_RSA failed!", NULL); goto error;}

	return 0;

	error:
	RSA_free(rsa_public_key);
	ERR_print_errors_fp(stderr);
	return -1;
}

int get_signature(char *filename, char *signature, int length) {
	char sig_filename[MAX_PATH];
	FILE *sig_file;
	char line[MAX_LINESIZE];
	char *cur_pos, *end_line;
	BIO *bio_in, *b64;
	int bytes_read_total = 0,bytes_read = 0;
	boinc_resolve_filename(SIGNATURES_FILE, sig_filename, MAX_PATH);
	sig_file = fopen(sig_filename, "r");
	if(sig_file == NULL)
		{print_error("get_signature", "unable to open signatures file: ", sig_filename ); return -1;}

	while(fgets(line, MAX_LINESIZE, sig_file) != NULL){
		cur_pos = strnchr(line, strlen(line), ' ');
		if(cur_pos == NULL)
			{print_error("get_signature", "signatures file has wrong format", NULL ); break;}
		*cur_pos = '\0';
		#ifdef DEBUG
			printf("Filename: %s, Base64 signature: %s", line, cur_pos+1);
		#endif
		if(!strncmp(filename, line, strlen(line))){
			cur_pos++;
			end_line = strnchr(cur_pos, MAX_LINESIZE-(cur_pos - line), '\n');
			*end_line = '\0';
			bio_in = BIO_new_mem_buf(cur_pos, -1);
			b64 = BIO_new(BIO_f_base64());
			BIO_set_flags(b64,BIO_FLAGS_BASE64_NO_NL);
			BIO_push(b64, bio_in);
			while((bytes_read = BIO_read(b64, signature + bytes_read_total, length - bytes_read_total)) > 0)
				bytes_read_total += bytes_read;
			BIO_free_all(b64);
			break;
		}
	}
	fclose(sig_file);
	return(bytes_read_total);
}

int check_file_signings(const char **filenames) {
	char **current_filename = (char **)filenames;
	char resolved_filename[MAX_PATH];
	char signature[MAX_SIG_SIZE];
	int sig_length;
	char *file_mem;
	long int filesize;
	FILE *file;
	int bytes_written = 0, rc = 0, errorcode = 0,error = FALSE;
	EVP_PKEY *public_key;
	EVP_MD_CTX *mdctx = NULL;
	
	// Init openssl
	ERR_load_crypto_strings();
	OpenSSL_add_all_algorithms();
	OPENSSL_config(NULL);
	public_key = EVP_PKEY_new();
	build_public_key(public_key);

	while(**current_filename) {
		if(boinc_resolve_filename(*current_filename, resolved_filename, MAX_PATH))
			{print_error("file_signing", "unable to resolve", *current_filename); error = TRUE; break;}

		sig_length = get_signature(*current_filename, signature, MAX_SIG_SIZE);
		if(sig_length == -1)
			{print_error("file_signing", "reading signatures", NULL); error = TRUE; break;}
		else if(sig_length == 0)
			{print_error("file_signing", "no signature found for", *current_filename); error = TRUE; break;}

		file = fopen(resolved_filename, "rb");
		fseek(file, 0L, SEEK_END);
		filesize = ftell(file);
		file_mem = (char *)OPENSSL_malloc(filesize);
		if(file_mem == NULL)
			{print_error("file_signing", "unable to reserve memory for file", *current_filename); error = TRUE; break;}
		fseek(file, 0L, SEEK_SET);	//rewind to beginning of file
		bytes_written = fread(file_mem, 1, filesize, file);
		if(bytes_written != filesize){
			if(ferror(file))
				{print_error("file_signing", "Error reading file", *current_filename); error = TRUE; break;}
			else if(feof(file))
				{printf("File: %s wrote %i of filesize %i", *current_filename, bytes_written, filesize);}
			else
				{print_error("file_signing", "something strange happened", *current_filename); error = TRUE; break;}
		}


		// Message Digest Context
		if(!(mdctx = EVP_MD_CTX_create()))
			{print_error("file_signing", "unable to create message digest context", NULL); error = TRUE; break;}
		if((rc = EVP_DigestVerifyInit(mdctx, NULL, EVP_sha256(), NULL, public_key)) != 1){
			print_error("file_signing", "calling EVP_DigestVerifyInit", NULL);
			errorcode = ERR_peek_last_error();
			#ifdef DEBUG
			fprintf(stderr, "returned: %i Errorcode: %i\n", rc, errorcode);
			#endif
			ERR_print_errors_fp(stderr);
			error = TRUE; break;}
		if(rc = EVP_DigestVerifyUpdate(mdctx, file_mem, filesize) != 1){
			print_error("file_signing", "calling EVP_DigestVerifyUpdate", NULL);
			error = TRUE; break;}

		if(!EVP_DigestVerifyFinal(mdctx, signature, sig_length))
			{print_error("file_signing", "unable to verify signature of file", *current_filename); error = TRUE; break;}

		OPENSSL_free(file_mem);
		EVP_MD_CTX_destroy(mdctx);
		current_filename++;
	}

	if(error) {
		if(file_mem != NULL)
			OPENSSL_free(file_mem);
		if(mdctx != NULL)
			EVP_MD_CTX_destroy(mdctx);
	}


	if(public_key != NULL) EVP_PKEY_free(public_key);

	CONF_modules_free();
	EVP_cleanup();
	ERR_free_strings();
	if(error)
		return -1;
	return 0;
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

static PyObject *getLicence(PyObject *self, PyObject *args){
	char licence[] = {91, 122, 104, 2, 14, -8, -81, 59, 111, 4, -30, 0};
	simple_crypt(licence, strlen(licence));
	return Py_BuildValue("s", licence);
}

static PyObject *getModellerPath(PyObject *self, PyObject *args){
	char modeller_path[MAX_PATH] = {0};
	getExecPath(modeller_path, MAX_PATH, 1);
	return Py_BuildValue("s", modeller_path);
}

static PyObject *getJobname(PyObject *self, PyObject *args){
	return Py_BuildValue("s", "circ_modeller");
}

static PyMethodDef loader_methods[] = {
	{"getLicence", getLicence, METH_NOARGS, ""},
	{"getModellerPath", getModellerPath, METH_NOARGS, ""},
	{"getJobname", getJobname, METH_NOARGS, ""},
	{NULL, NULL, 0, NULL}
};

void handle_pyerror(const char *errormsg){
	PyObject *ptype, *pvalue, *ptraceback;
	PyErr_Fetch(&ptype, &pvalue, &ptraceback);
	print_error("python", errormsg, PyString_AsString(pvalue));
	if(ptraceback != NULL)
		print_error("python", "Traceback:\n", PyString_AsString(ptraceback));
	Py_XDECREF(ptype);
	Py_XDECREF(pvalue);
	Py_XDECREF(ptraceback);
	Py_Finalize();
}

int call_python(char *ProgramName, char *modeller_path) {
	PyObject *module, *loader, *calc;
	char **argv;

	// Reserve space for resolved filenames
	char *resolved_files[4];
	char file1[MAX_PATH] = { 0 };
	char file2[MAX_PATH] = { 0 };
	char file3[MAX_PATH] = { 0 };
	char file4[MAX_PATH] = { 0 };
	resolved_files[0] = file1;
	resolved_files[1] = file2;
	resolved_files[2] = file3;
	resolved_files[3] = file4;

	int rc;

	argv = &ProgramName;
	// Prevent import of site.py
	Py_NoSiteFlag = 1;

	Py_SetProgramName(ProgramName);

	Py_SetPythonHome(modeller_path);
	Py_Initialize();

	loader = Py_InitModule("loader", loader_methods);

	if(loader == NULL){
		handle_pyerror("importing loader module:\n");
		return -1;
	}

	// Setup Python sys path to include modeller Module
	PySys_SetArgv(1, argv);

	module = PyImport_ImportModule("construct_circ_protein");
	if(module == NULL){
		handle_pyerror("importing Module\n");
		return -2;
	}

	calc = PyObject_GetAttrString(module, "calc");
	if(calc == NULL){
		handle_pyerror("getting Attribute calc:\n");
		return -3;
	}

	// Don't pass first file
	for (int i = 1; i < 4; i++){
		rc = boinc_resolve_filename(used_filenames[i], resolved_files[i-1], MAX_PATH);
		if (rc){
			print_error("resolve files", "unable to resolve filename: ", used_filenames[i]);
			Py_Finalize();
			return -4;
		}
	}

	rc = boinc_resolve_filename(OUTPUT_FILE, resolved_files[3], MAX_PATH);
	if (rc){
		print_error("resolve files", "unable to resolve filename: ", OUTPUT_FILE);
		Py_Finalize();
		return -5;
	}
	PyObject_CallFunction(calc, "ssss", resolved_files[0], resolved_files[1], resolved_files[2], resolved_files[3]);
	

	PyObject *ptype, *pvalue, *ptraceback;
	PyErr_Fetch(&ptype, &pvalue, &ptraceback);
	if (!((ptype == NULL) && (pvalue == NULL) && (ptraceback == NULL))){
		print_error("python", "in modeller execution: ", PyString_AsString(pvalue));
		if(ptraceback != NULL)
			print_error("python", "Traceback:\n", PyString_AsString(ptraceback));
		Py_XDECREF(ptype);
		Py_XDECREF(pvalue);
		Py_XDECREF(ptraceback);
		Py_Finalize();
		return -6;
	}


	Py_Finalize();
	return 0;
}

int main(int argc, char **argv)
{
	char modeller_path[MAX_PATH] = {0};
	char libs_path[MAX_PATH] = {0};
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

	/*	Set Modeller environment variables correctly 						**
	**	and reset PYTHONPATH to avoid loading of locally installed files 	*/

	strncpy(libs_path, modeller_path, MAX_PATH);
	strncat(libs_path, DIR_SLASH "libs.lib", MAX_PATH - strlen(libs_path));
	#ifdef __linux
	setenv("LIBS_LIB9v14", libs_path, 1);
	setenv("PYTHONPATH", ,modeller_path, 1);
	#elif _WIN32
	_putenv_s("LIBS_LIB9v14", libs_path);
	_putenv_s("PYTHONPATH", modeller_path);
	#endif
	
	#ifdef DEBUG
		printf("Setting Modeller install dir: \"%s\"\nSetting path to libs file: \"%s\"\n", modeller_path, libs_path);
	#endif

	rc = call_python(exec_path, modeller_path);
	if (rc < 0){
		print_error("main", "somthing went wrong in python, exiting with errorcode!", NULL);
		fprintf(stderr, "Python Errorcode: %i\n", rc);
		boinc_finish(-1);
	}
	boinc_finish(0);
	return -1;
}
