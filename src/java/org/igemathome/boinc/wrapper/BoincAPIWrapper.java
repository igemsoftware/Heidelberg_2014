package org.igemathome.boinc.wrapper;

public class BoincAPIWrapper {
	
	static {
		System.loadLibrary("boincAPIWrapper");
	}

        // run worker thread at normal thread priority on Win.
        // (default is idle priority)
	public int normal_thread_priority;
        // this is the main program, so
        // - lock a lock file in the slot directory
        // - write finish file on successful boinc_finish()
	public int main_program;
        // check for timeout of heartbeats from the client;
        // action is determined by direct_process_action (see below)
	public int check_heartbeat;
        // whether runtime system should read suspend/resume/quit/abort
        // msgs from client.
        // action is determined by direct_process_action (see below)
	public int handle_process_control;
        // whether runtime system should send CPU time / fraction done msgs
	public int send_status_msgs;
        // if heartbeat fail, or get process control msg, take
        // direction action (exit, suspend, resume).
        // Otherwise just set flag in BOINC status
	public int direct_process_action;
        // set this if application creates threads in main process
	public int multi_thread;
        // set this if application creates subprocesses.	
	public int multi_processi;


	public static native int init();

	public static native int finish(int status);

	public static native BoincAppInitData getInitData();

	public static native int parseInitDataFile();

	public static native int sendTrickleUp(String variety, String text);

	public static native int setMinCheckpointPeriod();

	public static native int checkpointCompleted();

	public static native int fractionDone(double fraction);

	public static native int suspendOtherActivities();

	public static native int resumeOtherActivities();

	public static native int reportAppStatus(double cpuTime, double checkpointCpuTime, double fractionDone);

	public static native int timeToCheckpoint();

	public static native void beginnCriticalSection();

	public static native int tryCrititalSection();

	public static native void endCriticalSection();

	public static native void needNetwork();

	public static native int networkPoll();

	public static native void networkDone();

	public static native void networkUsage(double sent, double received);

	public static native int isStandalone();

	//public static native void opsPerCpuSec(double fp, double integer);

	//public static native void opsCumulative(double fp, double integer);

	//public static native void setCreditClaim(double credit);
	
	//public static native int receiveTrickleDown(char[] buf, int len);

	public static native int initOptions(int BOINC_OPTIONS);

	public static native int getStatus(int BOINC_STATUS);

	public static native double getFractionDone();

	//public static native void registerTimerCallback(Runnable callback);
	
	public static native double workerThreadCpuTime();

	//public static native int initParallel();

	//public static native void webGraphicsUrl(String s);

	//public static native void removeDesktopAddr(String s);

	//public static native int setMacPList();

	//public static native int setMacIcon(String filename, char[] iconData, long iconSize);

/*------------------C++ API stuff----------------------------------------------*/
//	public static native int getInitData(Object data);	Already in C code

	public static native int wuCpuTime(double d);

	public static native double elapsedTime();

	public static native int uploadFile(String name);

	public static native int uploadStatus(String name);

	public static native String msgPrefix(String s, int i);

	public static native int reportAppStatusAux(double cpuTime, double checkpointCpuTime,
		 double fractionDone, int otherPID, double bytesSent, double bytesReceived);

	public static native int temporaryExit(int delay, String reason, boolean isNotice);

	public static native String boinc_resolve_filename_s(String logical_filename);

