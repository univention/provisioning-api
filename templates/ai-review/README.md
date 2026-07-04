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

The review summary takes the **merge request's intent** into account:
the job feeds the MR title and description,
and the descriptions of all issues linked to the MR,
into the summary review prompt,
so the review can state whether the changes do what they claim —
and not more.
See [Merge Request and Issue Context](#merge-request-and-issue-context).

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

Every ai-review configuration variable of the job's `variables` section
can be overwritten through an input.
The `AI_REVIEW_*` variables holding the generated prompt texts are the exception;
override them by redefining the job's `variables` in your own pipeline,
or point `summary_prompt_files` / `context_prompt_files` / `system_summary_prompt_files`
to your own files.

## Configuration

| Input                   | Default                                                                    | Sets variable                                                       |
|-------------------------|----------------------------------------------------------------------------|---------------------------------------------------------------------|
| `job_name`              | `ai-review`                                                                | – (job name)                                                        |
| `stage`                 | `test`                                                                     | – (pipeline stage)                                                  |
| `image`                 | `${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}/nikitafilonov/ai-review:v0.68.0` | – (job image)                                                       |
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
| `summary_prompt_files`  | `["/tmp/ai-review/summary-prompt.md"]`                                     | `PROMPT__SUMMARY_PROMPT_FILES`                                      |
| `context_prompt_files`  | `["/tmp/ai-review/context-prompt.md"]`                                     | `PROMPT__CONTEXT_PROMPT_FILES`                                      |
| `system_summary_prompt_files` | `["/tmp/ai-review/system-summary-prompt.md"]`                        | `PROMPT__SYSTEM_SUMMARY_PROMPT_FILES`                               |
| `include_summary_system_prompts` | `false`                                                           | `PROMPT__INCLUDE_SUMMARY_SYSTEM_PROMPTS`                            |
| `system_agent_prompt_files` | `["/tmp/ai-review/system-agent-prompt.md"]`                            | `PROMPT__SYSTEM_AGENT_PROMPT_FILES`                                 |
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

## Merge Request and Issue Context

ai-review's default prompts only contain the code diff,
so the review cannot judge whether a change does what it is supposed to do.
This component therefore generates its own summary and context prompt files
(in `before_script`, under `/tmp/ai-review/`),
which extend ai-review's default instructions with a "Merge request intent" section:

- the **MR title and description**,
  provided through ai-review's built-in `<<review_title>>` and `<<review_description>>`
  [prompt placeholders](https://github.com/Nikita-Filonov/ai-review/blob/main/docs/prompts/README.md)
  (ai-review fetches them from the GitLab API itself),
- the **descriptions of all issues linked to the MR**
  (GitLab [related_issues](https://docs.gitlab.com/api/merge_requests/#list-issues-related-to-the-merge-request) API,
  the links shown under "Related items" in the MR UI),
  fetched by the job and injected as the custom `<<issue_context>>` placeholder.

Notes:

- The intent section is only added to the **summary** and **context** review prompts,
  not to the per-file **inline** review prompts:
  the inline review sends one LLM request per changed file
  (multiplied by the agent loop's iterations),
  so embedding the descriptions there would multiply their token cost,
  while "does the change match its intent" is a whole-MR question anyway.
- The issue text is truncated to **127 KiB**,
  because Linux limits a single environment variable to 128 KiB.
- The prompts mark the descriptions as
  **data written by their authors, not instructions to the AI**,
  to blunt prompt-injection attempts via MR or issue descriptions.
- A failing issue lookup never fails the job;
  the review then simply runs without issue context.
- The description of a **confidential** linked issue is sent to the LLM
  like any other issue description,
  if the `GITLAB_TOKEN` can read it.

## Summary Comment Format

ai-review posts the LLM's summary output verbatim as the comment body,
and its default summary *system* prompt demands a plain-text paragraph
("no JSON, no markdown, 1-4 sentences").
This component replaces that system prompt with a generated one
(`system_summary_prompt_files`, with `include_summary_system_prompts: false`,
because *including* it would prepend the contradicting plain-text rule),
so the summary comment is structured into Markdown sections:

- **Summary** — what the changes do and what was done well,
- **Findings** — a bullet list of the most important issues, most severe first,
- **Intent** — a bullet list of unmet promises from the MR/issue intent
  and of changes unrelated to it.

Empty sections are omitted;
"No issues found." is posted when there is nothing to report.

In agent mode (`agent_enabled: true`, the default),
the model must answer every turn with a single JSON action object,
and ai-review posts an unparseable answer **verbatim** as the review comment —
models occasionally narrate before the JSON action.
The generated prompts defend against that in three ways:

- **Either-or contract**: each response is either ONLY a JSON action object
  or ONLY the final Markdown summary text, never a mix.
  A pure-Markdown final answer is safe by construction:
  ai-review posts an unparseable final response verbatim,
  which in that case is exactly the summary text.
- **Fenced actions**: the JSON action object must be wrapped
  in a ` ```json ` fenced code block.
  ai-review extracts a fenced block from the response before parsing,
  so narration around a fenced action is stripped instead of breaking the parse.
- **Note field**: commentary the model cannot suppress
  belongs in a `"note"` field inside the JSON object,
  which ai-review's parser ignores.

The amendments live in a generated addition to the agent system prompt
(`system_agent_prompt_files`, appended to ai-review's default, not a fork).

### Maintenance: forked upstream prompts

The generated summary, context, and summary-system prompts are forks of
ai-review's defaults in
[`ai_review/prompts/`](https://github.com/Nikita-Filonov/ai-review/tree/main/ai_review/prompts)
(see the "forked from" comments in `template.yml` for the exact version).
The `image` input is therefore pinned to an ai-review release
instead of `latest`,
so upstream prompt and behavior changes only arrive with a deliberate upgrade.
When bumping the pinned version,
diff `ai_review/prompts/` between the two releases
and fold relevant upstream changes into the `AI_REVIEW_*` prompt variables.

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
