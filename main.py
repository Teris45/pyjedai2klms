import json
import sys
import traceback
from utils.mclient import MinioClient

# Here you may define the imports your tool needs...
# import pandas as pd
# import numpy as np
# ...

def run(json):

    """
        This is the core method that initiates tool .py files execution. 
        It can be as large and complex as the tools needs. In this file you may import, call,
        and define any lib, method, variable or function you need for you tool execution.
        Any specific files you need can be in the same directory with this main.py or in subdirs
        with appropriate import statements with respect to dir structure.

        Any logic you implement here is going to be copied inside your tool image when 
        you build it using docker build or the provided Makefile.
        
            The MinIO initialization that is given down below is an example you may use it or not.
            MinIO access credentials are in the form of <ACCESS ID, ACCESS KEY, SESSION TOKEN>
            and are generated upon the OAuth 2.0 token of the user executing the tool. 

            For development purpose you may define your own credentials for your local MinIO 
            instance by commenting the MinIO init part.

    """

    try:
        """
        Init a MinIO Client using the custom STELAR MinIO util file.

        We access the MinIO credentials from the JSON field named 'minio' which 
        was acquired along the tool parameters.

        This credentials can be used for tool specific access too wherever needed
        inside this main.py file.

        """
        ################################## MINIO INIT #################################
        minio_id = json['minio']['id']
        minio_key = json['minio']['key']
        minio_skey = json['minio']['skey']
        minio_endpoint = json['minio']['endpoint_url']
        
        mc = MinioClient(minio_id, minio_key, minio_skey, minio_endpoint)

        # It is strongly suggested to use the get_object and put_object methods of the MinioClient
        # as they handle input paths provided by STELAR API appropriately. (S3 like paths)
        ###############################################################################


        """
        Acquire tool specific parameters from json['parameters] which was given by the 
        KLMS Data API during the creation of the Tool Execution Task.

        An example of parameters for a tool that adds two numbers x,y could be:
        {
            "inputs": {
                "any_name": [
                    "XXXXXXXX-bucket/temp1.csv",
                    "XXXXXXXX-bucket/temp2.csv"
                ],
                "temp_files": [
                    "XXXXXXXX-bucket/intermediate.json"
                ]
                
            },
            "outputs": {
                "correlations_file": "/path/to/write/the/file",
                "log_file": "/path/to/write/the/file"
            },
            "parameters": {
                "x": 5,
                "y": 2,
            },
            "secrets": {
                "api_key": "AKIASIOSFODNNEXAMPLE"
            },
            "minio": {
                "endpoint_url": "minio.XXXXXX.gr",
                "id": "XXXXXXXX",
                "key": "XXXXXXXX",
                "skey": "XXXXXXXX",
            }

        }

        The parameters JSON field can be as large as the tool needs.

        For our simple example in this main.py we would access x,y as:
            x = json['parameters']['x']
            y = json['parameters']['y']
        """        
        x = json['parameters']['x'] 
        y = json['parameters']['y']


        """

            Here you may implement the execution logic of your tool. At this point you have available:

                - Tool specific parameters from json['parameters']
                - A client for MinIO acccess named 'mc' with method putObject(...) and getObject(...)
        """

        ##### Tool Logic #####
        z=x+y

        """
            This json should contain any output of your tool that you consider valuable. Metrics field affects
            the metadata of the task execution. Status can be conventionally linked to HTTP status codes in order
            to mark success or error states.

            Output contains the resource ids from MinIO in which the valuable output data of your tool should be written
            An example of the output json is:

            {
                "message": "Tool executed successfully!",
                "outputs": {
                    "correlations_file": "XXXXXXXXX-bucket/2824af95-1467-4b0b-b12a-21eba4c3ac0f.csv",
                    "synopses_file": "XXXXXXXXX-bucket/21eba4c3ac0f.csv"			
                }
                "metrics": {	
                    "memory_allocated": "2048",
                    "peak_cpu_usage": "2.8"
                },
                "status": "success"
            }

        """
        json= {
                'message': 'Tool Executed Succesfully',
                'outputs': {}, 
                'metrics': { 
                    'z': z, 
                }, 
                'status': "success",
              }

        return json
    except Exception as e:
        print(traceback.format_exc())
        return {
            'message': 'An error occurred during data processing.',
            'error': traceback.format_exc(),
            'status': 500
        }
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError("Please provide 2 files.")
    with open(sys.argv[1]) as o:
        j = json.load(o)
    response = run(j)
    with open(sys.argv[2], 'w') as o:
        o.write(json.dumps(response, indent=4))