    public static class BoincAppInitData {
        private BoincAppInitData(int major_version, int minor_version, int release, int app_version, String app_name, String symstore, String acct_mgr_url, String project_preferences, int userid, int teamid, int hostid, String user_name, String team_name, String project_dir, String boinc_dir, String wu_name, String result_name, String authenticator, int slot, int client_pid, double user_total_credit, double user_expavg_credit, double host_total_credit, double host_expavg_credit, double resource_share_fraction, int host_info, int proxy_info, int global_prefs, double starting_elapsed_time, boolean using_sandbox, boolean vm_extensions_disabled, double rsc_fpops_est, double rsc_fpops_bound, double rsc_memory_bound, double rsc_disk_bound, double computation_deadline, double fraction_done_start, double fraction_done_end, String gpu_type, int gpu_device_num, int gpu_opencl_dev_index, double gpu_usage, double ncpus, boolean vbox_window, double checkpoint_period, double wu_cpu_time) {
            this.major_version = major_version;
			this.minor_version = minor_version;
			this.release = release;
			this.app_version = app_version;
			this.app_name = app_name;
			this.symstore = symstore;
			this.acct_mgr_url = acct_mgr_url;
			this.project_preferences = project_preferences;
			this.userid = userid;
			this.teamid = teamid;
			this.hostid = hostid;
			this.user_name = user_name;
			this.team_name = team_name;
			this.project_dir = project_dir;
			this.boinc_dir = boinc_dir;
			this.wu_name = wu_name;
			this.result_name = result_name;
			this.authenticator = authenticator;
			this.slot = slot;
			this.client_pid = client_pid;
			this.user_total_credit = user_total_credit;
			this.user_expavg_credit = user_expavg_credit;
			this.host_total_credit = host_total_credit;
			this.host_expavg_credit = host_expavg_credit;
			this.resource_share_fraction = resource_share_fraction;
			this.host_info = host_info;		//Currently only dummy values
			this.proxy_info = proxy_info;	//TODO: Implement
			this.global_prefs = global_prefs;
			this.starting_elapsed_time = starting_elapsed_time;
			this.using_sandbox = using_sandbox;
			this.vm_extensions_disabled = vm_extensions_disabled;
			this.rsc_fpops_est = rsc_fpops_est;
			this.rsc_fpops_bound = rsc_fpops_bound;
			this.rsc_memory_bound = rsc_memory_bound;
			this.rsc_disk_bound = rsc_disk_bound;
			this.computation_deadline = computation_deadline;
			this.fraction_done_start = fraction_done_start;
			this.fraction_done_end = fraction_done_end;
			this.gpu_type = gpu_type;
			this.gpu_device_num = gpu_device_num;
			this.gpu_opencl_dev_index = gpu_opencl_dev_index;
			this.gpu_usage = gpu_usage;
			this.ncpus = ncpus;
			this.vbox_window = vbox_window;
			this.checkpoint_period = checkpoint_period;
			this.wu_cpu_time = wu_cpu_time;
		}

		public String toString(){
			return 	"major_version: "+ this.major_version + "\n" +
					"minor_version: "+ this.minor_version + "\n" +
					"release: "+ this.release + "\n" +
					"app_version: "+ this.app_version + "\n" +
					"app_name: "+ this.app_name + "\n" +
					"symstore: "+ this.symstore + "\n" +
					"acct_mgr_url: "+ this.acct_mgr_url + "\n" +
					"project_preferences: "+ this.project_preferences + "\n" +
					"userid: "+ this.userid + "\n" +
					"teamid: "+ this.teamid + "\n" +
					"hostid: "+ this.hostid + "\n" +
					"user_name: "+ this.user_name + "\n" +
					"team_name: "+ this.team_name + "\n" +
					"project_dir: "+ this.project_dir + "\n" +
					"boinc_dir: "+ this.boinc_dir + "\n" +
					"wu_name: "+ this.wu_name + "\n" +
					"result_name: "+ this.result_name + "\n" +
					"authenticator: "+ this.authenticator + "\n" +
					"slot: "+ this.slot + "\n" +
					"client_pid: "+ this.client_pid + "\n" +
					"user_total_credit: "+ this.user_total_credit + "\n" +
					"user_expavg_credit: "+ this.user_expavg_credit + "\n" +
					"host_total_credit: "+ this.host_total_credit + "\n" +
					"host_expavg_credit: "+ this.host_expavg_credit + "\n" +
					"resource_share_fraction: "+ this.resource_share_fraction + "\n" +
					"starting_elapsed_time: "+ this.starting_elapsed_time + "\n" +
					"using_sandbox: "+ this.using_sandbox + "\n" +
					"vm_extensions_disabled: "+ this.vm_extensions_disabled + "\n" +
					"rsc_fpops_est: "+ this.rsc_fpops_est + "\n" +
					"rsc_fpops_bound: "+ this.rsc_fpops_bound + "\n" +
					"rsc_memory_bound: "+ this.rsc_memory_bound + "\n" +
					"rsc_disk_bound: "+ this.rsc_disk_bound + "\n" +
					"computation_deadline: "+ this.computation_deadline + "\n" +
					"fraction_done_start: "+ this.fraction_done_start + "\n" +
					"fraction_done_end: "+ this.fraction_done_end + "\n" +
					"gpu_type: "+ this.gpu_type + "\n" +
					"gpu_device_num: "+ this.gpu_device_num + "\n" +
					"gpu_opencl_dev_index: "+ this.gpu_opencl_dev_index + "\n" +
					"gpu_usage: "+ this.gpu_usage + "\n" +
					"ncpus: "+ this.ncpus + "\n" +
					"vbox_window: "+ this.vbox_window + "\n" +
					"checkpoint_period: "+ this.checkpoint_period + "\n" +
					"wu_cpu_time: "+ this.wu_cpu_time + "\n";
		}

