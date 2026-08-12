# Documentation currency policy

Documentation is an engineering deliverable and must be updated in the same change as the behaviour it describes.

Update documentation whenever control behaviour, APIs, NATS subjects or payloads, configuration, hardware support, safety behaviour, deployment, data formats, tests, workflows, dependencies, or units change. Update `MASTER_CONTEXT.md` whenever architecture, boundaries, conventions, or validation status changes.

Distinguish implemented, automated-test verified, bench-tested, production-validated, and planned or unverified behaviour. Code existence alone is not evidence of hardware or production validation.

Run `python tests/test_documentation.py`. Pull-request paths are classified by `tests/documentation_change_policy.py` using `tests/documentation_change_policy.json`; behaviour-affecting changes require documentation in the same change. Intentional exemptions are recorded with reasons in that JSON file. Both checks run in CI.
