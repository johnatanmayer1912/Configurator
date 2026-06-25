# NX-OS Change Package

**Generated:** 2026-06-23 11:15:13
**Application:** NX-OS Configuration Authority v4.0.0
**Site:** HQ_DC
**Scenario:** vPC Core Pair (40G) (`vpc_core_pair`)
**NX-OS train:** 9.3
**Lab ready:** Yes

## Files in this folder

- `HQ_DC_vpc_core_pair_CORE1-VPC_20260623_111513_device.json`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260623_111513_config.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260623_111513_diff.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260623_111513_risk.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260623_111513_scenario.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260623_111513_blueprint_summary.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260623_111513_device.json`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260623_111513_config.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260623_111513_diff.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260623_111513_risk.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260623_111513_scenario.txt`

## Switches

- **CORE1-VPC** (primary)
  - Keepalive: local `1.1.1.1` → remote `1.1.1.2`
- **CORE1-VPC-B** (secondary)
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
