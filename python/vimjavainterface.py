import sys
from pyjni import *

try:
    import vim, vimpyenhanced
    vim.command(":function! IsNull(val) \n return a:val is function('IsNull') \n endfunction")
except:
    print sys.exc_info()[1]

def execute_vim_action(env, expr, action):
    try:
        py_expr = env.contents.GetPythonString(expr)
        return env.contents.NewStringUTF(action(py_expr))
    except:
        env.contents.ThrowNew(env.contents.FindClass("vimjavainterface/VimException"), str(sys.exc_info()[1]))

#implementation of native methods for java Vim class
def vim_eval(env, this, expr):
    return execute_vim_action(env, expr, vim.eval_as_string)

def vim_command(env, this, cmd):
    execute_vim_action(env, cmd, vim.command)

def vim_safe_eval(env, this, expr):
    return execute_vim_action(env, expr, vim.safe.eval_as_string)

def vim_safe_command(env, this, cmd):
    execute_vim_action(env, cmd, vim.safe.command)

#end implementation of native methods for java Vim class

jvm = None
jvm_native_callbacks = None

def create_jvm(jvmlib = None, classpath = None, additional_options = None):
    global jvm
    global jvm_native_callbacks

    if jvm != None:
        raise JNIError("JVM already created")

    if jvmlib == None:
        jvmlib = vim.eval('g:jvm_lib')
    if classpath == None:
        classpath = vim.eval('g:jvm_classpath')
    if additional_options == None:
        if int(vim.eval("exists('g:jvm_additional_options')")):
            additional_options = vim.eval('g:jvm_additional_options')
        else:
            additional_options = []

    for runtimedir in vim.eval("&runtimepath").split(","):
        plugindir = os.path.join(runtimedir, "plugin")
        classpath.append(plugindir)
        classpath.append(os.path.join(plugindir, "*.jar"))

    vm = JavaVM.Create(jvmlib, classpath, additional_options)
    vimclass = vm.GetEnv().FindClass("vimjavainterface/Vim")

    vimevalfunc = JNIFUNCTYPE(jstring, POINTER(JNIEnv), jobject, jstring)(vim_eval)
    vimcommandfunc = JNIFUNCTYPE(None, POINTER(JNIEnv), jobject, jstring)(vim_command)
    vimsafeevalfunc = JNIFUNCTYPE(jstring, POINTER(JNIEnv), jobject, jstring)(vim_safe_eval)
    vimsafecommandfunc = JNIFUNCTYPE(None, POINTER(JNIEnv), jobject, jstring)(vim_safe_command)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("nativeEval", "(Ljava/lang/String;)Ljava/lang/String;", cast(vimevalfunc, c_void_p))),
                                1)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("nativeCommand", "(Ljava/lang/String;)V", cast(vimcommandfunc, c_void_p))),
                                1)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("nativeSafeEval", "(Ljava/lang/String;)Ljava/lang/String;", cast(vimsafeevalfunc, c_void_p))),
                                1)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("nativeSafeCommand", "(Ljava/lang/String;)V", cast(vimsafecommandfunc, c_void_p))),
                                1)
    jvm = vm
    jvm_native_callbacks = [vimevalfunc, vimcommandfunc, vimsafeevalfunc, vimsafecommandfunc] #to prevent garbage collection
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
    result = call_java(target, dispatcher, vim.eval_as_string("a:000"))
    vim.command("return eval('%s')" % result.replace("'", "''"))
