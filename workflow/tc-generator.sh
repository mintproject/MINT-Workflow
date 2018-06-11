#!/bin/bash

cat <<EOF

# Lucas' PIHM image from DockerHub
cont PIHM_Docker {
    type "docker"
    image "docker://lucasaugustomcc/pihm"
}

tr PIHM-setup.sh {
    site condor_pool {
        type "STAGEABLE"
        container "PIHM_Docker"
        pfn "file://$PWD/PIHM/PIHM-setup.sh"
    }
}

tr PIHM-wrapper.sh {
    site condor_pool {
        type "STAGEABLE"
        container "PIHM_Docker"
        pfn "file://$PWD/PIHM/PIHM-wrapper.sh"
    }
}

tr Cycles-setup.sh {
    site condor_pool {
        type "STAGEABLE"
        pfn "file://$PWD/Cycles/Cycles-setup.sh"
    }
}

tr Cycles-wrapper.sh {
    site condor_pool {
        type "STAGEABLE"
        pfn "file://$PWD/Cycles/Cycles-wrapper.sh"
    }
}

tr LDAS.sh {
    site condor_pool {
        type "STAGEABLE"
        pfn "file://$PWD/weather/LDAS.sh"
    }
} 

tr LDAS-Cycles-transformation.sh {
    site condor_pool {
        type "STAGEABLE"
        pfn "file://$PWD/transformations/LDAS-Cycles-transformation.sh"
    }
} 

tr LDAS-PIHM-transformation.sh {
    site condor_pool {
        type "STAGEABLE"
        pfn "file://$PWD/transformations/LDAS-PIHM-transformation.sh"
    }
} 

tr PIHM-Cycles-transformation.sh {
    site condor_pool {
        type "STAGEABLE"
        pfn "file://$PWD/transformations/PIHM-Cycles-transformation.sh"
    }
} 

EOF

