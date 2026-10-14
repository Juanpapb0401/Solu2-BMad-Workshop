# Ronda 10 — gaps de epics.md → node IDs nuevos (de la pasada ATDD R10)
Prefijo: test/atdd/module1_<op>.test.py:: (verificar nombre exacto de archivo con pytest --collect-only). P=TestPreconditions, I=TestInvariants.
- G-2 | revoke · I · test_revoke_busy_timeout_exhausted_503_no_partial_commit
- G-3 | resolve · I · test_resolve_after_drop_isolates_other_course_and_logs_each_deny
- G-4 | resolve · P · test_resolve_identity_barred_denies_before_membership[SUSPENDED|EXPELLED]; test_resolve_identity_barred_precedes_subject_mismatch
- G-4b | resolve · P · test_resolve_suspended_or_completed_membership_denies_context_missing[SUSPENDED|COMPLETED]
- G-5 | resolve · P · test_resolve_header_cs101_arn_cs480_mismatch_403
- G-6 | resolve · P · test_resolve_lowercase_course_header_404_unknown_course
- G-7 | resolve · P · test_resolve_missing_identity_and_course_reports_identity_first
- G-8 | ingest · P · test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-distinto|eco-ausente]
- G-9 | ingest · I · test_ingest_institutional_id_case_distinct_identity
- G-10 | revoke · P · test_revoke_drop_reason_281_chars_400_no_mutation
- G-11 | revoke · P · test_revoke_empty_reason_and_missing_timestamp_rule_ids_order
- G-12 | revoke · P · test_revoke_timestamp_outside_rfc3339_grammar_400[6 ids]
- G-13 | ingest_rules · I · test_ingest_credential_lookup_by_key_prefix_then_verifies_hash
- G-14 | guard · TestDDLGuards · test_guard_edge_case_seed_duplicates_rejected_by_pk
- G-17 | resolve · I · test_resolve_deny_response_has_no_quota_or_priority_fields
- G-1, G-15, G-16 | sin test (NFR PLANNED / DEFER B: recuperación de cola tras fallo de persistencia post-aceptación; AD-12 cola llena SÍ tiene RED: T-RES-13, T-ROS-13, T-REV-06)
- T-REV-01 → T-REV-01b test_revoke_preserves_other_course
