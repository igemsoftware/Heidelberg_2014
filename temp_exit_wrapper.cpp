#include <boinc_api.h>
extern "C" int boinc_temporary_exit_wrapper(int delay, const char *reason, int is_notice){
	if (is_notice)
		return boinc_temporary_exit(delay,reason, true);
	else
		return boinc_temporary_exit(delay, reason, false);
}

