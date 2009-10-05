executing_in_vim = False

try:
    import vim
    executing_in_vim = True
except:
    pass

from pyjni import *
    
if executing_in_vim:
    vim.command(":let g:null=[]")
    vim.command(":function! SimpleSerializer(arg)\n:return a:arg\n:endfunction")

def EvalAndSerializeVimExpression(serialization_function, expr):
    return vim.eval('%s(%s)' % (serialization_function, expr))

def VimEval(env, this, serialization_function, expr):
    try:
        py_serialization_function = env.contents.GetPythonString(serialization_function)
        py_expr = env.contents.GetPythonString(expr)
        return env.contents.NewStringUTF(EvalAndSerializeVimExpression(py_serialization_function, py_expr))
    except:
        return env.contents.NewStringUTF("")

def VimCommand(env, this, cmd):
    try:
        py_cmd = env.contents.GetPythonString(cmd)
        vim.command(py_cmd)
    except:
        pass

def GetVimClass(env):
    return env.FindClass("vimjavainterface/Vim")

def CreateJVM():
    vm = JavaVM.Create('C:/Program Files (x86)/Java/jre6/bin/client/jvm.dll', ["C:/Users/Bruno/Downloads/clojure_1.0.0/*.jar", "C:/git/VimJavaInterface/VimJavaInterface/build/classes/"])
    vimclass = GetVimClass(vm.GetEnv())
    
    vimevalfunc = JNIFUNCTYPE(jstring, POINTER(JNIEnv), jobject, jstring, jstring)(VimEval)
    vimcommandfunc = JNIFUNCTYPE(None, POINTER(JNIEnv), jobject, jstring)(VimCommand)
    
    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("eval", "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
                                                        cast(vimevalfunc, c_void_p))), 1)

    vm.GetEnv().RegisterNatives(vimclass,
                                pointer(JNINativeMethod("command", "(Ljava/lang/String;)V",
                                                        cast(vimcommandfunc, c_void_p))), 1)
    return vm

jvm = CreateJVM()

def CallJavaMethod(target, dispatcher, deserializer, serialized_parameters, vm = jvm):
    env = vm.GetEnv()
    env.PushLocalFrame(10)
    
    try:
        vimclass = GetVimClass(env)
        vim_dispatch_method = env.GetStaticMethodID(
            vimclass, "dispatch", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;")

        jvm_target = env.NewStringUTF(target)
        jvm_dispatcher = env.NewStringUTF(dispatcher)
        jvm_deserializer = env.NewStringUTF(deserializer)
        jvm_serialized_parameters = env.NewStringUTF(serialized_parameters)

        arg_array = (jvalue * 4)()
        arg_array[0].l = jvm_target
        arg_array[1].l = jvm_dispatcher
        arg_array[2].l = jvm_deserializer        
        arg_array[3].l = jvm_serialized_parameters

        #here we go into java
        jvm_result = env.CallStaticObjectMethodA(vimclass, vim_dispatch_method, arg_array)
        py_result = env.GetPythonString(jvm_result)

        return py_result
    finally:
        env.PopLocalFrame(None)

def CallJavaMethodFromVimScript(target, dispatcher, deserializer, serialization_function, vm = jvm):
    result = CallJavaMethod(target, dispatcher, deserializer, EvalAndSerializeVimExpression(serialization_function, "a:000"), vm)
    vim.command("return %s" % result)    

print "Version " + str(jvm.GetEnv().GetVersion())

#print CallJavaMethod("vimjavainterface.Vim/command", None, None, ":echo has('win32')", jvm)
#print vimjavainterface.CallJavaMethod("vimjavainterface.Vim/eval", None, None, "IdentitySerializer")

