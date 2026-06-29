<div class="atlas-chapter-header">
  <span class="atlas-chapter-num">Course Overview</span>
  <h1 class="atlas-chapter-title">The Atlas Journey</h1>
  <p class="atlas-chapter-desc">A narrative-driven masterclass. Build a complete, distributed application from scratch and learn the architectural philosophy by doing.</p>
</div>

<div class="atlas-narrative">

This track is designed for developers who **learn by doing**. Instead of reading abstract theory, we are going to build a practical application.

By the end of this journey, you will have built an intelligent **Notes Application** that features:
- A custom Worker to process text.
- A Storage Worker to persist data to disk.
- A central Manager to orchestrate the system.

<div class="admonition concept">
  <p class="admonition-title">The Two Tracks of Atlas</p>
  <p>Atlas provides two distinct ways to learn:</p>
  <ol>
    <li><strong>The Journey (You are here)</strong>: A continuous, narrative-driven tutorial. We will build a project step-by-step.</li>
    <li><strong><a href="../compendium/manifests.md">The Compendium</a></strong>: The exhaustive reference manuals. If you ever wonder <em>"What does the `cost` field do in the adapter manifest?"</em>, the Compendium has the answer.</li>
  </ol>
</div>

## What We Are Building

We are going to build a simple `NotesApp`. Here is how the Capability Graph will look when we are finished:

```mermaid
graph TD
    App(NotesApp Manager) --> UI(Notes UI Worker)
    UI --> Storage(Storage Worker)
    UI --> Logger(Logger Worker)
```

Let's begin.

<br>
<strong><a href="01-scaffolding/" style="color: var(--atlas-red); text-decoration: none; border-bottom: 1px solid var(--atlas-red); padding-bottom: 2px;">Next Chapter: Scaffolding & CLI &rarr;</a></strong>

</div>
