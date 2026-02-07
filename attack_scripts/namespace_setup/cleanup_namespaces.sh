#!/bin/bash
# cleanup_namespaces.sh - Remove all namespaces

if [[ $EUID -ne 0 ]]; then
    echo "Error: Run with sudo"
    exit 1
fi

echo "Removing namespaces..."

for ns in recon bruteforce exploit postaccess multistage; do
    if ip netns list | grep -q "^$ns"; then
        ip netns del "$ns"
        echo "  Removed $ns"
    fi
done

echo "Done."
