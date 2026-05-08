# Content Guidelines

These guidelines keep the Knowledge Hub consistent as it expands.

## Page Types

Use one of these page types for new wiki pages:

- `Main page`: the landing page and general orientation.
- `How-to page`: practical method, posture, or workflow pages.
- `Issue page`: overview of a social issue.
- `Issue subpage`: focused page under an issue category.
- `Directory`: organization, service, or resource lists.
- `Policy timeline`: selected policy changes and public strategy context.
- `Development page`: version log, next steps, and maintainer notes.
- `Legal page`: imprint, privacy, license, and legal notices.

## Required Page Elements

Every published article page in `web/` should include:

- A visible title.
- A short subtitle.
- A visible revision timestamp in the page header.
- An infobox.
- English and German versions with matching content intent.
- A search-index entry.
- A sidebar entry when the page is a navigable article.
- Embedded references when factual claims, policies, services, organizations, rights, phone numbers, or eligibility details are included.

## Revision Timestamps

Update the visible timestamp whenever content changes.

Use Berlin local time:

```html
<time datetime="2026-05-08T14:30:00+02:00">8 May 2026, 14:30 CEST</time>
```

For German pages:

```html
<time datetime="2026-05-08T14:30:00+02:00">8. Mai 2026, 14:30 CEST</time>
```

Structural-only changes, such as sidebar order or CSS, do not require changing every article timestamp. They should be recorded by the automated version log.

## Source Practice

Keep references embedded in the article they support.

Prefer source types in this order:

- Official public authority pages for law, eligibility, public services, and emergency information.
- Organization pages for services, opening times, volunteering, donations, and contact details.
- Academic or institutional research for concepts, methods, and evidence.
- Journalism only when it reports something not available from primary sources.

For time-sensitive information, check the current source page before updating the timestamp. This includes opening hours, addresses, phone numbers, eligibility, urgent support, legal rights, and active policies.

## Translation Practice

German pages should not be shorter or weaker copies of English pages. When one language changes, update the other language in the same revision unless the change is intentionally language-specific.

Use natural German wording rather than literal translation when needed, but preserve:

- Scope.
- Claims.
- Source links.
- Practical cautions.
- Revision time.

## Tone

Keep the wiki clear, practical, and careful.

- Avoid overclaiming.
- Separate facts from interpretation.
- Mark open questions when information is incomplete.
- Do not turn support pages into personal opinion pages.
- Do not present the hub as legal, medical, emergency, or professional social-work advice.
