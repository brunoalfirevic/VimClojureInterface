import string
import os
from itertools import chain
from glob import glob
from ctypes import *

#platform dependent calling convention definitions
JNIFUNCTYPE = WINFUNCTYPE
lib_loader  = windll
path_separator = ';'

#platform dependent data type definitions
jint  = c_long
jlong = c_int64
jbyte = c_byte          #signed char

#data type definitions
jboolean  = c_ubyte     #unsigned char
jchar     = c_ushort
jshort    = c_short
jfloat    = c_float
jdouble   = c_double
jsize     = jint

jobject       = c_void_p
jclass        = jobject
jweak         = jobject
jclass        = jobject
jthrowable    = jobject
jstring       = jobject
jarray        = jobject
jbooleanArray = jarray
jbyteArray    = jarray
jcharArray    = jarray
jshortArray   = jarray
jintArray     = jarray
jlongArray    = jarray
jfloatArray   = jarray
jdoubleArray  = jarray
jobjectArray  = jarray

jmethodID = c_void_p
jfieldID  = c_void_p

class jvalue(Union):
    _fields_ = [("z", jboolean), ("b", jbyte), ("c", jchar), ("s", jshort), ("i", jint), ("j", jlong), ("f", jfloat), ("d", jdouble), ("l", jobject)]

class jobjectRefType(c_int):
    pass

#constants
JNI_VERSION_1_2 = 65538
JNI_VERSION_1_4 = 65540
JNI_VERSION_1_6 = 65542

JNI_FALSE = 0
JNI_TRUE = 1

JNI_COMMIT = 1
JNI_ABORT = 2

JNIInvalidRefType    = jobjectRefType(0)
JNILocalRefType      = jobjectRefType(1)
JNIGlobalRefType     = jobjectRefType(2)
JNIWeakGlobalRefType = jobjectRefType(3)

#possible return values for JNI functions
JNI_OK        =    0              #success
JNI_ERR       =   -1              #unknown error
JNI_EDETACHED =   -2              #thread detached from the VM
JNI_EVERSION  =   -3              #JNI version error
JNI_ENOMEM    =   -4              #not enough memory
JNI_EEXIST    =   -5              #VM already created
JNI_EINVAL    =   -6              #invalid arguments

#exceptions
class PyJniError(Exception):
    pass

class JNIError(PyJniError):
    pass

class JavaInvocationError(PyJniError):
    pass

#structure definitions
class JavaVMOption(Structure):
    _fields_ = [("optionString", c_char_p), ("extraInfo", c_void_p)]

class JavaVMInitArgs(Structure):
    _fields_ = [("version", jint ), ("nOptions", jint), ("options", POINTER(JavaVMOption)), ("ignoreUnrecognized", jboolean)]

class JavaVMAttachArgs(Structure):
    _fields_ = [("version", jint), ("name", c_char_p), ("group", jobject)]

class JNINativeMethod(Structure):
    _fields_ = [("name", c_char_p), ("signature", c_char_p), ("fn_ptr", c_void_p)]

class JNIEnv(Structure):
    _fields_ = [("functions", POINTER(c_void_p))]

    def GetVersion(self):
        return self.__getFunc(4, jint)()

    def FindClass(self, name):
        return self.__getFunc(6, jclass, c_char_p)(name)

    def ThrowNew(self, clazz, message):
        return self.__getFunc(14, jint, jclass, c_char_p)(clazz, message)

    def ExceptionOccurred(self):
        return self.__getFunc(15, jthrowable)()

    def ExceptionDescribe(self):
        self.__getFunc(16, None)()

    def ExceptionClear(self):
        return self.__getFunc(17, None)()

    def ExceptionCheck(self):
        return self.__getFunc(228, jboolean)()

    def GetStaticMethodID(self, clazz, name, sig):
        return self.__getFunc(113, jmethodID, jclass, c_char_p, c_char_p)(clazz, name, sig)

    def RegisterNatives(self, clazz, methods, n_methods):
        return self.__getFunc(215, jint, jclass, POINTER(JNINativeMethod), jint)(clazz, methods, n_methods)

    def CallStaticObjectMethodA(self, clazz, method_id, args):
        return self.__getFunc(116, jobject, jclass, jmethodID, c_void_p)(clazz, method_id, args)

    def PushLocalFrame(self, capacity):
        return self.__getFunc(19, jint, jint)(capacity)

    def PopLocalFrame(self, result):
        return self.__getFunc(20, jobject, jobject)(result)

    def NewStringUTF(self, chars):
        if chars == None:
            return None
        return self.__getFunc(167, jstring, c_char_p)(chars)

    def GetStringUTFChars(self, str, is_copy):
        return self.__getFunc(169, c_char_p, jstring, POINTER(jboolean))(str, is_copy)

    def ReleaseStringUTFChars(self, str, utf):
        return self.__getFunc(170, None, jstring, c_char_p)(str, utf)

    def GetPythonString(self, jvmstring):
        if jvmstring == None:
            return None

        chars = self.GetStringUTFChars(jvmstring, None)
        try:
            result = str(chars)
        finally:
            self.ReleaseStringUTFChars(jvmstring, chars)

        return result

    def __getFunc(self, index, return_type, *types):
        return lambda *vals: JNIFUNCTYPE(return_type, POINTER(JNIEnv), *types)(self.functions[index])(pointer(self), *vals)

class JavaVM(Structure):
    _fields_ = [("functions", POINTER(c_void_p))]

    def GetEnv(self):
        env_ptr = POINTER(JNIEnv)()
        if self.__getFunc(6, POINTER(POINTER(JNIEnv)), jint)(byref(env_ptr), self.version) != JNI_OK:
            return None
        return env_ptr.contents

    @staticmethod
    def Create(jvm_lib_path, classpath = [], additional_options = [], version = JNI_VERSION_1_6):
        processpath = lambda path: os.path.normpath(os.path.expandvars(os.path.expanduser(path)))

        libjvm = lib_loader.LoadLibrary(processpath(jvm_lib_path))

        jvm_ptr = POINTER(JavaVM)()
        env_ptr = POINTER(JNIEnv)()

        option_count = len(additional_options)
        if len(classpath) != 0:
            option_count = option_count + 1

        vm_options = (JavaVMOption * option_count)()
        for i in range(len(additional_options)):
            vm_options[i] = JavaVMOption(additional_options[i])

        if len(classpath) != 0:
            full_classpath = string.join(chain(*map(glob, map(processpath, classpath))), path_separator)
            vm_options[option_count-1] = JavaVMOption('-Djava.class.path=%s' % full_classpath)

        args = JavaVMInitArgs(version, option_count, vm_options, JNI_FALSE)
        if libjvm.JNI_CreateJavaVM(byref(jvm_ptr), byref(env_ptr), byref(args)) != JNI_OK:
            raise JNIError, "Could not create java virtual machine"

        jvm = jvm_ptr.contents
        jvm.__setVersion(version)

        return jvm

    def __setVersion(self, version):
        self.version = version

    def __getFunc(self, index, *types):
        return lambda *vals: JNIFUNCTYPE(jint, POINTER(JavaVM), *types)(self.functions[index])(pointer(self), *vals)
