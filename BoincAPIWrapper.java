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

	public static native int getInitData(Object appInitData);

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

	public static native void opsPerCpuSec(double fp, double integer);

	public static native void opsCumulative(double fp, double integer);

	public static native void setCreditClaim(double credit);
	
	public static native int receiveTrickleDown(char[] buf, int len);

	public static native int initOptions(int BOINC_OPTIONS);

	public static native int getStatus(int BOINC_STATUS);

	public static native double getFractionDone();

	public static native void registerTimerCallback(Runnable callback);
	
	public static native double workerThreadCpuTime();

	public static native int initParallel();

	public static native void webGraphicsUrl(String s);

	public static native void removeDesktopAddr(String s);

	public static native int setMacPList();

	public static native int setMacIcon(String filename, char[] iconData, long iconSize);


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


}
