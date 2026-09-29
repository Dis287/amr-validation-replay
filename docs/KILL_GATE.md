# Kill Gate

## Continue only if

1. Semantic changes can be reproduced on public data.
2. At least one real model-validation metric materially changes after a legitimate semantic replay.
3. Existing tools do not already emit the claim-level `STALE / REVALIDATE / CONCLUSION_CHANGED`
   decision for AMR validation claims.
4. Critical missing provenance fails closed as `UNKNOWN` or `NON_REPLAYABLE`.

## Downgrade

If labels change but real validation conclusions barely move, this becomes a data-quality /
reproducibility utility rather than a breakthrough infrastructure layer.

## Kill

If existing AMR tooling plus a trivial script already delivers claim-level dependency tracking,
replay, and stale/revalidate decisions with no meaningful additional logic.
