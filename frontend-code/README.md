# Earth Query Agent

You are a senior frontend engineer and UI/UX designer helping me build a high-quality student hackathon project called "SatQuery AI" for an ISRO/SIH remote-sensing challenge.

IMPORTANT:

This is NOT a generic AI dashboard.

This is NOT a model-selection interface.

This is NOT a form where the user manually chooses VQA, Prithvi, VLM, SAR, optical, change detection, etc.

The core product concept is:

"ASK, DON'T CONFIGURE."

The user should simply ask a natural-language question about satellite imagery.

SatQuery AI must then:

1. Understand the user's query.

2. Infer the user's intent.

3. Determine what kind of remote-sensing analysis is required.

4. Determine how many images are required.

5. Determine what type of imagery is required.

6. Select the appropriate specialist workflow/model internally.

7. Explain to the user WHY that workflow was selected.

8. Ask the user only for the imagery required for that workflow.

9. Validate the uploaded imagery.

10. Execute the analysis.

11. Present the result in a human-understandable way.

12. Show supporting visual evidence.

13. Show confidence only when confidence data is actually available.

14. Show an auditable execution summary.

The user should NEVER manually select the model or analysis type.

==================================================

PROJECT PROBLEM

==================================================

Remote-sensing imagery is extremely useful for:

- agriculture

- disaster management

- urban planning

- forest monitoring

- water-resource assessment

- infrastructure monitoring

- environmental monitoring

However, remote-sensing AI systems are often fragmented into individual task-specific applications.

One system may perform VQA.

Another may perform captioning.

Another may perform grounding.

Another may perform change detection.

Another may perform Optical + SAR analysis.

This forces non-expert users to understand technical concepts such as:

- VQA

- Vision-Language Models

- Prithvi

- SAR

- Optical imagery

- bi-temporal analysis

- image pairs

- model selection

- preprocessing

- parameters

SatQuery AI solves this by introducing an agentic natural-language layer above specialist remote-sensing models.

The user interacts primarily with the QUESTION, not with the machine-learning pipeline.

==================================================

CORE PRODUCT FLOW

==================================================

The application must follow this flow:

USER

  ↓

Natural-language query

  ↓

Query understanding

  ↓

Intent detection

  ↓

Required input detection

  ↓

Workflow/model routing

  ↓

Explain WHY the workflow was selected

  ↓

Ask for required imagery

  ↓

Validate imagery

  ↓

Execute specialist analysis

  ↓

Generate evidence

  ↓

Generate result

  ↓

Explain result in simple language

  ↓

Confidence/evidence

  ↓

Auditable execution trace

The UI must visually communicate this flow.

==================================================

SUPPORTED USER INTENTS

==================================================

The system should support these major workflows.

--------------------------------

1. SINGLE-IMAGE VQA

--------------------------------

VQA means Visual Question Answering.

Example:

"Are there roads near the settlement?"

Required input:

- 1 image

The system should infer that this is a single-image visual question-answering task.

The user should NOT have to select "VQA".

--------------------------------

2. CAPTIONING / SCENE DESCRIPTION

--------------------------------

Example:

"Describe the land-cover in this image."

Required input:

- 1 image

The system should infer that this is scene description/captioning.

--------------------------------

3. TEXT-GUIDED SPATIAL GROUNDING

--------------------------------

Example:

"Highlight the water body."

Required input:

- 1 image

The output should ideally contain:

- textual interpretation

- highlighted region

- bounding box/polygon/mask where supported

Do NOT simply answer "There is a water body."

The purpose is to identify WHERE the requested feature occurs.

--------------------------------

4. BI-TEMPORAL CHANGE ANALYSIS

--------------------------------

Example:

"What changed between these two dates?"

or:

"Has the built-up area increased?"

This means:

SAME GEOGRAPHIC AREA

+

DIFFERENT ACQUISITION DATES

Required inputs:

T1 — Earlier observation

T2 — Later observation

The UI should dynamically create two upload slots.

The UI must explain:

"This question requires comparison across acquisition dates, so SatQuery needs an earlier and later observation of the same geographic area."

Possible outputs:

