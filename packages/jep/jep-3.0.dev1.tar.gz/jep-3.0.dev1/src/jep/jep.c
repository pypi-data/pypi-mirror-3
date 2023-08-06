/* -*- Mode: C; indent-tabs-mode: nil; c-basic-offset: 4 c-style: "K&R" -*- */
/* 
   jep - Java Embedded Python

   Copyright (c) 2004 - 2011 Mike Johnson.

   This file is licenced under the the zlib/libpng License.

   This software is provided 'as-is', without any express or implied
   warranty. In no event will the authors be held liable for any
   damages arising from the use of this software.
   
   Permission is granted to anyone to use this software for any
   purpose, including commercial applications, and to alter it and
   redistribute it freely, subject to the following restrictions:

   1. The origin of this software must not be misrepresented; you
   must not claim that you wrote the original software. If you use
   this software in a product, an acknowledgment in the product
   documentation would be appreciated but is not required.

   2. Altered source versions must be plainly marked as such, and
   must not be misrepresented as being the original software.

   3. This notice may not be removed or altered from any source
   distribution.   
*/

#include "util.h"
#include "jep.h"
#include "pyembed.h"


#ifdef WIN32
# include "winconfig.h"

BOOL APIENTRY DllMain(HANDLE hModule,
                      DWORD  ul_reason_for_call,
                      LPVOID lpReserved) {
	return TRUE;
}
#endif


// -------------------------------------------------- jni functions


JNIEXPORT jint JNICALL
JNI_OnLoad(JavaVM *vm, void *reserved) {
    pyembed_startup();
    return JNI_VERSION_1_2;
}


JNIEXPORT void JNICALL
JNI_OnUnload(JavaVM *vm, void *reserved) {
    pyembed_shutdown();
}


/*
 * Class:     jep_Jep
 * Method:    init
 * Signature: (Ljava/lang/ClassLoader;)I
 */
JNIEXPORT jlong JNICALL Java_jep_Jep_init
(JNIEnv *env, jobject obj, jobject cl) {
    return pyembed_thread_init(env, cl, obj);
}


/*
 * Class:     jep_Jep
 * Method:    run
 * Signature: (ILjava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_run
(JNIEnv *env, jobject obj, jlong tstate, jstring str) {
    const char *filename;

    filename = jstring2char(env, str);
    pyembed_run(env, tstate, (char *) filename);
    release_utf_char(env, str, filename);
}


/*
 * Class:     jep_Jep
 * Method:    invoke
 * Signature: (JLjava/lang/String;[Ljava/lang/Object;[II)Ljava/lang/Object;
 */
JNIEXPORT jobject JNICALL Java_jep_Jep_invoke
(JNIEnv *env,
 jobject obj,
 jlong tstate,
 jstring name,
 jobjectArray args,
 jintArray types) {
    const char *cname;
    jobject ret;

    cname = jstring2char(env, name);
    ret = pyembed_invoke_method(env, (intptr_t) tstate, cname, args, types);
    release_utf_char(env, name, cname);

    return ret;
}


/*
 * Class:     jep_Jep
 * Method:    compileString
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_jep_Jep_compileString
(JNIEnv *env, jobject obj, jlong tstate, jstring jstr) {
    const char *str;
    jint ret;

    str = jstring2char(env, jstr);
    ret = (jint) pyembed_compile_string(env, tstate, (char *) str);
    release_utf_char(env, jstr, str);
    return ret;
}


/*
 * Class:     jep_Jep
 * Method:    eval
 * Signature: (ILjava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_eval
(JNIEnv *env, jobject obj, jlong tstate, jstring jstr) {
    const char *str;

    str = jstring2char(env, jstr);
    pyembed_eval(env, tstate, (char *) str);
    release_utf_char(env, jstr, str);
}


/*
 * Class:     jep_Jep
 * Method:    getValue
 * Signature: (ILjava/lang/String;)Ljava/lang/Object;
 */
JNIEXPORT jobject JNICALL Java_jep_Jep_getValue
(JNIEnv *env, jobject obj, jlong tstate, jstring jstr) {
    const char *str;
    jobject ret;

    str = jstring2char(env, jstr);
    ret = pyembed_getvalue(env, tstate, (char *) str);
    release_utf_char(env, jstr, str);
    return ret;
}


/*
 * Class:     jep_Jep
 * Method:    getValue_floatarray
 * Signature: (ILjava/lang/String;)L[F
 */
