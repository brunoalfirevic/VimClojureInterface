py create_jvm()

function! vimJavaInterface#ForceInit()
endfunction

function! vimJavaInterface#CallJavaMethod(class, method, ...)
    execute "py delegate_vim_function_to_java('" . a:class . "/" . a:method . "', None)"
endfunction

function! vimJavaInterface#CallJava(target, dispatcher, ...)
    execute "py delegate_vim_function_to_java('" . a:target . "', '" . a:dispatcher . "')"
endfunction
