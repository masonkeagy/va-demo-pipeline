# Dynamics 365 UAT deployment and regression checks

The `uat` GitHub Actions environment targets
`https://org9bc0cd2d.crm.dynamics.com`. Pull requests now run through the full
stage chain. After build, integration, and DAST checks, the workflow pauses at
the `uat` environment for reviewer approval before importing the solution.
After approval, the deployment job imports the solution and runs authenticated
Dataverse smoke checks under the same protected environment. The next stage
runs the Web Resource Jest tests without a second UAT approval. Pushes to `main`
and manually started workflows use the same approval gate.

## GitHub setup

1. In **Settings → Environments**, create an environment named `uat` and
   configure required reviewers. The workflow cannot send an approval request
   unless this protection rule is enabled. This repository already has a UAT
   reviewer configured. Review the pending `uat` deployment from the GitHub
   Actions run page when GitHub sends the approval notification.
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

The preproduction and production jobs still generate simulated deployment
records; they are not real environment deployments. They run after successful
UAT regression to preserve the end-to-end demo stage flow. Do not treat their
success as a release to actual preproduction or production systems.

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
- The authenticated UAT smoke-test step intentionally fails if credentials
  are absent or the solution is not installed; it never converts missing
  tests or API failures into a successful placeholder report.
