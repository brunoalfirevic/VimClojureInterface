py << EOF
import vim

sys.path.append(vim.eval('expand("<sfile>:p:h")'))

try:
    import vimjavainterface
finally:
    del sys.path[-1:]

vimjavainterface.create_jvm()
vimjavainterface.capture_jvm_output_streams()
EOF

function! vimjavainterface#InitJvm()
endfunction

function! vimjavainterface#CallJava(class, method, args)
    py vimjavainterface.delegate_vim_function_to_java(vim.eval('a:class'), vim.eval('a:method'), 'a:args')
endfunction

function! vimjavainterface#CallJavaMethod(class, method, ...)
    return vimjavainterface#CallJava(a:class, a:method, a:000)
endfunction

if exists('#User#JvmLoaded')
    doautocmd User JvmLoaded
endif

