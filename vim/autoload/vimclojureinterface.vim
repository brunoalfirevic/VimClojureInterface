function! vimclojureinterface#ForceInit()
endfunction

function! vimclojureinterface#CallClojure(function, ...)
    return vimjavainterface#CallJavaMethod('vimclojureinterface.Dispatcher', 'dispatch', a:function, a:000)
endfunction

function! CljEval(expr)
    return vimclojureinterface#CallClojure('vimclojureinterface/eval-string', a:expr)
endfunction

command! -range -nargs=* Cljp echo CljEval(<q-args> != '' ? <q-args> : join(getbufline(bufname("%"), <line1>, <line2>), "\n"))

command! -range -nargs=* Clj call CljEval(<q-args> != '' ? <q-args> : join(getbufline(bufname("%"), <line1>, <line2>), "\n"))

