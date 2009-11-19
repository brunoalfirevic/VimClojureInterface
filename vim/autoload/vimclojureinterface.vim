if exists('#User#ClojureRuntimeLoaded')
    doautocmd User ClojureRuntimeLoaded
endif

function! vimclojureinterface#CallClojure(function, args)
    return vimjavainterface#CallJavaMethod('vimclojureinterface.Dispatcher', 'dispatch', a:function, a:args)
endfunction

function! vimclojureinterface#CallClojureFunc(function, ...)
    return vimclojureinterface#CallClojure(a:function, a:000)
endfunction

