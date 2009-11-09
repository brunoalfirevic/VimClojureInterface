py << EOF
import vim

sys.path.append(vim.eval('expand("<sfile>:p:h")'))

try:
    import vimjavainterface
finally:
    del sys.path[-1:]

vimjavainterface.create_jvm()
EOF

function! vimjavainterface#ForceInit()
endfunction

function! vimjavainterface#CallJava(target, dispatcher, args)
    execute "py vimjavainterface.delegate_vim_function_to_java('" . escape(a:target, "'") . "', '" . escape(a:dispatcher, "'") . "', 'a:args')"
endfunction

function! vimjavainterface#CallJavaMethod(class, method, ...)
    return vimjavainterface#CallJava(a:target . "/" . a:method, '', a:000)
endfunction


