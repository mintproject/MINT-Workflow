#!/bin/bash

cat <<EOF

# Lucas' PIHM image from DockerHub
cont PIHM_Docker {
    type "docker"
    image "docker://lucasaugustomcc/pihm"
}

tr PIHM-wrapper.sh {
    site condor_pool {
        type "STAGEABLE"
        container "PIHM_Docker"
        pfn "file://$PWD/PIHM/PIHM-wrapper.sh"
    }
}

tr Cycles-prepare-inputs.sh {
    site condor_pool {
        type "STAGEABLE"
        pfn "file://$PWD/Cycles/Cycles-prepare-inputs.sh"
    }
}

tr Cycles-wrapper.sh {
    site condor_pool {
        type "STAGEABLE"
        pfn "file://$PWD/Cycles/Cycles-wrapper.sh"
    }
}

EOF

