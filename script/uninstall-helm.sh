#!/bin/bash

# Script to uninstall the image-rec Helm chart
# Assumes release name 'image-rec' and namespace 'default' unless overridden

# Variables (customize if needed)
RELEASE_NAME="image-rec"
NAMESPACE="default"

# Function to check command availability
command_exists() {
    command -v "$1" >/dev/null 2>&1 || { echo >&2 "Error: $1 is required but not installed."; exit 1; }
}

# Check for required tools
command_exists helm || exit 1
command_exists kubectl || exit 1

echo "Starting Helm chart uninstall process..."

# Step 1: List installed Helm releases to confirm the release exists
echo "Checking for installed Helm releases in namespace '$NAMESPACE'..."
helm list --namespace "$NAMESPACE" --short | grep -q "$RELEASE_NAME"
if [ $? -eq 0 ]; then
    echo "Found release '$RELEASE_NAME' in namespace '$NAMESPACE'."
else
    echo "No release named '$RELEASE_NAME' found in namespace '$NAMESPACE'. Listing all releases across all namespaces..."
    helm list --all-namespaces
    echo "Please verify the release name and namespace, then rerun with correct values."
    exit 1
fi

# Step 2: Uninstall the Helm chart
echo "Uninstalling Helm release '$RELEASE_NAME' from namespace '$NAMESPACE'..."
helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE"
if [ $? -eq 0 ]; then
    echo "Successfully uninstalled '$RELEASE_NAME'."
else
    echo "Failed to uninstall '$RELEASE_NAME'. Attempting force uninstall..."
    helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE" --force
    if [ $? -eq 0 ]; then
        echo "Force uninstall succeeded."
    else
        echo "Uninstall failed even with force. Check cluster state manually."
        exit 1
    fi
fi

# Step 3: Verify removal of resources
echo "Verifying removal of resources..."

# Check pods
echo "Checking pods in namespace '$NAMESPACE'..."
kubectl get pods --namespace "$NAMESPACE" --no-headers | grep -q "$RELEASE_NAME"
if [ $? -eq 0 ]; then
    echo "Warning: Pods related to '$RELEASE_NAME' still exist. Cleaning up manually..."
    kubectl delete pod -l app.kubernetes.io/name="$RELEASE_NAME" --namespace "$NAMESPACE" --force --grace-period=0
else
    echo "No pods found for '$RELEASE_NAME'."
fi

# Check deployments
echo "Checking deployments in namespace '$NAMESPACE'..."
kubectl get deployments --namespace "$NAMESPACE" --no-headers | grep -q "$RELEASE_NAME"
if [ $? -eq 0 ]; then
    echo "Warning: Deployment for '$RELEASE_NAME' still exists. Deleting..."
    kubectl delete deployment "$RELEASE_NAME" --namespace "$NAMESPACE"
else
    echo "No deployments found for '$RELEASE_NAME'."
fi

# Check services
echo "Checking services in namespace '$NAMESPACE'..."
kubectl get services --namespace "$NAMESPACE" --no-headers | grep -q "$RELEASE_NAME"
if [ $? -eq 0 ]; then
    echo "Warning: Service for '$RELEASE_NAME' still exists. Deleting..."
    kubectl delete service "$RELEASE_NAME" --namespace "$NAMESPACE"
else
    echo "No services found for '$RELEASE_NAME'."
fi

echo "Uninstall process completed successfully!"
