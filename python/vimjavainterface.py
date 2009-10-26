try:
    import vim
    vim.command(":let g:null=[]")
except:
    pass

from pyjni import *
import sys
import threading #we need to call this inside VIM because process can crash if this is first imported after creating JVM.. wierd

def eval_and_serialize_vim_expression(expr):
    return vim.eval('string(%s)' % expr)

def throw_java_exception(env, exc):
    env.contents.ThrowNew(env.contents.FindClass("vimjavainterface/VimException"), str(exc))

#implementation of native methods for java Vim class
def vim_eval(env, this, expr):
    try:
        py_expr = env.contents.GetPythonString(expr)
        return env.contents.NewStringUTF(eval_and_serialize_vim_expression(py_expr))
    except:
        throw_java_exception(env, sys.exc_info()[1])

def vim_command(env, this, cmd):
    try:
        py_cmd = env.contents.GetPythonString(cmd)
        vim.command(py_cmd)
    except:
        throw_java_exception(env, sys.exc_info()[1])

#end implementation of native methods for java Vim class

jvm = None

def create_jvm(jvmlib = None, classpath = None, additional_options = None):
    if jvmlib == None:
        jvmlib = vim.eval('g:jvm_lib')
    if classpath == None:
        classpath = vim.eval('g:jvm_classpath')
    if additional_options == None:
        if int(vim.eval("exists('g:jvm_additional_options')")):
            additional_options = vim.eval('g:jvm_additional_options')
        else:
            additional_options = []

    vm = JavaVM.Create(jvmlib, classpath, additional_options)
    vimclass = vm.GetEnv().FindClass("vimjavainterface/Vim")

    vimevalfunc = JNIFUNCTYPE(jstring, POINTER(JNIEnv), jobject, jstring)(vim_eval)
    vimcommandfunc = JNIFUNCTYPE(None, POINTER(JNIEnv), jobject, jstring)(vim_command)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("nativeEval", "(Ljava/lang/String;)Ljava/lang/String;",
                                                        cast(vimevalfunc, c_void_p))), 1)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("nativeCommand", "(Ljava/lang/String;)V",
                                                        cast(vimcommandfunc, c_void_p))), 1)
    global jvm
    jvm = vm
    return vm

def call_java(target, dispatcher, serialized_parameters):
    env = jvm.GetEnv()
    env.PushLocalFrame(10)

    try:
        dispatchclass = env.FindClass("vimjavainterface/Dispatcher")
        dispatchmethod = env.GetStaticMethodID(dispatchclass, "dispatch", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;")

        jvm_target = env.NewStringUTF(target)
        jvm_dispatcher = env.NewStringUTF(dispatcher)
        jvm_serialized_parameters = env.NewStringUTF(serialized_parameters)

        arg_array = (jvalue * 3)()
        arg_array[0].l = jvm_target
        arg_array[1].l = jvm_dispatcher
        arg_array[2].l = jvm_serialized_parameters
        
        #here we go into java
        jvm_result = env.CallStaticObjectMethodA(dispatchclass, dispatchmethod, arg_array)
        exception = env.ExceptionOccurred()

        if exception:
            env.ExceptionClear()
            
            exception_describer_class = env.FindClass("vimjavainterface/ExceptionDescriber")
            describe_method = env.GetStaticMethodID(exception_describer_class, "describe", "(Ljava/lang/Throwable;)Ljava/lang/String;")

            describe_arg_array = (jvalue * 1)()
            describe_arg_array[0].l = exception

            jvm_exception_description = env.CallStaticObjectMethodA(exception_describer_class, describe_method, describe_arg_array)
            if env.ExceptionCheck():
                env.ExceptionClear()
                raise JavaInvocationError("Exception occurred during execution of java code, but more information could not be obtained")

            py_exception_description = env.GetPythonString(jvm_exception_description)
            raise JavaInvocationError(py_exception_description)
        return env.GetPythonString(jvm_result)
    finally:
        env.PopLocalFrame(None)

def delegate_vim_function_to_java(target, dispatcher):
    result = call_java(target, dispatcher, eval_and_serialize_vim_expression("a:000"))
    vim.command("return eval(%s)" % result)