- change description

- affected region

- change magnitude

- before/after comparison

- change map

- spatial evidence

- confidence when available

--------------------------------

5. CROSS-MODAL OPTICAL + SAR ANALYSIS

--------------------------------

Example:

"Use optical and SAR imagery to identify flooded areas."

This means:

OPTICAL / MULTISPECTRAL IMAGE

+

SAR IMAGE

The important distinction is:

OPTICAL + SAR = different sensing modalities.

BI-TEMPORAL = different acquisition times.

Do NOT confuse these two concepts.

Optical + SAR does NOT automatically mean bi-temporal.

The system should explain this naturally to the user.

For example:

"Your query requests complementary information from optical and radar observations. SatQuery therefore requires one optical/multispectral image and one SAR image."

==================================================

CRITICAL LOGIC RULE

==================================================

The user NEVER selects:

- VQA

- Captioning

- Grounding

- Bi-temporal

- Optical

- SAR

- Prithvi

- VLM

- model parameters

- specialist model

The system decides these based on the query and available inputs.

DO NOT create dropdowns such as:

"Select Task"

"Select Model"

"Select Modality"

DO NOT create a model configuration dashboard.

Instead, show the decision as an explanation AFTER query interpretation.

Example:

USER:

"What changed between these two dates?"

SATQUERY:

┌─────────────────────────────────────────┐

│ QUERY UNDERSTOOD                         │

│                                          │

│ Bi-Temporal Change Analysis              │

│                                          │

│ Why?                                     │

│ Your question asks how the same area     │

│ changed across two acquisition dates.    │

│                                          │

│ Required imagery                         │

│ ○ T1 — Earlier observation               │

│ ○ T2 — Later observation                 │

└─────────────────────────────────────────┘

The user then uploads the two images.

==================================================

MODEL EXPLANATION

==================================================

After the query is interpreted, add an attractive section:

"WHY THIS WORKFLOW?"

This should explain:

1. What SatQuery understood.

2. What analysis is required.

3. Which specialist component/workflow is being used.

4. Why that component is appropriate.

5. What inputs are required.

For example:

QUERY:

"What changed between these two dates?"

INTENT:

Bi-Temporal Change Analysis

WORKFLOW:

Temporal Change Analysis

WHY:

"Your query asks for differences between two observations of the same geographic area. SatQuery therefore routes the request through a temporal change-analysis workflow rather than a single-image VQA workflow."

REQUIRED INPUTS:

T1 Earlier Image

T2 Later Image

Do NOT claim a model was used unless the actual application/backend has selected that model.

If the current project is using mocked model routing, clearly label it as:

"Demo / simulated routing"

Do not fake scientific results.

==================================================

MODEL TERMINOLOGY

==================================================

Use terminology accurately.

Prithvi-EO-2.0:

A remote-sensing foundation model/component used for Earth Observation representation/perception.

RS-VLM:

Remote-Sensing Vision-Language Model.

VLM:

Vision-Language Model.

The UI should explain these in simple language if they are shown.

For example:

"Prithvi-EO-2.0

Remote-sensing perception component

Used to extract Earth Observation visual representations."

"RS-VLM

Remote-sensing vision-language reasoning component

Connects satellite imagery with natural-language questions."

Do not claim that every result was directly generated by Prithvi.

Do not claim a specific architecture such as Siamese-UNet is actually running unless the backend really uses it.

The frontend should be BACKEND-READY.

==================================================

REMOTE-SENSING DATA

==================================================

The system may work with:

- Optical / multispectral imagery

- SAR imagery

- bi-temporal image pairs

- pre-georeferenced/co-registered imagery where available

Supported file formats should be handled carefully.

Preferred remote-sensing format:

- GeoTIFF / TIFF

For demo/public benchmark imagery, PNG/JPEG may also be accepted if supported by the application.

DO NOT pretend that PNG/JPEG contains geospatial metadata if it does not.

Metadata such as:

- acquisition date

- sensor

- resolution

- coordinates

- modality

should only be displayed when actually available.

==================================================

FILE UPLOAD MUST ACTUALLY WORK

==================================================

