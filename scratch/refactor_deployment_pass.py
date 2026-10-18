"""One-shot refactor: split generate_deployment into build / wire / render passes."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "api" / "main.py"
text = p.read_text(encoding="utf-8")

marker_start = '            logger.info(f"PIPELINE_EXECUTION_START"'
marker_end = "            devices.append(device)  # track for cross-switch wiring\n"
idx_start = text.find(marker_start)
idx_end = text.find(marker_end)
if idx_start < 0 or idx_end < 0:
    raise SystemExit(f"markers not found start={idx_start} end={idx_end}")
idx_end += len(marker_end)

pipeline_block = text[idx_start:idx_end]

defer_block = """            # Pass 1 complete — register device; render in pass 3
            device_by_hostname[switch_config.hostname] = device
            pending_switches.append({
                "switch_config": switch_config,
                "device": device,
                "vpc_pair": vpc_pair,
                "switch_idx": switch_idx,
            })
            continue

"""

pass2_block = """
    # Pass 2: cross-switch core→leaf wiring (order-independent)
    wire_core_leaf_downlinks(device_by_hostname, input.switches, catalog, request_id)
    for vpc_err in validate_all_vpc_pairs(device_by_hostname, input.vpc_pairs, device_validator):
        errors.append({"hostname": "vPC-validation", "error": vpc_err})

    # Pass 3: pipeline / export per switch
    for pend in pending_switches:
        switch_config = pend["switch_config"]
        device = pend["device"]
        vpc_pair = pend["vpc_pair"]
        switch_idx = pend["switch_idx"]
        try:
"""

pipeline_lines = pipeline_block.splitlines(keepends=True)
indented_pipeline = "".join(("    " + line if line.strip() else line) for line in pipeline_lines)

pass3_close = """
        except ValidationError as e:
            logger.error(
                "SWITCH_VALIDATION_ERROR_PASS3",
                request_id=request_id,
                switch_index=switch_idx,
                hostname=switch_config.hostname,
                error_report=e.report,
            )
            errors.append({"hostname": switch_config.hostname, "error": e.report["errors"]})
        except Exception as e:
            logger.error(
                "SWITCH_PROCESSING_ERROR_PASS3",
                request_id=request_id,
                switch_index=switch_idx,
                hostname=switch_config.hostname,
                error=str(e),
            )
            errors.append({"hostname": switch_config.hostname, "error": str(e)})

"""

loop_end_marker = (
    '    logger.info(f"SWITCH_PROCESSING_COMPLETE",\n'
    "               request_id=request_id,\n"
    "               total_switches=len(input.switches),"
)
loop_end = text.find(loop_end_marker)
if loop_end < 0:
    raise SystemExit("loop end not found")

new_text = (
    text[:idx_start]
    + defer_block
    + text[idx_end:loop_end]
    + pass2_block
    + indented_pipeline
    + pass3_close
    + text[loop_end:]
)
p.write_text(new_text, encoding="utf-8")
print("Refactored generate_deployment to three-pass")
