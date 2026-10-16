# 04 - Prove access boundaries

Try two separate checks: who can open the app, and what a restricted user can query directly.

**Time limit:** 15 minutes, 01:05-01:20. Use 3 minutes for the claim/plan, 6 for app entry, 4 for SQL proof, and 2 for recording/restoration.

## Action

This app uses **owner's rights**, not per-visitor row filtering. An admitted visitor sees service-identity rows; denied direct SQL does not prove that visitor cannot invoke an owner's-rights write endpoint later.

[Prompt CoCo: Explain the two access checks](../coco-prompts/challenge-access.md)

## Your decision

Use the separate restricted test user supplied by the administrator. Review and approve the grant/revoke for your app only, plus the read and no-row write test below. An administrator account cannot prove access is denied, and changing a worksheet role doesn't change who is signed into the browser.

[Prompt CoCo: Walk me through the approved access checks](../coco-prompts/prove-access.md)

Use an isolated browser profile and clean restricted-user session for each entry check: denied before grant, allowed after grant, denied after revoke. Existing sessions may not invalidate instantly; record actual behavior. If entry persists, stop for administrator review of direct/inherited grants, not broad revocation.

Direct SQL should show Engineering-only governed-view rows. The no-row UPDATE must fail for the intended access-control reason, not missing warehouse/setup. A successful zero-row update is a **failed negative test**. Keep the exact service grant revoked before write-back development.

The supplied setup gives the restricted role access to selected views, not RAW tables. The department policy denies other primary roles by default. Shared contract and inventory views are not department-filtered, so this is not complete tenant isolation.

## Expected evidence

Record whether browser entry was denied, allowed, then denied again. Save the restricted SQL role, returned departments and permission error. Confirm the app grant is revoked before continuing. These results don't establish per-visitor filtering inside the app.

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
