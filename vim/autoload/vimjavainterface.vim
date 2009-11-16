py << EOF
import vim

sys.path.append(vim.eval('expand("<sfile>:p:h")'))

try:
    import vimjavainterface
finally:
    del sys.path[-1:]

vimjavainterface.create_jvm()
EOF

function! vimjavainterface#CallJava(class, method, args)
    execute "py vimjavainterface.delegate_vim_function_to_java('" . escape(a:class, "'") . "', '" . escape(a:method, "'") . "', 'a:args')"
endfunction

function! vimjavainterface#CallJavaMethod(class, method, ...)
    return vimjavainterface#CallJava(a:class, a:method, a:000)
endfunction


