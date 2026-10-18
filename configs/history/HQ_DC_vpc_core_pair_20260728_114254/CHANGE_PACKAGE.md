# NX-OS Change Package

**Generated:** 2026-07-28 11:42:54
**Application:** NX-OS Configuration Authority v6.38.0
**Site:** HQ_DC
**Scenario:** vPC Core Pair (40G) (`vpc_core_pair`)
**NX-OS train:** 9.3
**Lab ready:** Yes

## Files in this folder

- `CORE1-VPC_20260728_114254_device.json`
- `CORE1-VPC_20260728_114254_config.txt`
- `CORE1-VPC_20260728_114254_diff.txt`
- `CORE1-VPC_20260728_114254_risk.txt`
- `CORE1-VPC_20260728_114254_scenario.txt`
- `CORE1-VPC_20260728_114254_blueprint_summary.txt`
- `k_20260728_114254_device.json`
- `k_20260728_114254_config.txt`
- `k_20260728_114254_diff.txt`
- `k_20260728_114254_risk.txt`
- `k_20260728_114254_scenario.txt`

## Switches

- **CORE1-VPC** (primary)
  - Keepalive: local `1.1.1.1` → remote `1.1.1.2`
- **k** (secondary)
  - Keepalive: local `1.1.1.2` → remote `1.1.1.1`

## vPC pair notes

- Paste **primary** config on switch A first, then **secondary** on switch B.
- Secondary hostname uses `-B` suffix; keepalive IPs are swapped automatically.
- After paste: `show vpc brief`, `show interface status`, `copy run start` only after lab sign-off.

## Rollback reminder

- Keep the pasted running-config backup before applying this build.
- Use **Compare** on Review step or `_diff.txt` artifacts to review deltas.

## Post-paste checklist

1. `show running-config | sec vpc`
2. `show vpc brief`
3. `show interface status err-disabled`
4. `show ip route vrf management`
