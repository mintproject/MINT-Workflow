#!/bin/bash

cat <<EOF

cont Ubuntu18_Docker {
    type "docker"
    image "docker://mintproject/base-ubuntu18:latest"
}

cont PIHM_Docker {
    type "docker"
    image "docker://mintproject/pihm:latest"
}

tr LDAS-data-find {
    site condor_pool {
        type "STAGEABLE"
        container "Ubuntu18_Docker"
        pfn "file://$PWD/weather/LDAS-data-find"
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

tr FLDAS-Cycles-transformation.py {
    site condor_pool {
        type "STAGEABLE"
        container "Ubuntu18_Docker"
        pfn "file://$PWD/transformations/FLDAS-Cycles-transformation.py"
    }
} 

tr LDAS-PIHM-transformation.sh {
    site condor_pool {
        type "STAGEABLE"
        container "PIHM_Docker"
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

