(ns vimclojureinterface
  "Support for scripting Vim in Clojure"
  (:import vimjavainterface.Vim)
  (:gen-class 
     :name vimclojureinterface.Dispatcher
     :methods [#^{:static true} [dispatch [String java.util.Collection] Object]]))

(defn -dispatch [target args]
  (apply @(resolve (symbol target))
         (map (fn [arg] 
                (cond 
                  (instance? java.util.Map arg) (into {} arg)
                  (instance? java.util.Collection arg) (into [] arg)
                  :else arg))
              args)))

(defn eval-string [expr-str]
  (eval (read-string expr-str)))

(defn vim-eval [expr]
  (Vim/eval expr))

(defn vim-cmd [cmd]
  (Vim/command cmd))

(defn vim-safe-eval [expr]
  (Vim/safeEval expr))

(defn vim-safe-cmd [cmd]
  (Vim/safeCommand cmd))

