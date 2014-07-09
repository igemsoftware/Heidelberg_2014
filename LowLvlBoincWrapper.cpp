#include <jni.h>
#include <cstdio>
/* Header for class LowLvlBoincWrapper */

#ifndef _Included_LowLvlBoincWrapper
#define _Included_LowLvlBoincWrapper
#ifdef __cplusplus
extern "C" {
#endif
/*
 * Class:     LowLvlBoincWrapper
 * Method:    init
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_init
  (JNIEnv *, jclass){
	printf("Welcome to C++\n");
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    finish
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_finish
  (JNIEnv *, jclass, jint){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    getInitData
 * Signature: (Ljava/lang/Object;)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_getInitData
  (JNIEnv *, jclass, jobject){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    parseInitDataFile
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_parseInitDataFile
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    sendTrickleUp
 * Signature: (Ljava/lang/String;Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_sendTrickleUp
  (JNIEnv *, jclass, jstring) {
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    setMinCheckpointPeriod
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_setMinCheckpointPeriod
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    checkpointCompleted
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_checkpointCompleted
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    fractionDone
 * Signature: (D)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_fractionDone
  (JNIEnv *, jclass, jdouble){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    suspendOtherActivities
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_suspendOtherActivities
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    resumeOtherActivities
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_resumeOtherActivities
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    reportAppStatus
 * Signature: (DDD)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_reportAppStatus
  (JNIEnv *, jclass, jdouble, jdouble, jdouble);

/*
 * Class:     LowLvlBoincWrapper
 * Method:    timeToCheckpoint
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_timeToCheckpoint
  (JNIEnv *, jclass);

/*
 * Class:     LowLvlBoincWrapper
 * Method:    beginnCriticalSection
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_beginnCriticalSection
  (JNIEnv *, jclass){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    tryCrititalSection
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_tryCrititalSection
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    endCriticalSection
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_endCriticalSection
  (JNIEnv *, jclass){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    needNetwork
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_needNetwork
  (JNIEnv *, jclass) {
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    networkPoll
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_networkPoll
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    networkDone
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_networkDone
  (JNIEnv *, jclass){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    networkUsage
 * Signature: (DD)V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_networkUsage
  (JNIEnv *, jclass, jdouble, jdouble){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    isStandalone
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_isStandalone
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    opsPerCpuSec
 * Signature: (DD)V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_opsPerCpuSec
  (JNIEnv *, jclass, jdouble, jdouble){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    opsCumulative
 * Signature: (DD)V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_opsCumulative
  (JNIEnv *, jclass, jdouble, jdouble){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    setCreditClaim
 * Signature: (D)V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_setCreditClaim
  (JNIEnv *, jclass, jdouble){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    receiveTrickleDown
 * Signature: ([CI)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_receiveTrickleDown
  (JNIEnv *, jclass, jcharArray, jint){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    initOptions
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_initOptions
  (JNIEnv *, jclass, jint){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    getStatus
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_getStatus
  (JNIEnv *, jclass, jint){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    getFractionDone
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_LowLvlBoincWrapper_getFractionDone
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    registerTimerCallback
 * Signature: (Ljava/lang/Runnable;)V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_registerTimerCallback
  (JNIEnv *, jclass, jobject){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    workerThreadCpuTime
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_LowLvlBoincWrapper_workerThreadCpuTime
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    initParallel
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_initParallel
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    webGraphicsUrl
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_webGraphicsUrl
  (JNIEnv *, jclass, jstring){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    removeDesktopAddr
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_LowLvlBoincWrapper_removeDesktopAddr
  (JNIEnv *, jclass, jstring){
     return;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    setMacPList
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_setMacPList
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    setMacIcon
 * Signature: (Ljava/lang/String;[CJ)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_setMacIcon
  (JNIEnv *, jclass, jstring, jcharArray, jlong){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    wuCpuTime
 * Signature: (D)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_wuCpuTime
  (JNIEnv *, jclass, jdouble){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    elapsedTime
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_LowLvlBoincWrapper_elapsedTime
  (JNIEnv *, jclass){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    uploadFile
 * Signature: (Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_uploadFile
  (JNIEnv *, jclass, jstring){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    uploadStatus
 * Signature: (Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_uploadStatus
  (JNIEnv *, jclass, jstring){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    msgPrefix
 * Signature: (Ljava/lang/String;I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_LowLvlBoincWrapper_msgPrefix
  (JNIEnv *, jclass, jstring, jint){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    reportAppStatusAux
 * Signature: (DDDIDD)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_reportAppStatusAux
  (JNIEnv *, jclass, jdouble, jdouble, jdouble, jint, jdouble, jdouble){
     return 0;
  }

/*
 * Class:     LowLvlBoincWrapper
 * Method:    temporaryExit
 * Signature: (ILjava/lang/String;Z)I
 */
JNIEXPORT jint JNICALL Java_LowLvlBoincWrapper_temporaryExit
  (JNIEnv *, jclass, jint, jstring, jboolean){
     return 0;
  }

#ifdef __cplusplus
}
#endif
#endif
