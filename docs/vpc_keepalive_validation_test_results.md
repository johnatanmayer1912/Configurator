# vPC Keepalive IP Validation Test Results

**Version:** 6.38.8  
**Date:** 2026-08-02  
**Test File:** `tests/e2e/test_vpc_keepalive_validation.py`

## Summary

All 6 test scenarios passed successfully. The validation logic now correctly implements the user's requirements:
- Each switch in a vPC pair must have a different keepalive IP
- Same keepalive IPs can be reused across different vPC domains
- No IP mirroring requirement between switches in a pair

## Test Scenarios

### Scenario 1: Single Pair Correct
**Configuration:**
- Domain 10: SW1=10.0.0.1, SW2=10.0.0.2

**Expected:** VALID (no errors)

**Result:** ✅ PASSED
- Valid: True
- Issues: []
- Summary: {'critical': 0, 'warning': 0, 'info': 0}

**Details:** Different IPs within the same vPC pair are correctly validated.

---

### Scenario 2: Single Pair Incorrect IPs
**Configuration:**
- Domain 10: SW1=10.0.0.1, SW2=10.10.10.2

**Expected:** VALID (different IPs within pair is allowed)

**Result:** ✅ PASSED
- Valid: True
- Issues: []
- Summary: {'critical': 0, 'warning': 0, 'info': 0}

**Details:** Even with different IP subnets, as long as the IPs are different within the pair, validation passes.

---

### Scenario 3: Two Pairs Same IPs Different Domains
**Configuration:**
- Domain 10: SW1=10.0.0.1, SW2=10.0.0.2
- Domain 100: SW3=10.0.0.1, SW4=10.0.0.2

**Expected:** VALID (same IPs allowed across different domains)

**Result:** ✅ PASSED
- Valid: True
- Issues: []
- Summary: {'critical': 0, 'warning': 0, 'info': 0}

**Details:** Same keepalive IPs (10.0.0.1, 10.0.0.2) are correctly reused across different vPC domains (10 and 100).

---

### Scenario 4: Two Pairs Mixed IPs
**Configuration:**
- Domain 10: SW1=10.10.0.1, SW2=10.0.0.2
- Domain 100: SW3=10.0.0.1, SW4=10.0.20.2

**Expected:** VALID (different IPs within each pair)

**Result:** ✅ PASSED
- Valid: True
- Issues: []
- Summary: {'critical': 0, 'warning': 0, 'info': 0}

**Details:** Different IPs within each pair are correctly validated, regardless of IP subnets.

---

### Scenario 5: Same IP Within Pair (Invalid)
**Configuration:**
- Domain 10: SW1=10.0.0.1, SW2=10.0.0.1

**Expected:** INVALID (same IP within pair is not allowed)

**Result:** ✅ PASSED
- Valid: False
- Issues: [{'severity': 'critical', 'category': 'vpc_mismatch', 'message': 'vPC keepalive IP conflict: SW1 and SW2 both use keepalive IP (10.0.0.1) in domain 10', 'affected_switches': ['SW1', 'SW2'], 'suggestion': 'Configure different keepalive IPs for SW1 and SW2 within vPC domain 10'}]
- Summary: {'critical': 1, 'warning': 0, 'info': 0}

**Details:** Correctly detects when both switches in a vPC pair use the same keepalive IP and reports a critical error.

---

### Scenario 6: Random IPs Two Pairs
**Configuration:**
- Domain 10: SW1=192.168.1.1, SW2=192.168.1.2
- Domain 100: SW3=172.16.1.1, SW4=172.16.1.2

**Expected:** VALID (different IPs within each pair)

**Result:** ✅ PASSED
- Valid: True
- Issues: []
- Summary: {'critical': 0, 'warning': 0, 'info': 0}

**Details:** Random IP addresses from different subnets are correctly validated as long as they differ within each pair.

---

## Validation Logic Changes

### Previous Logic (Incorrect)
- Required IP mirroring: primary.local_ka == secondary.remote_ka
- Required IP mirroring: secondary.local_ka == primary.remote_ka
- This enforced a specific source/destination relationship that didn't match user requirements

### New Logic (Correct)
- Only checks that switches in the same vPC pair have different keepalive IPs
- Allows same keepalive IPs across different vPC domains
- No mirroring requirement between switches

### Code Changes
**File:** `api/main.py` (lines 4071-4075, 4120-4132)

Removed:
- IP mirroring validation checks
- local_ka == remote_ka self-reference check

Added:
- Simple check: primary.local_ka != secondary.local_ka
- Clear error message when same IP is used within a pair

## Template Changes

**File:** `templates/deployment_templates.json` (lines 23-28)

Updated vPC Core + Leaf template:
- CORE1: local_ka="10.0.0.1" (removed remote_ka)
- CORE2: local_ka="10.0.0.2" (removed remote_ka)
- LEAF10G-1: local_ka="10.0.0.1" (removed remote_ka)
- LEAF10G-2: local_ka="10.0.0.2" (removed remote_ka)

This matches the user's model where each switch has a single keepalive IP.

## Test Execution

**Command:** `python -m pytest tests/e2e/test_vpc_keepalive_validation.py -v -s`

**Result:** 6 passed in 0.80s

All tests passed successfully, confirming the validation logic works correctly according to the user's requirements.