JNIEXPORT jobject JNICALL Java_jep_Jep_getValue_1floatarray
(JNIEnv *env, jobject obj, jlong tstate, jstring jstr) {
    const char *str;
    jobject ret;

    str = jstring2char(env, jstr);
    ret = pyembed_getvalue_array(env, tstate, (char *) str, JFLOAT_ID);
    release_utf_char(env, jstr, str);
    return ret;
}


/*
 * Class:     jep_Jep
 * Method:    getValue_bytearray
 * Signature: (ILjava/lang/String;)L[B;
 */
JNIEXPORT jobject JNICALL Java_jep_Jep_getValue_1bytearray
(JNIEnv *env, jobject obj, jlong tstate, jstring jstr) {
    const char *str;
    jobject ret;

    str = jstring2char(env, jstr);
    ret = pyembed_getvalue_array(env, tstate, (char *) str, JBYTE_ID);
    release_utf_char(env, jstr, str);
    return ret;
}



/*
 * Class:     jep_Jep
 * Method:    createModule
 * Signature: (JLjava/lang/String;)J
 */
JNIEXPORT jlong JNICALL Java_jep_Jep_createModule
(JNIEnv *env, jobject obj, jlong tstate, jstring jstr) {
    const char *str;
    jlong ret;

    str = jstring2char(env, jstr);
    ret = pyembed_create_module(env, tstate, (char *) str);
    release_utf_char(env, jstr, str);
    return ret;
}


/*
 * Class:     jep_Jep
 * Method:    setClassLoader
 * Signature: (ILjava/lang/ClassLoader;)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_setClassLoader
(JNIEnv *env, jobject obj, jlong tstate, jobject cl) {
    pyembed_setloader(env, tstate, cl);
}


/*
 * Class:     jep_Jep
 * Method:    close
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_close
(JNIEnv *env, jobject obj, jlong tstate) {
    pyembed_thread_close(tstate);
}


// -------------------------------------------------- set() methods

/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (ILjava/lang/String;Ljava/lang/Object;)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2Ljava_lang_Object_2
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jobject jval) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_object(env, tstate, 0, name, jval);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (JLjava/lang/String;Ljava/lang/Class;)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2Ljava_lang_Class_2
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jclass jval) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_class(env, tstate, 0, name, jval);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (ILjava/lang/String;Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2Ljava_lang_String_2
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jstring jval) {
    const char *name, *value;

    name  = jstring2char(env, jname);
    value = jstring2char(env, jval);
    pyembed_setparameter_string(env, tstate, 0, name, value);
    release_utf_char(env, jname, name);
    release_utf_char(env, jval, value);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (ILjava/lang/String;I)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2I
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jint jval) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_int(env, tstate, 0, name, (int) jval);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (ILjava/lang/String;J)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2J
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jlong jval) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_long(env, tstate, 0, name, (jeplong) jval);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (ILjava/lang/String;D)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2D
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jdouble jval) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_double(env, tstate, 0, name, (double) jval);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (ILjava/lang/String;F)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2F
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jfloat jval) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_float(env, tstate, 0, name, (float) jval);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (JLjava/lang/String;[Z)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2_3Z
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jbooleanArray jarr) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_array(env, tstate, 0, name, (jobjectArray) jarr);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (JLjava/lang/String;[I)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2_3I
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jintArray jarr) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_array(env, tstate, 0, name, (jobjectArray) jarr);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (JLjava/lang/String;[S)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2_3S
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jshortArray jarr) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_array(env, tstate, 0, name, (jobjectArray) jarr);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (JLjava/lang/String;[B)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2_3B
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jbyteArray jarr) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_array(env, tstate, 0, name, (jobjectArray) jarr);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (JLjava/lang/String;[J)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2_3J
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jlongArray jarr) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_array(env, tstate, 0, name, (jobjectArray) jarr);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (JLjava/lang/String;[D)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2_3D
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jdoubleArray jarr) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_array(env, tstate, 0, name, (jobjectArray) jarr);
    release_utf_char(env, jname, name);
}


/*
 * Class:     jep_Jep
 * Method:    set
 * Signature: (JLjava/lang/String;[F)V
 */
JNIEXPORT void JNICALL Java_jep_Jep_set__JLjava_lang_String_2_3F
(JNIEnv *env, jobject obj, jlong tstate, jstring jname, jfloatArray jarr) {
    const char *name;
    
    name = jstring2char(env, jname);
    pyembed_setparameter_array(env, tstate, 0, name, (jobjectArray) jarr);
    release_utf_char(env, jname, name);
}