This is extremely important.

The file upload UI must work in the browser.

Do NOT create fake "Choose File" buttons that do nothing.

Use real HTML file input behavior.

The user must be able to:

- click to select a file

- drag and drop if possible

- see upload progress/state

- see the selected filename

- see image preview

- remove the image

- replace the image

- see validation errors

- upload the correct number of images for the detected workflow

The upload component must dynamically change according to the detected intent.

Examples:

Captioning:

ONE IMAGE SLOT

Grounding:

ONE IMAGE SLOT

Bi-temporal:

T1 EARLIER

+

T2 LATER

Optical + SAR:

OPTICAL

+

SAR

Do NOT show unnecessary slots.

==================================================

INPUT VALIDATION

==================================================

Before analysis, validate:

- required number of images

- file type

- image readability

- modality if metadata is available

- acquisition dates if available

- compatibility where possible

For bi-temporal analysis, clearly indicate:

✓ Two observations supplied

✓ Earlier observation identified

✓ Later observation identified

If dates cannot actually be extracted from the file, do NOT invent dates.

Instead allow the user to provide/confirm the observation date if the application requires it.

For Optical + SAR:

✓ Optical image supplied

✓ SAR image supplied

Again, do not fabricate sensor metadata.

==================================================

RESULT EXPERIENCE

==================================================

The result should NOT be just a paragraph.

Create a polished analysis result experience.

Use sections such as:

1. AI FINDING

2. WHAT THIS MEANS

3. STRUCTURED OBSERVATIONS

4. VISUAL EVIDENCE

5. CONFIDENCE

6. EXECUTION TRACE

Example:

AI FINDING

"Surface-water extent increased between the two observations."

WHAT THIS MEANS

"The later observation shows a larger water-covered region than the earlier observation, indicating an expansion of surface-water extent."

STRUCTURED OBSERVATIONS

• Water extent increased

• Change concentrated in the central basin

• Affected region identified

VISUAL EVIDENCE

[Before]

[After]

[Change Map]

==================================================

OUTCOME EXPLANATION

==================================================

The user should understand the result even if they are not a remote-sensing expert.

Do not just output:

"Δ water = +34.2 km²"

Instead show:

"Water-covered area increased by approximately 34.2 km²."

Then explain:

"This means that the area classified as water in the later observation is larger than in the earlier observation."

If a percentage is available:

"That corresponds to approximately a 231% increase."

But only display quantitative values if they actually come from the analysis/backend/demo data.

Do not fabricate measurements.

==================================================

VISUAL EVIDENCE

==================================================

Make evidence visually important.

For bi-temporal analysis, provide:

BEFORE (T1)

AFTER (T2)

CHANGE MAP

Prefer an interactive comparison where possible:

- side-by-side

- split slider

- overlay/change-map toggle

- zoom

- image focus

For grounding:

- highlighted region

- bounding box

- polygon/mask if available

For Optical + SAR:

- optical view

- SAR view

- combined interpretation

The result should feel like an actual remote-sensing analysis workstation.

==================================================

EXECUTION TRACE

==================================================

Add a beautiful but understandable execution trace.

Example:

01 Query Interpretation

Bi-temporal comparison intent detected.

02 Input Validation

Two compatible observations supplied.

03 Workflow Routing

Temporal change-analysis workflow selected.

04 Remote-Sensing Perception

Satellite imagery processed for spatial features.

05 Change Analysis

Differences between T1 and T2 evaluated.

06 Evidence Generation

Change evidence generated.

07 Response Synthesis

Final answer assembled.

IMPORTANT:

This is an AUDITABLE EXECUTION SUMMARY.

It is NOT hidden chain-of-thought.

Never expose private/internal chain-of-thought.

Only show high-level observable workflow information.

==================================================

UI / UX REQUIREMENTS

==================================================

The current UI must NOT look like a beginner project.

It should look like a serious SIH / ISRO student hackathon prototype.

However:

DO NOT make it look like a generic corporate SaaS template.

DO NOT overdo glassmorphism.

DO NOT fill the screen with unnecessary cards.

DO NOT use excessive gradients.

