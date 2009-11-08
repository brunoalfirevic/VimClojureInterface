function! vimclojureinterface#ForceInit()
endfunction

function! CljEval(expr)
    return vimjavainterface#CallJava('vimclojureinterface/eval-string', 'vimclojureinterface.Dispatcher/dispatch', a:expr)
endfunction

command! -range -nargs=* Cljp echo CljEval(<q-args> != '' ? <q-args> : join(getbufline(bufname("%"), <line1>, <line2>), "\n"))

command! -range -nargs=* Clj call CljEval(<q-args> != '' ? <q-args> : join(getbufline(bufname("%"), <line1>, <line2>), "\n"))


