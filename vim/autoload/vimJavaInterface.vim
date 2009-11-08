py << EOF
import vim

sys.path.append(vim.eval('expand("<sfile>:p:h")'))

try:
    import vimjavainterface
finally:
    del sys.path[-1:]

vimjavainterface.create_jvm()
EOF

function! vimJavaInterface#ForceInit()
endfunction

function! vimJavaInterface#CallJavaMethod(class, method, ...)
    execute "py vimjavainterface.delegate_vim_function_to_java('" . escape(a:class, "'") . "/" . escape(a:method, "'") . "', None)"
endfunction

function! vimJavaInterface#CallJava(target, dispatcher, ...)
    execute "py vimjavainterface.delegate_vim_function_to_java('" . escape(a:target, "'") . "', '" . escape(a:dispatcher, "'") . "')"
endfunction
