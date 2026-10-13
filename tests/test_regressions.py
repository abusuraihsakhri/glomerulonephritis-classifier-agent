"""Regression tests for integrity checks, CSV bools and defensive validation."""
import csv
import os
from pathlib import Path

import pytest

os.environ.setdefault("AUDIT_SECRET_KEY", "regression-tests-only-key-1234567890")

from agents.base import AuditTrail, PHIGuard, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main as enterprise_main, parse_csv_bool as enterprise_csv_bool
from glomerulonephritis_classifier_agent.cli import main as legacy_main
from glomerulonephritis_classifier_agent.cli import parse_csv_bool as legacy_csv_bool
from glomerulo_mind import parse_csv_bool as mind_csv_bool


def test_audit_tampering_detected():
    trail = AuditTrail(secret_key="integration-test-key-1234567890")
    trail.log("test", "test", "accepted", {"synthetic_id": "SYN-100"})
    assert trail.verify_integrity()
    received = trail.get_trail()
    received[0]["event_type"] = "local-copy-only"
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "unauthorized-change"
    assert not trail.verify_integrity()


def test_nested_phi_rejected():
    task = SystemTaskPayload(
        task_id="T100", target_identifier="SYN-100", primary_metric=2,
        attributes={"note": "MRN-994827"}
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(task)


@pytest.mark.parametrize("parser", [enterprise_csv_bool, legacy_csv_bool, mind_csv_bool])
def test_explicit_csv_bool(parser):
    assert parser("False") is False
    assert parser("TRUE") is True
    assert parser("0") is False
    assert parser("yes") is True
    with pytest.raises(ValueError):
        parser("sometimes")


def test_reject_whitespace_identifiers():
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="  ", target_identifier="SYN-1", primary_metric=1)


def test_batch_csv_false_does_not_escalate(tmp_path):
    source = tmp_path / "in.csv"
    destination = tmp_path / "out.csv"
    source.write_text("task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\\n"
                      "T1,SYN-1,10,1,NOMINAL,False\\n".replace("\\n", "\n"), encoding="utf-8")
    assert enterprise_main(["batch", "-i", str(source), "-o", str(destination)]) == 0
    with destination.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file))
    assert row["overall_urgency"] == "ROUTINE"


def test_legacy_batch_csv_false_does_not_escalate(tmp_path):
    source = tmp_path / "in.csv"
    destination = tmp_path / "out.csv"
    source.write_text("case_id,patient_synthetic_id,metric_primary,metric_secondary,status_flag,is_stat\n"
                      "T1,SYN-1,10,1,NORMAL,False\n", encoding="utf-8")
    assert legacy_main(["batch", "-i", str(source), "-o", str(destination)]) == 0
    with destination.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file))
    assert row["overall_status"] == "CONCORDANT_NORMAL"
