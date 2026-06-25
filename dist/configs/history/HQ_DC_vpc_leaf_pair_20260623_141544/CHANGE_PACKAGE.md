# NX-OS Change Package

**Generated:** 2026-06-23 14:15:44
**Application:** NX-OS Configuration Authority v6.0.0
**Site:** HQ_DC
**Scenario:** vPC Leaf Pair (Primary + Secondary) (`vpc_leaf_pair`)
**NX-OS train:** 9.3
**Lab ready:** Yes

## Files in this folder

- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-A_20260623_141544_device.json`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-A_20260623_141544_config.txt`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-A_20260623_141544_diff.txt`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-A_20260623_141544_risk.txt`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-A_20260623_141544_scenario.txt`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-A_20260623_141544_blueprint_summary.txt`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-B_20260623_141544_device.json`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-B_20260623_141544_config.txt`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-B_20260623_141544_diff.txt`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-B_20260623_141544_risk.txt`
- `HQ_DC_vpc_leaf_pair_DC-LEAF-01-B_20260623_141544_scenario.txt`

## Switches

- **DC-LEAF-01-A** (primary)
  - Keepalive: local `1.1.1.1` → remote `1.1.1.2`
- **DC-LEAF-01-B** (secondary)
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
