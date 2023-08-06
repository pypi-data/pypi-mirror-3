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


// shut up the compiler
#ifdef _POSIX_C_SOURCE
#  undef _POSIX_C_SOURCE
#endif
#include <jni.h>
#include <Python.h>

#ifndef _Included_pyjobject
#define _Included_pyjobject

#include "pyjclass.h"

// c storage for our stuff, managed by python interpreter.
// doesn't need much, just a dictionary for attributes and
// a jobject reference.
typedef struct {
    PyObject_HEAD
    jobject          object;      /* the jni object */
    PyJclass_Object *pyjclass;    /* pointer to pyjclass if this
                                     object represents a type */
    jclass           clazz;       /* java class object */
    PyObject        *attr;        /* list of tuples for get/set attr */
    PyObject        *methods;     /* list of method names */
    PyObject        *fields;      /* list of field names */
    int              finishAttr;  /* true if object attributes are finished */
} PyJobject_Object;

PyObject* pyjobject_new(JNIEnv*, jobject);
PyObject* pyjobject_new_class(JNIEnv*, jclass);
PyObject* pyjobject_find_method(PyJobject_Object*, PyObject*, PyObject*);
int pyjobject_check(PyObject *obj);

#endif // ndef pyjobject
