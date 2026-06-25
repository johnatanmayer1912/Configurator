# NX-OS Change Package

**Generated:** 2026-06-24 08:53:26
**Application:** NX-OS Configuration Authority v6.0.0
**Site:** HQ_DC
**Scenario:** vPC Core Pair (40G) (`vpc_core_pair`)
**NX-OS train:** 9.3
**Lab ready:** Yes

## Files in this folder

- `HQ_DC_vpc_core_pair_CORE1-VPC_20260624_085326_device.json`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260624_085326_config.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260624_085326_diff.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260624_085326_risk.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260624_085326_scenario.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC_20260624_085326_blueprint_summary.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260624_085326_device.json`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260624_085326_config.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260624_085326_diff.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260624_085326_risk.txt`
- `HQ_DC_vpc_core_pair_CORE1-VPC-B_20260624_085326_scenario.txt`

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
