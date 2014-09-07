#if __STDC_VERSION__ >= 199901L
#define _XOPEN_SOURCE 600
#else
#define _XOPEN_SOURCE 500
#endif /* __STDC_VERSION__ */
#undef _DEBUG
#include "Python.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#ifdef __linux
#include <dirent.h>
#elif _WIN32
#include "dirent.h"
#endif

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

#include <diagnostics.h>

#include "circ_modeller.h"

// CMAKE vars: APP_NAME, APP_VERSION


#include "config.h"


#include "keys.h"

#define APP_NAME "circ_modeller"
#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define APP_VERSION TOSTRING(APP_MAJOR) "." TOSTRING(APP_MINOR)

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
	EVP_PKEY *public_key = NULL;
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
		if (file == NULL)
			{print_error("file_signing", "unable to open file", resolved_filename); error = TRUE; break;}
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
				{fprintf(stderr, "File: %s wrote %i of filesize %i", *current_filename, bytes_written, filesize);}
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
		file_mem = NULL;
		mdctx = NULL;
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

int unzip_resources(char *basedir, char *libs, char *mdt) {
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
	mkdir(basedir);
    if(!fileExists(unzip_lock_finished)) {
    	if(createFailIfExists(unzip_lock_started) < 0){	// Lockfile exists --> other process extracting
    		/* Wait max 5 minutes for process to finish */
    		fprintf(stderr, "Other process allready extracting...\n");
    		boinc_temporary_exit_wrapper(20, "Other process allready extracting\n", FALSE);
    		return -1; 
    	}
    	else {								// Lockfile does not exist --> extract data
    		boinc_resolve_filename(RESOURCES_ZIP, unzip_file, MAX_PATH);
        	if(fileExists(unzip_file)) {
				rc = boinc_zip(UNZIP_IT, unzip_file, basedir);
				#ifdef DEBUG
				fprintf(stderr, "Unzip routine returned %i\n", rc);
				#endif
				if (rewrite_libs(libs) < 0) {
					print_error("Unzip", "rewrite_libs (libs.lib) failed", NULL);
				}
				if (rewrite_libs(mdt) < 0) {
					print_error("Unzip", "rewrite_libs (mdt.lib) failed", NULL);
				}
					
				lockfile = fopen(unzip_lock_finished, "w");
				fclose(lockfile);
				return rc;
        	}
			else {
				fprintf(stderr, "%s does not exist. Aborting...\n", unzip_file);
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
    for(i = 0; i < array_size; i++)
        array[i] ^= secret[i];
}

void handle_pyerror(const char *errormsg){
	PyObject *ptype, *pvalue, *ptraceback;
	PyErr_Fetch(&ptype, &pvalue, &ptraceback);
	print_error("python", errormsg, PyString_AsString(ptype));
	if (pvalue != NULL)
		print_error("python", "pvalue:\n", PyString_AsString(pvalue));
	if (ptraceback != NULL)
		print_error("python", "Traceback:\n", PyString_AsString(ptraceback));
	Py_XDECREF(ptype);
	Py_XDECREF(pvalue);
	Py_XDECREF(ptraceback);
	Py_Finalize();
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

static PyObject *logFunction(PyObject *self, PyObject *args){
	char *logstring;
	if (!PyArg_ParseTuple(args, "s", &logstring)){
		handle_pyerror("Parsing args tuble in log function");
		return 0;
	}
	int chars_written = fprintf(stderr, "%s\n", logstring);
	return Py_BuildValue("i", chars_written);

	
}

static PyMethodDef loader_methods[] = {
	{"getLicence", getLicence, METH_NOARGS, ""},
	{"getModellerPath", getModellerPath, METH_NOARGS, ""},
	{"getJobname", getJobname, METH_NOARGS, ""},
	{"log", logFunction, METH_VARARGS, "" },
	{NULL, NULL, 0, NULL}
};
#ifdef DEBUG
char* getPythonTraceback()
{
	// Python equivilant:
	// import traceback, sys
	// return "".join(traceback.format_exception(sys.exc_type,
	//    sys.exc_value, sys.exc_traceback))

	PyObject *type, *value, *traceback;
	PyObject *tracebackModule;
	char *chrRetval;

	PyErr_Fetch(&type, &value, &traceback);

	tracebackModule = PyImport_ImportModule("traceback");
	if (tracebackModule != NULL)
	{
		PyObject *tbList, *emptyString, *strRetval;

		tbList = PyObject_CallMethod(
			tracebackModule,
			"format_exception",
			"OOO",
			type,
			value == NULL ? Py_None : value,
			traceback == NULL ? Py_None : traceback);

		emptyString = PyString_FromString("");
		strRetval = PyObject_CallMethod(emptyString, "join",
			"O", tbList);

		chrRetval = strdup(PyString_AsString(strRetval));

		Py_DECREF(tbList);
		Py_DECREF(emptyString);
		Py_DECREF(strRetval);
		Py_DECREF(tracebackModule);
	}
	else
	{
		chrRetval = strdup("Unable to import traceback module.");
	}

	Py_DECREF(type);
	Py_XDECREF(value);
	Py_XDECREF(traceback);

	return chrRetval;
}
#endif

int call_python(char *ProgramName, char *modeller_path) {
	PyObject *module, *loader, *calc;
	char **argv;
	long cretval = 0;

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
#ifdef DEBUG
		char *traceback = getPythonTraceback();
		print_error("python", "importing loader module", traceback);
		free(traceback);
		Py_Finalize();
#else
		handle_pyerror("importing loader module:\n");
#endif
		return -1;
	}

	// Setup Python sys path to include modeller Module
	PySys_SetArgv(1, argv);

	module = PyImport_ImportModule("construct_circ_protein");
	if(module == NULL){
#ifdef DEBUG
		char *traceback = getPythonTraceback();
		print_error("python", "importing construct_circ_protein module", traceback);
		free(traceback);
		Py_Finalize();
#else
		handle_pyerror("importing Module\n");
#endif
		//handle_pyerror("importing Module\n");
		//PyErr_Print();
		return -2;
	}

	calc = PyObject_GetAttrString(module, "calc");
	if(calc == NULL){
#ifdef DEBUG
		char *traceback = getPythonTraceback();
		print_error("python", "getting calc attribute", traceback);
		free(traceback);
		Py_Finalize();
#else
		handle_pyerror("getting calc attribute\n");
#endif
		return -3;
	}

	// Don't pass first file
	for (int i = 0; i < 3; i++){
		rc = boinc_resolve_filename(used_filenames[i], resolved_files[i], MAX_PATH);
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


	fprintf(stderr, "Calling Python Method with Arguments: %s, %s, %s, %s\n", resolved_files[0], resolved_files[1], resolved_files[2], resolved_files[3]);

	PyObject *retval = PyObject_CallFunction(calc, "sssss", APP_NAME "-" APP_VERSION, resolved_files[0], resolved_files[1], resolved_files[2], resolved_files[3]);
	if (retval != Py_None)
		cretval = PyInt_AsLong(retval);
	/*
#ifdef DEBUG
	if (cretval != -1){
		print_error("python", "got ret value:", NULL);
		fprintf(stderr, "%il\n", cretval);
	}
	else{
		print_error("python", "unable to get return value", NULL);
		if (PyErr_Occurred() != NULL){
			char *traceback = getPythonTraceback();
			print_error("python", "in modeller execution", traceback);
			free(traceback);
			//handle_pyerror("in modeller execution\n");
			return -6;
		}
	}
#endif */
	if (PyErr_Occurred() != NULL){
#ifdef DEBUG
		char *traceback = getPythonTraceback();
		print_error("python", "in modeller execution", traceback);
		free(traceback);
		Py_Finalize();
#else
		handle_pyerror("in modeller execution\n");
#endif
		return -6;
	}

	Py_Finalize();
	return 0;
}

char *str_replace(char *orig, char *rep, char *with) {
	char *result; // the return string
	char *ins;    // the next insert point
	char *tmp;    // varies
	int len_rep;  // length of rep
	int len_with; // length of with
	int len_front; // distance between rep and end of last rep
	int count;    // number of replacements

	if (!orig)
		return NULL;
	if (!rep)
		rep = "";
	len_rep = strlen(rep);
	if (!with)
		with = "";
	len_with = strlen(with);

	ins = orig;
	for (count = 0; tmp = strstr(ins, rep); ++count) {
		ins = tmp + len_rep;
	}

	// first time through the loop, all the variable are set correctly
	// from here on,
	//    tmp points to the end of the result string
	//    ins points to the next occurrence of rep in orig
	//    orig points to the remainder of orig after "end of rep"
	tmp = result = malloc(strlen(orig) + (len_with - len_rep) * count + 1);

	if (!result)
		return NULL;

	while (count--) {
		ins = strstr(orig, rep);
		len_front = ins - orig;
		tmp = strncpy(tmp, orig, len_front) + len_front;
		tmp = strcpy(tmp, with) + len_with;
		orig += len_front + len_rep; // move to next "end of rep"
	}
	strcpy(tmp, orig);
	return result;
}

int rewrite_libs(char *libs){
	FILE *libs_file;
	long filesize = 0;
	char * file_mem;
	int bytes_written = 0;
	char *new_libs;

	libs_file = fopen(libs, "rb+");

	if (libs_file == NULL)
	{
		print_error("rewrite_libs", "unable to open file", libs);
		return -1;
	}
	fseek(libs_file, 0L, SEEK_END);
	filesize = ftell(libs_file);
	file_mem = (char *)malloc(filesize+1);
	if (file_mem == NULL){
		print_error("rewrite_libs", "unable to reserve memory for file", libs);
		fclose(libs_file);
		return -1;
	}
	
	fseek(libs_file, 0L, SEEK_SET);	//rewind to beginning of file
	bytes_written = fread(file_mem, 1, filesize, libs_file);
	if (bytes_written != filesize){
		if (ferror(libs_file))
			print_error("rewrite_libs", "Error reading file", libs);
		else if (feof(libs_file))
			fprintf(stderr, "File: %s wrote %i of filesize %i", libs, bytes_written, filesize);
		else
			print_error("file_signing", "something strange happened", libs);

		fclose(libs_file);
		free(file_mem);
		return -1;
	}
	*(file_mem + filesize) = '\0';
	new_libs = str_replace(file_mem, "VERSION", APP_NAME "-"APP_VERSION);
	fseek(libs_file, 0L, SEEK_SET);
	fwrite(new_libs, sizeof(char), strlen(new_libs), libs_file);
	fflush(libs_file);
	fclose(libs_file);
	free(new_libs);
	free(file_mem);
	return 0;
}

int delete_old_versions(char *basedir){
	struct dirent *entry;
	printf("Searching in dir %s for old versions\n", basedir);
	char delete_path[MAX_PATH] = { 0 };
	DIR *dir = { 0 };
	int app_major = 0, app_minor = 0;

	dir = opendir(basedir);
	if (dir == NULL){
		print_error("delete_old_files", "unable to open basedir", NULL);
		return -1;
	}
	while (entry = readdir(dir)){
		if (entry->d_type == DT_DIR){
			app_major = app_minor = 0;
			int count = sscanf(entry->d_name, APP_NAME"-%i.%i", &app_major, &app_minor);
			if (count == 2)
			{	
				if (app_major <= APP_MAJOR){
					if (app_minor < APP_MINOR || app_major < APP_MAJOR){
						strncpy(delete_path, basedir, MAX_PATH);
						strncat(delete_path, DIR_SLASH, MAX_PATH - strlen(delete_path));
						strncat(delete_path, entry->d_name, MAX_PATH - strlen(delete_path));
						print_error("delete_old_files", "Deleting: ", delete_path);
						DeleteDirectory(delete_path, 1);
					}
				}

			}
		}
	}
	closedir(dir);
	return 0;
}

int main(int argc, char **argv)
{
	char modeller_path[MAX_PATH] = {0};
	char libs_path[MAX_PATH] = {0};
	char mdt_path[MAX_PATH] = { 0 };
	char exec_path[MAX_PATH] = { 0 };
	char pylib_path[MAX_PATH] = { 0 };
	//char resolved_logfile[MAX_PATH] = { 0 };
	int rc;

	boinc_init();

	// Get Paths and append version path

	getExecPath(modeller_path, MAX_PATH, 1);
	delete_old_versions(modeller_path);
	strncat(modeller_path, DIR_SLASH APP_NAME "-"APP_VERSION, MAX_PATH-strlen(modeller_path));
	strcpy(pylib_path, modeller_path);
	strncat(pylib_path, DIR_SLASH "DLLs", MAX_PATH - strlen(pylib_path));
	getExecPath(exec_path, MAX_PATH, 0);
	//strncat(exec_path, DIR_SLASH APP_NAME "-"APP_VERSION, MAX_PATH - strlen(exec_path));

	strncpy(libs_path, modeller_path, MAX_PATH);
	strncat(libs_path, DIR_SLASH "libs.lib", MAX_PATH - strlen(libs_path));

	strncpy(mdt_path, modeller_path, MAX_PATH);
	strncat(mdt_path, DIR_SLASH "mdt.lib", MAX_PATH - strlen(mdt_path));
//#ifdef DEBUG
	// TODO, workaround for debugging in visual studio
	//chdir(modeller_path);
//#endif

	#ifdef DEBUG
	/* get following error when used:
		ERROR[python      ]: importing construce module Traceback (most recent call last):
		  File "C:\Users\Max\iGEM\modeller_resources_win\packaging\bla\construct_circ_protein.py", line 1, in <module>
			from modeller import *
		  File "C:\Program Files (x86)\Modeller9.14\modlib\modeller\__init__.py", line 108, in <module>
			print "Running in loader! Getting config from C functions."
		IOError: (9, 'Bad file descriptor')
		Reason: No Idea.. maybe because of different library versions when compiling (c-program / python 
		*/
		//freopen(STDERR_FILE,"a",stdout); // also redirect stdout to stderr
	#endif

	rc = unzip_resources(modeller_path, libs_path, mdt_path); // Extract modeller resource files if not existent
	if(rc < 0){
		printf("Temporary exiting...\n");
		boinc_temporary_exit_wrapper(20, "Something went wrong while extracting!\n", FALSE);
	}

	if(check_file_signings((const char **)used_filenames))
		{print_error("main", "verifying files failed!", NULL); boinc_finish(-1);}

	/*	Set Modeller environment variables correctly 						**
	**	and reset PYTHONPATH to avoid loading of locally installed files 	*/


	#ifdef __linux
	setenv("LIBS_LIB9v14", libs_path, 1);
	setenv("PYTHONPATH", modeller_path, 1);
	setenv("NUITKA_IMPORT_PATH", pylib_path, 1);
	#elif _WIN32
	_putenv_s("LIBS_LIB9v14", libs_path);
	_putenv_s("PYTHONPATH", modeller_path);
	_putenv_s("NUITKA_IMPORT_PATH", pylib_path);
	#endif
	
	#ifdef DEBUG
		fprintf(stderr, "Setting Modeller install dir: \"%s\"\nSetting path to libs file: \"%s\"\n", modeller_path, libs_path);
	#endif
	/*
	boinc_resolve_filename(LOGFILE, resolved_logfile, MAX_PATH);
	mylogfile = fopen(resolved_logfile, "w");
	if (mylogfile == NULL){
		print_error("main", "unable to open logfile!", NULL);
	}
	*/
	rc = call_python(exec_path, modeller_path);
	if (rc < 0){
		//if(mylogfile != NULL)
		//	fclose(mylogfile);
		print_error("main", "somthing went wrong in python, exiting with errorcode!", NULL);
		fprintf(stderr, "Python Errorcode: %i\n", rc);
		boinc_finish(-1);
	}

	/*
	if (mylogfile != NULL)
		fclose(mylogfile);
	remove(resolved_logfile);
	*/

	boinc_finish(0);
	return -1;
}