DO NOT use fake futuristic animations everywhere.

The design should feel like:

REMOTE-SENSING INTELLIGENCE WORKSTATION

+

MODERN AI ASSISTANT

+

PROFESSIONAL HACKATHON DEMO

Think:

- dark Earth-observation theme

- satellite/terrain-inspired visual language

- deep navy/black background

- cyan/teal primary accent

- subtle green for successful validation

- amber/red only for warnings/errors

- clean typography

- monospace labels for technical metadata

- strong visual hierarchy

- professional spacing

- subtle borders

- restrained glow

- interactive panels

==================================================

MAIN SCREEN STRUCTURE

==================================================

Build the application around a clear vertical journey.

HEADER

────────────────────────────────────────

SATQUERY AI

"Ask the Earth. Understand the Change."

Small status indicators:

- System Ready

- Agent Ready

- Backend/Model status if actually available

Do NOT make model selection controls visible.

------------------------------------------------

HERO / QUERY AREA

Large heading:

"Ask the Earth.

Understand the Change."

Supporting text:

"Describe what you want to know about satellite imagery. SatQuery automatically determines the required analysis."

Then a large conversational query input.

Example placeholder:

"Ask anything about the uploaded Earth observation imagery..."

Examples as clickable chips:

"Describe the land-cover in this image."

"What changed between these two dates?"

"Highlight the water body."

"Has the built-up area increased?"

"Identify flooded areas using optical and SAR imagery."

------------------------------------------------

QUERY UNDERSTANDING

After the user submits the query, animate/transition into:

"SATQUERY UNDERSTOOD"

Display:

Intent

Analysis type

Required imagery

Reason

This should feel like an AI agent making a decision.

------------------------------------------------

WHY THIS WORKFLOW

Create a prominent explanatory panel.

Show:

WHAT I UNDERSTOOD

WHY THIS WORKFLOW

WHAT I NEED FROM YOU

WHAT WILL HAPPEN NEXT

Example:

WHAT I UNDERSTOOD

"Your query is asking for change between two observations."

WHY THIS WORKFLOW

"Temporal comparison is required because the question refers to change across acquisition dates."

WHAT I NEED

"T1 Earlier observation + T2 Later observation"

NEXT

"Upload the two corresponding observations to continue."

------------------------------------------------

DYNAMIC IMAGERY UPLOAD

Only show the upload slots required by the detected workflow.

Make this a premium interactive component.

Each slot should contain:

- role label

- upload button

- drag-and-drop area

- image preview

- filename

- file size

- format

- validation status

- remove

- replace

Example:

T1

EARLIER OBSERVATION

"Baseline image"

T2

LATER OBSERVATION

"Comparison image"

For Optical + SAR:

OPTICAL / MULTISPECTRAL

SAR / RADAR

Do not show "select modality" controls if the query has already determined the requirement.

------------------------------------------------

ANALYSIS READY STATE

Before analysis:

Show a clear readiness indicator.

Example:

✓ Query understood

✓ Required inputs supplied

✓ Images readable

✓ Input configuration valid

Then:

[ ANALYZE WITH SATQUERY ]

------------------------------------------------

ANALYSIS PROGRESS

When analysis starts, show an interactive workflow timeline.

Example:

QUERY INTERPRETATION

      ↓

INPUT VALIDATION

      ↓

SPECIALIST ROUTING

      ↓

REMOTE-SENSING PERCEPTION

      ↓

TASK ANALYSIS

      ↓

EVIDENCE GENERATION

      ↓

RESULT SYNTHESIS

Animate only the currently running stage.

Do not fake completion instantly.

If the existing application already has progress logic, preserve it.

------------------------------------------------

MODEL ROUTING EXPLANATION

After/during analysis, show:

"AGENTIC ROUTING"

Display:

Selected workflow

Specialist component/model

Why it was selected

Input compatibility

For example:

AGENTIC ROUTING

Workflow:

Bi-Temporal Change Analysis

Specialist perception:

Prithvi-EO-2.0 / remote-sensing perception component

Reasoning:

Remote-Sensing Vision-Language reasoning

Why:

