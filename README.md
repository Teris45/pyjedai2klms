# Welcome to the KLMS Tool Template

<img src="https://raw.githubusercontent.com/stelar-eu/klms-tool-template/refs/heads/main/logo.png" alt="Stelar Tool Template" width="150"/>

Here you may find a lightweight and easy to use template that can encapsulate any data analysis and interlinking tools ready to run inside the KLMS Cluster. 

> This template is made for tools written in **Python**. Other language templates may also be implemented following this paradigm.


# Directory Structure

The directory structure used by the template is simple and straight-forward: 
```
.
├── run.sh 
├── main.py
├── requirements.txt
├── Makefile
├── Dockerfile
└── utils/
    └── minio_client.py
```
##  `run.sh`

This file is the entrypoint of the Docker Image as defined in the `Dockerfile`. It takes 3 arguments:

- `$1 --> token` : The OAuth 2.0 user token used for making cURL requests to the KLMS Data API for fetching and commiting job execution parameters and metrics.
- `$2 --> endpoint_url` : The URL at which the KLMS Data API is listening. At this url two cURL requests are made. The first one fetches the task execution parameters among various other task specs. 
- `$3 --> id` : A unique ID which is linked to the task execution inside the KLMS Cluster.

The `run.sh` script serves as a wrapper for executing `main.py`, effectively decoupling the tool's core source code from direct API calls. Instead, the tool's main runtime (`main.py`) will have the necessary parameters for job execution already available upon initiation. This separation ensures that `main.py` can focus solely on its core functionality, while `run.sh` handles the setup and provides the required execution parameters. 

`run.sh` has a very explicit structure and **should not be modified in any way**. The logic of this script should not concern the tool developer.

**As of November 23, 2024 the run.sh endpoints have been modified to meet the requirements of the refactored STELAR API to be released in early December 2024.**

## `requirements.txt`
Inside this file any python libaries should be declared in order to be installed in the tool image when it is built. You may include libraries in the following way:

```python
minio
requests
numpy==2.1.2
```
The `requirements.txt` can be seen as any plain requirements setting file present in the vast majority of Python projects.

## `main.py`

The `main.py` file is the central component responsible for initiating the tool's execution. You may imagine this as **tool.py**. It serves as the entry point for running the program, containing all essential logic and any necessary configurations for the tool's behavior.

-   **Custom and Explicit Structure**: `main.py` is designed with a clear and custom structure to explicitly define the workflow of the tool. It ensures that the program’s core functionality is readable, maintainable, and logically organized.
    
-   **Imports Needed Tool `.py` Files**: The script also imports various Python files (`.py`) that contain supplementary functions, modules, or classes required by the tool. This modular approach facilitates better organization and reusability of code.

From a technical scope the `main.py` consists of a single specified method that can host the tool source (`run(json)`). The structure is briefly explained in the below pseudocode block:

```python
def run(json):
	
	#Any tool specific code can go in here
	#Method and libraries can be also defined and imported.
...

if __name__='__main__':

	json = read from sys.argv[1]
	...
	response = run(json)
	...
    write to sys.argv[2]	
```

`run(json)` method has an **argument** `json` and **must return** a result in JSON form as shown below at `sys.argv[2]`.

As mentioned earlier, the program requires certain **arguments** to effectively receive and provide data/parameters necessary for tool execution. These arguments are provided by the `run.sh` wrapper script, and their presence during runtime can be assumed as a given.

The main responsibility of `main.py` is to control the initiation of execution, orchestrating different parts of the tool while keeping the source code modular and focused on the specific tasks that constitute the tool's functionality. For documentation purposes let's define what those arguments are:

 - `sys.argv[1]` : The first argument is the **input parameters in JSON format** fetched from the first cURL request made by the `run.sh` to the API. Its format may be found below:
	```json
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
	```

	**The `inputs` field contains sets of input files as defined in the tool spec and each field corresponds to an array of paths**
	
	**The `outputs` field provides the paths in which the tool should write its output prior the completion of its execution.**
	
	**The `secrets` field contains any sensitive credentials (API Keys, Passwords) that the tool needs. It is accessible only if the task signature, provided by the API during its creation, is included in the request to the KLMS API (For tools running inside the cluster this is ensured by `run.sh`)**
	
	**The tool developer may access tool specific parameters that were set during the execution call in the `parameters` field of the input JSON object. The `parameters` field can be as long as the tool need**.


 - `sys.argv[2]` : The second argument follows the same logic as the first one. **It is the output and metrics produced by the tool**, also in JSON format. This output block will be pushed to the KLMS API by the wrapper `run.sh` script.  Its format may be found below:
	```json
	{
		"message": "Tool executed successfully!",
		"outputs": {
			"correlations_file": "XXXXXXXXX-bucket/2824af95-1467-4b0b-b12a-21eba4c3ac0f.csv",
			"synopses_file": "XXXXXXXXX-bucket/21eba4c3ac0f.csv"			
		},
		"metrics": {	
			"memory_allocated": "2048",
			"peak_cpu_usage": "2.8"
		},
		"status": "success"
	}
	```

	**The tool developer needs to return the output JSON through the** `run(json)` **method in the above format.** The structure of the expected output is explained briefly below:
	 - `message` : A generic message recorded as metadata of the task execution
	 - `outputs` : The data objects generated by the tool execution which lie inside the MinIO Object store.
	 - `metrics` : Any valuable or outstanding metrics calculated during the tool's execution
	 - `status`:   A code defining the exit status of the tool execution. Conventionally linked to HTTP status codes. If the tool execution fails you may return a 500 or 424 or 409. 

