try:
    import vim
    vim.command(":let g:null=[]")
except:
    pass

from pyjni import *

def eval_and_serialize_vim_expression(expr):
    return vim.eval('string(%s)' % expr)

#TODO - what to return in case of Vim errors

#implementation of native methods for java Vim class
def vim_eval(env, this, expr):
    try:
        py_expr = env.contents.GetPythonString(expr)
        return env.contents.NewStringUTF(eval_and_serialize_vim_expression(py_expr))
    except:
        return env.contents.NewStringUTF("")

def vim_command(env, this, cmd):
    try:
        py_cmd = env.contents.GetPythonString(cmd)
        vim.command(py_cmd)
    except:
        pass

#end implementation of native methods for java Vim class

jvm = None

def create_jvm(jvmlib = None, classpath = None, additional_options = None):
    if jvmlib == None:
        jvmlib = vim.eval('g:jvm_lib')
    if classpath == None:
        classpath = vim.eval('g:jvm_classpath')
    if additional_options == None:
        additional_options = vim.eval('g:jvm_additional_options')

    vm = JavaVM.Create(jvmlib, classpath, additional_options)
    vimclass = vm.GetEnv().FindClass("vimjavainterface/Vim")

    vimevalfunc = JNIFUNCTYPE(jstring, POINTER(JNIEnv), jobject, jstring)(vim_eval)
    vimcommandfunc = JNIFUNCTYPE(None, POINTER(JNIEnv), jobject, jstring)(vim_command)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("_eval", "(Ljava/lang/String;)Ljava/lang/String;",
                                                        cast(vimevalfunc, c_void_p))), 1)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("_command", "(Ljava/lang/String;)V",
                                                        cast(vimcommandfunc, c_void_p))), 1)
    global jvm
    jvm = vm
    return vm

def call_java(target, dispatcher, serialized_parameters):
    env = jvm.GetEnv()
    env.PushLocalFrame(10)

    try:
        dispatchclass = env.FindClass("vimjavainterface/Dispatcher")
        dispatchmethod = env.GetStaticMethodID(
            dispatchclass, "dispatch", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;")

        jvm_target = env.NewStringUTF(target)
        jvm_dispatcher = env.NewStringUTF(dispatcher)
        jvm_serialized_parameters = env.NewStringUTF(serialized_parameters)

        arg_array = (jvalue * 3)()
        arg_array[0].l = jvm_target
        arg_array[1].l = jvm_dispatcher
        arg_array[2].l = jvm_serialized_parameters

        #here we go into java
        jvm_result = env.CallStaticObjectMethodA(dispatchclass, dispatchmethod, arg_array)
        py_result = env.GetPythonString(jvm_result)

        return py_result
    finally:
        env.PopLocalFrame(None)

def delegate_vim_function_to_java(target, dispatcher):
    result = call_java(target, dispatcher, eval_and_serialize_vim_expression("a:000"))
    vim.command("return eval(%s)" % result)
