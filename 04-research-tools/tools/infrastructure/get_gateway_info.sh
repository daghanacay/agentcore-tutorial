#!/bin/bash
# Script to retrieve gateway information using AWS CLI
#
# Usage:
#   ./get_gateway_info.sh <gateway-name> [region]
#
# Example:
#   ./get_gateway_info.sh research-tool-gateway ap-southeast-2

set -e

# Check if gateway name provided
if [ -z "$1" ]; then
    echo "Error: Gateway name is required"
    echo "Usage: $0 <gateway-name> [region]"
    exit 1
fi

GATEWAY_NAME="$1"
REGION="${2:-ap-southeast-2}"  # Default to ap-southeast-2 if not provided

echo "========================================="
echo "Retrieving Gateway Information"
echo "========================================="
echo "Gateway Name: $GATEWAY_NAME"
echo "Region: $REGION"
echo ""

# Get gateway details using agentcore CLI
echo "Fetching gateway details..."
agentcore gateway get-mcp-gateway \
    --name "$GATEWAY_NAME" \
    --region "$REGION" > gateway_info.json

# Check if command succeeded
if [ $? -eq 0 ]; then
    echo "✓ Gateway information saved to gateway_info.json"
    echo ""

    # Display the information
    echo "Gateway Details:"
    echo "========================================="
    cat gateway_info.json | jq '.'
    echo ""

    # Extract and display key values
    echo "Environment Variables:"
    echo "========================================="

    # Method 1: Using jq (recommended)
    if command -v jq &> /dev/null; then
        GATEWAY_ID=$(jq -r '.id' gateway_info.json)
        GATEWAY_ARN=$(jq -r '.arn' gateway_info.json)
        GATEWAY_URL=$(jq -r '.url' gateway_info.json)
        ROLE_ARN=$(jq -r '.executionRoleArn' gateway_info.json)

        echo "export GATEWAY_ID='$GATEWAY_ID'"
        echo "export GATEWAY_ARN='$GATEWAY_ARN'"
        echo "export GATEWAY_URL='$GATEWAY_URL'"
        echo "export ROLE_ARN='$ROLE_ARN'"

        # Save to file that can be sourced
        cat > gateway_env.sh << EOF
# Gateway environment variables
# Source this file: source gateway_env.sh

export GATEWAY_ID='$GATEWAY_ID'
export GATEWAY_ARN='$GATEWAY_ARN'
export GATEWAY_URL='$GATEWAY_URL'
export ROLE_ARN='$ROLE_ARN'
EOF

        echo ""
        echo "✓ Environment variables saved to gateway_env.sh"
        echo "  Run: source gateway_env.sh"

    else
        echo "Warning: jq not found. Install jq to automatically extract values."
        echo "  Install with: sudo apt-get install jq (Ubuntu/Debian)"
        echo "               brew install jq (macOS)"
    fi

    echo ""
    echo "========================================="
    echo "Next Steps:"
    echo "========================================="
    echo "1. Source the environment variables:"
    echo "   source gateway_env.sh"
    echo ""
    echo "2. Verify the values:"
    echo "   echo \$GATEWAY_ARN"
    echo ""
    echo "3. Add gateway targets using the environment variables"

else
    echo "✗ Failed to retrieve gateway information"
    echo "Make sure:"
    echo "  1. Gateway exists with name: $GATEWAY_NAME"
    echo "  2. You have proper AWS credentials configured"
    echo "  3. Region is correct: $REGION"
    exit 1
fi
