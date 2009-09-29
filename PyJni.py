from ctypes import *

#platform dependent calling convention definitions
JNIFUNCTYPE = WINFUNCTYPE
dll_loader  = windll

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

#possible return values for JNI functions.
JNI_OK        =    0              #success
JNI_ERR       =   -1              #unknown error
JNI_EDETACHED =   -2              #thread detached from the VM
JNI_EVERSION  =   -3              #JNI version error
JNI_ENOMEM    =   -4              #not enough memory
JNI_EEXIST    =   -5              #VM already created
JNI_EINVAL    =   -6              #invalid arguments

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

    def ExceptionDescribe(self):
        self.__getFunc(16, None)()

    def GetStaticMethodID(self, clazz, name, sig):
        return self.__getFunc(113, jmethodID, jclass, c_char_p, c_char_p)(clazz, name, sig)

    def ExceptionCheck(self):
        return self.__getFunc(228, jboolean)()
    
    def RegisterNatives(self, clazz, methods, n_methods):
        return self.__getFunc(215, jint, jclass, POINTER(JNINativeMethod), jint)(clazz, methods, n_methods)

    def CallStaticIntMethodA(self, clazz, method_id, args):
        return self.__getFunc(131, jint, jclass, jmethodID, c_void_p)(clazz, method_id, args)

    def __getFunc(self, index, return_type, *types):
        return lambda *vals: JNIFUNCTYPE(return_type, POINTER(JNIEnv), *types)(self.functions[index])(pointer(self), *vals)

jvm = None

class JavaVM(Structure):
    _fields_ = [("functions", POINTER(c_void_p))]
    
    def GetEnv(self):
        env_ptr = POINTER(JNIEnv)()
        self.__getFunc(6, POINTER(POINTER(JNIEnv)), jint)(byref(env_ptr), self.version)
        return env_ptr.contents
    
    @staticmethod
    def Create(jvm_lib_path, classpath = "", version = JNI_VERSION_1_6):
        global jvm
        if jvm == None:
            libjvm = dll_loader.LoadLibrary(jvm_lib_path)

            jvm_ptr = POINTER(JavaVM)()
            env_ptr = POINTER(JNIEnv)()

            args = JavaVMInitArgs(version, 1, pointer(JavaVMOption(classpath)), JNI_FALSE)
            libjvm.JNI_CreateJavaVM(byref(jvm_ptr), byref(env_ptr), byref(args))
            jvm = jvm_ptr.contents
            jvm.__setVersion(version)

        return jvm

    def __setVersion(self, version):
        self.version = version

    def __getFunc(self, index, *types):
        return lambda *vals: JNIFUNCTYPE(jint, POINTER(JavaVM), *types)(self.functions[index])(pointer(self), *vals)

def CallJavaMethod(self, clazz, method, transfer_register):
    pass

def VimEval(env, this, param):
    return param * param

JavaVM.Create('C:/Program Files (x86)/Java/jre6/bin/client/jvm.dll', "-Djava.class.path=C:/Users/Bruno/Downloads/clojure_1.0.0/clojure.jar;C:/git/VimJavaInterface/VimJavaInterface/build/classes")
print "Version " + str(jvm.GetEnv().GetVersion())

vimclass = jvm.GetEnv().FindClass("VimJavaInterface/Vim")
vimevalfunc = JNIFUNCTYPE(c_int, POINTER(JNIEnv), jobject, c_int)(VimEval)
jvm.GetEnv().RegisterNatives(vimclass, pointer(JNINativeMethod("Eval", "(I)I", cast(vimevalfunc, c_void_p))), 1)


vimclientclass = jvm.GetEnv().FindClass("VimJavaScript/VimJavaScript")
vimclientmethod = jvm.GetEnv().GetStaticMethodID(vimclientclass, "EvalNumber", "(I)I")
vimclientargs = (jvalue * 1)()
vimclientargs[0].i = 6

print jvm.GetEnv().CallStaticIntMethodA(vimclientclass, vimclientmethod, vimclientargs)

