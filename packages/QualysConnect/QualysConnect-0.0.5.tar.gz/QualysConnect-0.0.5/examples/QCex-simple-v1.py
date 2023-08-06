#!/usr/bin/env python
import sys
import logging

from qualysconnect.util import build_v1_connector

# Questions?  See:
#  https://bitbucket.org/uWaterloo_IST_ISS/python-qualysconnect

if __name__ == '__main__':
    # Basic command line processing.
    if len(sys.argv) != 2:
        print 'A single IPv4 address is expected as the only argument'
        sys.exit(2)
    
    # Set the MAXIMUM level of log messages displayed @ runtime. 
    logging.basicConfig(level=logging.INFO)
    
    # Call helper that creates a connection w/ HTTP-Basic to QualysGuard v1 API
    qgs=build_v1_connector()

    # Formulate a request to the QualysGuard V1 API 
    #  docs @
    #  https://community.qualys.com/docs/DOC-1324
    #  http://www.qualys.com/docs/QualysGuard_API_User_Guide.pdf
    ret = qgs.request("asset_search.php?target_ips=%s&"%(sys.argv[1]))

    print ret
