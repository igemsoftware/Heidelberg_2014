#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/rsa.h>
#include <openssl/engine.h>
#include <openssl/bn.h>
#include <openssl/err.h>
#include <openssl/pem.h>

EVP_PKEY *private_key;
FILE *outputfile;

void print_error(char *place, char *msg, char *param){
	if(param != NULL)
		fprintf(stderr, "ERROR[%-12.12s]: %s %s\n", place, msg, param);
	else
		fprintf(stderr, "ERROR[%-12.12s]: %s\n", place, msg);
}

void usage(char *prog_name){
	printf("Usage:\n%s private_key output_file boinc_title1 file1 [boinc_title2 file2] ...\n", prog_name);
}


int process_files(char **parameters, int param_count){
	int i, success = 0;
	size_t siglen;
	long int filesize=0, bytes_written=0;
	unsigned char *signature, *file_mem;
	char *boincname, *filename;
	EVP_MD_CTX *mdctx = NULL;
	FILE *current_file;
	BIO *b64, *bio_out;
	printf("Boinc filename     Filename           Status\n");
	printf("--------------------------------------------------------\n");
	for(i = 0; i<param_count; i+=2){
		printf("DEBUG: i=%i", i);
		boincname = parameters[i];
		filename = parameters[i+1];
		printf("%-18.18s %-18.18s ", boincname, filename);
		if(!(mdctx = EVP_MD_CTX_create())) goto err;

		if(1 != EVP_DigestSignInit(mdctx, NULL, EVP_sha256(), NULL, private_key)) goto err;

		/* Open file and get size */
		current_file = fopen(filename, "rb");
		if(current_file == NULL)
			{print_error("file_signing", "unable to open file", filename); goto err;}
		fseek(current_file, 0L, SEEK_END);
		filesize = ftell(current_file);
		file_mem = (unsigned char *)OPENSSL_malloc(filesize);
		if(file_mem == NULL)
			{print_error("file_signing", "unable to reserve memory for file", filename); goto err;}
		fseek(current_file, 0L, SEEK_SET);	//rewind to beginning of file

		/* read file to memory */
		bytes_written = fread(file_mem, 1, filesize, current_file);

		if(bytes_written != filesize){
			if(ferror(current_file))
				{print_error("file_signing", "Error reading file", filename); goto err;}
			else if(feof(current_file))
				{printf("File: %s wrote %li of filesize %li", filename, bytes_written, filesize); goto err;}
			else
				{print_error("file_signing", "something strange happened", filename); goto err;}
		}

		if(1 != EVP_DigestSignUpdate(mdctx, file_mem, filesize)) goto err;

		if(1 != EVP_DigestSignFinal(mdctx, NULL, &siglen)) goto err; // Get signature size

		if(!(signature = OPENSSL_malloc(sizeof(unsigned char) * siglen))) goto err;

		if(1 != EVP_DigestSignFinal(mdctx, signature, &siglen)) goto err;
		fwrite(boincname, sizeof(char), strlen(boincname), outputfile);
		fputc(' ', outputfile);
		b64 = BIO_new(BIO_f_base64());
		bio_out = BIO_new_fp(outputfile, BIO_NOCLOSE);
		BIO_set_flags(b64,BIO_FLAGS_BASE64_NO_NL);
		BIO_push(b64, bio_out);
		BIO_write(b64, signature, sizeof(unsigned char) * siglen);
		BIO_flush(b64);
		BIO_free_all(b64);
		fputc('\n', outputfile);

		success = 1;

		printf("%-18.18s\n", "Success!");

		err:
		if(mdctx) EVP_MD_CTX_destroy(mdctx);
		if(current_file) fclose(current_file);
		if(file_mem) OPENSSL_free(file_mem);
		if(signature) OPENSSL_free(signature);
		if(!success)
			printf("%-18.18s\n", "Failed!");
	}
}

int main(int argc, char **argv){
	char *keyfilename, *outputfilename;
	char **files;
	FILE *keyfile;
	char error = 0;
	if(argc < 5 || ((argc -1)%2) != 0){
		usage(argv[0]);
		exit(-1);
	}
	keyfilename = argv[1];
	outputfilename = argv[2];
	
	ERR_load_crypto_strings();
	OpenSSL_add_all_algorithms();
	OPENSSL_config(NULL);


	if(NULL == (keyfile = fopen(keyfilename, "r"))){
		print_error("main", "unable to open private key", keyfilename);
		exit(-1);
	}
	if(NULL == (private_key = PEM_read_PrivateKey(keyfile, NULL, NULL, NULL))){
		print_error("main", "reading private key file. File in PEM format?", keyfilename);
		error = 1; goto error;
	}
	if(NULL == (outputfile = fopen(outputfilename, "w"))){
		print_error("main", "unable to open output file", outputfilename);
		exit(-1);
	}


	files = argv+3;
	process_files(files, argc - 3);
	
	error:
	CONF_modules_free();
	EVP_cleanup();
	ERR_free_strings();
	
	if(keyfile) fclose(keyfile);
	if(outputfile) fclose(outputfile);
	if(error)
		return -1;
	return 0;
}
