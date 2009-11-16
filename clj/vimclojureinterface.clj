;   Copyright (c) Bruno Alfirevic. All rights reserved.
;   The use and distribution terms for this software are covered by the
;   Eclipse Public License 1.0 (http://opensource.org/licenses/eclipse-1.0.php)
;   which can be found in the file epl-v10.html at the root of this distribution.
;   By using this software in any fashion, you are agreeing to be bound by
;   the terms of this license.
;   You must not remove this notice, or any other, from this software.

(ns vimclojureinterface
  "Support for scripting Vim in Clojure"
  (:import vimjavainterface.Vim)
  (:gen-class
     :name vimclojureinterface.Dispatcher
     :methods [#^{:static true} [dispatch [String java.util.Collection] Object]]))

(defn- -dispatch [target args]
  (apply @(find-var (symbol target))
         (map (fn [arg]
                (cond
                  (instance? java.util.Map arg) (into {} arg)
                  (instance? java.util.Collection arg) (into [] arg)
                  :else arg))
              args)))

(defn vim-eval [expr]
  (Vim/eval expr))

(defn vim-cmd [cmd]
  (Vim/command cmd))

(defn vim-safe-eval [expr]
  (Vim/safeEval expr))

(defn vim-safe-cmd [cmd]
  (Vim/safeCommand cmd))

(def #^{:private true}
  repl-state
  (atom {:ns (create-ns 'user)}))

(defn repl-eval [expr-str]
  (binding [*ns* (:ns @repl-state)]
    (let [result (load-string expr-str)]
      (reset! repl-state {:ns *ns*})
      result)))

