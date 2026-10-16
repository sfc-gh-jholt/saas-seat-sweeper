# 04 - Prove access boundaries

Challenge CoCo's authorization reasoning, then prove app entry and direct-SQL permissions as separate claims.

**Time limit:** 15 minutes, 01:05-01:20. Use 3 minutes for the claim/plan, 6 for app entry, 4 for SQL proof, and 2 for recording/restoration.

## Action

This app uses **owner's rights**, not per-visitor row filtering. An admitted visitor sees service-identity rows; denied direct SQL does not prove that visitor cannot invoke an owner's-rights write endpoint later.

[Prompt CoCo: Challenge the restricted-visitor claim](../coco-prompts/challenge-access.md)

## Your decision

Check code/policy citations and the administrator-prepared restricted identity. Approve only your exact service's USAGE grant/revoke experiment, the specified restricted read and no-row write-denial probe. The restricted user must lack administrative, ownership, inherited or alternate-role access. ACCOUNTADMIN cannot prove denial; switching a worksheet role does not change browser identity.

[Prompt CoCo: Guide the approved entry and SQL permission proofs](../coco-prompts/prove-access.md)

Use an isolated browser profile and clean restricted-user session for each entry check: denied before grant, allowed after grant, denied after revoke. Existing sessions may not invalidate instantly; record actual behavior. If entry persists, stop for administrator review of direct/inherited grants, not broad revocation.

Direct SQL should show Engineering-only governed-view rows. The no-row UPDATE must fail for the intended access-control reason, not missing warehouse/setup. A successful zero-row update is a **failed negative test**. Keep the exact service grant revoked before write-back development.

The demo grants restricted users raw-table SELECT and defaults permissively for other roles. This proves only the named view/role boundary, not tenant isolation. Caller-aware authorization needs separate design and tests, not a helper flag change.

## Expected evidence

Record restricted username/role, clean-session denied/allowed/denied results, direct-SQL departments, actual write-denial error and final revoked grant. Distinguish observed results from CoCo's prediction and the owner's-rights UI limitation.

## Recovery

At minute 70, if no genuinely restricted identity exists, observe the prepared administrator test and mark yours unverified. At minute 77, capture unresolved outcomes, restore the exact revoked state where possible and assign unexpected access to the administrator. Do not improvise role design or consume the break.

## Manual commands

After approval, first test denial in the restricted browser; then grant only this service:

```bash
snow sql --connection "$PARTICIPANT_CONNECTION" --role ACCOUNTADMIN -q "GRANT USAGE ON APPLICATION SERVICE ${PARTICIPANT_APP_FQN} TO ROLE SAAS_SWEEPER_RESTRICTED;"
```

Test allowed entry in a clean session; revoke, then test another clean session:

```bash
snow sql --connection "$PARTICIPANT_CONNECTION" --role ACCOUNTADMIN -q "REVOKE USAGE ON APPLICATION SERVICE ${PARTICIPANT_APP_FQN} FROM ROLE SAAS_SWEEPER_RESTRICTED;"
```

For the separate SQL proof, replace the connection with the assigned restricted user's connection:

```bash
export RESTRICTED_CONNECTION="REPLACE_WITH_RESTRICTED_TEST_CONNECTION"
snow sql --connection "$RESTRICTED_CONNECTION" --role SAAS_SWEEPER_RESTRICTED --secondary-roles NONE --warehouse "$PARTICIPANT_WAREHOUSE" -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(); SELECT department, total_monthly_spend FROM SAAS_SEAT_SWEEPER.APP.V_SPEND_BY_DEPARTMENT_RLS;"
```

Only after checking that identity output, execute the approved no-row probe:

```bash
snow sql --connection "$RESTRICTED_CONNECTION" --role SAAS_SWEEPER_RESTRICTED --secondary-roles NONE --warehouse "$PARTICIPANT_WAREHOUSE" -q "UPDATE SAAS_SEAT_SWEEPER.RAW.EMPLOYEE_ASSETS SET status = 'Flagged' WHERE 1 = 0;"
```

## Checklist

- [ ] Distinct restricted identity used, or proof explicitly unverified.
- [ ] Exact service grant revoked after the experiment.
- [ ] View rows and intended privilege denial checked independently.
- [ ] Successful zero-row DML was not mistaken for denial.
- [ ] No per-visitor UI or production tenant-isolation claim.

Next: [Break](05-break.md).
