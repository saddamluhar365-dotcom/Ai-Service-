# Worker layer

The worker manager routes GPU-required work to Kaggle when the official CLI is authenticated and available. CPU-safe work can run locally.

Kaggle integration uses the official `kaggle` CLI and creates a private, short-lived kernel definition per work order. Customer data must be staged through an approved durable artifact mechanism before production execution; local filesystem paths are never assumed to exist inside Kaggle.
