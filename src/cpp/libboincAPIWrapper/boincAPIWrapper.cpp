#include <jni.h>
#include <cstdio>
#include <boinc_api.h>
/* Header for class BoincAPIWrapper */

#ifndef _Included_org_igemathome_boinc_wrapper_BoincAPIWrapper
#define _Included_org_igemathome_boinc_wrapper_BoincAPIWrapper
#ifdef __cplusplus
extern "C" {
#endif
/*
 * Class:     BoincAPIWrapper
 * Method:    init
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_init
  (JNIEnv *, jclass){
    //fclose(stderr); // Very strange workaround for preventing segfault in libboincapi
    return boinc_init();
    //return 1;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    finish
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_finish
  (JNIEnv *, jclass, jint status){
    return boinc_finish(0);
    //exit(0);
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    getInitData
 * Signature: (Ljava/lang/Object;)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_getInitData
  (JNIEnv *, jclass, jobject){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    parseInitDataFile
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_parseInitDataFile
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    sendTrickleUp
 * Signature: (Ljava/lang/String;Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_sendTrickleUp
  (JNIEnv *, jclass, jstring) {
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    setMinCheckpointPeriod
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_setMinCheckpointPeriod
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    checkpointCompleted
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_checkpointCompleted
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    fractionDone
 * Signature: (D)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_fractionDone
  (JNIEnv *, jclass, jdouble){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    suspendOtherActivities
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_suspendOtherActivities
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    resumeOtherActivities
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_resumeOtherActivities
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    reportAppStatus
 * Signature: (DDD)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_reportAppStatus
  (JNIEnv *, jclass, jdouble, jdouble, jdouble);

/*
 * Class:     BoincAPIWrapper
 * Method:    timeToCheckpoint
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_timeToCheckpoint
  (JNIEnv *, jclass);

/*
 * Class:     BoincAPIWrapper
 * Method:    beginnCriticalSection
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_beginnCriticalSection
  (JNIEnv *, jclass){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    tryCrititalSection
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_tryCrititalSection
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    endCriticalSection
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_endCriticalSection
  (JNIEnv *, jclass){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    needNetwork
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_needNetwork
  (JNIEnv *, jclass) {
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    networkPoll
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_networkPoll
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    networkDone
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_networkDone
  (JNIEnv *, jclass){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    networkUsage
 * Signature: (DD)V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_networkUsage
  (JNIEnv *, jclass, jdouble, jdouble){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    isStandalone
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_isStandalone
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    opsPerCpuSec
 * Signature: (DD)V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_opsPerCpuSec
  (JNIEnv *, jclass, jdouble, jdouble){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    opsCumulative
 * Signature: (DD)V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_opsCumulative
  (JNIEnv *, jclass, jdouble, jdouble){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    setCreditClaim
 * Signature: (D)V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_setCreditClaim
  (JNIEnv *, jclass, jdouble){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    receiveTrickleDown
 * Signature: ([CI)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_receiveTrickleDown
  (JNIEnv *, jclass, jcharArray, jint){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    initOptions
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_initOptions
  (JNIEnv *, jclass, jint){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    getStatus
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_getStatus
  (JNIEnv *, jclass, jint){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    getFractionDone
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_getFractionDone
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    registerTimerCallback
 * Signature: (Ljava/lang/Runnable;)V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_registerTimerCallback
  (JNIEnv *, jclass, jobject){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    workerThreadCpuTime
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_workerThreadCpuTime
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    initParallel
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_initParallel
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    webGraphicsUrl
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_webGraphicsUrl
  (JNIEnv *, jclass, jstring){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    removeDesktopAddr
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_removeDesktopAddr
  (JNIEnv *, jclass, jstring){
     return;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    setMacPList
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_setMacPList
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    setMacIcon
 * Signature: (Ljava/lang/String;[CJ)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_setMacIcon
  (JNIEnv *, jclass, jstring, jcharArray, jlong){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    wuCpuTime
 * Signature: (D)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_wuCpuTime
  (JNIEnv *, jclass, jdouble){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    elapsedTime
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_elapsedTime
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    uploadFile
 * Signature: (Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_uploadFile
  (JNIEnv *, jclass, jstring){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    uploadStatus
 * Signature: (Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_uploadStatus
  (JNIEnv *, jclass, jstring){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    msgPrefix
 * Signature: (Ljava/lang/String;I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_msgPrefix
  (JNIEnv *, jclass, jstring, jint){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    reportAppStatusAux
 * Signature: (DDDIDD)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_reportAppStatusAux
  (JNIEnv *, jclass, jdouble, jdouble, jdouble, jint, jdouble, jdouble){
     return 0;
  }

/*
 * Class:     BoincAPIWrapper
 * Method:    temporaryExit
 * Signature: (ILjava/lang/String;Z)I
 */
JNIEXPORT jint JNICALL Java_org_igemathome_boinc_wrapper_BoincAPIWrapper_temporaryExit
  (JNIEnv *, jclass, jint, jstring, jboolean){
     return 0;
  }

#ifdef __cplusplus
}
#endif
#endif
