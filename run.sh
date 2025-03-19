#!/bin/bash

# Check if three arguments are provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <token> <endpoint_url> <id> <signature>"
    exit 2
fi

# Assign command-line arguments to variables
token="$1"
endpoint_url="$2"
id="$3"
signature="$4"

# Construct the first curl command with dynamic arguments and store the response in a variable
# Signature is used to gain access to any secret fields defined during the creation of the task.
# Secret fields are not accessible without a valid signature.
echo "[STELAR INFO] Performing cURL to the KLMS API to fetch input..."
response=$(curl -s -L -X GET -H "Authorization: $token" "$endpoint_url/api/v2/task/$id/$signature/input")

# Check if the curl request was successful
success=$(echo "$response" | jq -r '.success')
if [ "$success" != "true" ]; then
    echo "[STELAR INFO] cURL request to input endpoint V2 has failed!. Aborting..."
    exit 3
fi

# Extract the "result" part from the JSON response
result=$(echo "$response" | jq '.result')

echo "[STELAR INFO] Tool input was fetched from the API endpoint V2."
printf "\n"
# Store the "result" part into a file named "input.json"
echo "$result" > input.json

# Execute the tool and force stdout to be unbuffered
python -u main.py input.json output.json

# Perform the second curl request with replacements and store the response in a variable
output_json=$(<output.json)  # Read content of output.json file into a variable

echo "$output_json"

# Replace task_exec_id and output_json with variables. The signature is used to verify that the tool is authenticated.
# We will not be using token, as it may expire prior to tool completion.
printf "\n"
echo "[STELAR INFO] Performing cURL to the KLMS API to propagate output..."
response=$(curl -s -X POST -H "Content-Type: application/json" "$endpoint_url/api/v2/task/$id/$signature/output" -d "$output_json")

echo "[STELAR INFO] The output request to the KLMS API returned:"
echo "$response"
printf "\n"

# Check if the second curl request was successful
success=$(echo "$response" | jq -r '.success')
if [ "$success" != "true" ]; then
    echo "[STELAR INFO] cURL request to output endpoint V2 has failed. Aborting..."
    exit 4
fi

echo "[STELAR INFO] Tool output was propagated to the API endpoint V2."
