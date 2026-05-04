# Memory Quality Probe Manifests

This directory stores the current probe contract for Long Span vNext `Memory Quality`.

## Current Contract

- Active manifest: `memory_quality_semantic_probe_plan_20260504.json`
- Selection method: `semantic_boundary_with_distance_reference`
- Scope: the five active `user-level selective v1` reading windows
- Shape: five semantic probe targets per window

Memory Quality probes are no longer generated from hard `20% / 40% / 60% / 80% / end` ratios. Distance is only a distribution reference. The selected sentence must be a semantic boundary that is useful for reviewing whether the reader's memory state has retained important material.

## Runtime Rule

The reader does not stop or split a unit just to satisfy a probe. During a run, the benchmark captures a probe snapshot after the first completed read step whose covered range reaches or crosses the target sentence from this manifest.

If `memory_quality_probe_export.enabled=true`, the active runner must provide explicit `probe_targets` from a manifest. Missing targets are an error, not a reason to fall back to ratio probes.
