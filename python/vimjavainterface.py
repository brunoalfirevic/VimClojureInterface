import sys, vim, vimpyenhanced
from pyjni import *

vim.command(":function! IsNull(val) \n return a:val is function('IsNull') \n endfunction")

jvm = None

def execute_vim_action(env, expr, action):
    try:
        py_expr = env.contents.GetPythonString(expr)
        return env.contents.NewStringUTF(action(py_expr))
    except:
        env.contents.ThrowNew(jvm.vim_exception_class, str(sys.exc_info()[1]))

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

def create_jvm(jvmlib = None, classpath = None, additional_options = None):
    global jvm
    if jvm != None:
        raise JNIError("JVM already created")

    if jvmlib == None:
        jvmlib = vim.eval('g:jvm_lib')
    if classpath == None:
        classpath = vim.eval('g:jvm_classpath')
        for runtimedir in vim.eval("&runtimepath").split(","):
            plugindir = os.path.join(runtimedir, "plugin")
            classpath.append(plugindir)
            classpath.append(os.path.join(plugindir, "*.jar"))
    if additional_options == None:
        if int(vim.eval("exists('g:jvm_additional_options')")):
            additional_options = vim.eval('g:jvm_additional_options')
        else:
            additional_options = []

    vm = JavaVM.Create(jvmlib, classpath, additional_options)
    env = vm.GetEnv()
    vimclass = env.FindClass("vimjavainterface/Vim")

    vimevalfunc = JNIFUNCTYPE(jstring, POINTER(JNIEnv), jobject, jstring)(vim_eval)
    vimcommandfunc = JNIFUNCTYPE(None, POINTER(JNIEnv), jobject, jstring)(vim_command)
    vimsafeevalfunc = JNIFUNCTYPE(jstring, POINTER(JNIEnv), jobject, jstring)(vim_safe_eval)
    vimsafecommandfunc = JNIFUNCTYPE(None, POINTER(JNIEnv), jobject, jstring)(vim_safe_command)

    env.RegisterNative(vimclass, "nativeEval", "(Ljava/lang/String;)Ljava/lang/String;", vimevalfunc)
    env.RegisterNative(vimclass, "nativeCommand", "(Ljava/lang/String;)V", vimcommandfunc)
    env.RegisterNative(vimclass, "nativeSafeEval", "(Ljava/lang/String;)Ljava/lang/String;", vimsafeevalfunc)
    env.RegisterNative(vimclass, "nativeSafeCommand", "(Ljava/lang/String;)V", vimsafecommandfunc)

    vm.dispatchclass = env.NewGlobalRef(env.FindClass("vimjavainterface/Dispatcher"))
    vm.dispatchmethod = env.NewGlobalRef(env.GetStaticMethodID(vm.dispatchclass, "dispatch", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"))
    vm.exception_describer_class = env.NewGlobalRef(env.FindClass("vimjavainterface/ExceptionDescriber"))
    vm.exception_describe_method = env.NewGlobalRef(env.GetStaticMethodID(vm.exception_describer_class, "describe", "(Ljava/lang/Throwable;)Ljava/lang/String;"))
    vm.vim_exception_class = env.NewGlobalRef(env.FindClass("vimjavainterface/VimException"))

    jvm = vm
    return vm

def call_java(targetclass, targetmethod, serialized_parameters):
    env = jvm.GetEnv()
    env.PushLocalFrame(15)

    try:
        jvm_target_class = env.NewStringUTF(targetclass)
        jvm_target_method = env.NewStringUTF(targetmethod)
        jvm_serialized_parameters = env.NewStringUTF(serialized_parameters)

        arg_array = (jvalue * 3)()
        arg_array[0].l = jvm_target_class
        arg_array[1].l = jvm_target_method
        arg_array[2].l = jvm_serialized_parameters

        #here we go into java
        jvm_result = env.CallStaticObjectMethodA(jvm.dispatchclass, jvm.dispatchmethod, arg_array)
        exception = env.ExceptionOccurred()

        if exception:
            env.ExceptionClear()

            describe_arg_array = (jvalue * 1)()
            describe_arg_array[0].l = exception

            jvm_exception_description = env.CallStaticObjectMethodA(jvm.exception_describer_class, jvm.exception_describe_method, describe_arg_array)
            if env.ExceptionCheck():
                env.ExceptionClear()
                raise JavaInvocationError("Exception occurred during execution of java code, but more information could not be obtained")

            py_exception_description = env.GetPythonString(jvm_exception_description)
            raise JavaInvocationError(py_exception_description)
        return env.GetPythonString(jvm_result)
    finally:
        env.PopLocalFrame(None)

def delegate_vim_function_to_java(targetclass, targetmethod, arg_parameter_name):
    result = call_java(targetclass, targetmethod, vim.eval_as_string(arg_parameter_name))
    vim.command("return eval('%s')" % result.replace("'", "''"))