## `Makefile`
This file bundles the logic of **building**, **tagging** and **pushing** the tool image. Its logic is nothing that should be concern the tool developer. The only thing that needs to be modified inside this file is the **repository name** and the **image name & tag**. For example, the `Makefile` at the top lines offers a variable holding this info:

```bash
IMGTAG=yourusername/yourimagereponame:yourversiontag
```
If someone (user: **jsmith**) wanted to push the image **footool:1.0.0** the above line should be modified as:
```bash
IMGTAG=jsmith/footool:1.0.0
```
More info about the building process may be found the **Usage** section.

## `Dockerfile`

The Dockerfile comprises the manifest upon which the tool image is created. Its logic is very simple but should not concern the tool developer. Its core responsibilities are:

- Installing **Python** inside the Tool Image
- Installing the libraries defined in `requirements.txt`
- Setting the **execution entrypoint** followed by any container created upon the image.

# Usage

In this section we delve into the usage of the template from a generic scope focused on how to setup, use, adjust and build finally the desired tool image.


## Install Dependencies

If you have the following packages installed in your system:

-	`git`
-	`docker`
-	`docker.io`
-	`build-essential`

you are good to go to the next step. If not please follow the next steps:

### Updating the package and repositories

```bash
sudo apt-get update
```

### Installing `git`:
```bash
sudo apt install git-all
```

### Installing `docker` and `docker.io`:
```bash
sudo apt install docker docker.io
```

### Installing `build-essential`:
```bash
sudo apt install build-essential
```

### Windows? No problem!

You may find detailed instructions in the links down below:

<a href="https://git-scm.com/book/en/v2/Getting-Started-Installing-Git#:~:text=Installing%20on%20Windows" target="_blank">Install Git in Windows</a>

<a href="https://www.simplilearn.com/tutorials/docker-tutorial/install-docker-on-windows" target="_blank">Install Docker in Windows</a>

<a href="https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows" target="_blank">Install Make (used to run the Makefile) in Windows</a>

## Your free copy to take home!
You may fetch this template to modify it locally by running the following `git clone` in your desired location:

```bash
git clone https://github.com/stelar-eu/klms-tool-template
```

## Setting up DockerHub Account & Credentials

Firstly you need to create an account in DockerHub by following this link https://app.docker.com/signup . 
**Be sure about your username** as this will be the name prepending to your repositories (Think DockerHub as GitHub). The registration process is easy and simple. 

After you succesfully create an account in DockerHub be sure to login on your local terminal by running:

```bash
sudo docker login
```
A prompt will appear asking for `username` and `password`. The credentials **are the ones you used for account registration in DockerHub**.

After that your local Docker Account is set up!

## Modify template up to Tool prerequisites

Now you are ready to start embedding your tool into the template. The files that need to be modified are :

- `main.py` as explained above in the **Directory Structure** section. Explanative comments are also available inside the script
- `requirements.txt` recording your tool python library names 
- `Makefile` with your appropriate **docker hub repository** and **image name**.


## Build it!

After you are satisfied with your tool embedding and you are ready to make it available to STELAR partners you may simply run:

```bash
make 
```

The `Makefile` will handle all the complicated steps needed to build the image and push it to your repository in DockerHub.



> Before hitting `make` make sure you have run `docker login` in order to authenticate/authorize for DockerHub.



## Great! Your tool is now published
Thanks for your effort! Your tool is now ready to be integrated inside the KLMS cluster.
