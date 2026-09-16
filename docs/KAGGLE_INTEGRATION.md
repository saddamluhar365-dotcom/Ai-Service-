# Kaggle integration contract

The agent treats Kaggle as an on-demand compute provider, not as its control plane.

1. A work order is created in the agent.
2. WorkerManager selects Kaggle only when GPU is required and Kaggle is authenticated/available.
3. A private short-lived kernel is pushed through the official Kaggle CLI.
4. The agent records the kernel handle as a checkpoint.
5. Production artifact transfer must use a durable approved store; a local filesystem path is never assumed to exist inside Kaggle.
6. The control plane remains responsible for retries, checkpoints, validation, and eventual worker shutdown/cleanup.

Kaggle API rate limits are dynamic, so retries must be bounded and backoff-aware rather than a tight loop.
