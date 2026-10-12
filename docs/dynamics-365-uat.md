# Dynamics 365 UAT deployment and regression checks

The `uat` GitHub Actions environment targets
`https://org9bc0cd2d.crm.dynamics.com`. Pull requests do not deploy. A push to
`main` or a manually started workflow builds the Dataverse solution, imports it
with Power Platform CLI, and runs the Web Resource Jest tests plus authenticated
Dataverse smoke checks.

## GitHub setup

1. In **Settings → Environments**, create an environment named `uat` and add
   required reviewers if deployments should wait for approval.
2. Add these secrets to the `uat` environment (or repository secrets):
   - `AZURE_TENANT_ID`: Microsoft Entra tenant ID.
   - `AZURE_CLIENT_ID`: application (client) ID for the deployment app
     registration.
   - `AZURE_CLIENT_SECRET`: active client secret for that app registration.
3. In the target Dataverse environment, create an application user for that
   app registration and assign a security role that permits solution import,
   publishing, environment-variable updates when configured, and reading the
   `WhoAmI` and `solution` APIs. Start with the least-privileged role that
   meets those operations; confirm the role with a dry run in a non-production
   environment.
4. Confirm the app registration is allowed to access Dataverse in the tenant
   and that its application user belongs to this environment. No Azure
   subscription, Azure login, or client secret should be added to source.

Do not create `ENABLE_PLACEHOLDER_RELEASE_STAGES`. The preproduction and
production workflow jobs are still scaffold simulations; UAT regression
success must not promote to them.

## Local commands

Install Power Platform CLI and set the three environment variables above in
your local shell, then build and deploy:

```powershell
./scripts/build.ps1 -Configuration Release
./scripts/package.ps1 -SolutionName CustomerServiceDemo -OutputDir ./dist
./scripts/deploy.ps1 -Environment uat -PackagePath ./dist
```

Run the authenticated smoke tests after import from PowerShell with Git Bash
on `PATH`, and Python, `pytest`, and `requests` installed:

```powershell
$env:UAT_URL = "https://org9bc0cd2d.crm.dynamics.com"
$env:SOLUTION_UNIQUE_NAME = "CustomerServiceDemo"
python -m pip install pytest requests
bash scripts/run-regression-tests.sh --uat-url $env:UAT_URL
```

The smoke checks validate token acquisition, Dataverse `WhoAmI`, and presence
of the `CustomerServiceDemo` solution. They do not exercise model-driven app
screens or business workflows. The checked-in solution currently has no root
components (`RootComponents` is empty), so meaningful UI/functional regression
coverage requires adding the actual solution components and test cases.

## First-run troubleshooting

- A token failure usually means the tenant/app IDs or secret are wrong, expired,
  or lack tenant consent.
- HTTP 401/403 from Dataverse usually means the app registration's application
  user is missing from this environment, or its security role lacks access.
- A failed solution import should be checked for missing solution dependencies
  and publisher/environment configuration before retrying.
- The regression job intentionally fails if credentials are absent or the
  solution is not installed; it never converts missing tests or API failures
  into a successful placeholder report.
