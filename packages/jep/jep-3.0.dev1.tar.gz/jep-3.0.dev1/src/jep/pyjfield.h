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

#ifndef _Included_pyjfield
#define _Included_pyjfield

#include "pyjobject.h"
#include "pyjclass.h"

// i needed an object to store methods in. this is a callable
// object and instances of these are dynamically added to a PyJobject
// using setattr.

typedef struct {
    PyObject_HEAD
    jfieldID          fieldId;             /* Resolved fieldid */
    jobject           rfield;              /* reflect/Field object */
    PyJobject_Object *pyjobject;           /* parent, should point to
                                              PyJObject_Object */
    int               fieldTypeId;         /* field's typeid */
    PyObject         *pyFieldName;         /* python name... :-) */
    int               isStatic;            /* -1 if not known,
                                              otherwise 1 or 0 */
    int               init;                /* 1 if init performed */
} PyJfield_Object;


PyJfield_Object* pyjfield_new(JNIEnv*, jobject, PyJobject_Object*);
int pyjfield_check(PyObject*);

PyObject* pyjfield_get(PyJfield_Object*);
int pyjfield_set(PyJfield_Object *self, PyObject *value);

#endif // ndef pyjfield