"The query requires interpretation of visual differences across two acquisition dates."

If this is simulated/mock routing, label it clearly.

------------------------------------------------

RESULT DASHBOARD

Make this the visual centerpiece.

Top:

AI INTELLIGENCE FINDING

Large readable answer.

Then:

WHAT THIS MEANS

Human-friendly explanation.

Then:

STRUCTURED OBSERVATIONS

Bulleted findings.

Then:

VISUAL EVIDENCE

Large image comparison.

Then:

CONFIDENCE

Only if supplied by the backend/mock analysis.

Explain confidence in plain language.

Then:

EXECUTION TRACE

Collapsible technical summary.

==================================================

INTERACTION DESIGN

==================================================

Make the application feel alive without becoming distracting.

Use:

- smooth panel transitions

- subtle hover states

- upload previews

- loading states

- step transitions

- active workflow indicators

- expandable explanation cards

- image comparison controls

- tooltips for technical terminology

Potential micro-interactions:

When query is submitted:

"Understanding your request..."

Then:

"Intent identified"

Then:

"Determining required imagery..."

Then:

"Workflow ready"

Then:

"Awaiting imagery"

Do not use fake long delays.

Keep interactions responsive.

==================================================

TECHNICAL TERMINOLOGY SHOULD BE EXPLAINABLE

==================================================

Technical terms should have tooltips or expandable explanations.

For example:

VQA

"Visual Question Answering — answering a natural-language question about an image."

SAR

"Synthetic Aperture Radar — radar-based Earth observation imagery."

Bi-temporal

"Two observations of the same area acquired at different times."

Optical

"Satellite imagery based on reflected electromagnetic radiation."

RS-VLM

"Remote-Sensing Vision-Language Model."

Prithvi-EO-2.0

"Remote-sensing foundation model used as an Earth Observation perception component."

Do not overwhelm the user with terminology.

Use progressive disclosure.

==================================================

DATASET / EVALUATION SECTION

==================================================

Include an optional collapsible section near the bottom:

"ISRO / SAC EVALUATION ALIGNMENT"

This should not interfere with the primary user workflow.

Display:

Single-Image VQA

Benchmark:

RSVQA / relevant benchmark

Captioning / Grounding

Benchmark:

VRSBench

Bi-temporal Change Analysis

Benchmark:

CDVQA / bi-temporal pairs

Optical-SAR

Evaluation:

co-registered Cartosat / RISAT imagery where applicable

Agentic Orchestration

Evaluation:

auditable execution trace + appropriate workflow routing

Make this informative rather than promotional.

==================================================

BACKEND-READY DESIGN

==================================================

The frontend must be structured so a real backend can be connected later.

Use data-driven state rather than hardcoding the UI.

Conceptually support:

query

intent

task

requiredInputs

uploadedImages

inputValidation

workflowExplanation

selectedWorkflow

selectedComponents

analysisProgress

result

evidence

confidence

executionTrace

If the backend later returns:

{

  intent,

  task,

  requiredInputs,

  workflow,

  models,

  explanation,

  validation,

  result,

  evidence,

  confidence,

  executionTrace

}

the frontend should be able to render it without rewriting the UI.

==================================================

DO NOT BREAK EXISTING FUNCTIONALITY

==================================================

This is extremely important.

I may already have working React components and handlers.

DO NOT unnecessarily rewrite:

- state management

- upload handlers

- analysis handlers

- query handlers

- result generation

- existing API/mock-service logic

- TypeScript interfaces

- working components

First inspect the existing project.

Then modify only what is necessary.

If a component already exists, improve it rather than replacing its functionality.

Preserve existing handlers and props unless a change is genuinely required.

If you need a new prop, make it optional where possible.

Do not introduce TypeScript errors.

Do not create unused variables.

Do not introduce undefined components.

Do not break imports.

Do not change working backend behavior.

==================================================

IMPORTANT: NO FAKE FUNCTIONALITY

==================================================

Do not create UI that looks functional but does nothing.

Specifically:

- File upload must actually work.

- Remove must actually remove.

- Replace must actually replace.

- Query submission must actually work.

