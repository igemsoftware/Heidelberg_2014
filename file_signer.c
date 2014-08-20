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

void usage(char *prog_name){
	printf("Usage:\n%s private_key output_file boinc_title1 file1 [boinc_title2 file2] ...\n", prog_name);
}

int generate_signature_b64(char *filename, char *signature){

}


int process_files(char **parameters, int param_count){
	int i;
	printf("Boinc filename     Filename           Status\n");
	printf("--------------------------------------------------------\n");
	for(i = 0; i<param_count; i+=2){
		printf("%-18.18s %-18.18s ", parameters[i], parameters[i+1]);
		
		
		printf("%-18.18s\n", "Success");
	}
}

int main(int argc, char **argv){
	char *keyfile, *outputfile;
	char **files;
	if(argc < 5 || ((argc -1)%2) != 0){
		usage(argv[0]);
		exit(-1);
	}
	
	files = argv+3;
	process_files(files, argc - 3);


}