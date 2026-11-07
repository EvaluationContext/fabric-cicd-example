# Fabric-CICD in Practice, sample repo

The solution deployed through the [Fabric-CICD in Practice](https://evaluationcontext.com/posts/fabric-cicd-first-deploy/) series. One workspace, five items, fabric-cicd 1.3.0 via `fab deploy`, Azure Pipelines. It grows with the posts; each post names the tag it ends on.

## What's in it

```text
.
├── .azure-pipelines/
│   ├── variables.yml               # service connection, capacity and git connection names, the one place to edit
│   ├── provision-feature.yml       # feature/* → a feature workspace, queued by hand once per branch
│   ├── feature-workspace-roles.json # who gets what on a feature workspace
│   ├── deploy-main.yml             # main → dev, on every merge, then tear down merged feature workspaces
│   ├── deploy-release.yml          # release/* → test → approval → prod
│   └── templates/
│       ├── fab-setup-steps.yml     # install fab, log in as the SPN with WIF
│       └── fab-deploy-steps.yml    # fab deploy one environment, publish the log
└── fabric/
    └── foo/                        ## workspace folder for foo-dev, foo-test, foo-prod and foo-feature-*
        ├── config.yml              # fabric-cicd: env → workspace name, item scope, publish rules
        ├── parameter.yml           # fabric-cicd: rewrites on the way in
        ├── Sales.Lakehouse/
        ├── Load Sales.DataPipeline/ # runs the notebook
        ├── Load Sales.Notebook/    # default lakehouse: Sales
        ├── Sales.SemanticModel/    # Direct Lake on the Sales SQL analytics endpoint
        └── Sales.Report/           # bound to Sales.SemanticModel by path
```

Five items, one of each kind of reference (none needs a connection):

| Reference | Carried by | Deploy needs |
| --------- | ---------- | ------------ |
| Report → semantic model | `definition.pbir` `byPath` | Nothing. Resolved by folder name in the target workspace |
| Notebook → lakehouse | `notebook-content.py` metadata, the lakehouse logicalId and a zero workspace id | Nothing. fabric-cicd swaps logicalIds and zero workspace ids for the target workspace|
| Pipeline → notebook | `pipeline-content.json`, the notebook logicalId and a zero workspace id | Nothing. Same logicalId rewrite as the notebook |
| Semantic model → lakehouse SQL endpoint | `expressions.tmdl`, endpoint host and id | `parameter.yml`: `$items.Lakehouse.Sales.$sqlendpoint` and `$sqlendpointid` |

A deploy publishes definitions and stops. On a fresh workspace the lakehouse is empty and the model has never refreshed, so the report opens with errors until the pipeline has run and the model has been refreshed. That is what pre and post deployment hooks are for; the series names the gap and leaves it there.

No warehouse. A warehouse deploys as an empty shell (its REST API has no definition operations), so the schema has to be published separately with SqlPackage. That is a post of its own, not this series.

## Feature workspaces

A `feature/*` branch gets its own workspace, `foo-feature-<repo slug>-<branch slug>`, made by `provision-feature.yml`:

1. **Create** an empty workspace on the feature capacity, with the roles in `feature-workspace-roles.json`.
2. **Fill** it with `fab deploy --target_env feature`, the workspace name passed as a config override. Only a deploy runs `parameter.yml`, which is what binds the semantic model to the new workspace's lakehouse; a git sync would leave it on dev's.
3. **Connect** it to the branch through the git connection, workspace side winning, and commit. The branch now holds this workspace's ids.
4. **Relate** it to `foo-dev`, so the Fabric UI lists it under dev.

Work in the workspace and commit from its Source control panel, or `fab import` one item at a time from the repo. Never update the workspace from git. When the pull request merges, `deploy-main.yml` publishes dev and the Teardown stage deletes this repo's feature workspaces whose branch is gone.

## Prerequisites

Made once, outside the pipelines. Post 1 walks through the first five, post 2 the rest.

1. Three workspaces named exactly as `core.workspace` in `fabric/foo/config.yml`, on a capacity, with the pipeline SPN as Contributor.
2. An app registration with a federated credential for the Azure DevOps service connection, and the Fabric tenant settings that allow service principals to use the APIs, create workspaces, and sync with git.
3. A workload-identity service connection in Azure DevOps, named in `.azure-pipelines/variables.yml`.
4. Azure DevOps environments `fabric-dev`, `fabric-test` and `fabric-prod`, with a manual approval check on `fabric-prod`.
5. Three pipelines pointing at `provision-feature.yml`, `deploy-main.yml` and `deploy-release.yml`.
6. A Fabric connection of type `AzureDevOpsSourceControl` holding the non-prod SPN's credential, named in `variables.yml` as `gitConnection`, owned by or shared with that SPN. The SPN needs Basic access in the Azure DevOps organisation and Contribute on the repo.
7. The non-prod SPN granted Contributor permissions on the capacity named in `variables.yml` as `featureCapacity`.
8. `foo-dev` connected to `main` at git folder `fabric/foo`, for the UI relation only. Never update it from git or commit from it.
9. The developers' security group object id in `feature-workspace-roles.json`.

## Running it

```bash
pip install ms-fabric-cli && fab auth login
fab deploy --config fabric/foo/config.yml --target_env dev
```

Or merge to `main` and let `deploy-main.yml` do it.

## Tags

| Tag | Post | State |
| --- | ---- | ----- |
| `post-1` | Groundwork | One workspace, three environments, pipelines, two parameter rules |
| `post-2` | Feature Workspaces | A workspace per feature branch, binding deploy, git integration, teardown on merge, one new measure |
