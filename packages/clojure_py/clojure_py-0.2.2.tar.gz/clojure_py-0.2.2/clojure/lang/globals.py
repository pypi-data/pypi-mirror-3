from clojure.lang.var import var as defineVar

currentCompiler = defineVar()
currentCompiler.setDynamic()


