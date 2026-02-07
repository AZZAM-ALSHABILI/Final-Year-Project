#!/bin/bash
# test_namespaces.sh - Test connectivity from each namespace

if [[ $EUID -ne 0 ]]; then
    echo "Error: Run with sudo"
    exit 1
fi

COWRIE="172.16.0.20"
DIONAEA="172.16.0.30"

echo "Testing namespace connectivity..."
echo ""

for ns in recon bruteforce exploit postaccess multistage; do
    if ! ip netns list | grep -q "^$ns"; then
        echo "$ns: NOT FOUND"
        continue
    fi

    # Test Cowrie
    if ip netns exec "$ns" ping -c 1 -W 2 "$COWRIE" >/dev/null 2>&1; then
        cowrie_status="OK"
    else
        cowrie_status="FAIL"
    fi

    # Test Dionaea
    if ip netns exec "$ns" ping -c 1 -W 2 "$DIONAEA" >/dev/null 2>&1; then
        dionaea_status="OK"
    else
        dionaea_status="FAIL"
    fi
    echo "$ns: Cowrie=$cowrie_status, Dionaea=$dionaea_status"
done

echo ""
echo "Done."
