# AI Review CI Component

## Problem

Getting an AI-assisted code review on a merge request
requires configuring the [ai-review](https://github.com/Nikita-Filonov/ai-review) tool
with more than a dozen environment variables
(LLM provider, model, API endpoints, tokens, review behavior),
and duplicating that configuration across repositories.

## Solution

This GitLab CI/CD component adds a **manual** `ai-review` job to merge request pipelines.
When triggered, it reviews the merge request diff with an LLM
(by default Claude Opus via the Univention LiteLLM proxy at `litellm.knut.univention.de`)
and posts the review as comments on the merge request.

The job is manual and `allow_failure: true`,
so it never blocks a pipeline.

## Jobs Produced

| Job                                       | Trigger                              | Purpose                                                      |
|-------------------------------------------|--------------------------------------|--------------------------------------------------------------|
| `ai-review` (configurable via `job_name`) | manual, merge request pipelines only | Reviews the MR diff with an LLM and posts comments on the MR |

## Usage

```yaml
include:
  - component: $CI_SERVER_FQDN/univention/dev/tooling/ci-components/ai-review@2.8.0
```

With a different model and stage:

```yaml
include:
  - component: $CI_SERVER_FQDN/univention/dev/tooling/ci-components/ai-review@2.8.0
    inputs:
      stage: "lint"
      llm_model: "gemini/gemini-2.5-pro"
```

Every variable of the job's `variables` section can be overwritten through an input.

## Configuration

| Input                   | Default                                                                    | Sets variable                                                       |
|-------------------------|----------------------------------------------------------------------------|---------------------------------------------------------------------|
| `job_name`              | `ai-review`                                                                | – (job name)                                                        |
| `stage`                 | `test`                                                                     | – (pipeline stage)                                                  |
| `image`                 | `${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}/nikitafilonov/ai-review:latest` | – (job image)                                                       |
| `llm_provider`          | `OPENAI`                                                                   | `LLM__PROVIDER`                                                     |
| `llm_model`             | `anthropic/claude-opus-4-8`                                                | `LLM__META__MODEL`                                                  |
| `llm_max_tokens`        | `50000`                                                                    | `LLM__META__MAX_TOKENS`                                             |
| `llm_temperature`       | (empty)                                                                    | `LLM__META__TEMPERATURE`                                            |
| `llm_api_url`           | `https://litellm.knut.univention.de`                                       | `LLM__HTTP_CLIENT__API_URL`                                         |
| `llm_api_token`         | `$OPENAI_API_KEY`                                                          | `LLM__HTTP_CLIENT__API_TOKEN`                                       |
| `vcs_provider`          | `GITLAB`                                                                   | `VCS__PROVIDER`                                                     |
| `vcs_project_id`        | `$CI_PROJECT_ID`                                                           | `VCS__PIPELINE__PROJECT_ID`                                         |
| `vcs_merge_request_id`  | `$CI_MERGE_REQUEST_IID`                                                    | `VCS__PIPELINE__MERGE_REQUEST_ID`                                   |
| `vcs_api_url`           | `$CI_SERVER_URL`                                                           | `VCS__HTTP_CLIENT__API_URL`                                         |
| `vcs_api_token`         | `$GITLAB_TOKEN`                                                            | `VCS__HTTP_CLIENT__API_TOKEN`                                       |
| `agent_enabled`         | `true`                                                                     | `AGENT__ENABLED`                                                    |
| `agent_command_timeout` | `60`                                                                       | `AGENT__COMMAND_TIMEOUT`                                            |
| `company_name`          | `Univention`                                                               | `PROMPT__CONTEXT__COMPANY_NAME`                                     |
| `review_mode`           | `ADDED_AND_REMOVED_WITH_CONTEXT`                                           | `REVIEW__MODE`                                                      |
| `review_context_lines`  | `20`                                                                       | `REVIEW__CONTEXT_LINES`                                             |
| `review_added_marker`   | (empty)                                                                    | `REVIEW__REVIEW_ADDED_MARKER`                                       |
| `review_removed_marker` | (empty)                                                                    | `REVIEW__REVIEW_REMOVED_MARKER`                                     |
| `debug`                 | `false`                                                                    | `LOGGER__LEVEL`, `ARTIFACTS__LLM_ENABLED`, `ARTIFACTS__VCS_ENABLED` |

See the [ai-review GitLab CI documentation](https://github.com/Nikita-Filonov/ai-review/blob/main/docs/ci/gitlab.yaml)
for the meaning of the variables.

Notes on selected inputs:

- `llm_provider`: LiteLLM's OpenAI-compatible interface also allows using non-OpenAI models,
  so the default `OPENAI` works for Anthropic and Google models, too.
- `llm_model`: available models are listed at <https://litellm.knut.univention.de/ui/?page=models>.
  LiteLLM encodes the names differently to what some AIs expect — ignore their warning.
- `llm_temperature`: keep it empty to use the model's default temperature.
  Some models reject requests that set a temperature (e.g., Opus 4.7+).
  When empty, the job unsets the variable before running ai-review,
  because ai-review cannot parse an empty value.
- `review_added_marker` / `review_removed_marker`:
  ai-review adds markers to diffs, which some models may need.
  Keep them empty when the agent complains about "added" or "removed" comments
  (the Anthropic models complain about them).

## Required Secrets

| CI/CD variable   | Used for                                 | Notes                                                                                                         |
|------------------|------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| `OPENAI_API_KEY` | Authentication against the LiteLLM proxy | Defined as a CI/CD group variable at `/univention/dev`                                                        |
| `GITLAB_TOKEN`   | Posting comments on the merge request    | Defined as a CI/CD group variable at `/univention/dev`; `$CI_JOB_TOKEN` lacks the permission to post comments |

Projects outside the `/univention/dev` group must define these variables themselves,
or pass different variable names via the `llm_api_token` and `vcs_api_token` inputs.
Use tokens with the minimum required scope
(the GitLab token only needs `api` scope to post MR comments).

## Debugging

Set the `debug` input to `true`
to enable debug logging
and to store the communication with GitLab and the AI model
as job artifacts in the `artifacts/` directory:

```yaml
include:
  - component: $CI_SERVER_FQDN/univention/dev/tooling/ci-components/ai-review@2.8.0
    inputs:
      debug: true
```
