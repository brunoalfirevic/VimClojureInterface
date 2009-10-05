function! vimJavaInterface#CallJavaMethod(class, method, serialization_func, ...)
    execute "py CallJavaMethod('" . a:class . "', '" . a:method . "', " . a:serialization_func . "')"
endfunction
