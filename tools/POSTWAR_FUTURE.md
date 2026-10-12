# War clock and postwar government

The Japanese ultimatum focus is removed. Southern bases and the southern campaign
now depend on the resource commission. The hidden 77-day opening phase starts
both 288-day preparation missions together. The obsolete `pacific.4` event is
disabled for queued old-save calls and cannot declare war. Concessions and naval
preparation still change both clocks by the same amount.

After the Borneo settlement, demands for freedom appear. `A01_pacific_settlement`
opens a 240-day dismissal hearing without replacing Ludolf. Decisions influence
the balance, and one extension adds 60 days. Neither monthly pressure nor a
supremacy range automatically removes the incumbent.

The key focus “Кабинет после поражения” directly offers the civilian and military
roots. There is no extra future-debate or sultan-petition focus. The debate is an
event; on Ludolf's route the sultan petition follows automatic autonomy creation.

- Autonomous sultanates are immediately created by their focus on Dutch-owned
  territory: Kutai (A11, 1055), Pontianak (A12, 334), Banjar (A13, 1022).
  They remain subjects and Japanese resource concessions persist. Their support
  allows Ludolf to receive a federal mandate. Equal citizenship, elected civil
  institutions and a democratic federal constitution follow.
- The council dismisses and imprisons Ludolf. Civil and military purges remove
  actual advisers and Surya Wirata and temporarily penalise administration and
  organisation. The final focus establishes the military state.

If hearings expire first, a final event settles the contest. Sultanate backing
is required for the federal option. All outcomes are guarded against duplicate
application and subsequent overwriting by another outcome.

## Secret route (spoilers)

During the hearings, before committing to another branch,
balance between -0.1 and +0.1 inclusive can schedule a private offer after seven
days. The offer rechecks that equilibrium and that the contest remains unresolved.
Accepting reveals four royal focuses; completing the royal root brings Emma to
power. That root also depends directly on the postwar cabinet. Before acceptance,
all four use `allow_branch` and no public prerequisite or decision exposes them.
`mark_focus_tree_layout_dirty` refreshes the tree after acceptance.

Wilhelmina can replace Emma from 31 August 1898. Her accession requires the royal
island charter. The subsequent constitution separates crown, civilian government
and military command. The two monarchs currently use the game's default portrait
selection; no custom historical portraits were added.

## Verification

`py tools/validate_postwar_future.py` executes actual effects in a strict script
model: incumbent retention, mission idempotency, automatic subjects and resource
rights, federal elections, military arrests and purges, mutually protected
outcomes, secret visibility, equilibrium boundaries and succession date. It also
audits focus prerequisites, sprites, event references and localisation.

Existing expansion, Borneo, Ludolf, independent-preparations, colonial-constraints,
prewar-gates and load-repair validators cover the previous mechanics.

No running-engine campaign or visual focus-tree test was performed. Use a new
campaign to exercise the entire changed chronology; already-resolved political
outcomes in an existing save are not rolled back.

## Indonesian militia and KNIL

The volunteer conclusion of the service negotiations (`A01_japan.32`) raises the
existing twelve divisions. Their three battalions now use vanilla `militia`,
enabled through `militia_tech` before loading the OOB. The template remains locked
and the existing Japanese-crisis cleanup removes it and its divisions after peace.
Vanilla PRC TSR templates also use `militia`; Ethiopia BBA uses the distinct
`irregular_infantry` type. No cloned infantry unit or invented militia stats are used.

The regular army focus, national spirits and adviser labels explain KNIL as the
Royal Netherlands East Indies Army, distinguish it from the temporary militia,
and explain what its reforms change in the mod. Historical terminology was checked
against the Netherlands National Archives:
https://www.nationaalarchief.nl/onderzoeken/zoekhulpen/militairen-nederlands-indie-knil-1815-1950-onderofficieren-en-soldaten
