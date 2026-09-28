# Fabric-CICD in Practice, sample repo

The solution deployed through the [Fabric-CICD in Practice](https://evaluationcontext.com/posts/fabric-cicd-first-deploy/) series. One workspace, four items, fabric-cicd 1.3.0 via `fab deploy`, Azure Pipelines. It grows with the posts; each post names the tag it ends on.

## What's in it

```text
.
├── .azure-pipelines/
│   ├── variables.yml               # service connection names, the one place to edit
│   ├── deploy-main.yml             # main → dev, on every merge
│   ├── deploy-release.yml          # release/* → test → plan → approval → prod
│   └── templates/
│       ├── fab-setup-steps.yml     # install fab, log in as the SPN with WIF
│       └── fab-deploy-steps.yml    # fab deploy one environment, publish the log
└── fabric/
    └── foo/                        ## workspace folder for foo-dev, foo-test, foo-prod
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

## Prerequisites

Made once, outside the pipelines. Post 1 walks through each.

1. Three workspaces named exactly as `core.workspace` in `fabric/foo/config.yml`, on a capacity, with the pipeline SPN as Contributor.
2. An app registration with a federated credential for the Azure DevOps service connection, and the two Fabric tenant settings that allow service principals to use the APIs and create items.
3. A workload-identity service connection in Azure DevOps, named in `.azure-pipelines/variables.yml`.
4. Azure DevOps environments `fabric-dev`, `fabric-test` and `fabric-prod`, with a manual approval check on `fabric-prod`.
5. Two pipelines pointing at `deploy-main.yml` and `deploy-release.yml`.

## Running it

```bash
pip install ms-fabric-cli && fab auth login
fab deploy --config fabric/foo/config.yml --target_env dev
```

Or merge to `main` and let `deploy-main.yml` do it.

## Tags

| Tag | Post | State |
| --- | ---- | ----- |
| `post-1` | Groundwork | One workspace, three environments, pipelines, no parameter rules yet |
