#!/bin/bash

pegasus-graphviz --nosimplify dax.xml | sed 's/\.sh//g' | sed 's/\.py//g' | sed 's/-wrapper//g' >dax.dot
dot -Tsvg -odax.svg dax.dot

pegasus-graphviz MINT-0.dag | sed 's/_sh_/_/g' | sed 's/_py_/_/g' | sed 's/-wrapper//g' > dag.dot
dot -Tsvg -odag.svg dag.dot


