(ns vimclojureinterface
  "Support for scripting Vim in Clojure"
  (:import vimjavainterface.Vim)
  (:gen-class
     :name vimclojureinterface.Dispatcher
     :methods [#^{:static true} [dispatch [String java.util.Collection] Object]]))

(def #^{:private true}
  repl-state
  (atom {:ns (create-ns 'user)}))

(defn- perform-dispatch [target args]
  (apply @(resolve (symbol target))
         (map (fn [arg]
                (cond
                  (instance? java.util.Map arg) (into {} arg)
                  (instance? java.util.Collection arg) (into [] arg)
                  :else arg))
              args)))

(defn- -dispatch [target args]
  (binding [*ns* (:ns @repl-state)]
    (let [result (perform-dispatch target args)]
      (reset! repl-state {:ns *ns*})
      result)))

(defn- eval-string [expr-str]
  (let [eof (Object.)]
    (with-in-str expr-str
      (loop [result nil]
        (let [input (read *in* false eof)]
          (if (not= input eof)
            (recur (eval input))
            result))))))

(defn vim-eval [expr]
  (Vim/eval expr))

(defn vim-cmd [cmd]
  (Vim/command cmd))

(defn vim-safe-eval [expr]
  (Vim/safeEval expr))

(defn vim-safe-cmd [cmd]
  (Vim/safeCommand cmd))

