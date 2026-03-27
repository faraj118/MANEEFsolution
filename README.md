### Maneef

a tailored maneef solution for engineering companies

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app maneef
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/maneef
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

## 🏗️ Infrastructure Tier Matrix
This matrix defines the hardware requirements and deployment strategy per customer profile for **Maneef ERP**.

| Tier | Profile | Model | CPU | RAM | Storage | Deployment Method |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Small** | 1-20 Users | Normal | 2 vCPU | 4GB | 50GB SSD | Bare Metal (Bench) |
| **Small** | 1-20 Users | High Avail. | 2 x 2 vCPU | 4GB | S3 / Shared | Docker Swarm |
| **Medium** | 20-100 Users | Normal | 4 vCPU | 16GB | 100GB NVMe | Docker Compose |
| **Medium** | 20-100 Users | High Avail. | 3 x 4 vCPU | 16GB | Distributed | Docker + MariaDB Galera |
| **Large** | 100+ Users | Normal | 8 vCPU | 32GB | 500GB NVMe | Docker (Dedicated DB) |
| **Large** | 100+ Users | High Avail. | Multi-Node | 64GB+ | Shared Storage | Kubernetes (K8s) |

### License

mit
