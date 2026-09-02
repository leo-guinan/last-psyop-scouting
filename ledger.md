# Last Psyop scouting ledger

Last read: 2026-09-02

Scope: public-source research only. This ledger maps the event, organizers, publicly named attendance signals, conceptual territories, and adjacent actors mentioned in event materials. It does not create private dossiers or infer identities, affiliations, beliefs, or attendance from weak signals.

## Evidence rules

- `observed`: directly visible in a cited public source.
- `attributed`: a source claims it; the claim is preserved as attribution.
- `hypothesis`: an interpretation to test.
- `unresolved`: conflicting or insufficient evidence.
- `excluded`: omitted because evidence would require private or unsafe inference.

Confidence is about the evidence for the row, not the person’s character.

## Current map

### Event

| ID | Entity | Observation | State | Source |
|---|---|---|---|---|
| E001 | Netwar Con: A Psyops Hackathon | Luma event for September 4–6, 2026 in Austin; approval required | observed / high | https://luma.com/psyop-hackathon |
| E002 | The Last Psyop / The September Event | Public site describes a mind-virus preparedness and prevention wargaming conference | observed / high | https://lastpsyop.com/ |
| E003 | Distribution Hall | Venue listed at 1500 E 4th St, Austin, TX 78702 | observed / high | https://www.distributionhall.com/ |
| E004 | Luma attendance display | 46 going; three visible names: Dillon Cortez, Harsh O, and 44 others | observed / high | https://luma.com/psyop-hackathon |

The visible names are not an exhaustive roster. The count is a time-sensitive platform display, not proof of physical attendance.

### Organizers and sponsor

| ID | Entity | Public signal | State | Source |
|---|---|---|---|---|
| E005 | Omar Shehata | Luma host; Prosocial Engineering owner/operator | observed / high | https://luma.com/psyop-hackathon; https://prosocialengineering.org/ |
| E006 | Katt / Kat the Vat | Supplied copy says Katt; Luma says Kat the Vat; newsletter says Katt | unresolved / medium | https://luma.com/psyop-hackathon |
| E007 | Ari / Meta Wizard | Supplied copy names Ari and Enigma Infrastructure; current Luma host line does not | unresolved / medium | https://luma.com/psyop-hackathon |
| E008 | Matthew Fisher | Luma-listed host | observed / high | https://luma.com/psyop-hackathon |
| E009 | Commenta Projects | Luma thanks it for financial sponsorship | observed / high | https://luma.com/psyop-hackathon |

The organizer discrepancies are the first thing to resolve. Do not silently merge names or assume that a current omission means removal.

### Public attendance signals

| ID | Entity | What is actually supported | State | Source |
|---|---|---|---|---|
| E026 | Dillon Cortez | Named in Luma’s 46-going display | observed / high | https://luma.com/psyop-hackathon |
| E027 | Harsh O | Named in Luma’s 46-going display | observed / high | https://luma.com/psyop-hackathon |
| E028 | 44 unnamed registrants | Aggregate count only | observed / high | https://luma.com/psyop-hackathon |
| E029 | Public attendance posts | Bounded web-search pass found event pages and discussion, but no independently verified self-authored attendance claim in this pass | observed / medium | — |

Stronger wording such as “plans to attend” requires a self-authored public statement or an official event artifact. “Luma-visible attendee” is the current ceiling for E026 and E027.

### Public discussion and planning-repository signals

| ID | Entity | What is actually supported | State | Source |
|---|---|---|---|---|
| E030 | `Prosocial-Engineering/netwar-con` | Public planning repository for the September Event; README links the event and lists alternative names | observed / high | https://github.com/Prosocial-Engineering/netwar-con |
| E031 | DefenderOfBasic | Pinned public post discusses explaining the hackathon to people being pitched or invited to join | observed / high | https://vanlett.com/DefenderOfBasic |
| E032 | DefenderOfBasic | 34 public GitHub contributions to the planning repository | observed / high | https://github.com/Prosocial-Engineering/netwar-con |
| E033 | suntzugi | 32 public GitHub contributions to the planning repository | observed / high | https://github.com/Prosocial-Engineering/netwar-con |
| E034 | Kat-Stack | 18 public GitHub contributions to the planning repository | observed / high | https://github.com/Prosocial-Engineering/netwar-con |
| E035 | OmarShehata | 2 public GitHub contributions to the planning repository | observed / high | https://github.com/Prosocial-Engineering/netwar-con |
| E036 | `Prosocial-Engineering/September-Game` | Linked by the planning README, but currently returns 404 | unresolved / medium | https://github.com/Prosocial-Engineering/netwar-con |

