#!/bin/bash

# Configuration
AGENT_NAME="search_specialist"  # Replace with your agent's name
PAYLOAD='{
           "jsonrpc": "2.0",
           "method": "message/send",
           "id": 1,
           "params": {
             "message": {
               "messageId": "msg-001",
               "role": "user",
               "parts": [
                 {
                   "kind": "text",
                   "text": "Tell me how important multi agent systems are?"
                 }
               ]
             }
           }
         }'

# Check for dependencies
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed."
    exit 1
fi

if ! command -v awscurl &> /dev/null; then
    echo "Error: awscurl is not installed. Run 'pip install awscurl'"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it to parse JSON output."
    exit 1
fi

# Set default region
REGION="ap-southeast-2"

echo "--- Retrieving Agent Metadata ---"

# 1. List all agent runtimes and filter for our agent
RUNTIMES=$(aws bedrock-agentcore-control list-agent-runtimes \
    --region "$REGION" \
    --output json)

# 2. Extract the ARN for our specific agent by name
RAW_ARN=$(echo "$RUNTIMES" | jq -r --arg name "$AGENT_NAME" \
    '.agentRuntimes[] | select(.agentRuntimeName == $name) | .agentRuntimeArn')

if [ -z "$RAW_ARN" ] || [ "$RAW_ARN" = "null" ]; then
    echo "Error: Could not retrieve Agent ARN. Ensure the agent is deployed and named correctly."
    echo "You can list agents using: agentcore list"
    exit 1
fi

echo "Found Agent ARN: $RAW_ARN"
echo "Region: $REGION"

# 3. URL Encode the ARN
# The AgentCore Runtime URL requires the ARN to be percent-encoded
# specifically replacing ':' with '%3A' and '/' with '%2F'
ENCODED_ARN=$(echo "$RAW_ARN" | sed 's/:/%3A/g; s/\//%2F/g')

# 4. Construct the URL
# Format: https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{EncodedARN}/invocations
URL="https://bedrock-agentcore.$REGION.amazonaws.com/runtimes/$ENCODED_ARN"

echo "--- Invoking Agent ---"
echo "URL: $URL"

# 5. Call with awscurl
# --service: bedrock-agentcore is the specific service name for SigV4 signing
awscurl --service bedrock-agentcore \
        --region "$REGION" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$PAYLOAD" \
        "$URL/invocations" | jq .