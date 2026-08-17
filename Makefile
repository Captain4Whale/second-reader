SHELL := /bin/bash

.PHONY: doctor setup setup-phoenix dev-backend dev-frontend dev run-demo start-backend-detached start-frontend-detached start-local-stack stop-local-stack status-local-stack start-phoenix stop-phoenix status-phoenix test build contract-check agent-check agent-context e2e preview-reactions backfill-covers dataset-review-pipeline library-source-intake closed-loop-benchmark-curation

DATASET_REVIEW_PIPELINE_ARGS ?=
LIBRARY_SOURCE_INTAKE_ARGS ?=
CLOSED_LOOP_BENCHMARK_CURATION_ARGS ?=

doctor:
	./scripts/doctor.sh

setup:
	./scripts/setup.sh

setup-phoenix:
	./scripts/setup-phoenix.sh

dev-backend:
	./scripts/dev-backend.sh

dev-frontend:
	./scripts/dev-frontend.sh

dev:
	./scripts/dev.sh

run-demo:
	./scripts/run-demo.sh

start-backend-detached:
	./scripts/start-backend-detached.sh

start-frontend-detached:
	./scripts/start-frontend-detached.sh

start-local-stack:
	./scripts/start-local-stack.sh

stop-local-stack:
	./scripts/stop-local-stack.sh

status-local-stack:
	./scripts/status-local-stack.sh

start-phoenix:
	./scripts/start-phoenix.sh

stop-phoenix:
	./scripts/stop-phoenix.sh

status-phoenix:
	./scripts/status-phoenix.sh

test:
	./scripts/test.sh

build:
	./scripts/build.sh

contract-check:
	./scripts/contract-check.sh

agent-check:
	./scripts/agent-check.sh

agent-context:
	./scripts/agent-context.sh

e2e:
	./scripts/e2e.sh

preview-reactions:
	./scripts/preview-reactions.sh

backfill-covers:
	./scripts/backfill-covers.sh

dataset-review-pipeline:
	./scripts/dataset-review-pipeline.sh $(DATASET_REVIEW_PIPELINE_ARGS)

library-source-intake:
	./scripts/library-source-intake.sh $(LIBRARY_SOURCE_INTAKE_ARGS)

closed-loop-benchmark-curation:
	./scripts/closed-loop-benchmark-curation.sh $(CLOSED_LOOP_BENCHMARK_CURATION_ARGS)
