#!/bin/bash

pegasus-graphviz --nosimplify dax.xml | sed 's/\.sh//g' | sed 's/-wrapper//g' >dax.dot
dot -Tsvg -odax.svg dax.dot

pegasus-graphviz MINT-0.dag | sed 's/_sh_/_/g' | sed 's/-wrapper//g' > dag.dag
dot -Tsvg -odag.svg dag.dot


