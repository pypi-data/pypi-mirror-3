(ns clojure.core-deftype)

(defn parse-opts [s]
  (loop [opts {} [k v & rs :as s] s]
    (if (keyword? k)
      (recur (assoc opts k v) rs)
      [opts s])))

(defn parse-impls [specs]
  (loop [ret {} s specs]
    (if (seq s)
      (recur (assoc ret (first s) (take-while seq? (next s)))
             (drop-while seq? (next s)))
      ret)))

(defn parse-opts+specs [opts+specs]
  (let [[opts specs] (parse-opts opts+specs)
        impls (parse-impls specs)
        interfaces (keys impls)
        methods (reduce #(assoc %1 (first %2) %2)
                         {}
                         (apply concat (vals impls)))]
    (when-let [bad-opts (seq (remove #{:no-print} (keys opts)))]
      (throw (IllegalArgumentException. (apply str "Unsupported option(s) -" bad-opts))))
    [interfaces methods opts]))

(defn debug [v]
    (py/print v)
    v)

(defn wrap-specs
    [name fields specs]
    (zipmap (map clojure.core/name (keys specs))
            (map #(prop-wrap name fields %)
                 (vals specs))))



(defmacro deftype
    [name fields & specs]
    (let [[interfaces methods] (parse-opts+specs specs)
          methods (wrap-specs name fields methods) 
          methods (if (= (count fields) 0)
                      methods
                      (assoc methods "__init__" (clojure.core/make-init fields)))]
          `(~'do (def ~name (py/type ~(.-name name)
                                      (py/tuple ~(vec (concat interfaces [py/object])))
                                      (.toDict ~methods)))
                ~@(map (fn [x] `(clojure.lang.protocol/extendForType ~x ~name))
                               interfaces))))

(defn abstract-fn [self & args]
    (throw (AbstractMethodCall self)))
    

(defmacro definterface
    [name & sigs]
    (let [methods (zipmap (map #(clojure.core/name (first %)) sigs)
                          (map #(identity `(~'fn ~(symbol (str name "_" (clojure.core/name (first %))))
                                                 ~@'([self & args] 
                                                 (throw (AbstractMethodCall self))))) sigs))]
                `(do (def ~name (py/type ~(clojure.core/name name)
                                      (py/tuple [py/object])
                                      (.toDict ~methods))))))


(defmacro defprotocol
    [name & sigs]
    (let [docstr (when (string? (first sigs)) (first sigs))
          sigs (if docstr (next sigs) sigs)
          methods (zipmap (map #(clojure.core/name (first %)) sigs)
                          (map #(identity `(~'fn ~(symbol (str name "_" (clojure.core/name (first %))))
                                                 ~@'([self & args] 
                                                 (throw (AbstractMethodCall self))))) sigs))
          methods (assoc methods "__doc__" docstr)]
         `(do (def ~name (py/type ~(clojure.core/name name)
                                      (py/tuple [py/object])
                                      (.toDict ~methods)))
                     (clojure.lang.protocol/protocolFromType ~'__name__ ~name)
                ~@(for [s sigs :when (string? (last s))]
                    `(py/setattr (resolve ~(list 'quote (first s)))
                                 "__doc__"
                                 ~(last s))))))


