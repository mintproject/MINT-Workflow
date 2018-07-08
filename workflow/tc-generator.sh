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

cont Cycles_Docker {
    type "docker"
    image "docker://mintproject/cycles:latest"
}

cont Economic_Docker {
    type "docker"
    image "docker://mintproject/economic:latest"
}

tr LDAS-data-find {
    site condor_pool {
        type "STAGEABLE"
        container "Ubuntu18_Docker"
        pfn "file://$PWD/weather/LDAS-data-find"
    }
}

tr PIHM-wrapper.py {
    site condor_pool {
        type "STAGEABLE"
        container "PIHM_Docker"
        pfn "file://$PWD/PIHM/PIHM-wrapper.py"
    }
}

tr Cycles-wrapper.sh {
    site condor_pool {
        type "STAGEABLE"
        container "Cycles_Docker"
        pfn "file://$PWD/Cycles/Cycles-wrapper.sh"
    }
}

tr economic-wrapper.sh {
    site condor_pool {
        type "STAGEABLE"
        container "Economic_Docker"
        pfn "file://$PWD/economic/economic-wrapper.sh"
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

tr PIHM-Cycles-transformation.py {
    site condor_pool {
        type "STAGEABLE"
        container "Ubuntu18_Docker"
        pfn "file://$PWD/transformations/PIHM-Cycles-transformation.py"
    }
} 

tr Cycles-to-crop.py {
    site condor_pool {
        type "STAGEABLE"
        container "Ubuntu18_Docker"
        pfn "file://$PWD/transformations/Cycles-to-crop.py"
    }
} 


EOF

