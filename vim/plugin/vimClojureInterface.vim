function! CljEval(expr)
    return vimJavaInterface#CallJava('vimclojureinterface/eval-string', 'vimclojureinterface.Dispatcher/dispatch', a:expr)
endfunction

command! -range -nargs=* Clj echo CljEval(<q-args> != '' ? <q-args> : join(getbufline(bufname("%"), <line1>, <line2>), "\n"))