	    public final int major_version;          // BOINC client version info
	    public final int minor_version;
	    public final int release;
	    public final int app_version;
	    public final String app_name;
	    public final String symstore;         // symstore URL (Windows)
	    public final String acct_mgr_url;
	        // if client is using account manager, its URL
	    public final String project_preferences;
	        // project prefs XML
	    public final int userid;
	        // project's DB ID for this user/team/host
	    public final int teamid;
	    public final int hostid;
	    public final String user_name;
	    public final String team_name;
	    public final String project_dir;      // where project files are stored on host
	    public final String boinc_dir;        // BOINC data directory
	    public final String wu_name;          // workunit name
	    public final String result_name;
	    public final String authenticator;    // user's authenticator
	    public final int slot;                   // the slot this job is running in (0, 1, ...)
	    public final int client_pid;             // process ID of BOINC client
	    public final double user_total_credit;
	    public final double user_expavg_credit;
	    public final double host_total_credit;
	    public final double host_expavg_credit;
	    public final double resource_share_fraction;     // this project's resource share frac
	    public final int host_info;
	    public final int proxy_info;      // in case app wants to use network
	    public final int global_prefs;
	    public final double starting_elapsed_time;   // elapsed time, counting previous episodes
	    public final boolean using_sandbox;         // client is using account-based sandboxing
	    public final boolean vm_extensions_disabled;
	        // client has already been notified that the VM extensions of
	        // the processor have been disabled

	    // info about the WU
	    public final double rsc_fpops_est;
	    public final double rsc_fpops_bound;
	    public final double rsc_memory_bound;
	    public final double rsc_disk_bound;
	    public final double computation_deadline;

	    // the following are used for compound apps,
	    // where each stage of the computation is a fixed fraction of the total.
	    //
	    public final double fraction_done_start;
	    public final double fraction_done_end;

	    // info for GPU apps
	    //
	    public final String gpu_type;
	    public final int gpu_device_num;
	    public final int gpu_opencl_dev_index;
	    public final double gpu_usage;   // APP_VERSION.gpu_usage.usage

	    // info for multicore apps: how many cores to use
	    //
	    public final double ncpus;

	    // client configuration info
	    //
	    public final boolean vbox_window;       // whether to open a console window for VM apps

	    // Items used by the BOINC runtime system
	    //
	    public final double checkpoint_period;     // recommended checkpoint period
	    //public SHMEM_SEG_NAME shmem_seg_name;
	    public final double wu_cpu_time;       // cpu time from previous episodes */
	}
}
