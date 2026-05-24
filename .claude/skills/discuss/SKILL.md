---
name: discuss
description: Structured discussion and decision support for user inquiries. Use when the user explicitly asks for discussion mode with wording like "use discuss skill", "discussion only", "lets discuss", or similar phrasing that requests analysis and recommendation. Break requests into atomic non-overlapping parts, synthesize options, recommend the best option with assumptions when information is missing, and end with numbered clarifying questions (or a permission-to-proceed prompt when context is sufficient).
---

# Discuss Workflow

Follow this workflow in order for each response.

## 1) Parse and Break Down

Extract atomic, non-overlapping parts from the user input.

Use this checklist and only include items that are actually present or can be safely inferred:
- Goals
- Constraints
- Success criteria
- Needs and preferences
- Key facts and context
- Unknowns and ambiguities

Keep each part short and distinct. Do not duplicate information across parts.

## 2) Think and Synthesize

Synthesize the parts into a clear problem framing:
- What must be optimized
- What tradeoffs matter most
- What assumptions are required due to missing information

State assumptions explicitly and keep them minimal.

## 3) Provide and Weigh Options

Generate 2-4 concrete options.

For each option, evaluate against the extracted parts:
- Goal fit
- Constraint fit
- Expected outcome against success criteria
- Risks and downsides

Keep comparison concise and decision-oriented.

## 4) Recommend the Best Option

Always choose one best option.

If information is incomplete, recommend based on explicit assumptions and note what could change the recommendation in follow-up.

## 5) Ask Clarifying Questions or Request Permission to Proceed

Use this decision rule:
- If key information is still missing, end with at least 3 focused clarifying questions aligned to the user's goals.
- If information is sufficient to proceed, ask for permission to proceed with the recommended direction.

Formatting requirements:
- Number all questions using `1.`, `2.`, `3.` so the user can answer by number.
- Keep each question short, concrete, and decision-relevant.

# Output Structure

Use this fixed structure and keep it concise:

1. Atomic Breakdown
2. Synthesis
3. Options and Tradeoffs
4. Recommendation
5. Clarifying Questions or Permission to Proceed

Keep the full response at most 200 words.

# Style Rules

- Be concise and on-point.
- Prefer direct language over long explanation.
- Keep analysis grounded in user-provided context.
- Avoid filler and repetition.

# Tool and Data Boundaries

Default to discussion-only mode.

- Do not perform web search or any external lookup unless the user explicitly asks for it.
- Do not read from or write to files unless the user explicitly asks for it or provides file content for analysis.
- Do not use tools unless the user explicitly asks for tool usage.
- Rely only on information already present in the current conversation unless the user requests expansion.
