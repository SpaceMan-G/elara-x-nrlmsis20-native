# Scientific and provenance contract

Production code is the accepted first-class `nrlmsis20` namespace. It does not call pymsis, compile or invoke Fortran, or bundle the official authority payload. Accepted compatibility flags are `lspec_select = [true, true, true, true, true, true, true, true, true, false]` and the same pattern for `lmass_include`. Public scientific outputs are `D(1:9)`, `TEX`, and `TN`.
