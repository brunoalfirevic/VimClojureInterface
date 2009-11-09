(ns vimclojureinterface
  "Support for scripting Vim in Clojure"
  (:import vimjavainterface.Vim)
  (:gen-class
     :name vimclojureinterface.Dispatcher
     :methods [#^{:static true} [dispatch [String java.util.Collection] Object]]))

(def #^{:private true}
  repl-state
  (atom {:ns (create-ns 'user)}))

(defn- -dispatch [target args]
  (apply @(find-var (symbol target))
         (map (fn [arg]
                (cond
                  (instance? java.util.Map arg) (into {} arg)
                  (instance? java.util.Collection arg) (into [] arg)
                  :else arg))
              args)))

(defn- eval-string [expr-str]
  (binding [*ns* (:ns @repl-state)]
    (with-in-str expr-str
      (loop [result nil]
        (let [eof (Object.)
              input (read *in* false eof)]
          (if (not= input eof)
            (recur (eval input))
            (do
              (reset! repl-state {:ns *ns*})
              result)))))))

(defn vim-eval [expr]
  (Vim/eval expr))

(defn vim-cmd [cmd]
  (Vim/command cmd))

(defn vim-safe-eval [expr]
  (Vim/safeEval expr))

(defn vim-safe-cmd [cmd]
  (Vim/safeCommand cmd))