None of these rows independently establishes physical attendance. Repository contribution is evidence of public project involvement only. The DefenderOfBasic post is recruitment/discussion evidence, not an attendance claim.

### Conceptual territories

These are territories discussed or used as examples in the organizers’ public writing. They are not event participants unless a separate source establishes that.

| ID | Territory | Public framing | State | Source |
|---|---|---|---|---|
| E010 | American liberal territory | Hank Green is used as an example of a live player in this territory | attributed / medium | https://www.psyop.report/p/1-can-you-name-your-lighthouse |
| E011 | Ithaca social fabric | Local information territory used to explain the lighthouse model | attributed / medium | same |
| E012 | r/ithaca | Described as the biggest local lighthouse in the Ithaca example | attributed / medium | same |
| E013 | Cornell University | Described as a vast sub-territory with global reach | attributed / medium | same |
| E014 | Ithaca College | Named as another local social bubble | attributed / medium | same |
| E015 | Flat Earth Society | Hypothetical territory used to explain belief-change monitoring | attributed / medium | same |
| E016 | tpot | Prior example involving linguistic-change tooling and the word “psyop” | attributed / medium | https://www.psyop.report/p/2-putting-fluoride-in-the-mental |

The safe scouting surface here is public artifacts and explicit opt-in monitoring—not scraping private groups or trying to identify ordinary members.

### Adjacent actors and frameworks

| ID | Entity | Why it appears | State | Source |
|---|---|---|---|---|
| E017 | Prosocial Engineering | Publicly describes itself as an open-source intelligence agency and open sociology/marketing lab | observed / high | https://prosocialengineering.org/ |
| E018 | Lighthouse model | Monitoring, defense, internal operations, and cross-territory requests | attributed / high | https://www.psyop.report/p/1-can-you-name-your-lighthouse |
| E019 | Infohazard / infoblessing | Vocabulary for harmful versus beneficial information effects | attributed / high | https://www.psyop.report/p/2-putting-fluoride-in-the-mental |
| E020 | SP!CE 2.2 / MITRE | Luma says the operator manual is based on this framework | attributed / medium | https://luma.com/psyop-hackathon |
| E021 | Social Engineer LLC | Named as a possible referee or monitoring reference | attributed / medium | https://www.psyop.report/p/2-putting-fluoride-in-the-mental |
| E022 | Leverage Research | Named as a possible referee or research reference | attributed / medium | same |
| E023 | Graphika | Named among monitoring/intelligence actors | attributed / medium | same |
| E024 | Palantir | Named among monitoring/intelligence actors | attributed / medium | same |
| E025 | Black Cube | Named among monitoring/intelligence actors | attributed / medium | same |

A mention is not evidence of attendance, endorsement, sponsorship, or contact.

## Research queue

1. Search public posts for the exact event names: `"Netwar Con"`, `"Last Psyop"`, `"September Event"`, and `psyop hackathon`.
2. Add location/context terms: `Austin`, `Distribution Hall`, and `September 4`.
3. Exclude obvious repost and noise classes where the platform allows it.
4. Classify every result as:
   - explicit attendance claim;
   - public question about attendance;
   - host/player or event discussion;
   - repost/reference;
   - unrelated topical noise.
5. Resolve a named account to a handle only when the public source itself makes the match clear. Do not use name similarity.
6. Search each organizer’s public website and public social surfaces for event-related artifacts.
7. Search the named territories for public event references, without treating ordinary community members as targets.
8. Locate the public MITRE/SP!CE source and compare the event’s description against the original framework.
9. Capture a new readback of Luma before the event and after the event. Record count changes separately from identity claims.
10. Recheck the linked `September-Game` repository and record whether the 404 resolves, redirects, or remains unavailable.
11. After the event, create a second ledger layer for submitted psyops: declared target, payload, channel, disclosure, success metric, harm metric, stop condition, and observed outcome.

## Falsifiers

- An official source corrects the organizer roster.
- A self-authored post contradicts the Luma-visible attendance signal.
- The operator manual differs materially from the event-page description.
- A claimed territory has no public event connection and remains only a conceptual example.
- A campaign outcome cannot be distinguished from ordinary drift, selection effects, or participant self-report.

Machine-readable rows are in `ledger.csv`.
