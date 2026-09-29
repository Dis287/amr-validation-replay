# Thesis

A model-validation result is a versioned scientific artifact.

For AMR, the apparent ground truth may depend on:
- organism/drug identity
- AST measurement
- method
- breakpoint authority
- breakpoint version
- categorical semantics
- population/sampling frame
- evaluation procedure

If one of these dependencies changes, a prior validation result may remain valid, change, become
stale, or become impossible to replay.

The opportunity is **claim-level dependency-aware replay**, not breakpoint interpretation itself.
Existing breakpoint interpreters and curated AMR resources are upstream dependencies, not targets
for reinvention.