(defmacro reify 
  "reify is a macro with the following structure:

 (reify options* specs*)
  
  Currently there are no options.

  Each spec consists of the protocol or interface name followed by zero
  or more method bodies:

  protocol-or-interface-or-Object
  (methodName [args+] body)*

  Methods should be supplied for all methods of the desired
  protocol(s) and interface(s). You can also define overrides for
  methods of Object. Note that the first parameter must be supplied to
  correspond to the target object ('this' in Java parlance). Thus
  methods for interfaces will take one more argument than do the
  interface declarations.  Note also that recur calls to the method
  head should *not* pass the target object, it will be supplied
  automatically and can not be substituted.

  The return type can be indicated by a type hint on the method name,
  and arg types can be indicated by a type hint on arg names. If you
  leave out all hints, reify will try to match on same name/arity
  method in the protocol(s)/interface(s) - this is preferred. If you
  supply any hints at all, no inference is done, so all hints (or
  default of Object) must be correct, for both arguments and return
  type. If a method is overloaded in a protocol/interface, multiple
  independent method definitions must be supplied.  If overloaded with
  same arity in an interface you must specify complete hints to
  disambiguate - a missing hint implies Object.

  recur works to method heads The method bodies of reify are lexical
  closures, and can refer to the surrounding local scope:
  
  (str (let [f \"foo\"] 
       (reify Object 
         (toString [this] f))))
  == \"foo\"

  (seq (let [f \"foo\"] 
       (reify clojure.lang.Seqable 
         (seq [this] (seq f)))))
  == (\\f \\o \\o))
  
  reify always implements clojure.lang.IObj and transfers meta
  data of the form to the created object.
  
  (meta ^{:k :v} (reify Object (toString [this] \"foo\")))
  == {:k :v}"
  {:added "1.2"} 
  [& opts+specs]
    (let [[interfaces methods] (parse-opts+specs opts+specs)
          methods (zipmap (map name (keys methods))
                          (map #(cons 'fn %) (vals methods)))]
         `(let [~'type (py/type ~"nm"
                               (py/tuple ~(vec (concat interfaces [py/object])))
                               (.toDict ~methods))]
                  
                ~@(map (fn [x] `(clojure.lang.protocol/extendForType ~x ~'type))
                               interfaces)
                  (~'type))))

(require 'copy)

(def recordfns) ; needed for recursive reasons

(def recordfns { "assoc" '(fn record-assoc
                               [self k v]
                               (let [copied (copy/copy self)]
                                    (py/setattr copied (name k) v)
                                    copied))
    
                 "containsKey" '(fn record-contains-key 
                                   [self k]
                                   (py/hasattr self (name k)))
                                   
                 "__contains__" '(fn __contains__
                                    [self k]
                                    (.containsKey self k))
                                    
                 "__getitem__" '(fn __getitem__
                                    [self k]
                                    (py/getattr self (name k)))                                    
                 
                 "entryAt"  '(fn entryAt
                                   [self k]
                                   (when (py/hasattr self (name k))
                                         (clojure.lang.mapentry/MapEntry 
                                             k
                                             (py/getattr self (name k)))))
                 "meta" '(fn meta
                            [self]
                            (if (.containsKey self :_meta)
                                (:_meta self)
                                nil))
                 
                 "withMeta" '(fn withMeta
                                 [self meta]
                                 (.assoc self :_meta meta))
                                 
                 "without" '(fn without
                                [self k]
                                (let [copied (copy/copy self)]
                                     (py/delattr copied (name k))
                                     copied))
                 "valAt" '(fn valAt
                              ([self k]
                               (.__getitem__ self (name k)))
                              ([self k default]
                               (if (.containsKey self k)
                                   (.valAt self k)
                                   default)))
                 
                 "keys" '(fn keys
                               [self]
                               (filter #(and (not (.startswith % "_"))
                                             (not (contains? (.-__methods__ self) %)))
                                        (py/dir self)))
                 
                 "count" '(fn count
                               [self]
                               (py/len (.keys self)))
                               
                 "empty" '(fn empty
                               [self]
                               (throw (clojure.core-deftype/AbstractMethodCall self)))
                               
                 ;; this may not be the fastest, but hey! it works. 
                 "__eq__" '(fn __eq__
                 	       [self other]
                 	       (if (py.bytecode/COMPARE_OP "is" self other)
                 	       	   true
                 	       	   (and (py.bytecode/COMPARE_OP "is"
                 	       	   	   (py/type self)
                 	       	   	   (py/type other))
                 	       	   	(every? identity (map = self other)) 
                 	       	   	(= (count self) (count other)))))
                 
                 "__hash__" '(fn __hash__
                 		[self]
                 		(if (py/hasattr self "_hash")
                 		     (py.bytecode/LOAD_ATTR "_hash" self)
                 		    (let [hash (reduce hash-combine 
                 		    		       (map #(py/getattr %2 %1) (keys self) (repeat self)))]
                 		    	 (py/setattr self "_hash" hash)
                 		    	 hash)))
                               
                 "seq" '(fn seq
                            [self]
                            (clojure.core-deftype/map #(.entryAt self %)
                                 (.keys self)))
                 
                 "__len__" '(fn len
                                [self]
                                (.count self))
                                
                 "cons" '(fn cons
                            [self [k v]]
                            (.assoc self k v))})


(defmacro defrecord
    [name fields & specs]
    (let [[interfaces methods] (parse-opts+specs specs)
          interfaces (concat interfaces [IPersistentMap])
          methods (wrap-specs name fields methods) 
          methods (if (= (count fields) 0)
                      methods
                      (assoc methods "__init__" (clojure.core/make-init fields)))
          methods (merge recordfns methods)
          methods (assoc methods "__methods__" methods)]
         `(~'do (def ~name (py/type ~(.-name name)
                                      (py/tuple ~(vec interfaces))
                                      (.toDict ~methods)))
                ~@(map (fn [x] `(clojure.lang.protocol/extendForType ~x ~name))
                               interfaces))))
