# Deception Configuration Verification

Scripts to verify honeypot deception configurations are correctly applied.

## Script Files

| Script | Target VM | Location |
|--------|-----------|----------|
| `verify_cowrie_deception.sh` | Cowrie | `scripts/` folder |
| `verify_dionaea_deception.sh` | Dionaea | `scripts/` folder |

## How to Use

### Cowrie Verification

1. Transfer script to Cowrie VM:
```bash
scp -P 22222 scripts/verify_cowrie_deception.sh cowrieadmin@172.16.0.20:~/
```

2. Run on Cowrie VM:
```bash
chmod +x ~/verify_cowrie_deception.sh
~/verify_cowrie_deception.sh
```

### Dionaea Verification

1. Transfer script to Dionaea VM:
```bash
scp scripts/verify_dionaea_deception.sh dionaeaadmin@172.16.0.30:~/
```

2. Run on Dionaea VM:
```bash
chmod +x ~/verify_dionaea_deception.sh
~/verify_dionaea_deception.sh
```

## Expected Output

Both scripts should show:
```
==========================================
RESULTS: X passed, 0 failed
==========================================
STATUS: All checks passed!
```

If any checks fail, review the corresponding deception configuration guide and reapply missing files.
