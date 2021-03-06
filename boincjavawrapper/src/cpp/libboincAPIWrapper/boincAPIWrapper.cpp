#include <jni.h>
#include <cstdio>
#include <string>
#include <boinc_api.h>
/* Header for class BoincAPIWrapper */

#define ERROR_BUFF_SIZE 250

#ifndef _Included_org_igemathome_wrapper_BoincAPIWrapper
#define _Included_org_igemathome_wrapper_BoincAPIWrapper
#ifdef __cplusplus
extern "C" {
#endif



/*
* Class:     BoincAPIWrapper
* Method:    init
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_init(JNIEnv *env, jclass){
  return boinc_init();
}

/*
* Class:     BoincAPIWrapper
* Method:    finish
* Signature: (I)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_finish(JNIEnv *env, jclass, jint status){
  return boinc_finish(status);
}

/*
* Class:     BoincAPIWrapper
* Method:    getInitData
* Signature: (Ljava/lang/Object;)I
*/
JNIEXPORT jobject JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_getInitData(JNIEnv *env, jclass jthis){
  struct APP_INIT_DATA app_init_data;
  printf("boinc_getInitData(APP_INIT_DATA): %i\n",boinc_get_init_data(app_init_data));
  jstring app_name = env->NewStringUTF((const char *) &app_init_data.app_name);
  jstring symstore = env->NewStringUTF((const char *) &app_init_data.symstore);
  jstring acct_mgr_url = env->NewStringUTF((const char *) &app_init_data.acct_mgr_url);
  jstring project_preferences = env->NewStringUTF((const char *) &app_init_data.project_preferences);
  jstring user_name = env->NewStringUTF((const char *) &app_init_data.user_name);
  jstring team_name = env->NewStringUTF((const char *) &app_init_data.team_name);
  jstring project_dir = env->NewStringUTF((const char *) &app_init_data.project_dir);
  jstring boinc_dir = env->NewStringUTF((const char *) &app_init_data.boinc_dir);
  jstring wu_name = env->NewStringUTF((const char *) &app_init_data.wu_name);
  jstring result_name = env->NewStringUTF((const char *) &app_init_data.result_name);
  jstring authenticator = env->NewStringUTF((const char *) &app_init_data.authenticator);
  jstring gpu_type = env->NewStringUTF((const char *) &app_init_data.gpu_type);

  jclass AppInitDataClass;
  jobject appInitData;
  jmethodID constructor;
  AppInitDataClass = env->FindClass("org/igemathome/boinc/wrapper/BoincAPIWrapper$BoincAppInitData");
  constructor = env->GetMethodID(AppInitDataClass, "<init>", "(IIIILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIDDDDDIIIDZZDDDDDDDLjava/lang/String;IIDDZDD)V");
  
  appInitData = env->NewObject( AppInitDataClass, constructor,
                                app_init_data.major_version,
                                app_init_data.minor_version,
                                app_init_data.release,
                                app_init_data.app_version,
                                app_name,
                                symstore,
                                acct_mgr_url,
                                project_preferences,
                                app_init_data.userid,
                                app_init_data.teamid,
                                app_init_data.hostid,
                                user_name,
                                team_name,
                                project_dir,
                                boinc_dir,
                                wu_name,
                                result_name,
                                authenticator,
                                app_init_data.slot,
                                app_init_data.client_pid,
                                app_init_data.user_total_credit,
                                app_init_data.user_expavg_credit,
                                app_init_data.host_total_credit,
                                app_init_data.host_expavg_credit,
                                app_init_data.resource_share_fraction,
                                -1, //host_info not 
                                -1, //proxy_info
                                -1, //global_prefs
                                app_init_data.starting_elapsed_time,
                                app_init_data.using_sandbox,
                                app_init_data.vm_extensions_disabled,
                                app_init_data.rsc_fpops_est,
                                app_init_data.rsc_fpops_bound,
                                app_init_data.rsc_memory_bound,
                                app_init_data.rsc_disk_bound,
                                app_init_data.computation_deadline,
                                app_init_data.fraction_done_start,
                                app_init_data.fraction_done_end,
                                gpu_type,
                                app_init_data.gpu_device_num,
                                app_init_data.gpu_opencl_dev_index,
                                app_init_data.gpu_usage,
                                app_init_data.ncpus,
                                app_init_data.vbox_window,
                                app_init_data.checkpoint_period,
                                app_init_data.wu_cpu_time);
  return appInitData;
  //env->CallStaticVoidMethod(AppInitDataClass, initDatam);
  //AppInitData = env->NewObject(AppInitDataClass,constructor, 123);
}

/*
* Class:     BoincAPIWrapper
* Method:    parseInitDataFile
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_parseInitDataFile(JNIEnv *env, jclass){
  return boinc_parse_init_data_file();
}

/*
* Class:     BoincAPIWrapper
* Method:    sendTrickleUp
* Signature: (Ljava/lang/String;Ljava/lang/String;)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_sendTrickleUp(JNIEnv *env, jclass, jstring variety, jstring text) {
  int rc;
  const char *variety_ptr;
  const char *text_ptr;

  variety_ptr = env->GetStringUTFChars(variety, 0);
  text_ptr = env->GetStringUTFChars(text, 0);
  
  rc = boinc_send_trickle_up((char *)variety_ptr, (char *)text_ptr);

  env->ReleaseStringUTFChars(variety, variety_ptr);
  env->ReleaseStringUTFChars(text, text_ptr);

  return rc;
}

/*
* Class:     BoincAPIWrapper
* Method:    setMinCheckpointPeriod
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_setMinCheckpointPeriod(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    checkpointCompleted
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_checkpointCompleted(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    fractionDone
* Signature: (D)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_fractionDone(JNIEnv *env, jclass, jdouble fraction_done){
  char error_buff[ERROR_BUFF_SIZE];
  if(!( (0 <= fraction_done) && (fraction_done <= 1) ) ){ // fraction_done value must be between 0 and 1
    sprintf(error_buff, "parameter fraction_done (value: %d) is out of range (0 <= fraction_done <= 1)", fraction_done);
    env->ThrowNew(env->FindClass("java/lang/IllegalArgumentException"), error_buff);
    return -1;
  }

  return boinc_fraction_done(fraction_done);
}

/*
* Class:     BoincAPIWrapper
* Method:    suspendOtherActivities
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_suspendOtherActivities(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    resumeOtherActivities
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_resumeOtherActivities(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    reportAppStatus
* Signature: (DDD)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_reportAppStatus(JNIEnv *env, jclass, jdouble, jdouble, jdouble){

}

/*
* Class:     BoincAPIWrapper
* Method:    timeToCheckpoint
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_timeToCheckpoint(JNIEnv *env, jclass){

}

/*
* Class:     BoincAPIWrapper
* Method:    beginnCriticalSection
* Signature: ()V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_beginnCriticalSection(JNIEnv *env, jclass){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    tryCrititalSection
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_tryCrititalSection(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    endCriticalSection
* Signature: ()V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_endCriticalSection(JNIEnv *env, jclass){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    needNetwork
* Signature: ()V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_needNetwork(JNIEnv *env, jclass) {
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    networkPoll
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_networkPoll(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    networkDone
* Signature: ()V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_networkDone(JNIEnv *env, jclass){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    networkUsage
* Signature: (DD)V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_networkUsage(JNIEnv *env, jclass, jdouble, jdouble){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    isStandalone
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_isStandalone(JNIEnv *env, jclass){
  return boinc_is_standalone();
}

/*
* Class:     BoincAPIWrapper
* Method:    opsPerCpuSec
* Signature: (DD)V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_opsPerCpuSec(JNIEnv *env, jclass, jdouble, jdouble){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    opsCumulative
* Signature: (DD)V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_opsCumulative(JNIEnv *env, jclass, jdouble, jdouble){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    setCreditClaim
* Signature: (D)V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_setCreditClaim(JNIEnv *env, jclass, jdouble){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    receiveTrickleDown
* Signature: ([CI)I
*/
  JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_receiveTrickleDown(JNIEnv *env, jclass, jcharArray, jint){
    
    return 0;
  }

/*
* Class:     BoincAPIWrapper
* Method:    initOptions
* Signature: (I)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_initOptions(JNIEnv *env, jclass, jint){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    getStatus
* Signature: (I)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_getStatus(JNIEnv *env, jclass, jint){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    getFractionDone
* Signature: ()D
*/
JNIEXPORT jdouble JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_getFractionDone(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    registerTimerCallback
* Signature: (Ljava/lang/Runnable;)V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_registerTimerCallback(JNIEnv *env, jclass, jobject){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    workerThreadCpuTime
* Signature: ()D
*/
JNIEXPORT jdouble JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_workerThreadCpuTime(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    initParallel
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_initParallel(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    webGraphicsUrl
* Signature: (Ljava/lang/String;)V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_webGraphicsUrl(JNIEnv *env, jclass, jstring){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    removeDesktopAddr
* Signature: (Ljava/lang/String;)V
*/
JNIEXPORT void JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_removeDesktopAddr(JNIEnv *env, jclass, jstring){
  return;
}

/*
* Class:     BoincAPIWrapper
* Method:    setMacPList
* Signature: ()I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_setMacPList(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    setMacIcon
* Signature: (Ljava/lang/String;[CJ)I
*/
  JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_setMacIcon(JNIEnv *env, jclass, jstring, jcharArray, jlong){
    return 0;
  }

/*
* Class:     BoincAPIWrapper
* Method:    wuCpuTime
* Signature: (D)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_wuCpuTime(JNIEnv *env, jclass, jdouble){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    elapsedTime
* Signature: ()D
*/
JNIEXPORT jdouble JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_elapsedTime(JNIEnv *env, jclass){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    uploadFile
* Signature: (Ljava/lang/String;)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_uploadFile(JNIEnv *env, jclass, jstring){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    uploadStatus
* Signature: (Ljava/lang/String;)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_uploadStatus(JNIEnv *env, jclass, jstring){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    msgPrefix
* Signature: (Ljava/lang/String;I)Ljava/lang/String;
*/
JNIEXPORT jstring JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_msgPrefix(JNIEnv *env, jclass, jstring, jint){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    reportAppStatusAux
* Signature: (DDDIDD)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_reportAppStatusAux(JNIEnv *env, jclass, jdouble, jdouble, jdouble, jint, jdouble, jdouble){
  return 0;
}

/*
* Class:     BoincAPIWrapper
* Method:    temporaryExit
* Signature: (ILjava/lang/String;Z)I
*/
JNIEXPORT jint JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_temporaryExit(JNIEnv *env, jclass, jint delay, jstring reason, jboolean is_notice){
  const char *reason_ptr;
  int rc;

  reason_ptr = env->GetStringUTFChars(reason, 0);
  rc = boinc_temporary_exit(delay, reason_ptr, is_notice);
  env->ReleaseStringUTFChars(reason, reason_ptr);

  return rc;
}

/*
 * Class:     org_igemathome_wrapper_BoincAPIWrapper
 * Method:    resolveFilename
 * Signature: (Ljava/lang/String;)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_org_igemathome_wrapper_BoincAPIWrapper_resolveFilename(JNIEnv *env, jclass, jstring logical_filename){
    char error_buff[ERROR_BUFF_SIZE];
    std::string physical_filename;
    const char *logical_filename_ptr;
    int rc;

    logical_filename_ptr = env->GetStringUTFChars(logical_filename, 0);
    rc = boinc_resolve_filename_s(logical_filename_ptr, physical_filename);
    env->ReleaseStringUTFChars(logical_filename, logical_filename_ptr);

    if(rc != 0) {
      sprintf(error_buff, "boinc_resolve_filename returned: %i", rc);
      env->ThrowNew(env->FindClass("java/io/FileNotFoundException"), error_buff);
      return NULL;
    }
    
    return env->NewStringUTF(physical_filename.c_str());
}


#ifdef __cplusplus
}
#endif
#endif
