from ctypes import *

#datatype nad platform dependent definitions
jint = c_long
jboolean = c_ubyte
JNIFUNCTYPE = WINFUNCTYPE
dll_loader = windll

#constants
JNI_VERSION_1_2 = 65538
JNI_VERSION_1_4 = 65540
JNI_VERSION_1_6 = 65542

#structure definitions
class JavaVMOption(Structure):
    _fields_ = [("optionString", c_char_p), ("extraInfo", c_void_p)]

class JavaVMInitArgs(Structure):
    _fields_ = [("version", jint ), ("nOptions", jint), ("options", POINTER(JavaVMOption)), ("ignoreUnrecognized", jboolean)]

class JNIEnv(Structure):
    _fields_ = [("functions", POINTER(c_void_p))]
    
    def GetVersion(self):
        return self.GetFunc(4)()

    def GetFunc(self, index, *types):
        return lambda *vals: JNIFUNCTYPE(jint, POINTER(JNIEnv), *types)(self.functions[index])(pointer(self), *vals)

class JavaVM(Structure):
    _fields_ = [("functions", POINTER(c_void_p))]
    
    def GetEnv(self):
        env_ptr = POINTER(JNIEnv)()
        self.GetFunc(6, POINTER(POINTER(JNIEnv)), jint)(byref(env_ptr), self.version)
        return env_ptr.contents

    def SetVersion(self, version):
        self.version = version
    
    def GetFunc(self, index, *types):
        return lambda *vals: JNIFUNCTYPE(jint, POINTER(JavaVM), *types)(self.functions[index])(pointer(self), *vals)        

jvm = None

def create_jvm(jvm_lib_path, classpath = "", version = JNI_VERSION_1_6):
    global jvm
    if jvm == None:
        libjvm = dll_loader.LoadLibrary(jvm_lib_path)

        jvm_ptr = POINTER(JavaVM)()
        env_ptr = POINTER(JNIEnv)()

        args = JavaVMInitArgs(version, 1, pointer(JavaVMOption(classpath)), 0)
        libjvm.JNI_CreateJavaVM(byref(jvm_ptr), byref(env_ptr), byref(args))
        jvm = jvm_ptr.contents
        jvm.SetVersion(version)

    return jvm

create_jvm('C:/Program Files (x86)/Java/jre6/bin/client/jvm.dll', "-Djava.class.path=C:/Users/Bruno/Downloads/clojure_1.0.0/clojure.jar")
print jvm.GetEnv().GetVersion()
