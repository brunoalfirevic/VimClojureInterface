py create_jvm()

function! vimJavaInterface#CallJavaMethod(class, method, ...)
    execute "py delegate_vim_function_to_java_method('" . a:class . "/" . a:method . "', None)"
endfunction

function! vimJavaInterface#CallJava(target, dispatcher, ...)
    execute "py delegate_vim_function_to_java_method('" . a:target . "', '" . a:dispatcher . "')"
endfunction