- Analysis button must actually work.

- Progress must reflect the existing analysis state.

- Result rendering must use the actual result object.

- Dynamic input requirements must be derived from the current intent/task.

- Do not hardcode the same workflow regardless of query.

If the current backend is mocked, that is acceptable.

But clearly separate:

DEMO / MOCK DATA

from:

REAL MODEL / BACKEND DATA

==================================================

DO NOT FABRICATE SCIENTIFIC RESULTS

==================================================

Never invent:

- satellite metadata

- sensor names

- coordinates

- acquisition dates

- confidence values

- area measurements

- model outputs

- model execution claims

unless they actually exist in the current data.

If demo values are used, label them as demo/mock values.

The frontend must be scientifically honest.

==================================================

IMPORTANT LOGIC EXAMPLES

==================================================

Example 1:

Query:

"Describe the land-cover in this image."

System:

Intent = Captioning / Scene Description

Required = 1 image

NOT:

Bi-temporal

NOT:

Optical + SAR

NOT:

Two upload slots

------------------------------------------------

Example 2:

Query:

"Highlight the water body."

System:

Intent = Text-Guided Spatial Grounding

Required = 1 image

Output:

Text + spatial evidence

------------------------------------------------

Example 3:

Query:

"What changed between these two dates?"

System:

Intent = Bi-Temporal Change Analysis

Required =

T1 Earlier

T2 Later

Explain:

Same geographic area + different acquisition dates.

------------------------------------------------

Example 4:

Query:

"Use optical and SAR imagery to identify flooded areas."

System:

Intent = Cross-Modal Optical + SAR

Required =

Optical

SAR

Explain:

Different sensing modalities provide complementary information.

Do NOT automatically classify this as bi-temporal unless the query/input actually indicates different dates.

==================================================

VISUAL DESIGN GOAL

==================================================

The final result should look like a serious SIH/ISRO hackathon prototype.

It should communicate:

"Someone built an intelligent remote-sensing agent."

It should NOT communicate:

"Someone generated a generic React dashboard."

The UI should have:

- strong hero section

- premium query interface

- intelligent workflow visualization

- dynamic imagery upload

- large visual analysis area

- polished result dashboard

- interactive evidence comparison

- clear model-routing explanation

- readable technical information

- subtle satellite/Earth-observation visual language

- responsive layout

- excellent spacing

- accessible contrast

- meaningful animations

Use Tailwind CSS if that is already the project's styling system.

Do not add unnecessary dependencies unless absolutely necessary.

==================================================

RESPONSIVE DESIGN

==================================================

The UI must work on:

- laptop

- desktop

- tablet

- smaller screens

On mobile:

- cards stack

- two image slots become vertical

- comparison views become scrollable

- query remains easy to use

- result remains readable

==================================================

FINAL REQUIREMENT

==================================================

Before changing code:

1. Inspect the existing project structure.

2. Identify the existing working flow.

3. Identify current components.

4. Preserve existing functionality.

5. Identify what can be improved visually.

6. Implement the UI incrementally.

7. Ensure TypeScript compiles.

8. Ensure file upload works.

9. Ensure the query-driven routing logic remains correct.

10. Ensure the user never has to manually select the model/workflow.

11. Ensure all displayed model explanations correspond to the actual current workflow/data.

12. Ensure the final UI clearly communicates:

ASK

↓

UNDERSTAND

↓

PLAN

↓

REQUEST REQUIRED IMAGERY

↓

ANALYZE

↓

EXPLAIN

↓

SHOW EVIDENCE

Do not simply make the existing UI prettier.

Re-think the visual hierarchy and interaction design while preserving the underlying functionality.

The final application should feel like an intelligent remote-sensing analysis assistant, not a collection of forms.

Most importantly:

THE USER ASKS.

SATQUERY DECIDES.

THE USER PROVIDES THE REQUIRED IMAGERY.

SATQUERY ANALYZES.

SATQUERY EXPLAINS.
i need a little detailed answers, while explaining the user. not so detailed but understandbale length atleast 4 5 lines

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/e41a8615-75c0-4faa-b061-fec1a8aa46d8).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
