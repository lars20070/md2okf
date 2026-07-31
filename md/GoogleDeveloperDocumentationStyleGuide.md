---
title: Google Developer Documentation Style Guide
source: https://developers.google.com/style
generated_at: 2026-07-31
pages: 70
format: Single-file Markdown
---

# Google Developer Documentation Style Guide

*Snapshot of [https://developers.google.com/style](https://developers.google.com/style) generated 2026-07-31.*

## Table of contents

### Introduction

- [About this guide](#style)
- [Highlights](#highlights)
- [What's new](#whats-new)
- [Philosophy of this guide](#philosophy)

### Key resources

- [Word list](#word-list)
- [Product names](#product-names)
- [Text-formatting summary](#text-formatting)

### General principles

- [Accessibility](#accessibility)
- [Excessive claims](#excessive-claims)
- [Future features](#future)
- [Global audience](#translation)
- [Inclusive language](#inclusive-documentation)
- [Jargon](#jargon)
- [Prescriptive documentation](#prescriptive-documentation)
- [Third-party content](#other-sources)
- [Timeless documentation](#timeless-documentation)
- [Voice and tone](#tone)

### Language and grammar

- [Abbreviations](#abbreviations)
- [Active voice](#voice)
- [Anthropomorphism](#anthropomorphism)
- [Articles (a, an, the)](#articles)
- [Capitalization](#capitalization)
- [Contractions](#contractions)
- [Pluralization](#pluralization)
- [Possessives](#possessives)
- [Prepositions](#prepositions)
- [Present tense](#tense)
- [Pronouns](#pronouns)
- [Second person](#person)
- [Sentence structure](#sentence-structure)
- [Verbs in reference documents](#reference-verbs)

### Punctuation

- [Colons](#colons)
- [Commas](#commas)
- [Dashes](#dashes)
- [Ellipses](#ellipses)
- [Hyphens](#hyphens)
- [Parentheses](#parentheses)
- [Periods and end punctuation](#periods)
- [Quotation marks](#quotation-marks)
- [Semicolons](#semicolons)
- [Slashes](#slashes)

### Formatting and organization

- [Dates and times](#dates-times)
- [Examples](#format-examples)
- [Figures and other images](#images)
- [Footnotes](#footnotes)
- [Headings and titles](#headings)
- [Italics with terms](#italics-terms)
- [Lists](#lists)
- [Mathematical notation](#mathematical-notation)
- [Notes and other notices](#notices)
- [Numbers](#numbers)
- [Paragraphs](#paragraph-structure)
- [Phone numbers](#phone-numbers)
- [Procedures](#procedures)
- [Tables](#tables)
- [Units of measurement](#units-of-measure)

### Linking

- [Cross-references and linking](#cross-references)
- [Headings as link targets](#headings-targets)

### Computer interfaces

- [API reference code comments](#api-reference-comments)
- [Code in text](#code-in-text)
- [Code samples](#code-samples)
- [Command-line syntax](#code-syntax)
- [Placeholder formatting](#placeholders)
- [UI elements and interaction](#ui-elements)

### HTML and CSS

- [HTML and semantic tagging](#semantic-tagging)
- [HTML formatting](#html-formatting)
- [Markdown versus HTML](#markdown)

### Names and naming

- [Example domains and names](#examples)
- [Filenames](#filenames)
- [Trademarks](#trademarks)

## Introduction

<a id="style"></a>

### About this guide

*Source: <https://developers.google.com/style>*

This style guide provides editorial guidelines for writing clear and consistent technical
documentation for an audience of software developers and other technical practitioners.

If you're new to the guide and looking for introductory topics about our style, then start with
[Highlights](#highlights), [Voice and tone](#tone), and
[Text-formatting summary](#text-formatting). Otherwise, use the guide as
a reference document for specific questions. For example, you can look up terms in the
[word list](#word-list).

<a id="style--editorial-resources"></a>

#### Editorial resources

We recommend using the following editorial resources.

<a id="style--reference-hierarchy"></a>

##### Reference hierarchy

Use the following references, including this guide, in this order:

1. **Project-specific style**. Follow style guidance specific to your project or product, such
   as necessary exceptions to this guide or terms that are relevant only to your product.
2. **This style guide**. If project-specific style guidelines don't provide explicit
   guidance, then follow this guide.
3. **Third-party references**. If the preceding references don't provide explicit guidance,
   then see these third-party references, depending on the nature of your question:

   | Type of question | Third-party reference |
   | --- | --- |
   | Spelling | Follow [Merriam-Webster.com](https://www.merriam-webster.com/). See also [Spelling](https://developers.google.com/style/spelling). |
   | Nontechnical style | Follow [*The Chicago Manual of Style*, 17th edition](https://www.chicagomanualofstyle.org/home.html) (subscription required). |
   | Technical style | See the [Microsoft Writing Style Guide](https://docs.microsoft.com/style-guide/welcome/). But consider whether Microsoft's guidance applies; some of it might apply only to Microsoft products and interfaces. |

At multiple stages of this hierarchy, it can be helpful to look to established usage. For
example, search your organization's documentation, or check a broad language corpus such
as [Google Ngram Viewer](https://books.google.com/ngrams/).

<a id="style--other-editorial-resources"></a>

##### Other editorial resources

You can use additional resources to research and inform your thinking, but don't consider them
part of Google developer documentation style.

Here are some other style guides from the tech community:

- [Apple Style Guide](https://help.apple.com/applestyleguide/)
- [Red Hat supplementary style guide for product documentation](https://redhat-documentation.github.io/supplementary-style-guide/)

<a id="style--annotations"></a>

<a id="style--annotations-used-in-this-guide"></a>

#### Annotations used in this guide

For guidance that applies only to Android or Google Cloud documentation, look for the following
logos:

- precedes terms and guidelines specific to Android
  documentation.
- precedes terms and guidelines specific to Google Cloud
  documentation.

<a id="style--rules"></a>

<a id="style--break-the-rules"></a>

#### Break the rules

> *Break any of these rules sooner than say anything outright barbarous.*
>
> —George Orwell,
> "[Politics and the English Language](https://www.orwellfoundation.com/the-orwell-foundation/orwell/essays-and-other-works/politics-and-the-english-language/)"

This guide contains guidelines, not rules. Depart from it when doing so improves your
content.

For example, if we recommend spelling a term as one word, and you determine that the
hyphenated version of a term in your domain is more appropriate for your readers, then
it's fine to use that instead. We acknowledge that sometimes there are competing forms
of the same word in wide use, especially as new terms emerge, and you might have good
reasons for departing from our guidance.

When you depart from this guide, be consistent throughout your document.

---

<a id="highlights"></a>

### Highlights

*Source: <https://developers.google.com/style/highlights>*

The style guide covers a lot of material, so the following page provides an overview of its most
important points. For more information about topics on the page, follow the links.

<a id="highlights--tone"></a>

<a id="highlights--tone-and-content"></a>

#### Tone and content

- [Be conversational and friendly](#tone) without being
  frivolous.
- [Don't pre-announce anything](#future) in
  documentation.
- [Use descriptive link text](#cross-references--descriptive-link-text).
- [Write accessibly](#accessibility).
- [Write for a global audience](#translation).

<a id="highlights--language"></a>

<a id="highlights--language-and-grammar"></a>

#### Language and grammar

- [Use second person](#person): "you" rather than
  "we."
- [Use active voice](#voice): make clear who's performing
  the action.
- [Use standard American spelling](https://developers.google.com/style/spelling) and
  punctuation.
- [Put conditions before instructions](#sentence-structure),
  not after.
- [For usage and spelling of specific words, see
  the word list](https://developers.google.com/style/wordlist).

<a id="highlights--formatting"></a>

<a id="highlights--formattingu002c-punctuationu002c-and-organization"></a>

#### Formatting, punctuation, and organization

- [Use sentence case](#capitalization) for document
  titles and section headings.
- [Use numbered lists](#lists--types-of-lists) for sequences.
- [Use bulleted lists](#lists--types-of-lists) for most other lists.
- [Use description lists](#lists--types-of-lists) for pairs of related
  pieces of data.
- [Use serial commas](https://developers.google.com/style/commas-serial).
- [Put code-related text in code font](#code-in-text).
- [Put UI elements in bold](#ui-elements).
- [Use unambiguous date formatting](#dates-times).

<a id="highlights--images"></a>

#### Images

- [Provide alt
  text](#images--text-associated-with-images).
- [Provide high-resolution or vector
  images](#images--high-resolution-images) when practical.

---

<a id="whats-new"></a>

### What's new

*Source: <https://developers.google.com/style/whats-new>*

This page provides a summary of significant changes to the style guide.

<a id="whats-new--20260707"></a>

<a id="whats-new--july-7u002c-2026"></a>

#### July 7, 2026

| New guidance or change | Page |
| --- | --- |
| Softened a statement regarding the effect of inconsistent terminology on translation costs. | [Write for a global audience](#translation) |
| Added cross-references between guidance about optional procedure steps and guidance about optional headings. | [Headings and titles](#headings),  [Procedures](#procedures) |
| Clarified that much of our guidance about writing inclusive documentation relates to the broader principle of avoiding figurative language, which can be ableist or unnecessarily graphic. Instead, we use literal, precise terms in their primary sense. | [Write inclusive documentation](#inclusive-documentation),  [Voice and tone](#tone),  [Word list](#word-list) |
| Updated guidance about creating custom heading targets, making anchor (`<a>`) elements equally as acceptable as section (`<section>`) elements. | [Make headings into link targets](#headings-targets) |
| Added guidance about ensuring that you contextualize UI elements when you document them outside of a numbered procedure. | [UI elements and interaction](#ui-elements) |
| Added word list entry: *managed instance group (MIG)* | [Word list](#word-list) |

<a id="whats-new--20260407"></a>

<a id="whats-new--april-7u002c-2026"></a>

#### April 7, 2026

| New guidance or change | Page |
| --- | --- |
| Added guidance about avoiding inconsistent end punctuation in list items. | [Lists](#lists) |
| Added *do the following* as a recommended phrase for introducing lists in procedures. | [Procedures](#procedures) |
| Clarified that ordered lists are appropriate for any list where sequence is significant. Added guidance about ensuring that it's clear whether the items in an unordered list are required or optional. | [Lists](#lists) |
| Added guidance that if you must refer to a step number, use the numeral. | [Numbers](#numbers) |
| Added guidance to use italics sparingly, and consolidated italics guidance into a new page. | [Use italics to discuss terms](#italics-terms),  [Text-formatting summary](#text-formatting) |
| Added guidance recommending the terms *selected* and *not selected* to refer to the state of a checkbox. | [UI elements and interaction](#ui-elements) |
| Changed guidance to recommend using code font for IP addresses and port numbers. Added package names to the list of items to place in code font. | [Code in text](#code-in-text) |
| Updated UI elements guidance with expanded definitions for *pane*, *panel*, and *section*. Added guidance about how to identify difficult-to-find UI elements without using directional language. | [UI elements and interaction](#ui-elements) |
| Added `.wasm` (Wasm file) to the table of file extensions and corresponding file type names. | [Filenames and file types](#filenames) |
| Reorganized and extended guidance about formatting abbreviation introductions. | [Abbreviations](#abbreviations),  [Text-formatting summary](#text-formatting) |
| Consolidated pluralization guidance into a new page, including guidance about abbreviations, product names, and code elements. | [Pluralization](#pluralization) |
| Restructured guidance about writing for a global audience to make it easier to navigate. | [Write for a global audience](#translation) |
| Expanded guidance about exclamation marks to clarify that we avoid them except in rare cases. | [Periods and other end punctuation](#periods),  [Voice and tone](#tone) |
| Created a page about how to format common mathematical notation. | [Mathematical notation](#mathematical-notation),  [Numbers](#numbers),  [Text-formatting summary](#text-formatting),  [Units of measurement](#units-of-measure) |
| Changed guidance for temperatures to recommend a nonbreaking space between a numeral and the degree symbol instead of between the degree symbol and the temperature scale. | [Units of measurement](#units-of-measure) |
| Added guidance about marking headings as optional. Restructured headings guidance to make it easier to navigate. | [Headings and titles](#headings) |
| Added an entry for *AI*, specifying that it rarely needs to be spelled out. | [Word list](#word-list),  [Abbreviations](#abbreviations) |
| Clarified that the word *can* can be used to convey both permission and ability. | [Word list](#word-list) |
| Clarified that when we mark a term "Use with caution" in the word list, we recommend following our standard jargon guidance. | [Word list](#word-list) |
| Clarified how we prefer to distinguish between a *page* (the whole web page) and a *document* (the text on a page that explains a product, feature, or service). | [Word list](#word-list) |
| Revised the entry for *style sheet* to also allow for *stylesheet*, prioritizing consistency in a document. | [Word list](#word-list) |
| Added explanations to several existing word list items regarding compound word usage: *clickthrough*, *hardcode*, *high availability*, *load balancing*, *plugin*, *third-party*, *time zone*, and *wake lock*. | [Word list](#word-list) |
| Expanded the entry for *first class*, *first-class*, *first-class citizen*, providing new recommended alternatives with examples. | [Word list](#word-list),  [Write inclusive documentation](#inclusive-documentation) |
| Expanded or added entries for *like*, *such as*, *for example*, and *for instance*. Made corresponding updates to the page about writing examples. | [Word list](#word-list),  [Format examples](#format-examples) |
| Added guidance to the *virtual machine (VM) instance* entry regarding Compute Engine instances. | [Word list](#word-list) |

<a id="whats-new--20250508"></a>

<a id="whats-new--may-8u002c-2025"></a>

#### May 8, 2025

| New guidance or change | Page |
| --- | --- |
| Removed outdated language that indicated that a list of options is treated differently than other unordered lists. | [Lists](#lists) |
| Added a page about writing prescriptive documentation. | [Prescriptive documentation](#prescriptive-documentation), [Word list](#word-list--should) |
| Removed guidance that said to include empty parentheses after method names. | [Code in text](#code-in-text) |
| Changed footnotes guidance to recommend using numbers instead of symbols. | [Footnotes](#footnotes) |
| Simplified contractions guidance, removing excess explanations and examples. | [Contractions](#contractions) |
| Added examples to guidance about introducing sections of a document. | [Headings and titles](#headings) |
| Added an example service account ID. | [Example domains and names](#examples) |
| Simplified and clarified guidance about articles, including using articles before abbreviations and product names. | [Abbreviations](#abbreviations), [Articles (a, an, the)](#articles), [Product names](#product-names), [Word list](#word-list) |
| Included a general explanation of why we don't document future features. | [Document future features](#future) |
| Revised guidance to recommend using an abbreviation in a title or heading only if the abbreviation is the more commonly known version of the word. | [Headings and titles](#headings) |
| Added a suggestion that when you use an imperative in running text, consider whether to write a procedure instead. | [Second person and first person](#person) |
| Generalized existing guidance on what to do when jargon is part of a command or code sample. | [Jargon](#jargon) |
| Consolidated guidance about cross-references and linking into one page. | [Cross-references and linking](#cross-references) |
| Added some specific reasons why we avoid directional language when orienting the reader to information on a page. | [Write accessible documentation](#accessibility) |
| Clarified that spacing around icons is a judgment call based on readability. | [UI elements and interaction](#ui-elements) |
| Removed an example phone number. | [Example domains and names](#examples) |
| Removed the word list entry for *property* because its usage heavily depends on the technical context. | [Word list](#word-list) |
 New word list entries: *choose*, *confidential*, *sensitive*, *image*, *Fast Healthcare Interoperability Resources (FHIR)* | [Word list](#word-list) |

<a id="whats-new--20250117"></a>

<a id="whats-new--january-17u002c-2025"></a>

#### January 17, 2025

| New guidance or change | Page |
| --- | --- |
| Consolidated spelling guidance into the introduction to the word list. Extended guidance about how to use the preferred dictionary to determine which spelling to use for a word with multiple spellings. | [Word list](#word-list) |
| Generalized guidance about when to use spaces or tabs for indentation in code samples. | [Code samples](#code-samples--guidelines) |
| Changed guidance for formatting telephone numbers to recommend using dashes instead of parentheses to set the area code off from the rest of the number. | [Format phone numbers](#phone-numbers) |
| Extended and clarified recommendation to avoid the abbreviations *i.e.*, *e.g.*, and *etc.* in most cases. | [Abbreviations](#abbreviations--dont-use), [Comma-separated lists](#lists--comma-separated-lists) |

<a id="whats-new--20241029"></a>

<a id="whats-new--october-29u002c-2024"></a>

#### October 29, 2024

| New guidance or change | Page |
| --- | --- |
| Consolidated and expanded guidance about hyphens and closed compounds. | [Hyphens](#hyphens) |
| Added *hotspot* to the word list. | [Word list](#word-list--hotspot) |

<a id="whats-new--20240815"></a>

<a id="whats-new--august-15u002c-2024"></a>

#### August 15, 2024

| New guidance or change | Page |
| --- | --- |
| Added guidance for distinguishing between binary and decimal units, such as gibibytes (GiB) and gigabytes (GB). Also corrected abbreviation of *kilobyte* to *kB*. | [Decimal and binary units](#units-of-measure--byte-units) |
| Expanded guidance for referring to figures and other images in text. Clarified that figure numbers are not required. | [Figure captions](#images--figure-captions) |
| Added word list entries: *curl*, *whitepaper*, *long-running operation* | [Word list](#word-list) |
| Updated word list entries: *ingest*, *execute*, *content type*, *media type*, *MIME* | [Word list](#word-list) |

<a id="whats-new--20240516"></a>

<a id="whats-new--may-16u002c-2024"></a>

#### May 16, 2024

| New guidance or change | Page |
| --- | --- |
| Added the term *generative AI*. | [Word list](#word-list--generative-ai) |
| Added the term *rehost*. Redirected the definition for *lift and shift* to *rehost*. | [Word list](#word-list--rehost) |
| Clarified that the style guide shows examples of how placeholders render but doesn't explain how to implement this visual styling. | [Format placeholders](#placeholders) |
| Added an example to the guidance showing how to use site-root-relative URLs to link to another page on the same server. | [Cross-references](https://developers.google.com/style/cross-references#same-server) |
| Clarified guidance about how to format anchor text. | [Make headings into link targets](#headings-targets--markdown) |

<a id="whats-new--20240321"></a>

<a id="whats-new--march-21u002c-2024"></a>

#### March 21, 2024

| New guidance or change | Page |
| --- | --- |
| Expanded guidance about avoidance of the term *drop-down*. | [Word list](#word-list--drop-down) |
| Added examples to guidance about writing documentation that focuses on the present state of the software. | [Timeless documentation](#timeless-documentation) |
| Added recommendation to use a more precise term than *workload* when possible, or to define what the term means in the specific context.  Added related guidance about avoiding ambiguous or overloaded words like *workload*, *solution*, and *support*, or defining them in each context. | [Word list](#word-list--workload),  [Jargon](#jargon) |
| Aligned guidance with XML and HTML specifications to recommend against the use of angle brackets as part of an element name, but instead to only use angle brackets as part of a tag. | [Code in text](#code-in-text) |

<a id="whats-new--20240122"></a>

<a id="whats-new--january-22u002c-2024"></a>

#### January 22, 2024

| New guidance or change | Page |
| --- | --- |
| Cleaned up word list by removing entries that only provided [hyphenation](#hyphens), [spelling](https://developers.google.com/style/spelling), or [abbreviation](#abbreviations) guidance that followed directly from our general guidance. | [Word list](https://developers.google.com/style/style/word-list) |
| Consolidated and clarified guidance regarding alt text, figure captions, and figure descriptions. | [Diagrams, figures, and other images](#images)  [Write accessible documentation](#accessibility) |
| Added recommendation to avoid linking to other document sets from navigation controls such as a table of contents. | [Links to other sites](https://developers.google.com/style/links-external) |
| Clarified guidance about avoiding words such as *above* and *below* in references to documentation and user interfaces for accessibility reasons, and provided example of appropriate non-directional usage. | [Word list](#word-list--above) |
| Removed prohibition against hyphenation of the phrase *open source*, so this term now follows our general guidance for hyphenation, which allows for hyphenation of an adjectival phrase to add clarity and remove ambiguity. | [Word list](https://developers.google.com/style/word-list#open-source) |
| Changed guidance for indicating the omission of code from an instructional code snippet to recommend the use of an explanatory comment instead of a mere ellipsis. | [Code samples](#code-samples) |

<a id="whats-new--20231108"></a>

<a id="whats-new--november-8u002c-2023"></a>

#### November 8, 2023

| New guidance or change | Page |
| --- | --- |
| Changed guidance regarding run-in headings in description lists to recommend that the punctuation (such as a colon) is not formatted as bold. Making the punctuation bold caused the punctuation to seem to be part of the heading string, which caused confusion in cases such as UI labels. | [Lists](#lists--description-lists-that-use-run-in-headings) |
| Removed the recommendation to use a special *external* icon (indicated by `class="external"`) for links. Readers and writers have expressed confusion about the meaning and usage of this icon. We strengthened guidance about using other, explicit means to inform the reader about the destination and behavior of a link. | [Link text](https://developers.google.com/style/link-text#write-link-text) |

<a id="whats-new--20231024"></a>

<a id="whats-new--october-24u002c-2023"></a>

#### October 24, 2023

| New guidance or change | Page |
| --- | --- |
| Removed page about custom font styling, which only said to use styles defined in the style sheet for the website. Redirected link to page about HTML formatting and semantic tagging. | [HTML and semantic tagging](https://developers.google.com/style/fonts) |
| Added word-list entry for *then* and expanded entry for *if* to recommend the use of the optional helper word *then* in many cases in which it might be omitted in casual usage. | [Word list](#word-list--then) |
| Simplified and unified guidance for *jank* and *janky* to recommend that these terms only be used for specific graphics issues. | [Word list](#word-list--jank) |
| Strengthened guidance against the use of *and/or* except in cases where space is limited. | [Slashes](#slashes--and-or) |

<a id="whats-new--20230929"></a>

<a id="whats-new--september-29u002c-2023"></a>

#### September 29, 2023

| New guidance or change | Page |
| --- | --- |
| Added several examples of when and how to use quotation marks. | [Quotation marks](#quotation-marks) |
| Added explanation of guidance against anthropomorphism. | [Anthropomorphism](#anthropomorphism) |
| Added guidance about using a hyphen with the prefix *non* before hyphenated compounds. | [Hyphens](#hyphens) |

<a id="whats-new--20230824"></a>

<a id="whats-new--august-24u002c-2023"></a>

#### August 24, 2023

| New guidance or change | Page |
| --- | --- |
| Added link buttons to each entry in the word list to make deep-linking to individual entries easier. | [Word list](#word-list) |
| Extended guidance about example names to recommend using an initial to represent a person's surname. | [Example person surnames](#examples--example-person-surnames) |
| Clarified guidance about when to use present tense and when to use future tense. | [Present tense](#tense) |
| Extended link text guidance to include an example for `mailto` links. | [Link text](https://developers.google.com/style/link-text) |

<a id="whats-new--20230726"></a>

<a id="whats-new--july-26u002c-2023"></a>

#### July 26, 2023

| New guidance or change | Page |
| --- | --- |
| Added link to [Google API guidelines](https://google.aip.dev/192) for information about code comments. | [API reference code comments](#api-reference-comments) |
| Revised guidance for the word *toggle* to recommend against use as a verb. | [UI elements and interaction](#ui-elements--term-toggle) |
| Extended and clarified guidance for names for directories and files. | [Filenames and file types](#filenames) |
| Added explanation for why to use code format for code items. | [Code in text](#code-in-text) |

<a id="whats-new--20230615"></a>

<a id="whats-new--june-15u002c-2023"></a>

#### June 15, 2023

| New guidance or change | Page |
| --- | --- |
| Consolidated guidance about periods and end punctuation. Also removed standalone pages about exclamation points and about spacing after periods. | [Periods and other end punctuation](#periods) |
| Revised guidance about hyphens to suggest a lookup strategy, categorize uses, and note exceptions. | [Hyphens](#hyphens) |
| Created firmer guidance about punctuation in lists for run-in headings and at the end of list items. | [Lists](#lists) |
| Strengthened capitalization guidance: when *not* to use capitalization, and how to use capitalization with product names. | [Capitalization](#capitalization), [Product names](#product-names) |
| Added guidance about using end punctuation when documenting a command-line option or argument. | [Document command-line syntax](#code-syntax) |
| Improved description and examples for using first-person pronouns (*we*, *our*). | [Second person and first person](#person) |
| Updated word list entries: *etc.*, *OK*, *user*, *we*, *you* | [Word list](#word-list) |

<a id="whats-new--20230509"></a>

<a id="whats-new--may-9u002c-2023"></a>

#### May 9, 2023

| New guidance or change | Page |
| --- | --- |
| Softened guidance regarding the choice between the pronouns *who* and *that*. | [Pronouns](#pronouns) |
| Added *web interface* as an alternative to *console* and *UI* in general references to a browser-based interface. | [Word list](#word-list--ui) |
| Clarified the purpose of the page about phone number formats. | [Format phone numbers in text](#phone-numbers) |

<a id="whats-new--20230331"></a>

<a id="whats-new--march-31u002c-2023"></a>

#### March 31, 2023

| New guidance or change | Page |
| --- | --- |
| Expanded and clarified guidance about using trademarks only as modifiers. This guidance emphasizes that you should never modify a trademark, such as by creating a possessive or plural form. | [Use trademarks only as modifiers](#trademarks--use-trademarks-only-as-modifiers) |
| Strengthened guidance against shortening product names to anything other than an approved alternative name. | [Google product names](#product-names--shortening) |
| Expanded guidance about using ARIA labels in text that describes icons in graphical user interfaces. This improves accessibility and increases consistency in terminology used to refer to visual elements in text. | [Buttons and icons](#ui-elements--buttons), [Accessibility](#accessibility) |
| New word list entry: *toolkit* | [Word list](#word-list) |

<a id="whats-new--20230213"></a>

<a id="whats-new--february-13u002c-2023"></a>

#### February 13, 2023

| New guidance or change | Page |
| --- | --- |
| Added a page about paragraph structure, which provides guidance about recommended paragraph length and order of information. | [Paragraph structure](#paragraph-structure) |
| Expanded accessibility guidance to say that a document should convey its information when you use it without images or animation. | [Write accessible documentation](#accessibility) |
| Clarified that letter keys should be represented with uppercase letters. | [Press and type keyboard keys](#ui-elements--keyboard) |
| Added *existing* to list of examples of potentially problematic words in timeless documentation. | [Timeless documentation](#timeless-documentation) |
| Recommended using an empty `alt` attribute for icons that include a text label. | [Buttons and icons](#ui-elements--buttons) |
| Strengthened and clarified guidance about avoiding culturally specific references and about using simple and consistent language. | [Voice and tone](#tone) |
| Created section about items that are sometimes—but not always—formatted in code font, such as email addresses. | [Items that are sometimes in code font](#code-in-text--sometimes) |
| Added information about example internationalized domain names. | [Example domain names](#examples--domains) |
| Expanded guidance about choosing example email addresses. | [Example email addresses](#examples--addresses) |
| Expanded guidance about using second-person *you* to refer to the reader of a document and, generally, using third-person *user* to refer to the intended user of the software that the reader is developing. | [Second person](#person) |

<a id="whats-new--20221212"></a>

<a id="whats-new--december-12u002c-2022"></a>

#### December 12, 2022

| New guidance or change | Page |
| --- | --- |
| New word list entry: *anti-pattern* | [Word list](#word-list) |

<a id="whats-new--20221107"></a>

<a id="whats-new--november-7u002c-2022"></a>

#### November 7, 2022

| New guidance or change | Page |
| --- | --- |
| To emphasize a negative, use `<em>`not`</em>`. | [Contractions](#contractions) |

<a id="whats-new--20221031"></a>

<a id="whats-new--october-31u002c-2022"></a>

#### October 31, 2022

| New guidance or change | Page |
| --- | --- |
| New word list entry: *standalone* | [Word list](#word-list) |

<a id="whats-new--20221003"></a>

<a id="whats-new--october-10u002c-2022"></a>

#### October 10, 2022

| New guidance or change | Page |
| --- | --- |
| Added guidance about how to document optional arguments for commands.  Special characters that indicate optional and mutually exclusive arguments in commands—such as brackets, braces, and pipes—break commands if the user doesn't edit them first. The new guidance offers several approaches for avoiding these problems. | [Code in text](#code-in-text), [Code samples](#code-samples), [Document command-line syntax](#code-syntax) |
| Clarified that contractions are recommended in general, but not required in all cases. | [Contractions](#contractions) |

<a id="whats-new--20220926"></a>

<a id="whats-new--september-26u002c-2022"></a>

#### September 26, 2022

| New guidance or change | Page |
| --- | --- |
| In figure captions, always use end punctuation, and use complete sentences when possible. | [Figures and other images](#images) |
| Added separators between word list terms, to improve readability. | [Word list](#word-list) |

<a id="whats-new--20220919"></a>

<a id="whats-new--september-19u002c-2022"></a>

#### September 19, 2022

| New guidance or change | Page |
| --- | --- |
| Added guidance to multiple pages about ways to make documentation more inclusive for readers who have a variety of cognitive patterns. | [Write accessible documentation](#accessibility), [Cross-references](#cross-references), [Numbers](#numbers), [Procedures](#procedures) |

<a id="whats-new--20220912"></a>

<a id="whats-new--september-12u002c-2022"></a>

#### September 12, 2022

| New guidance or change | Page |
| --- | --- |
| Don't present new information in tables through images or symbols alone. | [Tables](#tables) |
| Clarified guidance about using footnotes in tables. | [Tables](#tables) |
| Added instructions for how to look up a UI element's `aria-label` attribute. | [UI elements and interaction](#ui-elements) |

<a id="whats-new--20220905"></a>

<a id="whats-new--september-5u002c-2022"></a>

#### September 5, 2022

| New guidance or change | Page |
| --- | --- |
| Strengthened recommendation to avoid using semicolons where possible, and removed basic information about semicolons.  Our [accessibility guidance](#accessibility) recommends against using semicolons where possible, because screen readers may not clearly indicate them. So we changed our semicolon guidance to be more in line with our accessibility guidance. | [Semicolons](#semicolons) |
| Expanded and clarified guidance about what to put in code font. | [Code in text](#code-in-text) |

<a id="whats-new--20220829"></a>

<a id="whats-new--august-29u002c-2022"></a>

#### August 29, 2022

| New guidance or change | Page |
| --- | --- |
| Changed and clarified recommended phrasing for describing boolean parameters in reference docs. | [API reference code comments](#api-reference-comments) |
| Expanded and clarified explanation of why we use straight quotation marks and apostrophes. | [Quotation marks](#quotation-marks) |
| Added suggested alternative terms for *cloud-native*. | [Word list](#word-list) |
| New word list entries: *prebuilt*, *scroll* | [Word list](#word-list) |

<a id="whats-new--20220822"></a>

<a id="whats-new--august-22u002c-2022"></a>

#### August 22, 2022

| New guidance or change | Page |
| --- | --- |
| Clarified that *and then* is generally better than just *then*. | [Write for a global audience](#translation) |
| New word list entries: *canary*, *multi-service*, *precapture*, *pre-existing*, *presubmit*, *rebranding*, *roll out* | [Word list](#word-list) |

<a id="whats-new--20220815"></a>

<a id="whats-new--august-15u002c-2022"></a>

#### August 15, 2022

| New guidance or change | Page |
| --- | --- |
| Expanded table-formatting guidance, to improve accessibility. | [Tables](#tables) |
| Improved guidance about figure captions, descriptions, and alt text. | [Figures and other images](#images) |

<a id="whats-new--20220808"></a>

<a id="whats-new--august-8u002c-2022"></a>

#### August 8, 2022

| New guidance or change | Page |
| --- | --- |
| Write *a SQL* rather than *an SQL*.  Both are in use, but *a SQL* is significantly more common. | [Articles (a, an, the)](#articles) |
| Added information about our distinction between *don't use* and *avoid*. | [Word list](#word-list) |
| New word list entries: *nonce*, *SQL* | [Word list](#word-list) |

<a id="whats-new--20220801"></a>

<a id="whats-new--august-1u002c-2022"></a>

#### August 1, 2022

| New guidance or change | Page |
| --- | --- |
| Expanded guidance about *mobile* and related terms. | [Word list](#word-list) |
| It's OK to use *below* in set phrases such as *below (the) average*. | [Word list](#word-list) |
| Expanded our information about serial commas. | [Commas](#commas) |
| To refer to a file with the `.tiff` extension, use the phrase *TIFF file*. | [Filenames and file types](#filenames) |
| New word list entries: *admin*; *blue-green*; *cold*, *hot*, and *warm* (in the context of a failover, spare, or standby); *inline*; *mobile phone*; *online* | [Word list](#word-list) |

<a id="whats-new--20220725"></a>

<a id="whats-new--july-25u002c-2022"></a>

#### July 25, 2022

| New guidance or change | Page |
| --- | --- |
| Updated guidance about the term *Cloud console*. | [Word list](#word-list) |
| Clarified guidance about the term *see*. | [Word list](#word-list) |

<a id="whats-new--20220718"></a>

<a id="whats-new--july-18u002c-2022"></a>

#### July 18, 2022

| New guidance or change | Page |
| --- | --- |
| Revised guidance about using the term *element* in HTML and XML contexts. | [Word list](#word-list) |
| Revised and expanded guidance about how to form possessives. | [Possessives](#possessives) |
| New word list entry: *tag* | [Word list](#word-list) |

<a id="whats-new--20220620"></a>

<a id="whats-new--june-20u002c-2022"></a>

#### June 20, 2022

| New guidance or change | Page |
| --- | --- |
| New word list entry: *brown bag* | [Word list](#word-list) |

<a id="whats-new--20220613"></a>

<a id="whats-new--june-13u002c-2022"></a>

#### June 13, 2022

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about placement of *only*. | [Write for a global audience](#translation) |
| New word list entry: *using* | [Word list](#word-list) |

<a id="whats-new--20220606"></a>

<a id="whats-new--june-6u002c-2022"></a>

#### June 6, 2022

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about *Interconnect connection*. | [Word list](#word-list) |

<a id="whats-new--20220516"></a>

<a id="whats-new--may-16u002c-2022"></a>

#### May 16, 2022

| New guidance or change | Page |
| --- | --- |
| Offset footnote symbols using superscript. | [Footnotes](#footnotes) |
| New word list entries: *could*, *would* | [Word list](#word-list) |

<a id="whats-new--20220509"></a>

<a id="whats-new--may-9u002c-2022"></a>

#### May 9, 2022

| New guidance or change | Page |
| --- | --- |
| Strengthened guidance recommending avoiding humor in documentation.  Most humor is difficult to translate, and much humor is culturally specific. | [Write for a global audience](#translation) |
| Changed the link to a resource about identity-first language.  The site that we had previously linked to has disappeared. | [Write inclusive documentation](#inclusive-documentation) |

<a id="whats-new--20220425"></a>

<a id="whats-new--april-25u002c-2022"></a>

#### April 25, 2022

| New guidance or change | Page |
| --- | --- |
| Added a new page about jargon. | [Jargon](#jargon) |
| Expanded guidance about when to use the various notice types. | [Notes, cautions, warnings, and other notices](#notices) |
| Clarified and expanded guidance about when to remove locales from URLs. | [Link to other sites](https://developers.google.com/style/links-external) |
| New word list entries: *final solution*, `gsutil` | [Word list](#word-list) |

<a id="whats-new--20220418"></a>

<a id="whats-new--april-18u002c-2022"></a>

#### April 18, 2022

| New guidance or change | Page |
| --- | --- |
| Introduce an interactive element (such as a button that expands and collapses) in the text preceding the element, to improve accessibility. | [Write accessible documentation](#accessibility) |

<a id="whats-new--20220411"></a>

<a id="whats-new--april-11u002c-2022"></a>

#### April 11, 2022

| New guidance or change | Page |
| --- | --- |
| Changed guidance about taking screenshots. | [Figures and other images](#images) |
| In code samples, indicate omitted code using three dots and no spaces (`...`) | [Code samples](#code-samples) |
| New word list entries: *+* (appended to numbers in text) | [Word list](#word-list) |

<a id="whats-new--20220404"></a>

<a id="whats-new--april-4u002c-2022"></a>

#### April 4, 2022

| New guidance or change | Page |
| --- | --- |
| Removed guidance about using lettered lists for mutually exclusive options.  The semantic distinction that we were making isn't in wide use, and lettered lists aren't supported in standard Markdown, so we no longer recommend using lettered lists. | [Lists](#lists) |
| Clarified recommendation about how to italicize in Markdown. | [Text-formatting summary](#text-formatting) |
| Changed guidance about *dead-letter queue* and *hold the pointer over*. | [Word list](#word-list) |
| New word list entry: *break-glass* | [Word list](#word-list--break-glass) |

<a id="whats-new--20220328"></a>

<a id="whats-new--march-28u002c-2022"></a>

#### March 28, 2022

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about using an introductory phrase before the output of a command. | [Document command-line syntax](#code-syntax) |
| New word list entry: *Unicode* | [Word list](#word-list--unicode) |

<a id="whats-new--20220221"></a>

<a id="whats-new--february-21u002c-2022"></a>

#### February 21, 2022

| New guidance or change | Page |
| --- | --- |
| Use `gcloud` *CLI* instead of `gcloud` *command-line tool*. | [Word list](#word-list) |
| New word list entry: *shift left* | [Word list](#word-list) |

<a id="whats-new--20220207"></a>

<a id="whats-new--february-7u002c-2022"></a>

#### February 7, 2022

| New guidance or change | Page |
| --- | --- |
| In general, don't use a single *x* or a series of *x*'s as placeholders; instead, use a more informative placeholder. | [Formatting placeholders](#placeholders) |
| New word list entry: *GBps* | [Word list](#word-list) |

<a id="whats-new--20220131"></a>

<a id="whats-new--january-31u002c-2022"></a>

#### January 31, 2022

| New guidance or change | Page |
| --- | --- |
| Avoid repeating the exact page title as a heading on the page. | [Headings and titles](#headings) |
| Expanded guidance about *runtime* and *run time*. | [Word list](#word-list) |
| Added *.adoc* and *.md* to the list of examples of filename extensions. | [Filenames and file types](#filenames--file-type-names) |

<a id="whats-new--20220124"></a>

<a id="whats-new--january-24u002c-2022"></a>

#### January 24, 2022

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about video formats.  The main reason to avoid using animated GIF is that it's resource-inefficient. | [Figures and other images](#images) |
| Clarified guidance about changing an existing custom anchor for a heading. | [Making headings into link targets](#headings-targets) |

<a id="whats-new--20220118"></a>

<a id="whats-new--january-18u002c-2022"></a>

#### January 18, 2022

| New guidance or change | Page |
| --- | --- |
| For animations and videos, use a compressed format (such as MP4), not animated GIF. | [Figures and other images](#images) |
| Don't use *email* as a verb. | [Word list](#word-list) |
| New word list entry: *healthcare* | [Word list](#word-list) |

<a id="whats-new--20211231"></a>

<a id="whats-new--december-31u002c-2021"></a>

#### December 31, 2021

| New guidance or change | Page |
| --- | --- |
| Added headings to make guidance about using simple and unambiguous language easier to find. | [Writing for a global audience](https://developers.google.com/style/translation#clear-language) |
| Expanded guidance about demonstrative pronouns. | [Ambiguous pronoun references](#pronouns--ambiguous-pronoun-references) |
| Clarified guidance about when to use code format for URLs. | [Code in text](#code-in-text) |
| Refreshed guidance about optimizing for search (SEO). | [Text for images](#images--text-associated-with-images),  [Link text](https://developers.google.com/style/link-text),  [Filenames](#filenames),  [Headings](#headings) |

<a id="whats-new--20211130"></a>

<a id="whats-new--november-30u002c-2021"></a>

#### November 30, 2021

| New guidance or change | Page |
| --- | --- |
| Added examples and clarified guidance recommending use of optional pronouns and other helper words. | [Optional pronouns](#pronouns--optional-pronouns),  [Writing for a global audience](https://developers.google.com/style/translation#write-short,-clear,-and-precise-sentences) |
| Added guidance for linking to a section of another page. | [Links to sections on another page](https://developers.google.com/style/cross-references#different-page) |
| New word list entries: *portal*, *copy and paste*, *performant* | [Word list](#word-list) |

<a id="whats-new--20211101"></a>

<a id="whats-new--november-1u002c-2021"></a>

#### November 1, 2021

| New guidance or change | Page |
| --- | --- |
| Added guidance about expanding shortened words and symbols. | [Abbreviations](#abbreviations--dont-use) |
| Expanded guidance about the order of information in complex procedures, including the recommended order for goals, results, and justifications for steps. | [Procedures](https://developers.google.com/style/procedures#order-of-information-in-complex-steps) |
| Added guidance about including a description of default behaviors in API reference documents. | [API reference code comments](#api-reference-comments--parameters) |
| Reinforced guidance about including words like *file* after items in code font, such as filenames. | [Filenames](#filenames) |
| Added guidance about using alternatives to directional terms such as *above* and *below* when referring to location in a document. | [Writing accessible documentation](#accessibility--document-rendering) |
| New word list entries: *practitioner*, *left-nav, right-nav*, *create new* | [Word list](#word-list) |

<a id="whats-new--20211011"></a>

<a id="whats-new--october-11u002c-2021"></a>

#### October 11, 2021

| New guidance or change | Page |
| --- | --- |
| Simplified placeholder examples and clarified when to repeat an explanation for a placeholder. | [Formatting placeholders](https://developers.google.com/style/placeholders#explaining-placeholders) |
| Added guidance on using brackets and dots (`[...]`) to indicate omitted output in an example. | [Output from commands](#code-syntax--output) |

<a id="whats-new--20211004"></a>

<a id="whats-new--october-4u002c-2021"></a>

#### October 4, 2021

| New guidance or change | Page |
| --- | --- |
| Added page about philosophy and principles of the style guide. | [Philosophy of this style guide](#philosophy) |
| Clarified recommendation to include a noun after a code element and to avoid inflecting code elements. | [Code in text](#code-in-text) |
| Added guidance to not use numbers in headings to indicate a sequence of sections. | [Headings and titles](#headings) |
| Updated examples for verb forms in headings and titles, including special cases such as *Pricing* and *Billing*. | [Headings and titles](#headings) |

<a id="whats-new--20210913"></a>

<a id="whats-new--september-13u002c-2021"></a>

#### September 13, 2021

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about specifying the context for a task. | [Procedures](#procedures) |
| Avoid using *run the following command* to introduce code. Instead, focus on what the command does. | [Procedures](#procedures) |
| Expanded the guidance for *CLI*. | [Word list](#word-list--cli) |
| New word list entries: *ransomware* | [Word list](#word-list) |

<a id="whats-new--20210906"></a>

<a id="whats-new--september-6u002c-2021"></a>

#### September 6, 2021

| New guidance or change | Page |
| --- | --- |
| Avoid words and phrases that anchor the documentation to a point in time or assume knowledge of prior or future products and features. | [Timeless documentation](#timeless-documentation) |
| Added *navigation menu* to the list of UI terms. | [UI elements and interaction](#ui-elements) |
| Marked *slice and dice* as *don't use*. | [Word list](#word-list--slice) |
| New word list entries: *web application firewall*, *while* | [Word list](#word-list) |

<a id="whats-new--20210830"></a>

<a id="whats-new--august-30u002c-2021"></a>

#### August 30, 2021

| New guidance or change | Page |
| --- | --- |
| Introduce a list of placeholders with the phrase *This output includes the following values:*  The old guidance for what introductory phrase to use wasn't a complete sentence. | [Formatting placeholders](#placeholders) |

<a id="whats-new--20210816"></a>

<a id="whats-new--august-16u002c-2021"></a>

#### August 16, 2021

| New guidance or change | Page |
| --- | --- |
| Added guidance for heading and title phrasing.  Many writers ask what verb forms to use in headings and titles. The new guidance helps writers make that decision more easily, and it improves consistency for translators and readers. | [Headings and titles](#headings) |

<a id="whats-new--20210802"></a>

<a id="whats-new--august-2u002c-2021"></a>

#### August 2, 2021

| New guidance or change | Page |
| --- | --- |
| When you need an example project name, create a name that's meaningful or descriptive. | [Example domains and names](#examples) |
| New word list entry: *pop-up* | [Word list](#word-list--pop-up) |

<a id="whats-new--20210726"></a>

<a id="whats-new--july-26u002c-2021"></a>

#### July 26, 2021

| New guidance or change | Page |
| --- | --- |
| New word list entry: *intercluster* | [Word list](#word-list--intercluster) |

<a id="whats-new--20210719"></a>

<a id="whats-new--july-19u002c-2021"></a>

#### July 19, 2021

| New guidance or change | Page |
| --- | --- |
| Added guidance about whether to include an abbreviation if it is used only once in the document. | [Abbreviations](#abbreviations) |
| Clarified and added guidance about the terms *above*, *below*, *earlier*, *higher*, *later*, *lower*, and *under* | [Word list](#word-list) |

<a id="whats-new--20210712"></a>

<a id="whats-new--july-12u002c-2021"></a>

#### July 12, 2021

| New guidance or change | Page |
| --- | --- |
| Don't refer to casing styles by names like *camel case* or *snake case*. | [Capitalization](#capitalization--special-capitalization-style-names) |

<a id="whats-new--20210705"></a>

<a id="whats-new--july-5u002c-2021"></a>

#### July 5, 2021

| New guidance or change | Page |
| --- | --- |
| In the first sentence of each procedural step, include an imperative verb. | [Procedures](#procedures) |

<a id="whats-new--20210628"></a>

<a id="whats-new--june-28u002c-2021"></a>

#### June 28, 2021

| New guidance or change | Page |
| --- | --- |
| New word list entries: *can*, *might*, *must*  A writer asked us to clarify our guidance for these terms. | [Word list](#word-list) |

<a id="whats-new--20210621"></a>

<a id="whats-new--june-21u002c-2021"></a>

#### June 21, 2021

| New guidance or change | Page |
| --- | --- |
| Updated guidance on fictitious person names, and added a list of specific given names to use in examples.  Many writers have asked for a list of recommended names to use. | [Example domains and names](#examples--names) |

<a id="whats-new--20210607"></a>

<a id="whats-new--june-7u002c-2021"></a>

#### June 7, 2021

| New guidance or change | Page |
| --- | --- |
| Don't use UI element labels as if they were English verbs or nouns. | [UI elements and interaction](#ui-elements--referring-to-ui) |

<a id="whats-new--20210524"></a>

<a id="whats-new--may-24u002c-2021"></a>

#### May 24, 2021

| New guidance or change | Page |
| --- | --- |
| Clarified phrasing of guidance about avoiding using the same link text for different target pages. | [Link text](https://developers.google.com/style/link-text) |
| Added guidance about what to do when link text includes a command or other code-font element. | [Link text](https://developers.google.com/style/link-text) |
| Try to keep the main subject and verb as close to the beginning of a sentence as possible. | [Writing for a global audience](#translation) |
| Updated guidance about using a hyphen to indicate a range of numbers.  For example, we now recommend using an ordinary hyphen rather than a nonbreaking hyphen, for ease of authoring. | [Hyphens](#hyphens) |
| Removed the word list entry for *AJAX*.  The entry was outdated, and Wikipedia covers the term better. | [Word list](#word-list) |
| New word list entries: *webmaster*, *white label*  Use more specific terms. | [Word list](#word-list) |

<a id="whats-new--20210503"></a>

<a id="whats-new--may-3u002c-2021"></a>

#### May 3, 2021

| New guidance or change | Page |
| --- | --- |
| Don't put a link in a heading.  A link in a heading is easy for a reader to miss. | [Headings and titles](https://developers.google.com/style/headings#formatting-a-heading-or-title) |
| Clarified and reorganized the material about which preposition to use with each UI element. | [UI elements and interaction](#ui-elements--prepositions) |

<a id="whats-new--20210426"></a>

<a id="whats-new--april-26u002c-2021"></a>

#### April 26, 2021

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about when to create a custom anchor for a heading. | [Making headings into link targets](#headings-targets) |

<a id="whats-new--20210419"></a>

<a id="whats-new--april-19u002c-2021"></a>

#### April 19, 2021

| New guidance or change | Page |
| --- | --- |
| Write one-step procedures with a bullet. | [Procedures](#procedures) |
| In headings, use punctuation sparingly. | [Headings and titles](#headings) |
| Added a link to another resource about active and passive voice. | [Active voice](#voice) |
| Clarified guidance about the word *native*. | [Word list](#word-list) |
| New entry: *sherpa* | [Word list](#word-list) |

<a id="whats-new--20210412"></a>

<a id="whats-new--april-12u002c-2021"></a>

#### April 12, 2021

| New guidance or change | Page |
| --- | --- |
| Clarified that guidance that applies to text generally also applies to headings. | [Headings and titles](#headings) |
| Strengthened recommendation to use contractions. | [Contractions](#contractions) |
| New entry: *downscope* | [Word list](#word-list) |

<a id="whats-new--20210405"></a>

<a id="whats-new--april-5u002c-2021"></a>

#### April 5, 2021

| New guidance or change | Page |
| --- | --- |
| Expanded guidance about using simple words and phrases. | [Writing for a global audience](#translation) |
| New entry: *instance group* | [Word list](#word-list) |

<a id="whats-new--20210329"></a>

<a id="whats-new--march-29u002c-2021"></a>

#### March 29, 2021

| New guidance or change | Page |
| --- | --- |
| To form the plural of an abbreviation, treat the abbreviation like an English word, and follow standard English pluralizing patterns. | [Abbreviations](#abbreviations) |

<a id="whats-new--20210315"></a>

<a id="whats-new--march-15u002c-2021"></a>

#### March 15, 2021

| New guidance or change | Page |
| --- | --- |
| New entries: more than 60 terms to not use or to use with caution, for inclusive-language reasons (too many to list here) | [Word list](#word-list) |

<a id="whats-new--20210308"></a>

<a id="whats-new--march-8u002c-2021"></a>

#### March 8, 2021

| New guidance or change | Page |
| --- | --- |
| Expanded and clarified guidance about placeholders. | [Formatting placeholders](#placeholders) |
| New entries: *outside the box* (and related terms), and more than 40 networking terms (too many to list here) | [Word list](#word-list) |

<a id="whats-new--20210301"></a>

<a id="whats-new--march-1u002c-2021"></a>

#### March 1, 2021

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about spelling out an abbreviation. | [Abbreviations](#abbreviations) |
| Use *documentation set* instead of *docset*. | [Word list](#word-list) |

<a id="whats-new--20210215"></a>

<a id="whats-new--february-15u002c-2021"></a>

#### February 15, 2021

| New guidance or change | Page |
| --- | --- |
| New entry: *lock-in* | [Word list](#word-list) |

<a id="whats-new--20210201"></a>

<a id="whats-new--february-1u002c-2021"></a>

#### February 1, 2021

| New guidance or change | Page |
| --- | --- |
| Revised and clarified guidance about using *should*. | [Word list](#word-list--should) |
| In some contexts, you can use *active*/*standby* as a replacement for *master*/*slave*. | [Word list](#word-list--slave) |
| Updated guidance about using *firewalls*. | [Word list](#word-list--firewalls) |
| New entries: *black-box*, *external IP address*, *gray-box*, *IPsec*, *N/A*, *war room*, *white-box* | [Word list](#word-list) |

<a id="whats-new--20210125"></a>

<a id="whats-new--january-25u002c-2021"></a>

#### January 25, 2021

| New guidance or change | Page |
| --- | --- |
| Updated guidance about link text to remove reliance on external sources. | [Link text](https://developers.google.com/style/link-text) |
| Don't use abbreviations or product names as verbs. | [Abbreviations](#abbreviations--verbs), [Product names](#product-names--product-names-as-verbs) |

<a id="whats-new--20210111"></a>

<a id="whats-new--january-11u002c-2021"></a>

#### January 11, 2021

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about indentation in code samples. | [Code samples](#code-samples) |
| Added links to more coding-style guides. | [Code in text](#code-in-text) |
| Clarified that you can use *please* under certain specific circumstances. | [Word list](#word-list--please) |
| Clarified guidance about *terminate*. | [Word list](#word-list--terminate) |
| New entries: *hang*, *MTU*, *utilize* | [Word list](#word-list) |

<a id="whats-new--20210104"></a>

<a id="whats-new--january-4u002c-2021"></a>

#### January 4, 2021

| New guidance or change | Page |
| --- | --- |
| Merged landing page with "Other editorial resources" to help new readers learn how to use this guide. | [About this guide](#style) |
| New entry: *deprecate* | [Word list](#word-list) |

<a id="whats-new--20201228"></a>

<a id="whats-new--december-28u002c-2020"></a>

#### December 28, 2020

| New guidance or change | Page |
| --- | --- |
| Added an explanation of what placeholders are. | [Formatting placeholders](#placeholders) |

<a id="whats-new--20201214"></a>

<a id="whats-new--december-14u002c-2020"></a>

#### December 14, 2020

| New guidance or change | Page |
| --- | --- |
| Distinguished between the Google Cloud product called Identity and Access Management (IAM) and the general practice of identity and access management. | [Word list](#word-list--iam) |
| Clarified that the word *terminate* has a specific meaning in telephony. | [Word list](#word-list--terminate) |

<a id="whats-new--20201207"></a>

<a id="whats-new--december-7u002c-2020"></a>

#### December 7, 2020

| New guidance or change | Page |
| --- | --- |
| When you describe navigating through menus using angle brackets, add an `aria-label` attribute to each angle bracket, for use by screen readers: `<span aria-label="and then">></span>`. | [UI elements and interaction](#ui-elements) |
| New entry: *metageneration* | [Word list](#word-list) |

<a id="whats-new--20201130"></a>

<a id="whats-new--november-30u002c-2020"></a>

#### November 30, 2020

| New guidance or change | Page |
| --- | --- |
| Updated content-navigation titles for some style guide pages. | Content navigation |
| Clarified guidance for *just*. | [Word list](#word-list) |
| New entry: *time to live* | [Word list](#word-list) |

<a id="whats-new--20201123"></a>

<a id="whats-new--november-23u002c-2020"></a>

#### November 23, 2020

| New guidance or change | Page |
| --- | --- |
| Changed guidance about fictitious email addresses. | [Example domains and names](#examples) |
| New entry: *holiday, the holidays* | [Word list](#word-list) |

<a id="whats-new--20201116"></a>

<a id="whats-new--november-16u002c-2020"></a>

#### November 16, 2020

| New guidance or change | Page |
| --- | --- |
| In examples, use fictional street addresses. | [Example domains and names](#examples) |
| Clarified guidance for *functionality*. | [Word list](#word-list) |

<a id="whats-new--20201109"></a>

<a id="whats-new--november-9u002c-2020"></a>

#### November 9, 2020

| New guidance or change | Page |
| --- | --- |
| Format folder and directory names in code font. | [Code in text](#code-in-text) |

<a id="whats-new--20201102"></a>

<a id="whats-new--november-2u002c-2020"></a>

#### November 2, 2020

| New guidance or change | Page |
| --- | --- |
| Avoid double negatives. | [Writing accessible documentation](#accessibility) |
| Expanded guidance about how to write around unavoidable references to non-inclusive words. | [Writing inclusive documentation](#inclusive-documentation) |

<a id="whats-new--20201019"></a>

<a id="whats-new--october-19u002c-2020"></a>

#### October 19, 2020

We're changing the format of the updates to this page, to focus on what each
change is rather than where it is.

| New guidance or change | Page |
| --- | --- |
| You can use an asterisk to indicate emphasis in Markdown. Don't use a double underscore to indicate bold in Markdown. | [Text-formatting summary](#text-formatting) |

<a id="whats-new--20201012"></a>

<a id="whats-new--october-12u002c-2020"></a>

#### October 12, 2020

| New guidance or change | Page |
| --- | --- |
| Use *enable* or *turn on* consistently. | [Word list](#word-list--enable) |
| All pages about linking are now grouped together under a new **Linking** heading. | Content navigation |
| Don't link to the same document multiple times in close succession. | [Cross-references](https://developers.google.com/style/cross-references#references-to-other-documents) |
| For subsections, use the phrase *in the following sections*. | [Headings and titles](https://developers.google.com/style/headings#referring-to-subsections) |
| Don't create your own abbreviations. | [Abbreviations](#abbreviations--creating-abbreviations) |
| Don't reveal personally identifiable information. | [Example domains and names](#examples) |
| For exponents, use standard mathematical notation. | [Numbers](#numbers--exponents) |
| Expanded guidance about expressing times of day. | [Dates and times](#dates-times--expressing-times) |
| New entries: *aka*, *America*, *-aware*, *Black Friday*, *Cyber Monday*, *leverage*, *possible*, *postmortem* | [Word list](#word-list) |

<a id="whats-new--20201005"></a>

<a id="whats-new--october-5u002c-2020"></a>

#### October 5, 2020

- In the [word list](#word-list), updated guidance about
  the term *disable*.

<a id="whats-new--20200928"></a>

<a id="whats-new--september-28u002c-2020"></a>

#### September 28, 2020

- On the [Capitalization](#capitalization) page, expanded
  guidance about using consistent capitalization.
- On the [Procedures](#procedures) page, added guidance
  about including keyboard shortcuts in procedures.

<a id="whats-new--20200921"></a>

<a id="whats-new--september-21u002c-2020"></a>

#### September 21, 2020

- On the [Figures and other images](#images) page, added
  guidance about using image maps.
- On the [Text-formatting summary](#text-formatting)
  page, added guidance about using a variable to indicate a range of version
  numbers, and clarified guidance about using `<em>`.
- Added entries to the [word list](#word-list):
  *distributed denial-of-service (DDoS)*, *UTF*.

<a id="whats-new--20200914"></a>

<a id="whats-new--september-14u002c-2020"></a>

#### September 14, 2020

- On the [Figures and other images](#images) page and the
  [Tables](#tables) page, added guidance about introductory
  sentences.
- In the [word list](#word-list), clarified the
  distinction between terms to never use and terms to avoid when possible. Also
  added icons for both kinds of terms.

<a id="whats-new--20200907"></a>

<a id="whats-new--september-7u002c-2020"></a>

#### September 7, 2020

- On the [Writing for a global audience](#translation)
  page, clarified guidance about using simple verbs.
- Added entries to the [word list](#word-list):
  *single pane of glass*, *will*.

<a id="whats-new--20200831"></a>

<a id="whats-new--august-31u002c-2020"></a>

#### August 31, 2020

- On the [Figures and other images](#images)
  page, clarified guidance about using SVG.

<a id="whats-new--20200824"></a>

<a id="whats-new--august-24u002c-2020"></a>

#### August 24, 2020

- Added an entry to the [word list](#word-list):
  *see*.

<a id="whats-new--20200810"></a>

<a id="whats-new--august-10u002c-2020"></a>

#### August 10, 2020

- On the [UI elements and interaction](#ui-elements)
  page, added guidance about when to use *in* and when to use *on*.
- On the [Making headings into link
  targets](#headings-targets) page, added guidance about changing anchors, and reorganized the
  page.

<a id="whats-new--20200803"></a>

<a id="whats-new--august-3u002c-2020"></a>

#### August 3, 2020

- On the [Dates and times](#dates-times) page, added
  guidance about avoiding referring to seasons of the year.
- In the [word list](#word-list), added more suggested
  alternatives for *master* and *slave*.

<a id="whats-new--20200727"></a>

<a id="whats-new--july-27u002c-2020"></a>

#### July 27, 2020

- Added entries to the [word list](#word-list):
  *grandfathered*, *graylist*, *greylist*, *multi-regional*,
  *Unix epoch time*. Expanded and clarified guidance for the
  *blacklist*, *master*, and *multi-region* entries.

<a id="whats-new--20200720"></a>

<a id="whats-new--july-20u002c-2020"></a>

#### July 20, 2020

- Reorganized and updated the [Other editorial
  resources](https://developers.google.com/style/resources) page, and moved that page to near the top of the left nav.
- On the [Figures and other images](#images) page, added
  links to Web Content Accessibility Guidelines (WCAG) resources.
- On the [Procedures](#procedures) page, added guidance
  about introducing a procedure with an imperative.
- Added entries to the [word list](#word-list):
  *bar*, *baz*, *canceled*, *foo*, *like*, *such
  as*.
- As of this week, we've stopped including small-detail changes in this
  page. For example, when we corrected a typo in the style guide in the past, we
  used to mention that correction on this page, but we're no longer mentioning
  minor changes that have no effect on guidance.

<a id="whats-new--20200713"></a>

<a id="whats-new--july-13u002c-2020"></a>

#### July 13, 2020

- Renamed this summary-of-recent-changes page from "Release notes" to
  "What's new," and moved it to near the top of the left nav.
- In the [Pronouns](#pronouns) page, slightly updated the
  guidance about using gender-neutral *they*.

<a id="whats-new--20200629"></a>

<a id="whats-new--june-29u002c-2020"></a>

#### June 29, 2020

- On several pages, reorganized guidance about formatting code and
  command lines. In particular:
  - Moved the guidance that was in a page about command-line terminology
    to the [Documenting command-line syntax](#code-syntax) page,
    and deleted the separate command-line terminology page.
  - Moved the guidance about placeholders to a new [Formatting placeholders](#placeholders) page.
  - Added cross-references among various code-related pages.
- In the [word list](#word-list), corrected a typo.

<a id="whats-new--20200622"></a>

<a id="whats-new--june-22u002c-2020"></a>

#### June 22, 2020

- In the [word list](#word-list), changed guidance about
  using *earlier* and *later* for a range of version numbers.

<a id="whats-new--20200615"></a>

<a id="whats-new--june-15u002c-2020"></a>

#### June 15, 2020

- On the [Capitalization](#capitalization) page and other
  pages, made guidance consistent about capitalizing references to document
  titles.
- On the [Cross-references](#cross-references) page and
  other pages, added guidance about not forcing a link to open in a new tab.
- On the [Code in text](#code-in-text) page, added
  guidance about when to put UI elements in code font.
- Added an entry to the [word list](#word-list): *best
  effort*.

<a id="whats-new--20200608"></a>

<a id="whats-new--june-8u002c-2020"></a>

#### June 8, 2020

- On the [Writing inclusive
  documentation](#inclusive-documentation) page, added guidance about avoiding figurative language that
  relates to the slaughter of animals.

<a id="whats-new--20200601"></a>

<a id="whats-new--june-1u002c-2020"></a>

#### June 1, 2020

- On the [Figures and other images](#images) page,
  updated guidance about alt text, figure descriptions, and figure captions.
- Reorganized the [HTML and semantic
  tagging](#semantic-tagging) page, and added guidance about not using the [`br`
  element](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-br-element) to change visual presentation. Also replaced a broken link to a
  third-party site.
- On the [Numbers](#numbers) page, added guidance about
  avoiding using Roman numerals.
- Added entries to the [word list](#word-list):
  *currently*, *dash*, *NoOps*.

<a id="whats-new--20200525"></a>

<a id="whats-new--may-25u002c-2020"></a>

#### May 25, 2020

- On the [Numbers](#numbers) page, corrected two examples
  to match our guidance.
- On the [Abbreviations](#abbreviations) page, added
  guidance about use of the term *acronym*.
- Added entries to the [word list](#word-list):
  *happiness*, *scale*, *service level agreement*, *service level
  indicator*, *service level objective*. Also clarified guidance for
  *app*.

<a id="whats-new--20200518"></a>

<a id="whats-new--may-18u002c-2020"></a>

#### May 18, 2020

- On the [Filenames and file types](#filenames) page,
  added guidance about how to refer to a filename.
- On the [Headings and titles](#headings) page, updated
  the guidance about using code font in headings.
- On the [UI elements and interaction](#ui-elements) page
  and elsewhere, replaced the term *arrow notation* with *angle
  bracket*.
- On the [Procedures](#procedures) page, clarified the
  guidance about stating the location of an action before stating the action.
- Added entries to the [word list](#word-list):
  *config*, *extract*, *unarchive*, *uncompress*,
  *untar*. Also changed the guidance about *ssh* and related terms.
  Also corrected a typo.

<a id="whats-new--20200511"></a>

<a id="whats-new--may-11u002c-2020"></a>

#### May 11, 2020

- Major change: On the [Code in text](#code-in-text)
  page, changed guidance for placeholder styling. The new preferred style is
  all-uppercase with underscore delimiters.
- Also on the [Code in text](#code-in-text) page,
  corrected guidance about how to mark up placeholders with Markdown.
- On the [Figures and other images](#images) page,
  corrected a typo.

<a id="whats-new--20200504"></a>

<a id="whats-new--may-4u002c-2020"></a>

#### May 4, 2020

- On the [Second person and first person](#person) page,
  clarified guidance about when to use implicit *you*.
- On the [UI elements and interaction](#ui-elements)
  page, added guidance about *toggle*.
- Added entries to the [word list](#word-list):
  *dashboard*, *master*. Unrelatedly, fixed a longstanding word list
  typo.

<a id="whats-new--20200427"></a>

<a id="whats-new--april-27u002c-2020"></a>

#### April 27, 2020

- On the [Documenting command-line syntax](#code-syntax)
  page, added guidance about showing the output of commands.
- On the [Example domains and names](#examples) page,
  added example IPv6 addresses.
- On the [Words as words](https://developers.google.com/style/words-as-words) page,
  clarified guidance.
- In the [word list](#word-list), clarified guidance for
  the word *following*. Also clarified guidance for the various
  *console* terms.
- Added an entry to the [word list](#word-list):
  *native*.

<a id="whats-new--20200420"></a>

<a id="whats-new--april-20u002c-2020"></a>

#### April 20, 2020

- On the [Units of measurement](#units-of-measure) page,
  added guidance about using *per* when referring to rates.
- On the [UI elements and interaction](#ui-elements)
  page, clarified the distinction between text input and keyboard shortcuts, and
  added guidance about when to use the `code` and
  `kbd` elements. On the [Code in
  text](#code-in-text) page, added text input to the list of things to put in code font.
- On the [Accessible content](#accessibility) page, added
  a recommendation to use a screen reader to test your documentation. Also added
  guidance about introducing tables.
- On the [Example domains and names](#examples) page,
  changed the recommended example company names to avoid camel case.
- On the [Code in text](#code-in-text) page and the [Colons](#colons) page, clarified and expanded guidance about how
  to format a colon after text that's bold or in code font.
- Added entries to the [word list](#word-list):
  *key*, *key ring*, *per*, *vice versa*.

<a id="whats-new--20200413"></a>

<a id="whats-new--april-13u002c-2020"></a>

#### April 13, 2020

- On the [Lists](#lists) page, expanded the guidance
  about when not to use sentence-ending punctuation.
- Added cross-references between the [Abbreviations](#abbreviations) page and the [Headings and titles](#headings) page.
- On the [Numbers](#numbers) page, clarified the
  guidance about hyphens and en dashes in ranges of numbers.
- On the [Units of measure](#units-of-measure) page,
  clarified guidance about what counts as a unit.
- In the [word list](#word-list), clarified guidance
  about using *blacklist* and *whitelist*.
- Added entries to the [word list](#word-list):
  *ad tech*, *easily*, *fintech*, *NLU*, *quick*,
  *quickly*.

<a id="whats-new--20200406"></a>

<a id="whats-new--april-6u002c-2020"></a>

#### April 6, 2020

- On the [Abbreviations](#abbreviations) page, clarified
  guidance about using abbreviations in headings and titles.
- On the [Text-formatting summary](#text-formatting)
  page, added guidance on formatting mathematical variables.
- On the [Link text](https://developers.google.com/style/link-text) page, added guidance
  about abbreviations in link text.
- On the [Dates and times](#dates-times) page, added
  guidance about how to express time zones.
- In the [word list](#word-list), clarified guidance
  about *key-value pair*.
- Added an entry to the [word list](#word-list):
  *personally identifiable information (PII)*.

<a id="whats-new--20200330"></a>

<a id="whats-new--march-30u002c-2020"></a>

#### March 30, 2020

- On the [Hyphens](#hyphens) page, clarified guidance
  about ranges of numbers.
- In the [UI elements and interaction](#ui-elements)
  page, changed guidance for formatting input for text boxes to recommend using
  the HTML `code` element instead of the
  `kbd` element.

<a id="whats-new--20200323"></a>

<a id="whats-new--march-23u002c-2020"></a>

#### March 23, 2020

- On the [Capitalization](#capitalization) page, made the
  following changes:
  - Removed outdated guidance about capitalization after a run-in heading.
    For the current guidance, see "Description lists that use run-in headings" on
    the [Lists](#lists) page.
  - Clarified guidance about avoiding all-uppercase and camel case.
  - Clarified guidance about avoiding lowercase at the start of a
    sentence.
  - Clarified guidance about capitalization when referring to documents by
    title in various contexts.
- Expanded and reorganized the [Code in
  text](#code-in-text) page. In particular:
  - Expanded the guidance about documenting placeholders.
  - Expanded the list of items to put in code font.
- On the [Commas](#commas) page, added guidance about
  using a comma with *because*.
- On the [Dashes](#dashes) page, added guidance about not
  using en dashes.
- Added entries to the [word list](#word-list):
  *datastore*, *tutorial*. Also added guidance (in the entry for
  *documentation*) about phrases like *in this document*.

<a id="whats-new--20200302"></a>

<a id="whats-new--march-2u002c-2020"></a>

#### March 2, 2020

- On the [Capitalization](#capitalization) page, added
  guidance about using sentence case for labels and callouts.
- On the [Cross-references](#cross-references) page,
  added guidance about how to format the titles of web series.
- Added an entry to the [word list](#word-list): *web
  server*.

<a id="whats-new--20200224"></a>

<a id="whats-new--february-24u002c-2020"></a>

#### February 24, 2020

- On the [Resources](https://developers.google.com/style/resources) page, added links to the
  Kubernetes glossary and the Kubernetes style guide.
- On the [Lists](#lists) page, added guidance about how
  and when to use a bulleted list with run-in headings.
- Updated the [word list](#word-list) to refer to
  *Google Cloud* instead of *GCP*, in accord with a recent name change.
  In particular, changed entries for *GCP*, *GCP Console*, and *GCP
  project ID* to *Google Cloud*, *Google Cloud Console*, and
  *Google Cloud project ID*, respectively.
- Added an entry to the [word list](#word-list): *GKE
  node*. Also updated guidance for *GKE*.
- In the left nav, moved the word list and the product-names page to near
  the top.
- On the [Plurals in parentheses](https://developers.google.com/style/plurals-parentheses)
  page, added guidance about using the phrase *one or more*.

<a id="whats-new--20200113"></a>

<a id="whats-new--january-13u002c-2020"></a>

#### January 13, 2020

- In the [Writing for a global audience](#translation)
  page, fixed a broken link.
- In the [Code in text](#code-in-text) page, added
  *environment variable names* to the list of items to put in code font.
- Added entries to the [word list](#word-list):
  *A/B testing*, *BGP*.

<a id="whats-new--20200106"></a>

<a id="whats-new--january-6u002c-2020"></a>

#### January 6, 2020

- Added entries to the [word list](#word-list):
  *DevOps*, *ECMP*, *GFE*, *NoSQL*, *PostgreSQL*. Also
  updated guidance on *virtual machine (VM) instance*.

<a id="whats-new--20191223"></a>

<a id="whats-new--december-23u002c-2019"></a>

#### December 23, 2019

- Expanded and clarified the [Writing for a
  global audience](#translation) page.
- Renamed the "Typographical conventions" page to "[Text-formatting summary](#text-formatting)."
- On the [Tables](#tables) page, clarified guidance
  about punctuation in table column heads.
- On the [Filenames and file types](#filenames) page,
  added *.jar* to the list of filename extensions.
- On the [UI elements](#ui-elements) page and the word
  list, clarified guidance about when to use *box* and *field* to refer
  to text boxes.

<a id="whats-new--20191216"></a>

<a id="whats-new--december-16u002c-2019"></a>

#### December 16, 2019

- On the [Abbreviations](#abbreviations) page, expanded
  guidance about when to spell out abbreviations.
- On the [conventions page](https://developers.google.com/style/typographical-conventions),
  fixed two broken links.
- Added entries to the [word list](#word-list):
  *as*, *big-endian*, *google.dev*, *little-endian*.

<a id="whats-new--20191209"></a>

<a id="whats-new--december-9u002c-2019"></a>

#### December 9, 2019

- On the [Tables](#tables) page, added guidance about
  sorting tables, and clarified guidance about when to use tables.
- Reverted last week's changes about using *earlier* and
  *later* instead of *lower* and *higher*; those changes need
  further refining.

<a id="whats-new--20191202"></a>

<a id="whats-new--december-2u002c-2019"></a>

#### December 2, 2019

- On the [Cross-references](#cross-references)
  page, added guidance about using the word *about* in cross-references,
  rather than *on*.
- Added entries to the [word list](#word-list): *about
  versus on*, *for instance*, *SLA*. Also changed guidance about
  using *earlier* and *later* for a range of version numbers.

<a id="whats-new--20191125"></a>

<a id="whats-new--november-25u002c-2019"></a>

#### November 25, 2019

- On the [UI elements and interaction](#ui-elements)
  page, added guidance about focusing on the task rather than on UI elements as
  such.
- On various pages, added cross-references linking to other pages.

<a id="whats-new--20191118"></a>

<a id="whats-new--november-18u002c-2019"></a>

#### November 18, 2019

- Added a new [Typographic
  conventions](https://developers.google.com/style/typographical-conventions) page.
- Reorganized the [Units of
  measurement](#units-of-measure) page. Also added guidance about Kelvin temperatures.
- On the [Cross-references](#cross-references) page,
  clarified guidance about cross-references that aren't links.
- On the [UI elements and interaction](#ui-elements)
  page, added information about expander arrows.
- Added a term to the [word list](#word-list):
  *slice and dice*.

<a id="whats-new--20191111"></a>

<a id="whats-new--november-11u002c-2019"></a>

#### November 11, 2019

- On the [Figures and other images](#images) page,
  clarified guidance about figure descriptions.
- On the [Units of measurement](#units-of-measure) page,
  added guidance about ranges of numbers.
- On the [Product names](#product-names) page, clarified
  guidance about using full trademarked product names.
- Added terms to the [word list](#word-list):
  *billing charges*, *port*, *repo*, *UI*.

<a id="whats-new--20191028"></a>

<a id="whats-new--october-28u002c-2019"></a>

#### October 28, 2019

- Added guidance about what to do if there's [more than one way to complete a
  task](#procedures--same-task).
- Added terms to the [word list](#word-list):
  *just*, *multi-tenancy*.

<a id="whats-new--20191021"></a>

<a id="whats-new--october-21u002c-2019"></a>

#### October 21, 2019

- Added a page about [formatting
  words as words](https://developers.google.com/style/formatting-words-as-words).
- Added a page about [formatting key
  terms](https://developers.google.com/style/formatting-key-terms).
- Changed the guidance about how to capitalize a [UI element](#ui-elements) name when the label is
  all-uppercase in the UI.
- Added guidance about [explaining
  placeholders](https://developers.google.com/style/code-in-text#explain-placeholders).
- Updated the list of [items to put in
  code font](#code-in-text--code).
- Clarified the guidance about using official [capitalization](#capitalization) for names of products.
- Changed the title of the [style guide landing
  page](#style).
- Deleted the page about URLs in links, and moved the material that was on
  that page to the [cross-references](#cross-references)
  page. Also added some examples to that page.
- Removed unnecessary explanations of the icons that indicate that a
  guideline applies only in Android documentation or only in Google Cloud Platform
  documentation.
- Added examples to the [footnotes](#footnotes)
  page.
- Improved a link on the [Accessible
  content](#accessibility) page.
- Added terms to the [word list](#word-list):
  *BMaaS*, *US*.

<a id="whats-new--20191008"></a>

<a id="whats-new--october-8u002c-2019"></a>

#### October 8, 2019

- Reorganized the page about [notices](#notices), and
  added examples.
- Cleaned up some minor formatting and phrasing issues in the [word list](#word-list).
- Corrected a typo on the [Accessible
  content](#accessibility) page.
- Changed the title of the style guide to use sentence case.

<a id="whats-new--20190930"></a>

<a id="whats-new--september-30u002c-2019"></a>

#### September 30, 2019

- Added a term to the [word list](#word-list):
  *PoP*.

<a id="whats-new--20190923"></a>

<a id="whats-new--september-23u002c-2019"></a>

#### September 23, 2019

- Added a page about [footnotes](#footnotes).
- Reorganized the [Other editorial resources](https://developers.google.com/style/resources)
  page.

<a id="whats-new--20190916"></a>

<a id="whats-new--september-16u002c-2019"></a>

#### September 16, 2019

- Added a page about [using material from
  other sources](#other-sources).
- Added guidance about [using
  *a* and *an* with product names](#product-names--shortening).
- Removed contradictory guidance about quotation marks with [link text](https://developers.google.com/style/link-text).
- Clarified guidance about [periods
  with abbreviations](#abbreviations--periods).
- Clarified guidance about [capitalization
  following a colon](#capitalization).
- Moved the list of UI-related verbs from the UI elements page to the [word list](#word-list).
- Also added other terms to the [word list](#word-list):
  *cons*, *Gbps*, *Kbps*, *Mbps*, *pros*. Also updated
  the entry for *service*.

<a id="whats-new--20190624"></a>

<a id="whats-new--june-24u002c-2019"></a>

#### June 24, 2019

- Added guidance about US currency to the [Numbers](#numbers) page.

<a id="whats-new--20190617"></a>

<a id="whats-new--june-17u002c-2019"></a>

#### June 17, 2019

- Added further guidance about accessibility to the [Accessible content](#accessibility) page and other related
  pages.
- Added guidance about graphically violent terms to the [Writing inclusive documentation](#inclusive-documentation)
  page.
- Added guidance about the term *wheelchair-bound* to the [Writing inclusive documentation](#inclusive-documentation)
  page.
- Added guidance about currency to the [Units of measure](#units-of-measure) page.
- Added an example showing how to [use
  Markdown to mark up images](#images).
- Added terms to the [word list](#word-list):
  *disclosure triangle*, *hamburger menu*, *kebab menu*,
  *outpost*, *STONITH*. Also expanded guidance about *should*.

<a id="whats-new--20190520"></a>

<a id="whats-new--may-20u002c-2019"></a>

#### May 20, 2019

- Added a new page about [avoiding excessive claims](#excessive-claims).
- Added material about file types to the [Filenames and file types](#filenames) page.
- Added terms to the [word list](#word-list): *CSV*,
  *traditional*, *YAML*.

<a id="whats-new--20190429"></a>

<a id="whats-new--april-29u002c-2019"></a>

#### April 29, 2019

- Replaced the guidelines on the [Accessible content](#accessibility) page with a new set of more
  relevant guidelines.
- Added a term to the [word list](#word-list):
  *execute*.
- Added material about Linux signals on the [Command-line terminology](https://developers.google.com/style/command-line-terminology) page, and
  updated related entries in the word list.

<a id="whats-new--20190422"></a>

<a id="whats-new--april-22u002c-2019"></a>

#### April 22, 2019

- Added a term to the [word list](#word-list):
  *method*. Also added to the guidance for *Cloud*.

<a id="whats-new--20190415"></a>

<a id="whats-new--april-15u002c-2019"></a>

#### April 15, 2019

- Added more guidance about digit-group separators on the [Numbers](#numbers) page.
- Fixed a broken link on the [Numbers](#numbers)
  page, and another on the [Writing for a global
  audience](#translation) page.
- Updated guidance about example names on the [Example domains and names](#examples) page.
- Added guidance about removing personally identifying information from
  screenshots on the [Figures and other images](#images)
  page.
- Added guidance about using code font for names of command-line utilities
  on the [Code in text](#code-in-text) page.
- Added guidance about short and long versions of words like *app* and
  *demo* on the [Abbreviations](#abbreviations) page.

<a id="whats-new--20190304"></a>

<a id="whats-new--march-4u002c-2019"></a>

#### March 4, 2019

- Clarified guidance about person-first and identity-first language on the
  [Writing inclusive documentation](#inclusive-documentation)
  page.
- Added guidance about passive voice on the [Active voice](#voice) page.
- Added more guidance about links on the [Linking to other sites](https://developers.google.com/style/links-external) page.
- Added terms to the [word list](#word-list):
  *guru*, *spin up*. Also revised the guidance for *Container
  Engine*.

<a id="whats-new--20190225"></a>

<a id="whats-new--february-25u002c-2019"></a>

#### February 25, 2019

- Added extensive new material to the [inclusive documentation](#inclusive-documentation) page.
- Updated the [word list](#word-list):
  - Clarified guidance for *argument* and *flag*.
  - Added terms: *allows you to*, *desire*, *drop-down*,
    *wish*.
  - Removed the recommendations against using *enable* and
    *disable*, and clarified guidance for those terms.

<a id="whats-new--20190204"></a>

<a id="whats-new--february-4u002c-2019"></a>

#### February 4, 2019

- Added terms to the [word list](#word-list):
  *add-in*, *add-on*.
- Added guidelines about avoiding [repetitive procedures](#procedures--repetitive-procedures).

<a id="whats-new--20190128"></a>

<a id="whats-new--january-28u002c-2019"></a>

#### January 28, 2019

- Updated the [word list](#word-list):
  - Changed guidance for *above* and *below*.
  - Added terms: *gcloud*, *ML*.
  - Updated guidance for *&*.
  - Improved alphabetization.
- Fixed a broken link in the [Lists](#lists) page.

<a id="whats-new--20190114"></a>

<a id="whats-new--january-14u002c-2019"></a>

#### January 14, 2019

- Added terms to the [word list](#word-list):
  *comprise*, *console*, *fail over*, *GCP Console*, *Google
  Cloud Platform Console*, *populate*, *surface*.
- Reorganized the [UI elements](#ui-elements) page,
  and added guidance and examples.
- Added Markdown information to the [URLs for
  images](https://developers.google.com/style/img-elements) page.
- Clarified guidance about end punctuation for lists on the [Periods](#periods) page.
- Clarified guidance about nonbreaking spaces in the [Units of measurement](#units-of-measure) page.

<a id="whats-new--20181203"></a>

<a id="whats-new--december-3u002c-2018"></a>

#### December 3, 2018

- Added a term to the [word list](#word-list):
  *lifetime*.
- Elaborated on our guidance in the [Closed compounds and prefixes](https://developers.google.com/style/word-list#compounds) section of
  the word list.
- Added a new page about [command-line terminology](https://developers.google.com/style/command-line-terminology) for gcloud
  and Linux.
- Added a section on [straight and
  curly quotation marks](#quotation-marks--straight-and-curly-quotation-marks) to the Quotation marks page.
- Added guidance about avoiding overuse of bolding to the [Procedures](#procedures) page.
- Added guidance about the phrases *hold the pointer over* and
  *point to* to the [UI elements and
  interaction](#ui-elements) page.

<a id="whats-new--20181029"></a>

<a id="whats-new--october-29u002c-2018"></a>

#### October 29, 2018

- Added terms to the [word list](#word-list):
  *blacklist*, *whitelist*.
- Reorganized the [dates and times](#dates-times) page,
  and added guidance about times and about ISO 8601.

<a id="whats-new--20181008"></a>

<a id="whats-new--october-8u002c-2018"></a>

#### October 8, 2018

- Added recommendations for [example company names](#examples--example-company-names).
- Added guidance about using monospace formatting to the [UI elements and interaction](#ui-elements) page.
- Added guidance about giving the location of an action in a procedure
  to the [Procedures](#procedures) page.

<a id="whats-new--20180918"></a>

<a id="whats-new--september-18u002c-2018"></a>

#### September 18, 2018

- Added terms to the [word list](#word-list): *GKE*,
  *POJO*.

<a id="whats-new--20180904"></a>

<a id="whats-new--september-4u002c-2018"></a>

#### September 4, 2018

- Added guidance about cases where [filenames aren't under your
  control](#filenames--other-exceptions).
- Added a term to the [word list](#word-list):
  *big data*.

<a id="whats-new--20180813"></a>

<a id="whats-new--august-13u002c-2018"></a>

#### August 13, 2018

- Added guidance about [avoiding internet slang](#abbreviations--dont-use).
- Added terms to the [word list](#word-list):
  *multi-cloud*, *RTFM*, *tl;dr*, *ymmv*.

<a id="whats-new--20180730"></a>

<a id="whats-new--july-30u002c-2018"></a>

#### July 30, 2018

- Added terms to the [word list](#word-list):
  *disaster recovery*, *file system*, *high availability*,
  *high performance computing*, *OS*, *tarball*, *tar
  file*.
- Updated guidance in the word list for *on-premises*.
- Rephrased a paragraph of the [landing page](#style).

<a id="whats-new--20180625"></a>

<a id="whats-new--june-25u002c-2018"></a>

#### June 25, 2018

- Added terms to the [word list](#word-list):
  *IP*, *SAP*.

<a id="whats-new--20180619"></a>

<a id="whats-new--june-19u002c-2018"></a>

#### June 19, 2018

- Added a term to the [word list](#word-list):
  *trojan*.
- Improved the organization, formatting, and phrasing of the [filenames page](https://developers.google.com/style/file-names).

<a id="whats-new--20180612"></a>

<a id="whats-new--june-12u002c-2018"></a>

#### June 12, 2018

- Added terms to the [word list](#word-list):
  *appendix*, *index*, *matrix*.

<a id="whats-new--20180521"></a>

<a id="whats-new--may-21u002c-2018"></a>

#### May 21, 2018

- Changed the guidance about [how to link to Android
  reference documentation](#code-in-text--linking-api-terms-in-android).
- Added information about [using *the* with
  product names](https://developers.google.com/style/product-names#using-the-with-product-names).
- Added a note about indefinite and casual numbers to the [Numbers](#numbers) page.
- Fixed a broken link on the [authorial tone](#tone)
  page.

<a id="whats-new--20180514"></a>

<a id="whats-new--may-14u002c-2018"></a>

#### May 14, 2018

- Added terms to the [word list](#word-list):
  *multi-cluster*, *via*. Clarified guidance on *firewalls*.

<a id="whats-new--20180402"></a>

<a id="whats-new--april-2u002c-2018"></a>

#### April 2, 2018

- Added a page about [writing inclusive documentation](#inclusive-documentation).
- Added terms to the [word list](#word-list):
  *at scale*, *IAM*, *RFC*.

<a id="whats-new--20180326"></a>

<a id="whats-new--march-26u002c-2018"></a>

#### March 26, 2018

- Added information about [`alt` text for
  decorative images](#images--text-associated-with-images) to the images page.
- Added terms to the [word list](#word-list):
  *fill in*, *fill out*, *microservices*.

<a id="whats-new--20180226"></a>

<a id="whats-new--february-26u002c-2018"></a>

#### February 26, 2018

- Added a term to the [word list](#word-list):
  *ad hoc*.

<a id="whats-new--20180212"></a>

<a id="whats-new--february-12u002c-2018"></a>

#### February 12, 2018

- Added terms to the [word list](#word-list):
  *Cloud*, *Container Engine*, *ephemeral external IP address*,
  *firewalls*, *GCP*, *GCP project ID*, *internal IP
  address*, *NAT*, *network IP address*, *non-key*,
  *on-premises*, *persistent disk*, *project*, *RDP*,
  *static external IP address*, *subnet*, *table name*,
  *textbox*, *turn on*.
- Added information about closed compounds and prefixes to the [word list](https://developers.google.com/style/word-list#compounds).

<a id="whats-new--20180129"></a>

<a id="whats-new--january-29u002c-2018"></a>

#### January 29, 2018

- Added terms to the [word list](#word-list):
  *alpha*, *autohealing*, *autoscaling*, *autotagging*,
  *bare metal*, *beta*, *CLI*, *Cloud SDK*, *colocate*,
  *CPU*, *curated roles*, *data center campus*, *data
  cleaning*, *data source*, *ETL*, *IaaS*, *impact*,
  *ingest*, *k8s*, *key pair*, *PaaS*, *preemptible*,
  *regex*, *SaaS*, *screenshot*, *sign-in*, *sign into*,
  *sign-out*, *sub-command*, *v*, *virtual machine
  instance*.
- Added a section on placeholder variables to the [code in text](https://developers.google.com/style/code-in-text#placeholder-variables) page.

<a id="whats-new--20180108"></a>

<a id="whats-new--january-8u002c-2018"></a>

#### January 8, 2018

- Added terms to the [word list](#word-list):
  *argument*, *backup*, *dataflow*, *flag*, *higher*,
  *later*, *long press*, *multi-region*, *option*,
  *slave*, *touch & hold*, *transpile*, *wildcard*.
- Added an item (DNS record types) to the list of [items to put
  in code font](#code-in-text--some-specific-items-to-put-in-code-font).

<a id="whats-new--20171211"></a>

<a id="whats-new--december-11u002c-2017"></a>

#### December 11, 2017

- Added material on [numerical
  dimensions](#numbers--dimensions).
- Added material about [possessives of
  company and product names](https://developers.google.com/style/possessives#company--and-product-name-possessives).
- Added terms to the [word list](#word-list):
  *docset*, *documentation*, *startup*, *sync*.

<a id="whats-new--20171113"></a>

<a id="whats-new--november-13u002c-2017"></a>

#### November 13, 2017

- Changed guidelines on [end punctuation for
  list items](#lists--capitalization-and-end-punctuation).
- Added alphabetical headings to the [word
  list](#word-list), so you can now jump to a specific letter using the in-page TOC.
- Updated [word list](#word-list) entries for
  *error-prone*, *real time*, and *Search*.
- Added terms to the [word list](#word-list):
  *dataset*, *legacy*, *nonfatal*.

<a id="whats-new--20171023"></a>

<a id="whats-new--october-23u002c-2017"></a>

#### October 23, 2017

- Added a new page about [plurals in
  parentheses](https://developers.google.com/style/plurals-parentheses).
- Added a link to the C++ coding style guide, in the [Code style guides](#code-samples--coding) section.

<a id="whats-new--20170904"></a>

<a id="whats-new--september-4u002c-2017"></a>

#### September 4, 2017

- Added several more terms to the [word list](#word-list):
  *check*, *checkbox*, *clear*, *deselect*, *open
  source*, *select*, *target*, *uncheck*, *Unix-like*,
  *unselect*.
- Added material to the [Trademarks](#trademarks) page
  about using trademarks as adjectives. Also added links to a couple of other
  trademark-related pages from Google.
- Removed Android-specific material from the [Headings](#headings) page, to bring Android doc guidelines more
  into line with non-Android guidelines. Also, added notes about things not to
  include in headings.
- Removed Android label from material on the [Tables](#tables) page, to make that material also apply to
  non-Android docs.
- Added mention of degrees and percents to the [Units of measurement](#units-of-measure) page.

<a id="whats-new--20170828"></a>

<a id="whats-new--august-28u002c-2017"></a>

#### August 28, 2017

- Added 160+ terms to the [word list](#word-list). (Too
  many to list here.)
- Added recommendations for image size and placement to the [Images](#images) page.
- Moved material about Javadoc links to the [Code in text](#code-in-text) page.

<a id="whats-new--20170821"></a>

<a id="whats-new--august-21u002c-2017"></a>

#### August 21, 2017

- Added new [File names](https://developers.google.com/style/file-names) page.
- Added new [Units of measurement](#units-of-measure)
  page.
- Changed "[internet](#word-list--internet)" to
  lowercase.
- Added material about line lengths and Javadoc-style links to the [HTML formatting](#html-formatting) page.

<a id="whats-new--20170731"></a>

<a id="whats-new--july-31u002c-2017"></a>

#### July 31, 2017

- Added new [Headings and titles](#headings) page, mostly
  focused on Android documentation.
- Added information about [tables in Android docs](https://developers.google.com/style/tables#a-few-more-notes-about-tables) to
  the Tables page.

<a id="whats-new--20170710"></a>

<a id="whats-new--july-10u002c-2017"></a>

#### July 10, 2017

- Added words to the [word list](#word-list): *deep
  linking*, *jank*, *wake lock*.

<a id="whats-new--20170608"></a>

<a id="whats-new--june-8u002c-2017"></a>

#### June 8, 2017

- Public release.

---

<a id="philosophy"></a>

### Philosophy of this guide

*Source: <https://developers.google.com/style/philosophy>*

This document discusses some of the principles and philosophy behind this
style guide.

<a id="philosophy--purpose"></a>

<a id="philosophy--intended-purpose"></a>

#### Intended purpose

This style guide codifies and records our style decisions and describes our
house style. The guide doesn't claim to be objectively correct.

This guide is *not* intended to do the following:

- Provide an industry documentation standard.
- Compete with other well-known style guides.
- Replace another style guide that you already follow.
- Provide a complete set of basic writing guidelines.
- Provide legal advice. For legal advice, consult a lawyer.

> [!NOTE]
> **Note**: Two disclaimers:
> - The guidance in this style guide doesn't limit the changes that Google can
>   make to its documentation.
> - If you don't read a given guideline, then you are still responsible for
>   behaving ethically and lawfully with regard to documentation.

<a id="philosophy--reasons-for-guidelines"></a>

<a id="philosophy--explanation-of-reasons-for-guidelines"></a>

#### Explanation of reasons for guidelines

We generally don't explain the reasoning behind most of our guidelines. We
have a couple of reasons for that:

- Many of our decisions are driven by accessibility, localization,
  globalization, and ease of understanding. Giving those reasons as explanations
  everywhere they apply would be repetitive.
- Often, a given guideline is one good option among several; in those cases,
  we sometimes just chose one option for consistency.
- Too much explanation can clutter up a page. Readers most often want a
  brief answer to a specific question, rather than a detailed explanation.

That said, we recognize that it's sometimes useful to know why we made a
given choice, so we've started to include occasional explanations in the [What's new](#whats-new) page.

---

## Key resources

<a id="word-list"></a>

### Word list

*Source: <https://developers.google.com/style/word-list>*

> [!NOTE]
> **Note**: This document includes references to potentially disrespectful
> or offensive terms. These terms are listed here to provide usage
> guidance and alternative terms.

<a id="word-list--overview"></a>

This word list covers style and usage guidelines that are specific to developer documentation.

If the term that you're looking for isn't on this list, check our other
[editorial resources](#style--editorial-resources), including our preferred
dictionary,
[Merriam-Webster](https://www.merriam-webster.com/). If there are multiple spellings in
the Merriam-Webster word entry, use the first form listed, which is the most common spelling. For
example, in the
[entry for *cancel*](https://www.merriam-webster.com/dictionary/canceled),
the first form listed for the past tense is *canceled*, indicating that it's more common than
*cancelled*.

If you're looking for a technical definition, then it's often a good idea to check the
authoritative documentation on the topic.

Terminology decisions, including how and when to define or contextualize
terms, often require judgments based on factors like your product area,
your audience, and prevailing convention. Here are some other pages of this
guide that can help you make those types of judgments:

- [Jargon](#jargon)
- [Inclusive language](#inclusive-documentation)
- [Write for a global audience](#translation)
- [Hyphens](#hyphens)
- [Capitalization](#capitalization)

As always, it's fine to deviate from our guidance if that serves your readers
better. For more information, see [Break the rules](#style--rules).

<a id="word-list--word-list"></a>

#### Word list

All word list entries have a link
icon next to them. To link directly to an entry, you can right-click and
copy the link address, or click and copy the URL from your address bar.

Some word list entries include guidance to *avoid* or *don't use* a
term. Apply this guidance as follows:

- **Use with caution**. A recommendation to avoid using the term *when
  possible*, or to use the term with caution. The term might be ambiguous
  or obscure, so we provide alternative term suggestions or suggest that you
  use a more specific term. However, you can use the term if needed. Where
  appropriate, define the term or use it only once, as explained on the
  [Jargon](#jargon) page.
- **Don't use**. In all cases, we prefer to *not use the term*. The
  term might be particularly ambiguous or it might have an offensive or
  non-inclusive association. If such a term appears in code, we recommend that
  you
  [replace or write around the term](#inclusive-documentation--replace-or-write-around-non-inclusive-terms).
- **Android**. Applies only to Android documentation.
- **Google Cloud**. Applies only to Google Cloud documentation.
- **Google Workspace**. Applies only to Google Workspace documentation.

<a id="word-list--letter-number"></a>

##### Numbers and Symbols

<a id="word-list--u002b"></a>

**+**
    OK to use *+* with numbers in text, such as *customer records with
    300+ demographic attributes*, except in formal contexts.
<a id="word-list--ampersand"></a>

**Avoid: & (ampersand)**
    Don't use *&* instead of *and* in headings, text, navigation, or
    tables of contents.
    It's OK to use *&* when referencing UI elements that use *&*, or
    in table headings and diagram labels where space constraints require
    abbreviation.
    It's OK to use `&` for technical purposes in code.
<a id="word-list--2-step-verification"></a>

**2-Step Verification**
    When referring to Google's
    [2-Step Verification](https://www.google.com/landing/2step/),
    use initial caps.
    When referring to
    [generic 2-step verification](http://searchsecurity.techtarget.com/definition/two-step-verification),
    use lowercase.

<a id="word-list--letter-a"></a>

##### A

<a id="word-list--a-an"></a>

**a and an**
    Use *a* when the next word starts with a consonant *sound*,
    regardless of what letter it starts with. For more information, see [Articles (a, an, the)](#articles).
<a id="word-list--ab"></a>

**A/B testing**
    Capitalize and use slash notation for *A/B*.
<a id="word-list--abnormal"></a>

**Avoid: abnormal**
    Don't use to refer to a person.
    OK to use to refer to a condition of a computer system.
<a id="word-list--abort"></a>

**Avoid: abort**
    Avoid in general usage. Instead, use words like *stop*, *exit*,
    *cancel*, or *end*. In Linux, *abort* refers to a type of
    signal that terminates an abnormal process.
<a id="word-list--about-on"></a>

**about versus on**
    When a cross-reference includes information that describes what the
    cross-reference links to, use *about* instead of *on*.
    Recommended: For more information
    about indexes, see [Managing indexes](https://cloud.google.com/firestore/docs/query-data/indexing).
    Not recommended: For more information
    on indexes, see [Managing
    indexes](https://cloud.google.com/firestore/docs/query-data/indexing).
<a id="word-list--above"></a>

**Avoid: above**
    Don't use for a range of version numbers. Instead, use
    [*later*](#word-list--later).
    Don't use to refer to a position in a document. Instead, use
    *earlier* or *preceding*.
    Don't use to refer to a position in the UI. Instead, write instructions
    that avoid directional language. For more information,
    see [Writing accessible documentation](#accessibility).
    It's OK to use *above* in a non-directional way, such as when describing a hierarchy.
<a id="word-list--access"></a>

**Avoid: access (verb)**
    Avoid when you can. Instead, use friendlier words like *see*,
    *edit*, *find*, *use*, or *view*.
<a id="word-list--access-token"></a>

**access token**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--account-name"></a>

**Don't use: account name**
    Don't use. Instead, use [*username*](https://developers.google.com/style/word-list#username).
<a id="word-list--actionable"></a>

**Avoid: actionable**
    Avoid unless it's the clearest and simplest phrasing for your audience.
    Instead, leave it out or replace it with a phrase like *that you can act
    on* or *useful*.
    Don't use *actionable* in the legal sense without consulting a
    lawyer.
<a id="word-list--action-bar"></a>

**Don't use: (Android) action bar**
    In Android documentation, don't use. Instead, use
    [*app bar*](#word-list--app-bar).
<a id="word-list--ad-tech"></a>

**ad tech**
    Write out on first mention: *advertising technology (ad tech)*.
    Don't use *adtech* or *ad-tech*.
<a id="word-list--address-bar"></a>

**address bar**
    Use to refer to the URL bar or the combined URL bar and search box in a
    browser.
    Don't use *omnibox*.
<a id="word-list--ad-hoc"></a>

**ad hoc**
    OK to use in database and analytics contexts to mean "free-form" or
    "user-written" (for example, *ad hoc queries* or *an ad hoc
    chart*). For other contexts, try to find a more specific English
    equivalent.
    Don't hyphenate or italicize the term.
<a id="word-list--admin"></a>

**Don't use: admin**
    Write out *administrator* unless it's the name of a UI label or other
    element.
    It's OK to use *admin* in Android
    documentation.
<a id="word-list--administrator"></a>

**Don't use: (Android) administrator**
    In Android documentation, don't use. Instead, use *admin*.
<a id="word-list--advertised-route-priority"></a>

**advertised route priority**
    OK to also use *base advertised route priority* when discussing
    region-to-region costs.
    Don't shorten or use variations of these terms.
<a id="word-list--agnostic"></a>

**Don't use: agnostic**
    Don't use. Instead, use a more precise term like
    *platform-independent*.
<a id="word-list--ai"></a>

**AI**
    In general, you can use *AI* without spelling out *artificial intelligence*.
    Most readers are familiar with the abbreviation *AI*. If you think your audience isn't
    familiar with the term, spell it out on first use.
<a id="word-list--aka"></a>

**Don't use: aka**
    Don't use. Instead, write out *also known as*, or present an
    alternative term using parentheses or the word *or*. You can also
    write out a definition.
    Recommended:
    Geographic data, also known as geospatial data, is ...
    Recommended: Geographic data
    (geospatial data) is ...
    Recommended: Geographic data, or
    geospatial data, is ...
<a id="word-list--all-apps-screen"></a>

**(Android) all apps screen**
    In Android documentation: Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--allowlist"></a>

**Don't use: allowlist (verb), allowlisted, allowlisting**
    Don't use as a verb. Instead, rewrite to improve clarity.
    OK to use *allowlist* as a noun.
    For more information, see [blacklist](#word-list--blacklist).
<a id="word-list--allows-you-to"></a>

**Don't use: allows you to**
    Don't use. Instead, use *lets you*. For more information, see [enable](#word-list--enable).
<a id="word-list--alpha"></a>

**alpha**
    Lowercase except when part of a product name.
    Recommended: PRODUCT_NAME
    Alpha
    Recommended: PRODUCT_NAME
    is in alpha.
<a id="word-list--america"></a>

**Avoid: America, American**
    Use only to refer to the *Americas* or the *American continent*.
    Don't use to refer to the United States. Instead, use a more precise term
    like *the US* or *the United States*, and *people in the
    US*. For more information, see [US](#word-list--us).
<a id="word-list--among"></a>

**among**
    See [between versus among](#word-list--between).
<a id="word-list--am-pm"></a>

**AM, PM**
    To be consistent with [Material Design](https://material.io/design/communication/data-formats.html#date-and-time),
    use all caps, no periods, and a space before.
    Recommended: 9:00 AM
    Recommended: 10:30 PM
<a id="word-list--and-or"></a>

**Avoid: and/or**
    Don't use unless space is limited, such as in a table. For more
    information, see [Slashes](#slashes--and-or).
<a id="word-list--android"></a>

**(Android) Android**
    When referring to the operating system, capitalize *Android*.
<a id="word-list--android-powered"></a>

**(Android) Android-powered device**
    Not *Android device*.
<a id="word-list--and-so-on"></a>

**Avoid: and so on**
    Avoid using *and so on* whenever possible. For more information,
    see [etc.](#word-list--etc)
<a id="word-list--anti"></a>

**anti***
    See [guidance about hyphens with prefixes](#hyphens--prefixes).
<a id="word-list--anti-pattern"></a>

**Avoid: anti-pattern**
    Avoid using *anti-pattern*, particularly as a standalone heading.
    Instead, consider using a more specific and broadly understood term.
    Recommended: Avoid these five SQL
    errors.
    Recommended: Avoid these five
    programming practices that make SQL queries inefficient.
    Not recommended: Avoid these five SQL
    anti-patterns.
<a id="word-list--api"></a>

**API**
    Use *API* to refer to either a web API or a language-specific API.
    Don't use *API* when referring to a method or a class. For example,
    don't write *This resource has one API* to mean "This resource has
    one method."
<a id="word-list--api-console"></a>

**Don't use: API Console, APIs console, developer console, dev console, or Google API Console**
    Don't use. Instead, refer to the *Google APIs Explorer* or to the
    *Google Cloud console*. For more information, see
    [console](#word-list--console).
<a id="word-list--api-console-key"></a>

**API Console key**
    In most contexts, use *API key* instead of *API Console key*.
    In Apps admin APIs, it's OK to use *API Console key* to distinguish
    from other API keys.
<a id="word-list--api-key"></a>

**API key**
    Not *developer key* or *dev key*.
<a id="word-list--apis-explorer"></a>

**APIs Explorer**
    Not *API explorer* or other variants.
<a id="word-list--app"></a>

**app**
    In general, use *app* instead of *application* when referring to
    programs for end users, especially in the context of mobile or web
    software.
    In some contexts, such as enterprise software, it's OK to use
    *application* to convey a sense of greater complexity.
    Use *application* in standard phrases such as *application
    programming interface*.
<a id="word-list--app-bar"></a>

**(Android) app bar**
    In Android contexts, formerly *action bar*.
<a id="word-list--appendix"></a>

**appendix**
    Use the plural *appendixes*, not *appendices*.
<a id="word-list--application"></a>

**application**
    See [app](#word-list--app).
<a id="word-list--as"></a>

**as**
    If you mean *because*, then use *because* instead of
    *as*. *As* is ambiguous; it can refer to the passage of time.
    *Because* refers to causation or the reason for something.
<a id="word-list--as-of-this-writing"></a>

**Avoid: as of this writing**
    Avoid because this phrase is implied. The phrase can also prematurely
    disclose product or feature strategy or inappropriately imply that a
    product or feature might change.
    See also [currently](#word-list--currently) and [presently](#word-list--presently).
    Recommended: BigQuery doesn't support
    that function.
    Not recommended: As of this writing,
    BigQuery doesn't support that function.
    For more information, see [Timeless
    documentation](#timeless-documentation).
<a id="word-list--authentication-and-authorization"></a>

**authentication and authorization**
    In general, use the word *authenticated* only to refer to users,
    and use *authorized* only to refer to requests that are sent by a
    client app on behalf of an authenticated user.

    A user *authenticates* their identity by entering their password
    (or giving some other proof of identity). The *authenticated
    user* then *authorizes* the client app to send an
    *authorized request* to the server on the user's behalf.
    When you want to use a preposition with *authenticate*, use
    *against*.
<a id="word-list--authn-authz"></a>

**Don't use: authN, authZ**
    Don't use. Instead, use *authentication* or *authorization*.
<a id="word-list--auto"></a>

**auto***
    See [guidance about hyphens with prefixes](#hyphens--prefixes).
<a id="word-list--autohealing"></a>

**autohealing**
    Not *auto-healing*.
<a id="word-list--auto-mode-vpc"></a>

**auto mode VPC network**
    Not *auto mode network*.
<a id="word-list--autopopulate"></a>

**autopopulate**
    Not *auto populate* or *auto-populate*.
<a id="word-list--autoscaling"></a>

**autoscaling**
    Not *auto-scaling*.
<a id="word-list--autotagging"></a>

**autotagging**
    Not *auto-tagging*.
<a id="word-list--autoupdate"></a>

**Don't use: autoupdate**
    Don't use. Instead, use *automatically update*.
<a id="word-list--aware"></a>

**Avoid: -aware**
    Avoid using as a compound modifier, as in *healthcare-aware*.
    OK to use when it's part of a product name, such as *Identity-Aware
    Proxy*.

<a id="word-list--letter-b"></a>

##### B

<a id="word-list--backend"></a>

**backend**
    Not *back-end* or *back end*.
<a id="word-list--bar"></a>

**Avoid: bar**
    Avoid when possible. For more information, see [foo](#word-list--foo).
<a id="word-list--bare-metal"></a>

**bare metal**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
    Hyphenate when used as a compound modifier, such as *bare-metal
    server*.
<a id="word-list--base64"></a>

**base64**
    Lowercase except at the beginning of a sentence,
    heading, or list item. Otherwise, capitalize *Base64* only if it's part of a
    formal name.
    Write *base64* in code font *only* if it's a string literal or
    otherwise quoted from code.
<a id="word-list--baz"></a>

**Avoid: baz**
    Avoid when possible. For more information, see [foo](#word-list--foo).
<a id="word-list--below"></a>

**Avoid: below**
    Don't use for a range of version numbers. Instead, use
    [*earlier*](#word-list--earlier).
    Don't use to refer to a position in a document. Instead, use *later*
    or *following*.
    Don't use to refer to a position in the UI. Instead, write instructions
    that avoid directional language. For more information, see
    [Writing accessible documentation](#accessibility).
    It's OK to use *below* in set phrases such as *below (the)
    average*, *below the mean*, *below zero*.
    It's OK to use *below* in a non-directional way, such as when describing a hierarchy.
<a id="word-list--best-effort"></a>

**Avoid: best effort**
    Avoid where possible. Instead, use more specific wording. After providing
    a description, you can add a phrase like "sometimes referred to as *best
    effort*."
<a id="word-list--beta"></a>

**beta**
    Lowercase except when part of a product name.
    Recommended: PRODUCT_NAME
    Beta
    Recommended: PRODUCT_NAME
    is currently in beta.
<a id="word-list--between"></a>

**between versus among**
    It's fine to use *between* when talking about more than two things;
    however, *between* isn't interchangeable with *among*.
    Use *between* when you're talking about two or more distinct
    things:
    Recommended: JavaScript introduces
    dependencies between the DOM, the CSSOM, and JavaScript execution.
    Use *among* when you're talking about things that are part of a group
    or things that aren't distinct:
    Recommended: ... a conventional SQL
    database that can be shared among multiple apps.
    More examples:
    Recommended: Because screen
    dimensions vary widely among devices (for example, between phones and
    tablets, and even among different phones), you should configure the
    viewport so that your pages render correctly on many different devices.
    Not recommended: Because screen
    dimensions vary widely between devices (for example, between phones and
    tablets, and even between different phones), you should configure the
    viewport so that your pages render correctly on many different devices.
    Recommended: You can share services
    among multiple clients.
    Not recommended: You can share
    services between multiple clients.
    See also [Grammar Girl's
    discussion of *between* and *among*](http://www.quickanddirtytips.com/education/grammar/between-versus-among).
<a id="word-list--big-endian"></a>

**big-endian**
    Hyphenate. Lowercase except at the beginning of a sentence,
    heading, or list item.
    Recommended: The codebase assumes
    big-endian byte ordering.
    Not recommended: The codebase assumes
    Big Endian byte ordering.
    Not recommended: The codebase assumes
    Big-endian byte ordering.
    Not recommended: The codebase assumes big
    endian byte ordering.
<a id="word-list--billing-charges"></a>

**Avoid: billing charges**
    Don't use *billing charges* to mean charges that appear on a bill.
    Instead, use *billed charges*.
    Use *billing charges* to describe the cost of creating the bill.
<a id="word-list--black-box"></a>

**Avoid: black-box**
    Avoid using *black-box*, *blackbox*, or *black box* to
    describe monitoring and testing. Consider using a more precise term for
    clarity.

    - For monitoring, use *synthetic monitoring*.
    - For testing, use *opaque-box testing*.
<a id="word-list--black-friday"></a>

**Avoid: Black Friday**
    Avoid unless explicitly referring to an event in the US. Instead use
    *peak scale event*.
<a id="word-list--blackhat"></a>

**Don't use: blackhat, black hat, black-hat**
    Don't use. Instead, use precise terms for the kind of violation or
    practice, such as *illegal*, *unethical*, or *in violation of
    rules*.
<a id="word-list--blackhole"></a>

**Don't use: blackhole (verb), blackholed (adjective)**
    Don't use. Instead, use a more descriptive term or phrase, such as
    *dropped without notification*.
<a id="word-list--blacklist"></a>

**Don't use: blacklist, black list, black-list**
    Don't use *blacklist*, *whitelist*, and *graylist*.
    Instead, use more precise terms that are appropriate for your domain.
    - For the noun *blacklist*, consider using a replacement such as
      *denylist*, *excludelist*, or *blocklist*.
    - For the noun *whitelist*, consider using a replacement such as
      *allowlist*, *trustlist*, or *safelist*.
    - For the noun *graylist* (*greylist*), consider using a
      replacement such as *provisional list*.
    In all of these cases, consider that there might not actually be a list
    involved. When replacing problematic terms, be sure to be technically
    accurate for the specific context.
    For the verb forms of these words, a simple word-for-word replacement
    typically isn't the best solution. Instead, replace verbs such as
    *blacklisted* with phrases that accurately convey the relevant
    action. For example:
    Recommended: To deny requests from
    an IP address, add it to the `dos.yaml` file.
    Not recommended: To denylist an IP
    address, add it to the `dos.yaml` file.
    Don't use: To blacklist an IP
    address, add it to the `dos.yaml` file.
    If the command or code that you're documenting uses one of these words,
    then use the words only in direct reference to the code items
    ([formatted as code](#code-in-text)), and make it clear
    what you're referring to.
    Recommended: Add a user to the
    allowlist (`whitelist`) by entering the following:
    `whitelist adduser EMAIL_ADDRESS`.
    Not recommended: Add a user to the
    whitelist by entering the following: `whitelist adduser
    EMAIL_ADDRESS`.
    For more information, see the
    [inclusive documentation](#inclusive-documentation) page.
<a id="word-list--blacklisted"></a>

**Don't use: blacklisted, black listed, black-listed**
    Don't use. See [blacklist](#word-list--blacklist).
<a id="word-list--blacklisting"></a>

**Don't use: blacklisting, black listing, black-listing**
    Don't use. See [blacklist](#word-list--blacklist).
<a id="word-list--blast-radius"></a>

**Don't use: blast radius**
    Don't use. Instead, use a more precise term like *affected area* or
    *spatial impact*.
<a id="word-list--blind"></a>

**Avoid: blind**
    Avoid using *blind to* or *blind eye to*. Instead, use more
    precise terms like *ignore*, *unaware of*, *disregard*,
    *avoid*, or *reject*.
    Avoid using *blind writes*. Instead, use a more precise phrase, such
    as *a write operation without a read operation*.
    Avoid using *blind change* or *change blindly*. Instead, use a
    more precise phrase such as *change without first confirming the
    value*.
    When referring to people, use terms like *person who is blind*,
    *screen reader user* (if applicable), *person who is visually
    impaired*, *person who is low-vision*, *magnification user*
    (if applicable).
<a id="word-list--blue-green"></a>

**blue-green**
    Not *blue/green* or *blue green*.
<a id="word-list--boolean"></a>

**boolean**
    In most contexts, *boolean* refers to a specific data type in a
    specific programming language. In such cases, use code font and the exact
    spelling and capitalization of the programming keyword.
    When referring to the abstract data type, use lowercase.
    If you refer to *Boolean mathematics* or *Boolean logic*, use
    uppercase.
<a id="word-list--branding-information"></a>

**branding information**
    In the Google Cloud console, the phrase *branding information* refers
    to the information that Google shows to users when the client asks them to
    authorize access: specifically, the project's name and logo, and the
    developer's Google Account. This information is set in the **Consent
    screen** page.
<a id="word-list--break-glass"></a>

**Don't use: break-glass**
    Don't use. Instead, use a more precise term depending on context:

    - To describe a general emergency or procedure that grants emergency
      access, use *emergency access*.
    - To describe a fallback procedure, use *manual fallback* or
      *preplanned procedure*.
<a id="word-list--brown-bag"></a>

**Don't use: brown bag, brown-bag**
    Don't use. Instead, use a more precise term like *learning session*,
    *lunch and learn*, *lunchtime learning session*,
    *casual training*, or *informal training*.
<a id="word-list--build-cop"></a>

**Don't use: build cop, build sheriff**
    Don't use. Instead, use a more precise term like *build monitor*.
<a id="word-list--button"></a>

**button**
    In a UI, a link isn't the same as a button; don't use the term
    *button* to refer to a link.
    Use *button* to refer to mechanical buttons (like the volume control
    buttons on the side of a phone) and capacitive touch buttons on a phone
    (like the Home button). You *press* mechanical buttons, and
    *tap* capacitive and on-screen buttons.

<a id="word-list--letter-c"></a>

##### C

<a id="word-list--can"></a>

**can**
    Use *can* in the following ways:

    - To convey permission or ability (for example, "You can access the
      server").
    - To refer to an optional action (for example, "You can also view
      logs with the Log Viewer").
    - To describe a possible outcome (for example, "The process can
      take 30 minutes").
    See also [could](#word-list--could), [may](#word-list--may),
    [might](#word-list--might), [must](#word-list--must),
    [should](#word-list--should), and [would](#word-list--would).
    For information about clarifying who's performing an action, see
    [Active voice](#voice).
<a id="word-list--canary"></a>

**Avoid: canary**
    Don't use *canary* as a verb, and don't use *canarying*.
    When possible, avoid [jargon](#jargon) like *canary* and
    *canary testing*. If you use one of these phrases, define it on first
    use or provide a link to the definition, and use it consistently
    throughout the document.
<a id="word-list--cell-phone"></a>

**Don't use: cell phone, cellphone**
    Don't use. Instead, use *mobile phone*, or if you're talking about
    more than phones, then use *mobile device*.
    It's OK to use *phone* (without *mobile*) when the context is
    clear.
<a id="word-list--cellular-data"></a>

**Don't use: cellular data**
    Don't use. Instead, use *mobile data*.
<a id="word-list--cellular-network"></a>

**Don't use: cellular network**
    Don't use. Instead, use *mobile network*.
<a id="word-list--chapter"></a>

**chapter**
    When referring to documentation that isn't in the form of a book, don't
    use the term *chapter*. Instead, refer to documents, pages, or
    sections.
<a id="word-list--check"></a>

**Avoid: check**
    Don't use to refer to marking a checkbox. Instead, use *select*.
    Recommended: Select **Automatically
    check for updates**.
    Not recommended: Check **Automatically
    check for updates**.
<a id="word-list--checkbox"></a>

**checkbox**
    Not *check box*.
<a id="word-list--choose"></a>

**choose**
    *Choose* is fine to use for generic contexts. For UI elements, use
    [select](#word-list--select).
<a id="word-list--chubby"></a>

**Don't use: chubby**
    Don't use. Instead, use a word that clearly explains what you mean, such
    as *unused* or *overextended*.
<a id="word-list--clear"></a>

**clear**
    Use (as a verb) to refer to clearing a check mark from a checkbox.
    Recommended: Clear **Automatically
    check for updates**.
    Not recommended: Uncheck
    **Automatically check for updates**.
    Not recommended: Deselect
    **Automatically check for updates**.
<a id="word-list--cli"></a>

**Avoid: CLI**
    Don't use *CLI* generically to refer to a command-line interface.
    Instead, refer to the specific command-line interface, such as the
    [Google Cloud CLI](#word-list--gcloud).
<a id="word-list--click"></a>

**click**
    When the environment is a desktop with a mouse, use *click* for most
    targets, such as buttons, links, list items, and radio buttons. Don't use
    *click on*.
    Recommended: Click **OK**.
    Not recommended: Click on **OK**.
    Hyphenate *right-click*, *left-click*, and *double-click*.
    When a click or tap action reveals a collapsed list, you can write
    *click to expand* or simply *expand*.
    It's OK to write *click in* when referring to a region that needs
    focus (for example: *click in the window*), but not when referring to
    a control or a link.
    For Android apps, don't use
    *click*. Instead, use [tap](#word-list--tap).
<a id="word-list--click-here"></a>

**Don't use: click here**
    Don't use. For information and alternatives, see
    [Avoid vague link text](#cross-references--vague-link-text).
<a id="word-list--clickthrough"></a>

**clickthrough (noun), click through (verb)**
<a id="word-list--client"></a>

**client**
    In REST and RPC API documentation, *client* is short for *client
    app*—that is, the app that the developer is writing.
    Don't use *client* as an abbreviation for *client library*;
    instead, use *library*.
<a id="word-list--client-id"></a>

**client ID**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--client-secret"></a>

**client secret**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--cloud"></a>

**Avoid: (Cloud) Cloud**
    Don't use as short for *Google Cloud*.
    For generic references such as *the cloud* or *hybrid cloud*,
    use lowercase.
<a id="word-list--gcp-console"></a>

**Don't use: (Cloud) Cloud console**
    Don't use. Instead, refer to the full name *Google Cloud console*.
    If you aren't discussing any other console (such as the Google Admin
    console), you can abbreviate to *the console* after first mention.
    Use *the* before the tool name. For more information, see
    [console](#word-list--console).
<a id="word-list--cloud-sdk"></a>

**Cloud SDK**
    Not *Google Cloud SDK*.
<a id="word-list--co"></a>

**co***
    See [guidance about hyphens with prefixes](#hyphens--prefixes).
<a id="word-list--codebase"></a>

**codebase**
    Not *code base*.
<a id="word-list--codelab"></a>

**codelab**
    Not *code lab* or *code-lab*. For more information, see
    [documentation](#word-list--documentation).
<a id="word-list--cold"></a>

**cold**
    When possible, avoid [jargon](#jargon) like *cold
    failover*, *cold standby*, and *cold spare*. If you use one
    of these phrases, define it on first use and use it consistently
    throughout the document.
<a id="word-list--colocate"></a>

**colocate**
    Not *co-locate* or *colo*.
<a id="word-list--compliant"></a>

**Avoid: compliant, compliance**
    Use with caution. A claim that a product or its output is *compliant*
    with a standard is a strong statement.
<a id="word-list--comprise"></a>

**Don't use: comprise**
    Don't use. Instead, use *consist of*, *contain*, or
    *include*.
<a id="word-list--config"></a>

**Avoid: config**
    Avoid when possible. Instead, spell out the full word when it's used in a
    non-code sense: *configuration* or *configuring*. Use the
    verbatim code item name when referring to, for example, a data structure
    or a file with that name.
<a id="word-list--confidential"></a>

**confidential**
    *Confidential* data is data that is protected to prevent unauthorized access. See
    [sensitive](#word-list--sensitive).
<a id="word-list--cons"></a>

**Don't use: cons**
    Don't use. Instead, use a more precise term, such as *disadvantages*.
<a id="word-list--console"></a>

**Avoid: console**
    Don't use in isolation. Instead, use the name of the specific console,
    such as the [Google Cloud
    console](https://console.cloud.google.com/) or the Google Admin console.
    Use *the* before the name of a console.
    After giving the full name of a console, you can use a shortened version
    of the name, such as the *Admin console*.
    If you're only discussing the Google Cloud console, after giving the full
    name you can refer to *the console*.
    To refer to a sub-page of a console, use the term *page*.
    If a specific term for a browser-based interface is unavailable, use
    *web interface*.
<a id="word-list--content-type"></a>

**Avoid: content type**
    Be as specific as possible when writing about a content type, and use the term only when applicable.
    For example, you can use this term if you're referring to the value of the `Content-Type` HTTP header.
    Also see [media type](#word-list--media-type).
<a id="word-list--control-keys"></a>

**Control+S, Command+S, and other keyboard commands**
    To refer to a `Control` character, use
    `Control`+CHARACTER.
    Don't use *Ctl-S*, *Cmd-S*, or *Cloverleaf-S*.
    In most cases, use an uppercase letter for CHARACTER.
    In macOS, many keyboard commands use the `Command` key instead of
    the `Control` key, and there's an `Option` key instead
    of an `Alt` key. If your audience includes macOS users and
    Windows or Linux users, then mention both keyboard commands.
    Recommended: `Control+S`
    (`Command+S` on macOS)
<a id="word-list--copy-paste"></a>

**Avoid: Copy and paste**
    Avoid using. Instead, explain what to enter into a field and not how.
    Recommended: In the
    **Query** field, enter the output from the previous step.
    Not recommended: Copy the output from
    the previous step and paste into the **Query** field.
<a id="word-list--could"></a>

**Avoid: could**
    Avoid using. Instead, use *can* where possible.
    See also [can](#word-list--can), [may](#word-list--may),
    [might](#word-list--might), [must](#word-list--must),
    [should](#word-list--should) and [would](#word-list--would).
    For information about clarifying who's performing an action, see
    [Active voice](#voice).
    For information about tenses, see [Present
    tense](#tense).
<a id="word-list--cpu"></a>

**CPU**
    All caps. No need to expand the abbreviation on first mention.
<a id="word-list--crazy"></a>

**Don't use: crazy, bonkers, mad, lunatic, insane, loony**
    Don't use. Instead, use *complicated*, *complex*,
    *baffling*, *strange*, or *unexpected*, and only for
    inanimate objects.
<a id="word-list--create-new"></a>

**Avoid: Create a new ...**
    Avoid using unless you need to distinguish the item from another recently
    created item. Instead, use *Create a ...*
    Recommended: Create a project.
    Not recommended: Create a new project.
<a id="word-list--cripple"></a>

**Don't use: cripple**
    Don't use. Instead, use more precise language. For example, instead of
    *it crippled the server*, write *it slowed the server down*.
    When referring to people, use terms that specifically describe a physical
    impairment, such as *person with a motor disability*; *person with
    a mobility impairment* (refers to walking or moving about); *person
    with dexterity impairment* (refers to using a standard mouse or
    keyboard); *person who uses a wheelchair, walker, or cane*;
    *wheelchair user*; *person with restricted or limited mobility*.
<a id="word-list--cross-site-request-forgery"></a>

**cross-site request forgery**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--curated-roles"></a>

**Don't use: curated roles**
    Don't use. Instead, use *predefined roles*.
<a id="word-list--currently"></a>

**Avoid: currently**
    Avoid because this word is implied. The word can also prematurely disclose
    product or feature strategy or inappropriately imply that a product or
    feature might change.
    See also
    [as of this writing](#word-list--as-of-this-writing) and
    [presently](#word-list--presently).
    Recommended: Windows isn't supported.
    Not recommended: Windows isn't
    currently supported.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--custom-mode-vpc-network"></a>

**custom mode VPC network**
    Not *custom mode network*.
<a id="word-list--curl"></a>

**curl**
    Not *cURL*.
    For information about when to use code format, see
    [Items that are sometimes in code font](#code-in-text--items-that-are-sometimes-in-code-font).
<a id="word-list--cyber-monday"></a>

**Cyber Monday**
    Avoid unless explicitly referring to an event in the US. Instead use
    *peak scale event*.

<a id="word-list--letter-d"></a>

##### D

<a id="word-list--dash"></a>

**dash**
    A dash (`—`) isn't the same character as a hyphen
    (`-`). The characters are used for different purposes.
    Therefore, don't use the word *dash* to refer to a hyphen.
<a id="word-list--dashboard"></a>

**Avoid: dashboard**
    Don't use to refer to the Google Cloud console. For more information, see
    [console](#word-list--console).
    Use *dashboard* not *Dashboard* unless it's officially part of a
    product name.
<a id="word-list--data"></a>

**data**
    Use *data* as singular, not plural; *the data is*, not
    *the data are*.
    Use data as a mass noun, not a count noun; *less data*, not
    *fewer data*.
<a id="word-list--data-center"></a>

**data center**
    Not *datacenter*.
<a id="word-list--data-center-campus"></a>

**data center campus**
    Use when referring to an entire physical location, which can encompass one
    or more data centers.
<a id="word-list--data-cleaning"></a>

**data cleaning**
    Not *data cleansing*.
<a id="word-list--dataflow"></a>

**data flow (noun); dataflow (noun)**
    If it's possible to replace with the phrase *flow of data*, then use
    two words: *data flow*.
    If that replacement doesn't work, such as when referring to something like
    stream processing or reactive programming, then use one word:
    *dataflow*.
<a id="word-list--data-source"></a>

**data source**
    Not *datasource*.
<a id="word-list--datastore"></a>

**datastore**
    Not *data store*.
<a id="word-list--data-type"></a>

**data type**
    Not *datatype*.
<a id="word-list--dead-letter"></a>

**dead-letter queue, dead letter**
    Define on first use, for example *dead-letter queue (unprocessed
    messages queue)*.
<a id="word-list--deep-linking"></a>

**deep linking**
    Not *deep-linking*. However, if you can replace with
    *linking*, then do so.
<a id="word-list--deficient"></a>

**Avoid: deficient**
    Don't use to refer to a person.
    OK to use to refer to a condition of a computer system.
<a id="word-list--deformed"></a>

**Avoid: deformed**
    Don't use to refer to a person.
    OK to use to refer to a condition of a computer system or
    inanimate object.
<a id="word-list--dmz"></a>

**Don't use: demilitarized zone (DMZ)**
    Don't use. Instead, use a more precise term like *perimeter network*.
<a id="word-list--denigrate"></a>

**Don't use: denigrate**
    Don't use. Instead, use *disparage*.
<a id="word-list--denylisted"></a>

**Don't use: denylist (verb), denylisted, denylisting**
    Don't use as a verb. Instead, rewrite to improve clarity.
    OK to use *denylist* as a noun.
    For more information, see [blacklist](#word-list--blacklist).
<a id="word-list--deprecate"></a>

**deprecate**
    To *deprecate* an item is to recommend against the item's use,
    typically as a warning that the item will soon be unavailable or
    unsupported. Don't use *deprecated* to mean *removed*,
    *deleted*, *shut down*, or *turned down*.
<a id="word-list--deselect"></a>

**Don't use: deselect**
    Don't use to refer to clearing a check mark from a checkbox. Instead, use
    *clear*.
    Recommended: Clear **Automatically
    check for updates**.
    Not recommended: Deselect
    **Automatically check for updates**.
    Not recommended: Uncheck
    **Automatically check for updates**.
<a id="word-list--desire"></a>

**Don't use: desire, desired**
    Don't use. Instead, use a word like *want* or *need*.
    Recommended: Set the value to the
    size that you want.
    Not recommended: Set the value to
    the size that you desire.
    Not recommended: Set the value to
    the desired size.
<a id="word-list--developers-console"></a>

**Don't use: Developers Console**
    Don't use. For more information, see [console](#word-list--console).
<a id="word-list--devops"></a>

**DevOps**
    Short for *development operations*. No need to spell out on first
    mention unless the audience requires it. For more information, see [DevOps](https://wikipedia.org/wiki/DevOps).
<a id="word-list--dialog"></a>

**dialog**
    Use *dialog* for the UI element sometimes called a [dialog box](http://wikipedia.org/wiki/Dialog_box).
    Use *dialogue* only for verbal interaction between people.
<a id="word-list--directory"></a>

**directory, folder**
    If the context that you're documenting (such as an IDE's GUI) uses one
    term or the other, use that term. If not, then use *directory* in a
    command-line context, and *folder* in a GUI context. When in doubt,
    default to *directory*.
<a id="word-list--disable"></a>

**Avoid: disable**
    Don't use *disable* or *disabled* to describe something that's
    broken.
    When describing a user action or the state of a UI element, use a more
    precise term where possible. You can use *inactive*,
    *unavailable*, *deactivate*, *turn off*, or
    *deselect*, depending on the context. Use the same term consistently throughout your
    document.
    See also [enable](#word-list--enable).
<a id="word-list--disclosure-triangle"></a>

**Don't use: disclosure triangle, disclosure widget**
    Don't use. Instead, use *expander arrow*.
<a id="word-list--display"></a>

**display (verb)**
    Don't use as an intransitive verb. *Display* is a transitive verb;
    therefore, it requires an object. It is often misused in technical
    documentation, as demonstrated by the following example:
    Recommended: The Output Directories
    area appears.
    Recommended: The Output Directories
    area is displayed.
    Not recommended: The Output
    Directories area displays.
    The following example demonstrates correct usage of the verb
    *display* but means something quite different from the preceding
    examples.
    Recommended: The Output Directories
    area displays the vector image.
<a id="word-list--ddos"></a>

**distributed denial-of-service (DDoS)**
    Hyphenate as shown. On subsequent mention, use *DDoS*.
<a id="word-list--dns-server-policy"></a>

**DNS server policy**
    Lowercase *server policy*.
<a id="word-list--dnskey"></a>

**DNSKEY**
    One word, all capital letters.
<a id="word-list--documentation"></a>

**documentation or document or documents**
    To refer specifically to the text on a page that explains a product, feature, or service,
    use *this document*, and not *this article*, *this topic*, *this doc*, or
    *this page*. It's OK to use *this tutorial*, *this quickstart*, or *this
    codelab* for those specific documentation types.

    Always spell out *documentation* except in cases where space is limited, such as in
    tabs and URLs.

    See also
    [page](#word-list--page).
    Recommended: You can find many
    examples in this document.
    Not recommended: You can find many
    examples in this article.
    Recommended: This document provides
    guidance about creating tables.
    Not recommended: This page provides
    guidance about creating tables.
<a id="word-list--docset"></a>

**documentation set**
    Not *doc set* or *docset*.
<a id="word-list--does-not-yet"></a>

**Avoid: does not yet**
    Avoid in timeless documentation because this phrase can become outdated.
    The phrase can also prematurely disclose product or feature strategy or
    inappropriately imply that a product or feature might change.
    Recommended: The Google Cloud console
    doesn't support this IAM role.
    Not recommended: The Google Cloud
    console does not yet support this IAM role.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--dojo"></a>

**Don't use: dojo**
    Don't use. Instead, use a precise term that is accurate for the context,
    such as *training* or *workshop*.
<a id="word-list--domain-name-registrar"></a>

**domain name registrar**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--dnssec"></a>

**Domain Name System Security Extensions (DNSSEC)**
    Write out and capitalize each word on first use. OK to abbreviate as
    *DNSSEC* after first use.
<a id="word-list--double-tap"></a>

**(Android) double-tap**
    Hyphenate. Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--downscope"></a>

**Avoid: downscope**
    Consider using a more descriptive term like *constrain scope* or
    *reduce scope*. Because *downscope* might not be broadly
    understood, if you use the term, make sure to define it on first use.
        Don't use *down scope* or *down-scope*
            Recommended: Reducing the scope of a
            token helps you follow the principle of least privilege.
            Recommended (first use): The IAM
            recommender helps you *downscope* (reduce) the permissions that are
            available to your users.
<a id="word-list--drag"></a>

**drag**
    Use *drag*, not *click and drag* and not *drag and drop*.
    OK to use *drag-and-drop* as an adjective.
    Recommended: Drag the USER
    to the **Authorized** box.
<a id="word-list--drop-down"></a>

**Avoid: drop-down**
    In most cases, you can omit *drop-down* from phrases like *drop-down list* or
    *drop-down menu*, and just use *list* or *menu*. Include *drop-down* as a
    modifier only if the omission would cause ambiguity. Don't use *drop-down* as a
    standalone noun.
<a id="word-list--dumb-down"></a>

**Don't use: dumb down**
    Don't use. Instead, use a word or phrase what's happening, such as
    *simplify* or *remove technical jargon*.
<a id="word-list--dummy-variable"></a>

**Don't use: dummy variable**
    Don't use to refer to placeholders. Instead, use *placeholder*.
    Also don't use if referring to the concept in statistics known as a
    [dummy variable](https://en.wikipedia.org/wiki/Dummy_variable_(statistics)).
    Instead, use alternate terms such as
    *indicator variable*, *design variable*, *one-hot
    encoding*, *Boolean indicator*, *binary variable*, or
    *qualitative variable*.

<a id="word-list--letter-e"></a>

##### E

<a id="word-list--each"></a>

**each**
    *Each* refers to every individual item taken individually, not to a
    group of items taken collectively. In other words, *each* isn't a
    synonym for *all*. For example, *a list of each item* is
    ambiguous; *a list of all the items* or *a list of the items* is
    generally clearer.
<a id="word-list--earlier"></a>

**earlier**
    Use for a range of version numbers, not *lower*.
    Recommended: Use version 2.2 or
    earlier.
    Not recommended: Use version 2.2 or
    lower.
    In Android documentation, don't use
    *earlier* for a range of version numbers. Instead, use *lower*.
    When referring to a position in a document, use *earlier* or
    *preceding*, not *higher*.
<a id="word-list--easy"></a>

**Avoid: easy, easily**
    What might be easy for you might not be easy for others. Try eliminating
    this word from the sentence because usually the same meaning can be conveyed
    without it.
<a id="word-list--ecommerce"></a>

**ecommerce**
    Not *e-commerce*.
<a id="word-list--edge-availability-domain"></a>

**edge availability domain**
    Don't use *edge availability zone*, *metro availability domain*,
    or *metro availability zone*. Don't shorten to *EAD*.
<a id="word-list--eg"></a>

**Don't use: e.g.**
    Don't use. Instead, use phrases like *for example* or *such as*.
    Many people confuse *e.g.* and *i.e.*
<a id="word-list--egress"></a>

**egress**
    When referring to the networking term, use lowercase.
<a id="word-list--either"></a>

**either**
    When using *either*, use parallel syntax.
    Recommended: Do either option 1 or
    option 2.
    Recommended: Either do option 1 or
    do option 2.
    Not recommended: Either do option 1
    or option 2.
    In general, use *either* only for a choice between two things, not
    for a choice among multiple things. Writing *either A or B or C* will
    distract some readers, but if it's the best phrasing for your situation,
    then use it.
<a id="word-list--element"></a>

**element**
    In HTML and XML, a tag is a component of an element that indicates
    the start or end of the element. (For example, the
    `<i>` start tag indicates the beginning of the
    `<i>example</i>` element.) In general, don't use
    the term *tag* to refer to an entire element.
<a id="word-list--email"></a>

**email**
    Not *e-mail*, *Email*, or *E-mail*.
    Don't use as a verb.
    Use a specific verb in front of the word. For example, *send email*.
    This construction is better for translation and a
    [global audience](#translation).
<a id="word-list--emoji"></a>

**emoji**
    Use *emoji* for both singular and plural forms. See [Don't
    know the difference between emoji and emoticons? Let me explain](https://www.theguardian.com/technology/2015/feb/06/difference-between-emoji-and-emoticons-explained) and [What's the Plural of Emoji?](http://www.theatlantic.com/technology/archive/2016/01/whats-the-plural-of-emoji-emojis/422763/)
<a id="word-list--enable"></a>

**enable**
    In procedures, use the appropriate label and action for the
    [UI element](#ui-elements) that the user interacts with. When describing a
    user action or the state of a UI element, use a more precise term where possible. It's OK to
    use *enable* when not referring to a person.
    For turning on or activating an option or feature, use *enable* or
    *[turn on](#word-list--turn-on)* consistently:

    - Use the same term in introductory text as described in the
      procedure.
    - Use the same term throughout the document unless there's a
      difference in the UI elements for different procedures.
    Recommended: To enable the API,
    click the toggle.
    Recommended: Enable the API for your
    project.
    For making it feasible to do something, use *lets you*.
    Recommended: The API lets you detect
    features in images.
    Not recommended: The API enables you
    to detect features in images.
    Not recommended: The API allows you
    to detect features in images.
    In Google Workspace documentation, if possible, use
    *turn on* or *on* instead. If referring to the state of a UI element, use
    *available*.
<a id="word-list--endpoint"></a>

**endpoint**
    Not *end point*.
<a id="word-list--enter"></a>

**enter**
    Use *enter* to refer to the user entering text. If it's important to
    not press `Enter`, explicitly say so. See also
    [*type*](#word-list--type).
    Recommended: In the **Owner** box,
    enter your name.
    Recommended: In the **Size** box,
    type a font size.
<a id="word-list--ephemeral-external-ip-address"></a>

**ephemeral external IP address**
    Don't use *ephemeral IP address* or *external IP address* to
    refer to ephemeral external IP addresses.
<a id="word-list--error-prone"></a>

**error-prone (adjective)**
    Hyphenate. Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--etc"></a>

**Avoid: etc.**
    Avoid using *etc.*, *and so forth*, and *and so on*
    wherever possible. If you really need to use one, use *etc.*
    Always include the period, even if a comma follows immediately after.
    Recommended: Your app might experience
    problems such as instability or high latency.
    Recommended: Your app might experience
    problems, including instability or high latency.
    Not recommended: Your app might
    experience instability, high latency, and so on.
    Not recommended: Your app might
    experience instability, high latency, etc.
    Not recommended: If your app
    experiences instability, high latency, etc., follow these steps:
<a id="word-list--eventually"></a>

**Avoid: eventually**
    Avoid in timeless documentation because this word can become outdated. The
    word can also prematurely disclose product or feature strategy or
    inappropriately imply that a product or feature might change.
    See also
    [future](#word-list--future) and [soon](#word-list--soon).
    Recommended: This version of the SDK
    is deprecated.
    Not recommended: This version of the
    SDK is deprecated and eventually will be no longer supported.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--execute"></a>

**execute**
    Verb commonly used to refer to function calls, SQL queries, and other processes. When the meaning
    is the same, use the simpler word *run* instead. If you need to use a more precise term
    for your context, use that term.
<a id="word-list--expander-arrow"></a>

**expander arrow**
    The UI element used to expand or collapse a section of navigation or
    content. If you describe this element, use the terms *expander arrow*
    and *expandable section*
    Don't use terms like *expando* or *zippy*.
<a id="word-list--exploit"></a>

**exploit**
    Don't use *exploit* to mean "use."
    Only use *exploit* in the negative sense, such as to describe
    *exploiting a security vulnerability*.
<a id="word-list--external-vpn-gateway"></a>

**external VPN gateway**
    Write *external* and *gateway* all lowercase except at the
    beginning of a sentence, heading or list item.
<a id="word-list--extract"></a>

**extract**
    Use instead of *unarchive*, *uncompress*, *untar*, or *unzip*.

<a id="word-list--letter-f"></a>

##### F

<a id="word-list--failover"></a>

**fail over (verb), failover (noun, adjective)**
<a id="word-list--fat"></a>

**Don't use: fat**
    Don't use. Instead, use a precise modifier that conveys the appropriate
    meaning. For example, use *high-capacity network connection* instead
    of *fat connection* or *full-featured client* instead of *fat
    client*.
    Instead of using fat in a negative sense, such as *trim the fat*,
    refer in a more concrete manner to the *removal of unused items*.
    OK to use as an acronym when referring to file allocation table (FAT).
<a id="word-list--female-adapter"></a>

**Don't use: female adapter**
    Don't use. Instead, use a genderless word like *socket*.
<a id="word-list--fhir"></a>

**Fast Healthcare Interoperability Resources (FHIR)**
    Refer to *a FHIR* (pronounced "a fire," as in "a FHIR store"), not *an FHIR*.
    For more information, see
    [Indefinite articles before abbreviations](#abbreviations--articles).
<a id="word-list--filename"></a>

**filename**
    Not *file name*
<a id="word-list--file-system"></a>

**file system**
    Not *filesystem*.
<a id="word-list--fill-in"></a>

**fill in; fill out**
    Use *fill in* when referring to entering information in individual
    fields.
    Use *fill out* when referring to completing an entire form.
        Recommended: Fill out the
            questionnaire. Be sure to fill in the required fields.
<a id="word-list--final-solution"></a>

**Don't use: final solution**
    Don't use. Instead, use *solution* as a standalone term or, depending
    on the context, *definitive*, *optimal*, *best*, or *last
    solution*.
<a id="word-list--fintech"></a>

**fintech**
    Write out on first mention: *financial technology (fintech)*. Don't
    use *FinTech* or *fin-tech*.
<a id="word-list--firewalls"></a>

**firewalls**
    Don't use in Compute Engine or networking documentation. Instead, use
    *firewall rules*.
    Exception: If you're explaining how firewall rules work, you can explain
    that every network has an implied virtual distributed firewall.
    Outside of Compute Engine or networking documentation, the term
    *firewalls* is acceptable.
<a id="word-list--first-class"></a>

**Don't use: first class, first-class, first-class citizen**
    Don't use *first class* or *first-class citizen*. Instead, use
    another term that's appropriate for the context, such as *higher-order*,
    *anonymous*, or *nested*, or loosely describe the specific
    characteristics or features of the entity, resource, language, or framework.
    Recommended: These widgets have full access to the event system and lifecycle hooks.
    Not recommended: The widgets are first-class components in the UI framework.
    Recommended: Virtual machines are higher-order resources that can participate in resource groups and are integrated in a variety of identity, networking, and storage services.
    Not recommended: Virtual machines are treated as first-class resources across the identity, networking, and storage services.
    For more information, see
    [Write inclusive documentation](#inclusive-documentation).
<a id="word-list--following"></a>

**following**
    It's not necessary to use a noun after *following* unless it helps
    provide clarity and enables accessibility. See [Tables](#tables--table-placement).
    Recommended: ... in the following
    code sample ...
    Recommended: ... in the following
    table ...
    Recommended: ... do the following:
    ...
<a id="word-list--foo"></a>

**Avoid: foo**
    Avoid when possible even though it's a common term in the developer
    community. Instead, use a clearer and more meaningful placeholder name.
<a id="word-list--for-example"></a>

**for example**
    When you introduce an example using the phrase *for example*, follow the phrase by a comma. For clarity, when
    introducing an example, separate the example using dashes, commas, or parentheses from the
    rest of the sentence as appropriate, or introduce the example in a separate sentence.
    Recommended: Enter a name for the instance—for example, `my-instance-99`.
    Recommended: Enter a six-digit hex number (for example, `228B22`), and then click **OK**.
    Recommended: Enter a six-digit hex number, and then click **OK**. For example, if you want the color forest
    green, enter `228B22`.
    For more information, see [Format examples](#format-examples).
<a id="word-list--for-instance"></a>

**Avoid: for instance**
    Don't use the phrase *for instance* to introduce examples to avoid confusion with the
    noun *instance*. Instead, use *for example*, *like*, or *such as*. For
    more information, see [for example](#word-list--for-example).
<a id="word-list--frontend"></a>

**frontend**
    Not *front-end* or *front end*.
<a id="word-list--functionality"></a>

**Avoid: functionality**
    Use with caution. With respect to hardware or software,
    *functionality* refers to a set of associated functions or
    capabilities and how they work. However, the word is sometimes overused,
    especially when the intended meaning is *capabilities* or
    *features*.
<a id="word-list--future"></a>

**Avoid: future, in the future**
    Avoid in timeless documentation because this word or phrase can become
    outdated.
    See also [eventually](#word-list--eventually) and [soon](#word-list--soon). For more
    information, see [Timeless
    documentation](#timeless-documentation).

<a id="word-list--letter-g"></a>

##### G

<a id="word-list--gigabytes-per-second"></a>

**GBps**
    Short for *gigabytes per second*. By convention, we don't use
    *GB/s*. For more information, see [Units of measurement](#units-of-measure).
<a id="word-list--gbps"></a>

**Gbps**
    Short for *gigabits per second*. By convention, we don't use
    *Gb/s*. For more information, see [Units of measurement](#units-of-measure).
<a id="word-list--gcloud"></a>

**(Cloud) `gcloud` CLI**
    Use the full name *Google Cloud CLI* the first time that you mention
    the product on a page.
<a id="word-list--gender"></a>

**Don't use: gender-neutral he, him, or his (or she or her)**
    Don't use. Instead, use the singular *they* (see [Jane Austen and other famous authors violate what everyone learned in
    their English class](http://www.pemberley.com/janeinfo/austheir.html)). Don't use *he/she* or *(s)he* or other
    such punctuational approaches. For more information, see
    [Pronouns](#pronouns).
<a id="word-list--generative-ai"></a>

**generative AI**
    Spell out *generative*. Use sentence case.
    Don't use *gen AI* or *Gen AI*.
    Don't hyphenate *generative AI* as an adjective unless you must do
    so for clarity. See also [AI](#word-list--ai).
<a id="word-list--ghetto"></a>

**Don't use: ghetto**
    Don't use. Instead use more precise terms like *clumsy*,
    *workaround*, or *inelegant* to refer to code that isn't in a
    production-ready state.
<a id="word-list--gimp"></a>

**Don't use: gimp, gimpy**
    Don't use. Instead, use precise, non-figurative language to refer to a
    deficiency in a component.
    OK to use in reference to companies, tools, software packages, and other
    entities that use the term in their names.
<a id="word-list--gke-node"></a>

**GKE node**
    Use when first introducing GKE nodes on a given page. For subsequent
    mentions, you can use *node*. A GKE node is a worker machine that
    runs containerized applications and other workloads. The machine is a
    Compute Engine VM that GKE creates during cluster creation. See also [virtual machine (VM) instance](#word-list--virtual-machine-instance).
<a id="word-list--google"></a>

**Avoid: Google, Googling**
    Don't use as a verb or gerund. Instead, use *search with Google*.
<a id="word-list--google-account"></a>

**Google Account, Google Accounts**
    Capitalize *Account*.
<a id="word-list--google-api-client-library"></a>

**Google API Client Library for LANGUAGE (Java, .NET, etc.)**
    On second and subsequent use, you can abbreviate to
    *LANGUAGE client library*.
<a id="word-list--google-api-console"></a>

**Don't use: Google API Console, Google APIs Console**
    Don't use. For more information, see [console](#word-list--console).
<a id="word-list--gcp"></a>

**Google Cloud**
    Not *GCP*, *Cloud Platform*, or *Cloud*.
<a id="word-list--google-cloud-platform-console"></a>

**Google Cloud console**
    If you're only discussing the Google Cloud console, it's OK to shorten to
    *the console* after first use on a given page.
    Use *the* before the console name. For more information, see [console](#word-list--console).
<a id="word-list--gcp-project-id"></a>

**Google Cloud project ID**
    Not *Cloud project ID* or *GCP project ID*. You can also
    shorten to *project ID*, but be aware that that term is ambiguous in
    some contexts.
<a id="word-list--google-developers-console"></a>

**Don't use: Google Developers Console**
    Don't use. For more information, see [console](#word-list--console).
<a id="word-list--google-io"></a>

**Google I/O**
    Not *I-O* or *IO*.
<a id="word-list--google-play-services"></a>

**Google Play services**
    Write *services* in lowercase.
<a id="word-list--google-play-services-SDK"></a>

**Google Play services SDK**
    Write *services* in lowercase.
<a id="word-list--grandfather-clause"></a>

**Don't use: grandfather clause, grand-father clause, grand father clause**
    Don't use. See [grandfathered](#word-list--grandfathered).
<a id="word-list--grandfathered"></a>

**Don't use: grandfathered**
    Don't use to refer to something that is allowed to violate a rule because
    it predates the rule. Instead, use an adjective like *legacy* or
    *exempt* or a verb like *made an exception*.
    Recommended: The app is exempt because
    it was released before the new requirements were announced.
    Not recommended: The app is
    grandfathered in because it was released before the new requirements were
    announced.
<a id="word-list--gray-box"></a>

**Avoid: gray-box, grey-box**
    Avoid using *gray-box*, *graybox*, or *gray box* to
    describe testing.
    To refer to testing that's a combination of clear and opaque testing
    methods, describe exactly what it's doing.
    If you need to refer to this type of testing after you describe it,
    consider using a more precise term for clarity, such as *translucent-box
    testing*.
<a id="word-list--grayed-out"></a>

**Don't use: grayed-out, greyed-out, gray out, grey out**
    Don't use. Instead, use *unavailable*.
<a id="word-list--grayhat"></a>

**Don't use: grayhat, greyhat, gray hat, grey hat**
    Don't use. Follow the guidance for [black hat](#word-list--blackhat) when
    referring to someone violating rules or laws.
<a id="word-list--graylist"></a>

**Don't use: graylist, greylist, gray list, grey list, gray-list, grey-list**
    Don't use. See [blacklist](#word-list--blacklist).
<a id="word-list--graylisted"></a>

**Don't use: graylisted, greylisted, gray listed, grey listed, gray-listed, grey-listed**
    Don't use. See [blacklist](#word-list--blacklist).
<a id="word-list--graylisting"></a>

**Don't use: graylisting, greylisting, gray listing, grey listing, gray-listing, grey-listing**
    Don't use. See [blacklist](#word-list--blacklist).
<a id="word-list--gsutil"></a>

**(Cloud) `gsutil`**
    In the Google Cloud context, use code font for both the name of the
    command-line utility and the command.
<a id="word-list--guru"></a>

**Don't use: guru**
    If possible, use a more precise term. For example, if you mean
    *expert* or *teacher*, use those terms.
<a id="word-list--guys"></a>

**Don't use: guys, you guys**
    When referring to a group of people use non-gendered language, such as
    *everyone* or *folks*.
<a id="word-list--gypsy"></a>

**Don't use: gypsy**
    Don't use. To refer to the people, use *Romani*, *Roma*, or
    *Traveller*, as appropriate for the specific group you're referring
    to. In place of metaphorical uses of the term, use more precise phrases.

<a id="word-list--letter-h"></a>

##### H

<a id="word-list--hamburger"></a>

**Don't use: hamburger, hamburger menu**
    Don't use. Instead use the `aria-label` for that particular
    icon. For example, **Menu**.
    For more information, see
    [Buttons and icons](#ui-elements--buttons).
<a id="word-list--hands-off"></a>

**Don't use: hands off, hands-off**
    Use a less figurative phrase, such as *automated*. If you're
    referring to a group that doesn't do anything during a process, write a
    description.
<a id="word-list--hands-on"></a>

**Don't use: hands on, hands-on**
    Use a less figurative phrase, such as *customizable*, or write a
    description of the activity.
<a id="word-list--hang"></a>

**Don't use: hang, hung**
    Don't use to refer to a computer or system that is not responding.
    Instead, use *stop responding* or *not responding*. For more
    information, see [Avoid figurative
    language](#inclusive-documentation--figurative-language).
<a id="word-list--happiness"></a>

**happiness and satisfaction**
    Use *happiness* when referring to a customer's perception of a
    site's reliability. Use *satisfaction* when referring to whether the
    site meets the customer's needs.
    Site reliability engineering (SRE) content generally refers to
    measuring *customer happiness* instead of *customer
    satisfaction*. The two phrases are not equivalent.
    The distinction the SRE documentation makes is between satisfying a need
    (a dispassionate act) and establishing an emotional response (creating
    happiness). Although it is difficult to measure happiness precisely, SRE
    uses [service level indicators
    (SLIs)](#word-list--service-level-indicator) to quantify user perception. For example, a customer might feel
    a "need" to watch a show on TV. If the show is available, the customer's
    need is satisfied. But if playback is slow or choppy, the customer might
    not be happy.
    For more information about SRE and measuring reliability, see [The Happiness Test](https://www.coursera.org/lecture/site-reliability-engineering-slos/the-happiness-test-ELmSr).
<a id="word-list--hardcode"></a>

**hardcode (verb), hardcoded (adjective)**
    Don't hyphenate.
<a id="word-list--he"></a>

**Avoid: he, him, his**
    Don't use a gendered pronoun except for a specific individual of known
    gender. Use *they* and *their* for the general singular pronoun.
<a id="word-list--healthcare"></a>

**healthcare**
    Not *health care* or *health-care*.
<a id="word-list--health-check"></a>

**Avoid: health check**
    Use with caution. When describing an action taken for a computer system,
    only use the term *health check* if this is the term that appears in
    the interface. Be certain to remove any ambiguity regarding whether the
    term refers to health in the medical sense.
    Use detailed, non-figurative language as much as possible, such as
    referring to a node *being responsive* instead of referring to a node
    being healthy.
<a id="word-list--healthy"></a>

**Avoid: healthy**
    Don't use. See [health check](#word-list--health-check).
<a id="word-list--high-availability"></a>

**high availability (noun), high-availability (adjective)**
    Spell as *high availability* when used as a noun and as *high-availability* when
    used as an adjective. See also [load balancing (noun), load-balancing (adjective)](#word-list--load-balancing).
    Lowercase except when part of a product name, but OK to abbreviate as
    *HA* after first use.
<a id="word-list--higher"></a>

**higher**
    Don't use for a range of version numbers. Instead, use [*later*](#word-list--later).
    Don't use to refer to a position in a document. Use *earlier* or
    *preceding*.
    Don't use to refer to a position in the UI. Instead, write instructions
    that avoid directional language. For more information, see [Writing accessible documentation](#accessibility).
    In Android documentation, use
    *higher* for a range of version numbers, not *later*.
    A release with the highest version number might not be the latest version.
    For example, if version 2.0 of an operating system receives a bug-fix
    update after version 3.0 has been released, then version 2.0.1 might be
    the latest version, even though its version number is lower than 3.0.
<a id="word-list--high-performance-computing"></a>

**high performance computing (HPC)**
    Don't hyphenate. Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--hit"></a>

**Don't use: hit**
    Don't use as a synonym for *click*, *press*, or *type*.
<a id="word-list--hold-the-pointer-over"></a>

**hold the pointer over**
    Only use this verb phrase in the following cases:

    - When the user needs to hold their mouse over a UI element, but not
      click the UI element. This action involves waiting for the UI to
      react—for example, waiting for a tooltip to open or waiting for a
      submenu to open.
    - When the duration of time is important.

    The phrase *point to* is more common.
    See also [point to](#word-list--point-to).
    Recommended: In the **Admin**
    menu, hold the pointer over **File**, and then click **New**.
    Not recommended: In the **Admin**
    menu, hover over **File**, and then click **New**.
<a id="word-list--holiday"></a>

**Avoid: holiday, the holidays**
    Don't use to refer to the end of the year. Instead, refer to specific
    quarters or months.
<a id="word-list--home-screen"></a>

**(Android) home screen**
    Two words in Android contexts; not *homescreen* or
    *home-screen*.
<a id="word-list--hostname"></a>

**hostname**
    Not *host name*.
<a id="word-list--hot"></a>

**hot**
    When possible, avoid [jargon](#jargon) like *hot failover*,
    *hot standby*, and *hot spare*. If you use one of these phrases,
    define it on first use and use it consistently throughout the document. However, see
    [hotspot](#word-list--hotspot).
<a id="word-list--hotspot"></a>

**hotspot**
    In databases, *hotspots* occur when a small number of nearby rows are
    accessed frequently in a short period of time, causing CPU spikes and
    affecting performance. Use *hotspot* and *hotspots* as nouns.
    Don't use verb and gerund forms such as *hotspotting*, because they
    translate less consistently.
    When you use *hotspot*, define it the first time that you use it on
    a page as you normally do with jargon.
    Recommended: Hotspots in one table
    can affect the performance of other tables.
    Not recommended: Hotspotting in one
    table can affect the performance of other tables.
<a id="word-list--housekeeping"></a>

**Don't use: housekeeping, house keeping, house-keeping**
    Don't use. Instead, use less figurative and more precise terms, such as
    *maintenance* and *cleanup*.
<a id="word-list--hover"></a>

**Don't use: hover**
    Don't use. Instead use [*hold the
    pointer over*](#word-list--hold-the-pointer-over).
<a id="word-list--https"></a>

**HTTPS**
    Not *HTTPs*.

<a id="word-list--letter-i"></a>

##### I

<a id="word-list--iaas"></a>

**IaaS**
    Write out on first mention: *infrastructure as a service (IaaS)*.
<a id="word-list--iam"></a>

**IAM**
    When referring to the Google Cloud product, spell it out on first use:
    *Identity and Access Management (IAM)*.
    When referring to UI text, write this term the way it's written in the UI.
    When referring to the general practice of identity and access management,
    spell it out in lowercase on first use and include a parenthetical
    comment:
    Recommended: Identity and access
    management (generally referred to as *IAM*) is the practice of
    granting the right individuals access to the right resources for the
    right reasons.
<a id="word-list--id"></a>

**ID**
    Not *Id* or *id,* except in string literals or enums.
    In some contexts, it's best to spell out as *identifier* or
    *identification*.
<a id="word-list--ie"></a>

**Don't use: i.e.**
    Don't use. Instead, use phrases like *that is*. Many people confuse
    *e.g.* and *i.e.*
<a id="word-list--if"></a>

**if**
    Wondering whether to use *if* or *whether*? See [whether](#word-list--whether).
    Although it is common in casual usage to omit the word *then* in *if...then*
    statements, you should include helper words like *then* in technical documentation. For
    more information, see
    [Use clear, precise, and unambiguous language](https://developers.google.com/style/translation#clear-language).
<a id="word-list--image"></a>

**image**
    *Image* by itself doesn't localize well because of its many meanings. Consider adding
    context—for example, *disk image* or *container image*.
<a id="word-list--impact"></a>

**Avoid: impact**
    Use only as a noun. Instead of writing that something *has an
    impact*, use the word *affect*.
    Recommended: This issue affects
    user experience.
    Acceptable: This issue has an impact
    on user experience.
    Not recommended: This issue impacts
    user experience.
<a id="word-list--index"></a>

**index**
    Use the plural *indexes* unless there is a domain-specific reason
    (for example, a mathematical or financial context) to use *indices*.
<a id="word-list--ingest"></a>

**ingest**
    Use *import*, *load*, or *copy* when referring to simple movement of data. Use
    *ingest* only when referring to such operations that also involve significant processing
    of the data.
<a id="word-list--ingress"></a>

**ingress**
    When referring to the networking term, use lowercase. When referring
    to the GKE term or API, capitalize *Ingress*.
<a id="word-list--in-order-to"></a>

**Avoid: in order to**
    Avoid *in order to*; instead, use *to*.
    Use *in order to* when needed to clarify meaning or to make
    something easier to read.
    Recommended: You can use
    monitoring to help identify issues.
    Not recommended: You can use
    monitoring in order to help identify issues.
    Recommended: The infrastructure is
    required in order to support search.
    Not recommended: The infrastructure
    is required to support search.
<a id="word-list--inline"></a>

**inline**
    One word as an adjective, *inline*, not *in line* or
    *in-line*.
<a id="word-list--instance-group"></a>

**instance group**
    Don't abbreviate to *IG*. See also [managed instance
    group](#word-list--mig).
<a id="word-list--intercluster"></a>

**intercluster**
    Use unhyphenated *intercluster*, not *inter-cluster*.
<a id="word-list--interconnect-attachment"></a>

**interconnectAttachment**
    Use when referring to the API. Otherwise, use [*VLAN attachment*](#word-list--vlan).
<a id="word-list--interconnect-connection"></a>

**Interconnect connection**
    Only use *Interconnect connection* relative to a product as follows:

    - CDN Interconnect connection
    - Cloud Interconnect connection
    - Dedicated Interconnect connection
    - Partner Interconnect connection

    OK to use *connection* on subsequent mentions.
    When you're referring to a Google Cloud product, always specify the
    product name. Don't use *Interconnect* or *interconnect* as
    standalone terms, and don't use generic terms like *cloud interconnect
    connection* or *cross-connect*.
<a id="word-list--interconnect-connection-location"></a>

**Interconnect connection location**
    Only refer to an *Interconnect connection location* in context of a
    specific product, for example *CDN Interconnect*.
    OK to also use *colocation facility*.
<a id="word-list--interconnect-type"></a>

**Don't use: interconnect type**
    Don't use. Instead, use *connection type*. Examples of connection
    types are a *dedicated connection* or a *connection provided by a
    service provider*.
<a id="word-list--interface"></a>

**interface**
    OK to use as a noun.
    Don't use as a verb. Instead, use *interact*, *talk*,
    *speak*, *communicate*, or other similar terms.
<a id="word-list--internal-dns"></a>

**internal DNS**
    Write *internal* all lowercase except at the beginning of a
    sentence, heading, or list item.
<a id="word-list--idn"></a>

**Internationalized Domain Name (IDN)**
    Write out and capitalize each word on first use. OK to abbreviate as
    *IDN* after first use.
<a id="word-list--internet"></a>

**internet**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--ike"></a>

**Internet Key Exchange (IKE)**
    Write out and capitalize each word on first use. OK to abbreviate
    *IKE* after first use.
<a id="word-list--io"></a>

**I/O (see also [Google I/O](#word-list--google-io))**
    Not *I-O* or *IO*.
<a id="word-list--iot"></a>

**IoT**
    OK to use as an abbreviation for *Internet of Things*. Note
    the lowercase *o*.
<a id="word-list--ipsec"></a>

**IPsec**
    Not *IPSec* or *IPSECShort*.
    Short for *Internet Protocol Security*. No need to spell out on
    first mention.

<a id="word-list--letter-j"></a>

##### J

<a id="word-list--jank"></a>

**Avoid: jank, janky**
    Use only to refer to a glitch or problem with graphics that is caused by a loss of data or
    inadequate refresh rate. Don't use otherwise. Use a less figurative term to refer to something
    of poor or unreliable quality.
<a id="word-list--just"></a>

**Avoid: just**
    Avoid. Usually, *just* is a filler word that you can delete without
    affecting your meaning.
    Recommended: BigQuery skips the row.
    Not recommended: BigQuery just skips
    the row.
    If your meaning is unclear without *just*, then use a more specific
    term such as *only*, *instead*, or *previously*, or revise
    your language to be more specific. (Even if one of these replacement
    terms fits, you often don't need it.)
    Recommended: You can run DML
    statements in the same way that you'd run a `SELECT`
    statement.
    Not recommended: You can run DML
    statements just as you'd run a `SELECT` statement.
    Recommended: Let a user query only
    the table without full dataset access.
    Recommended: Let a user query the
    table without full dataset access.
    Not recommended: Let a user query
    just the table without full dataset access.
    Sometimes, *just* is useful for conveying that one approach is
    simpler than another. In those cases, use *just* instead of
    [*simply*](#word-list--simple).
    Recommended: Use the namespace ID
    `namespace:example-kind` or just `example-kind`.

<a id="word-list--letter-k"></a>

##### K

<a id="word-list--k8s"></a>

**Don't use: k8s**
    Don't use. Instead, use *Kubernetes*.
<a id="word-list--kilobytes-per-second"></a>

**KBps**
    Short for *kilobytes per second*. By convention, we don't use
    *KB/s*. For more information, see [Units of measurement](#units-of-measure).
<a id="word-list--kbps"></a>

**Kbps**
    Short for *kilobits per second*. By convention, we don't use
    *Kb/s*. For more information, see [Units of measurement](#units-of-measure).
<a id="word-list--kebab"></a>

**Don't use: kebab, kabob, kebab menu, kabob menu**
    Don't use. Instead use the `aria-label` for that particular
    icon. For example,
    **More**. For more information, see
    [Buttons and icons](#ui-elements--buttons).
<a id="word-list--kebab-case"></a>

**Don't use: kebab case, kabob case, kebab-case, kabob-case**
    Don't use. Instead, use *dash-case*.
<a id="word-list--key"></a>

**key**
    Don't use as an adjective in the sense of *crucial* or
    *important*.
    If you use *key* as a noun, specify which kind of key you're
    referring to on first mention, because there are many kinds of
    keys in technical contexts.
<a id="word-list--key-pair"></a>

**key pair**
    A pair of keys, such as a public key and a private key. Contrast with
    *key-value pair*, which refers to a pairing that specifies a value
    for a variable (as in configuration files).
<a id="word-list--key-ring"></a>

**key ring**
    Use instead of *keyring* (without the space) when referring to a
    grouping of Cloud KMS keys.
<a id="word-list--key-value"></a>

**key-value pair**
    Use instead of *key/value pair* or *key value pair*.
<a id="word-list--kill"></a>

**Avoid: kill**
    Avoid when possible. Instead, use words like *stop*, *exit*,
    *cancel*, or *end*. For exceptions to this rule, see
    [Documenting command-line
    syntax](#code-syntax--linux-signals).

<a id="word-list--letter-l"></a>

##### L

<a id="word-list--lame"></a>

**Don't use: lame**
    Don't use. Instead, use precise, non-figurative language to refer to a
    deficiency in a component.
<a id="word-list--later"></a>

**later**
    Use for a range of version numbers, not *higher*.
    Recommended: Use version 2.2 or
    later.
    Not recommended: Use version 2.2 or
    higher.
    Not recommended: Use version 2.2+.
    A release with the highest version number might not be the latest version.
    For example, if version 2.0 of an operating system receives a bug-fix
    update after version 3.0 has been released, then version 2.0.1 might be
    the latest version, even though its version number is lower than 3.0.
    In Android documentation, don't use
    *later* for a range of version numbers. Instead, use *higher*.
    When referring to a position in a document, use *later* or
    *following*, not *below*.
<a id="word-list--latest"></a>

**Avoid: latest**
    Avoid in timeless documentation because this word can become outdated.
    If you must use *latest*, give the reader a reference
    point—for example, a version number or release date.
    Recommended: To help keep your
    system secure, install the latest version of the tools.
    Recommended: The June 2021 release
    includes the latest tools that help secure your system.
    Not recommended: The product includes
    the latest tools that help secure your system.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--learnings"></a>

**Don't use: learnings**
    Don't use. Instead, refer to *knowledge* or *things that you
    learned*.
<a id="word-list--left-nav"></a>

**Don't use: left-nav, right-nav**
    Don't use directional language. For more information, see
    [Writing accessible documentation](#accessibility).
    If referring to applications, use *[navigation menu](#ui-elements--term-navigation-menu)*.
    If referring to navigational elements for documentation, use *content
    navigation menu*.
<a id="word-list--legacy"></a>

**legacy**
    If possible, use a more precise term. If you do use *legacy*,
    include or point to a definition to clarify what you mean in the current
    context. Don't use *legacy* with any sort of pejorative
    connotation.
<a id="word-list--lets"></a>

**Don't use: let's (as a contraction of *let us*)**
    Don't use if at all possible.
    Not recommended: Let's click the
    **OK** button now.
<a id="word-list--loa-cfa"></a>

**Letter of Authorization and Connecting Facility Assignment (LOA-CFA)**
    Write out and capitalize each word on first use. OK to abbreviate as
    *LOA-CFA* after first use.
<a id="word-list--leverage"></a>

**Avoid: leverage**
    Avoid using if you mean *use*. If possible, use a more precise term.
    For example, *use*, *build on*, or *take advantage of*.
<a id="word-list--lifecycle"></a>

**lifecycle**
    Not *life cycle* or *life-cycle*.
<a id="word-list--lift-and-shift"></a>

**lift and shift**
    See [rehost](#word-list--rehost).
<a id="word-list--like"></a>

**like**
    It's OK to use *like* for either drawing comparisons (in the sense of *similar to*)
    or introducing examples (in the sense of *such as*).
    Recommended: Common I/O operations, like reading files or
    making network requests, can be asynchronous.
    Recommended: The new compression algorithm works like a
    dictionary encoder, replacing repeated strings with shorter codes.
    See also [such as](#word-list--such-as). For more information, see [Format examples](#format-examples).
<a id="word-list--limits"></a>

**limits**
    In an API context, *limit* often refers to usage limits (number of
    queries allowed per second or per day). Where possible, specify the kind
    of limit that you mean, such as *usage limit* or *service
    limit*; the word *limit* can refer to many different kinds of
    limits, including rules about acceptable use. See also [quota](#word-list--quota).
<a id="word-list--lint"></a>

**lint**
    Write both command-line tool name and command in lowercase. Use code font
    except where inappropriate.
<a id="word-list--little-endian"></a>

**little-endian**
    Hyphenate. Lowercase except at the beginning of a sentence,
    heading, or list item.
    Recommended: The codebase assumes
    little-endian byte ordering.
    Not recommended: The codebase assumes
    Little Endian byte ordering.
    Not recommended: The codebase assumes
    Little-endian byte ordering.
    Not recommended: The codebase assumes
    little endian byte ordering.
<a id="word-list--livestream"></a>

**livestream**
    Not *live stream*.
<a id="word-list--load-balancing"></a>

**load balancing (noun), load-balancing (adjective)**
    Spell as *load balancing* when used as a noun and as *load-balancing* when
    used as an adjective. See also [high availability (noun),
    high-availability (adjective)](#word-list--high-availability).
<a id="word-list--lock-screen"></a>

**(Android) lock screen**
    Two words in Android contexts; not *lockscreen* or
    *lock-screen*.
<a id="word-list--login"></a>

**login (noun or adjective), log in (verb)**
    For the verb form, *sign in* is generally better.
    If you're documenting a tool that uses the term *log in*, then use
    that term.
<a id="word-list--long-press"></a>

**Don't use: (Android) long press**
    In Android documentation, don't use. Instead, use *touch & hold*.
    (Not *touch and hold*.)
<a id="word-list--lro"></a>

**long-running operation**
    Not *long running operation*.
    OK to abbreviate as *LRO* after the first use.
<a id="word-list--lower"></a>

**lower**
    Don't use for a range of version numbers. Instead, use [*earlier*](#word-list--earlier).
    Don't use to refer to a position in a document. Instead, use *later*
    or *following*.
    Don't use to refer to a position in the UI. Instead, write instructions
    that avoid directional language. For more information, see [Writing accessible documentation](#accessibility).
    In Android documentation, use
    *lower* for a range of version numbers, not *earlier*.

<a id="word-list--letter-m"></a>

##### M

<a id="word-list--male-adapter"></a>

**Don't use: male adapter**
    Don't use. Instead, use a genderless word like *plug*.
<a id="word-list--man-hours"></a>

**Don't use: man hours, manhours, man-hours**
    Avoid using gendered terms. Instead use terms like *person hours*.
<a id="word-list--mitm"></a>

**Don't use: man-in-the-middle (MITM)**
    Avoid using gendered terms. Instead use terms like *on-path
    attacker* or *person-in-the-middle (PITM)*.
<a id="word-list--mig"></a>

**managed instance group (MIG)**
    OK to abbreviate to *MIG* on subsequent mention. See also
    [instance group](#word-list--instance-group).
<a id="word-list--manmade"></a>

**Don't use: manmade, man made**
    Avoid using gendered terms. Instead use a word like *artificial*,
    *manufactured*, or *synthetic*.
<a id="word-list--manned"></a>

**Don't use: manned**
    Avoid using gendered terms. Instead use terms like *staffed* or
    *crewed*.
<a id="word-list--manpower"></a>

**Don't use: manpower, man power, man-power**
    Avoid using gendered terms. Instead use terms like *staff* or
    *workforce*.
<a id="word-list--markdown"></a>

**Markdown**
    Always capitalized, even when you're referring to a nonstandard version.
<a id="word-list--master"></a>

**Don't use: master**
    Use with caution. Never use in conjunction with *slave*. Where
    possible, replace *master* with a specific term that is accurate for
    the context, such as *primary*, *main*, *original*,
    *parent*, *initiator*, *driver*, *controller*,
    *manager*, *mixer*, *aggregator*, *publisher*,
    *leader*, or *active*.

    Guidance | Recommended | Not recommended || Don't use *master* in conjunction with *slave* in any context. | Cloud SQL primary/replica | Cloud SQL master/slave |
    | Avoid using *master* where possible. | - GKE control plane - Jenkins controller - root key (in security) - primary key (in databases) | - GKE master plane - Jenkins master - master key (in security) - master key (in databases) |
    If the command or code that you're documenting uses the literal word
    *master*, then use this word only in direct reference to the code
    item ([formatted as code](#code-in-text)), make it clear
    what you're referring to, and use the new term thereafter.
    See also [*slave*](#word-list--slave).
<a id="word-list--material-design"></a>

**Material Design**
    Capitalize each word in *Material Design*.
<a id="word-list--matrix"></a>

**matrix**
    Use the plural *matrixes* unless there is a domain-specific reason
    (for example, a mathematical context) to use *matrices*.
<a id="word-list--may"></a>

**may**
    In general, reserve for official policy or legal considerations.
    To convey *possibility*, use *can* or *might*
    instead.
    To convey *permission*, use *can* instead.
    See also [can](#word-list--can), [could](#word-list--could),
    [might](#word-list--might), [must](#word-list--must),
    [should](#word-list--should), and [would](#word-list--would).
    For information about clarifying who's performing an action, see
    [Active voice](#voice).
<a id="word-list--megabytes-per-second"></a>

**MBps**
    Short for *megabytes per second*. By convention, we don't use
    *MB/s*. For more information, see
    [Units of measurement](#units-of-measure).
<a id="word-list--mbps"></a>

**Mbps**
    Short for *megabits per second*. By convention, we don't use
    *Mb/s*. For more information, see
    [Units of measurement](#units-of-measure).
<a id="word-list--media-type"></a>

**media type**
    In general, use the term [*media type*](https://www.iana.org/assignments/media-types/media-types.xhtml).
    In contexts where you need to refer to a *content type*—For example, if you mention
    the `Content-Type` HTTP header—it's okay to use *content type* instead, to avoid
    confusion. Don't use *MIME type*.
<a id="word-list--meta"></a>

**meta***
    See [guidance about hyphens with prefixes](#hyphens--prefixes).
<a id="word-list--metafeed"></a>

**metafeed**
    Not *meta-feed*.
<a id="word-list--metageneration"></a>

**metageneration**
    Not *meta-generation*.
<a id="word-list--method"></a>

**method**
    In programming contexts where *method* refers to a member of a class
    (as in Java), avoid also using the word generically to mean "approach" or
    "manner."
<a id="word-list--metro"></a>

**metropolitan area (metro)**
    In networking, a *metro* is a city where a colocation facility is
    located.
<a id="word-list--microservices"></a>

**microservices**
    Not *Microservices* or *micro-services*.
<a id="word-list--might"></a>

**might**
    Use to convey possibility or an uncertain outcome (for example, "You
    might be prompted to enter your credentials").
    See also [can](#word-list--can), [could](#word-list--could),
    [may](#word-list--may), [must](#word-list--must),
    [should](#word-list--should), and [would](#word-list--would).
    For information about clarifying who's performing an action, see
    [Active voice](#voice).
<a id="word-list--mime-type"></a>

**Avoid: MIME type**
    *MIME* stands for "Multipurpose Internet Mail Extensions," and was originally used to
    refer to email standards.
    Don't use *MIME* when you mean [*media type*](https://www.iana.org/assignments/media-types/media-types.xhtml).
    If you feel that might be ambiguous to an audience familiar with the term *MIME*,
    then you can write *media (MIME) type* for clarity.
<a id="word-list--mobile"></a>

**Don't use: mobile**
    Don't use *mobile* as a standalone noun. Instead, specify
    *mobile phone*, or if you're talking about more than phones, then use
    *mobile device*.
<a id="word-list--mobile-data"></a>

**mobile data**
    Use instead of *cellular data*.
<a id="word-list--mobile-device"></a>

**mobile device**
    Use *mobile device* when you're referring to more than phones (for
    example, tablets and phones). It's OK to use *phone* (without
    *mobile*) when the context is clear.
<a id="word-list--mobile-network"></a>

**mobile network**
    Use instead of *cellular network*.
<a id="word-list--mobile-phone"></a>

**mobile phone**
    If you're talking about more than phones, then use *mobile device*.
    It's OK to use *phone* (without *mobile*) when the context is
    clear.
<a id="word-list--mom-test"></a>

**Don't use: mom test**
    Don't use *mom test*, *grandmother test*, *grandma test*,
    or *girlfriend test*. Instead, use terms like *beginner user
    test* or *novice user test*.
<a id="word-list--monkey"></a>

**Don't use: monkey, monkey test**
    Don't use *monkey* to refer to people. When referring to tests, refer
    to the specific function. For example: *automated, random tests*.
<a id="word-list--multi"></a>

**multi***
    See [guidance about hyphens with prefixes](#hyphens--prefixes).
<a id="word-list--multi-cluster"></a>

**multi-cluster**
    Hyphenate. We generally prefer to close prefixed words, but this is an
    exception because it's an established term.
<a id="word-list--multi-region"></a>

**multi-region, multi-regional**
    Hyphenate when referring to a Google Cloud location that consists of more
    than one region.
    You can use *multi-regional* as an adjective in the context of
    multi-regions, but consider *multi-region* as
    an attributive noun instead, such as in "The dataset is in the EU
    multi-region location." Use *multiregional* in other contexts.
<a id="word-list--multi-service"></a>

**multi-service**
    Hyphenate. We generally prefer to close prefixed words, but this is
    an exception because it's an established term.
<a id="word-list--multi-tenancy"></a>

**multi-tenancy**
    Hyphenate. We generally prefer to close prefixed words, but this is
    an exception because it's an established term.
<a id="word-list--must"></a>

**must**
    Use to describe a required action or state (for example, "You must have
    the Editor role"). You can also write *you need* in order to convey a
    requirement.
    See also [can](#word-list--can), [could](#word-list--could),
    [may](#word-list--may), [might](#word-list--might),
    [should](#word-list--should), and [would](#word-list--would).
    For information about clarifying who's performing an action, see
    [Active voice](#voice).

<a id="word-list--letter-n"></a>

##### N

<a id="word-list--na"></a>

**N/A**
    Not *NA*. Spell out as *not available* or *not applicable*
    on first reference.
<a id="word-list--name-server"></a>

**name server**
    Not *nameserver*.
<a id="word-list--namespace"></a>

**namespace**
    Not *name space*.
<a id="word-list--native"></a>

**Avoid: native**
    Avoid using *native* to refer to people.
    When referring to software products, try to use a more precise
    term—for example, use *built-in* to describe a feature that's
    part of a product.
    The term *native* isn't necessarily clear—for example,
    *cloud-native* could mean that something was written for the cloud,
    or that it's built in to a cloud platform, or that it currently exists in
    a cloud platform.
    Alternatives to a term like *cloud-native* could include:
    *modern cloud*, *born in the cloud*, *cloud first*, and
    *cloud-born*.
<a id="word-list--navigation-bar"></a>

**navigation bar**
    Don't use to refer to a *navigation menu*. For more information, see
    [Navigation menu](#ui-elements--term-navigation-menu).
<a id="word-list--neither"></a>

**neither**
    Write *neither A nor B*, not *neither A or B*.
<a id="word-list--network-ip-address"></a>

**Don't use: network IP address**
    Don't use. Instead, use *internal IP address*.
<a id="word-list--new"></a>

**Avoid: new, newer**
    Avoid in timeless documentation because this word can become outdated.
    *New* also implies that the reader knows the older product and that
    labeling something as *new* is therefore meaningful.
    If you must use *new*, give the reader a reference point—for
    example, a version number or release date.
    Don't use *newer* to refer to a specific version of a product.
    Instead, use [*later*](#word-list--later). Make sure that you provide
    a version number or release date by which to understand *later*.

    In Android documentation, use
    [*higher*](#word-list--higher) instead of *later*.
    Recommended: The service's network
    analysis feature reports on network health.
    Not recommended: Network analysis, a
    new feature in the service, reports on network health.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--ninja"></a>

**Don't use: ninja**
    Don't use to refer to a person. Instead, use a term such as *expert*.
    OK to use in reference to companies, tools, software packages, and other
    entities that use the term in their names.
<a id="word-list--non"></a>

**non***
    See [guidance about hyphens with prefixes](#hyphens--prefixes).
<a id="word-list--nonce"></a>

**Avoid: nonce**
    Use with caution: this term has a secondary slang meaning that can cause
    confusion for global readers. Always define the term on first use, and
    only use it in specific technical contexts such as authentication and
    blockchain.
    In end-user documentation and other contexts, use a more descriptive
    phrase, such as *a number that will be used only once*.
<a id="word-list--non-key"></a>

**non-key**
    An exception to our usual preference for closed forms.
<a id="word-list--noops"></a>

**Don't use: NoOps**
    Don't use. Instead, use *fully managed*. If you must include the
    term, define it at first use with language such as *fully managed* or
    *no operations*, but not *non-operational*. Don't use
    *noops*.
    For an instruction that does nothing, use
    [*no-op*](https://wikipedia.org/wiki/NOP_(code)) or the
    specific instruction name for your context.
<a id="word-list--nosql"></a>

**NoSQL**
    Not *No-SQL* or *No SQL*.
<a id="word-list--notification-drawer"></a>

**(Android) notification drawer**
    In Android contexts, don't hyphenate. Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--now"></a>

**Avoid: now**
    Avoid when describing features of products or services because this word
    is implied.
    If the intent of the text is a comparison between past and present, you
    can use *now*—for example, "In versions of the tool earlier
    than 1.10, you could use only the default value, but now you can assign a
    custom value."
    Recommended: This feature lets you use
    combinations of user properties.
    Not recommended: This feature now lets
    you use combinations of user properties.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--nuke"></a>

**Don't use: nuke**
    Don't use. Instead use *remove* or *attack*. For example, a
    *denial-of-service attack*.

<a id="word-list--letter-o"></a>

##### O

<a id="word-list--oauth-20"></a>

**OAuth 2.0**
    Not *OAuth 2*, *OAuth2*, or *Oauth*.
<a id="word-list--off-the-shelf"></a>

**Don't use: off-the-shelf, commercial off-the-shelf (COTS)**
    Use more widely understood terms like *ready-made*, *prebuilt*,
    *standard*, or *default*.
<a id="word-list--old"></a>

**Avoid: old, older**
    Don't use to refer to a previous version of a product. Instead, use
    [*earlier*](#word-list--earlier).
    Make sure that you provide a version number by which to understand
    *earlier*.
    In Android documentation, use
    [*lower*](#word-list--lower) instead of *earlier*.
    Recommended: This functionality
    doesn't work in versions earlier than 1.17.0.
    Not recommended: This functionality
    doesn't work in older versions.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--omnibox"></a>

**Don't use: omnibox**
    Don't use. Instead, use *address bar*.
<a id="word-list--once"></a>

**once**
    If you mean *after*, then use *after* instead of *once*.
<a id="word-list--on-premises"></a>

**on-premises**
    Not *on prem*, *on premise*, or *on-premise*. Hyphenate
    when used as any part of speech.
    Use to refer to a customer's resources that they manage in their own
    facilities. Don't use *peer*.
    It can be acceptable to use *on-premises* as a noun when it would be
    awkward to repeatedly write out a full phrase like *an on-premises
    environment*. However, it's preferable to use the more complete phrase
    whenever possible.
    Recommended: An on-premises database.
    Recommended: The database runs
    on-premises.
    OK: Moving data from on-premises to
    Google Cloud.
<a id="word-list--os"></a>

**OS**
    OK to use as a shortening of "operating system."
<a id="word-list--outpost"></a>

**Don't use: outpost**
    Don't use. Instead, use *channel*.
    Recommended: social media channels
<a id="word-list--out"></a>

**Avoid: outside the box, out of the box, out-of-the-box**
    Avoid using in a figurative way. OK to use literally.
<a id="word-list--overview-screen"></a>

**Don't use: (Android) overview screen**
    In Android documentation, don't use. Instead, use *recents screen*.

<a id="word-list--letter-p"></a>

##### P

<a id="word-list--paas"></a>

**PaaS**
    Write out on first mention: *platform as a service (PaaS)*.
<a id="word-list--page"></a>

**page**
    Use *page* to refer to the following:

    - A whole web page, which can include text, images, links, banners, navigational panes,
      and other features.
    - A sub-page of a [console](#word-list--console) in particular.

    See also
    [documentation or document or documents](#word-list--documentation).
    Recommended: To refresh the page, press `F5`.
<a id="word-list--parameter"></a>

**parameter**
    In our API documentation, *parameter* is usually short for *query
    parameter*; it's a `NAME=VALUE` pair
    that's appended to a URL in an HTTP `GET` request. In some
    contexts, however, the term can have other meanings.
<a id="word-list--parent-child"></a>

**parent-child or parent/child**
    Not *parent – child* or *parent—child*.
<a id="word-list--path"></a>

**path**
    Avoid using *filepath*, *file path*, *pathname*, or *path
    name* if possible.
<a id="word-list--peer-gateway"></a>

**peer gateway**
    Don't use *on-premises gateway* when you mean a *peer gateway*.
    A peer gateway can be an on-premises device or service or another cloud
    gateway.
<a id="word-list--peer-network"></a>

**peer network**
    Don't use *on-premises network* when you mean a *peer network*.
    A peer network can be an on-premises network or another cloud network.
<a id="word-list--peering-zone"></a>

**peering zone**
    Not *peer zone*.
<a id="word-list--per"></a>

**per**
    To express a rate, use *per* instead of the division slash (/),
    unless space constraints require the use of the slash. For more
    information, see [Units of
    measurement](#units-of-measure--rates).
    Avoid *per* in contexts other than rate units.
    Recommended: requests per day
    Recommended: create a policy for each
    Pod
    Recommended: according to the style
    guide
    Recommended: in response to your
    request
    Not recommended: requests/day
    Not recommended: create a policy per
    Pod
    Not recommended: per the style guide
    Not recommended: as per your request
<a id="word-list--performant"></a>

**Avoid: performant**
    Avoid where possible. Instead, use a more precise term.
    Recommended: an accurate machine
    learning model
    Not recommended: a performant machine
    learning model
<a id="word-list--persist"></a>

**persist**
    Don't use as a transitive verb. It's best to avoid using as a verb at all,
    especially in [passive voice](#voice).
    Recommended: To make the token
    persistent ...
    OK: To make the token persist ...
    Not recommended: The token is persisted
    ...
    Not recommended: To persist the token
    ...
<a id="word-list--persistent-disk"></a>

**persistent disk**
    Not *PD*.
        Lowercase except at the start of a sentence.
<a id="word-list--pii"></a>

**personally identifiable information (PII)**
    Some government agencies use the less common term *personally
    identifying information*; use this alternate term only in contexts
    where you're referring to a document that uses this term.
<a id="word-list--pets-versus-cattle"></a>

**Don't use: pets versus cattle, pets vs. cattle, pets v. cattle**
    Don't use. Instead, use more precise terms like *persistent versus
    dynamic* or *manually configured versus automated*. For more
    information, see
    [Avoid
    figurative language](#inclusive-documentation--figurative-language).
<a id="word-list--plain-text"></a>

**plain text**
    In most contexts, use *plain text*, but use *plaintext* in a
    cryptography context.
<a id="word-list--please"></a>

**Avoid: please**
    Don't use *please* in the normal course of explaining how to use a
    product, even if you're explaining a difficult task.
    Don't use the phrase *please note*.
    Use *please* only when you're asking for permission or
    forgiveness—for example, when what you're asking for benefits you,
    inconveniences a reader, or suggests a potential issue with a product.
    Recommended: If the issue persists,
    please contact your account representative.
    For more information, see
    [voice and tone](#tone--politeness).
<a id="word-list--plugin"></a>

**plugin (noun), plug-in (adjective), plug in (verb)**
    Use the noun form *plugin* when referring to the software component. Use the adjective
    form *plug-in* when referring to the action of installing a software component. Use the
    verb form *plug in* when you're describing the process of installing a software
    component.
<a id="word-list--pm"></a>

**PM**
    See [AM, PM](#word-list--am-pm).
<a id="word-list--point-to"></a>

**point to**
    Use to refer to the action of pointing the mouse pointer (focus). This
    action doesn't imply a length of time waiting for the UI to react to user
    action.
    This is similar to the action [hold the
    pointer over (hover)](#word-list--hold-the-pointer-over). In most cases, it's better to use the verb
    phrase *hold the pointer over* if you want the user to wait for the
    UI to react.
<a id="word-list--pojo"></a>

**POJO**
    If you're not actually writing about a Plain Old Java Object for a Java
    audience, use *simple object*. You can write *a simple object,
    similar to a POJO in Java* if that helps your audience.
<a id="word-list--pop"></a>

**PoP**
    Acronym for *point of presence*.
    Recommended: point of presence (PoP)
    Not recommended: point of presence
    (POP)
<a id="word-list--pop-up"></a>

**pop-up, popup**
    Don't use.
    To describe a window that appears and asks for, or presents, additional
    information, use [*dialog*](#word-list--dialog).
    To describe a menu that rises from an interface (such as a right-click
    context menu), use *menu*.
<a id="word-list--populate"></a>

**populate**
    OK to use if you're writing about a process populating a table or other
    entity. If you're writing about a person, use *fill in*.
    Recommended: The SQL command
    populates the table with sample data.
    Recommended: When you have finished
    filling in the form ...
    Not recommended: When you have
    finished populating the form ...
<a id="word-list--port"></a>

**port**
    Use *listen on* (not *to*).
<a id="word-list--portal"></a>

**Avoid: portal**
    Don't use to refer to the Google Cloud console. For more information, see
    [console](#word-list--console).
<a id="word-list--possible"></a>

**Don't use: possible**
    Don't use *possible* or *impossible* to mean *you can* or
    *you can't*.
<a id="word-list--postgresql"></a>

**PostgreSQL**
    If the UI uses the name *Postgres*, it's OK to match the UI. Don't
    use *PostgreSQL*.
<a id="word-list--postmortem"></a>

**Avoid: postmortem**
    Avoid in general usage. Instead, use *retrospective*.
    In disaster recovery (DR) and DevOps contexts, use *blameless
    postmortem*.
<a id="word-list--practitioner"></a>

**practitioner**
    Avoid using without any supporting information to define the roles that
    you're referring to.
    Recommended: The framework describes
    best practices for architects, developers, administrators, and other cloud
    practitioners.
    Not recommended: The framework
    describes best practices for cloud practitioners.
<a id="word-list--pre"></a>

**pre***
    See [guidance about hyphens with prefixes](#hyphens--prefixes).
<a id="word-list--prebuilt"></a>

**prebuilt**
    Not *pre-built*.
<a id="word-list--precapture"></a>

**precapture**
    Not *pre-capture*.
<a id="word-list--preemptible"></a>

**preemptible**
    Not *pre-emptible* or *pre-emptive*.
<a id="word-list--pre-existing"></a>

**pre-existing**
    Not *preexisting*.
<a id="word-list--preferred-pronouns"></a>

**Don't use: preferred pronouns**
    Don't use. Instead, use *pronouns*.
<a id="word-list--prerecorded"></a>

**prerecorded**
    Not *pre-recorded*.
<a id="word-list--pre-shared-key"></a>

**pre-shared key**
    Not *preshared key*.
<a id="word-list--presently"></a>

**Avoid: presently, at present**
    Avoid because this word or phrase is implied. The word or phrase can also
    prematurely disclose product or feature strategy or inappropriately imply
    that a product or feature might change.
    See also [as of this writing](#word-list--as-of-this-writing) and
    [currently](#word-list--currently).
    Recommended: This setting is required.
    Not recommended: At present, this
    setting is required.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--press"></a>

**press**
    Use when referring to pressing a key or a key combination to cause an
    action to occur. Also use for mechanical buttons.
    For on-screen and soft (capacitive) buttons, use *tap*.
    Recommended: Press
    `Control+C` (or `Command+C` on macOS).
<a id="word-list--presubmit"></a>

**presubmit**
    Not *pre-submit*.
<a id="word-list--primitive"></a>

**Avoid: primitive**
    Use with caution. Don't use *primitive* in a disparaging sense.
<a id="word-list--project"></a>

**(Cloud) project**
    In Google Cloud documentation, use *Google Cloud project* on first
    mention and in any context in which there might be ambiguity about what
    kind of project you're referring to.
<a id="word-list--pros"></a>

**Don't use: pros**
    Don't use. Instead, use a more precise term, such as *advantages*.

<a id="word-list--letter-q"></a>

##### Q

<a id="word-list--quick"></a>

**Avoid: quick, quickly**
    What might be quick for you might not be quick for others. Try
    eliminating this word from the sentence because usually the same meaning
    can be conveyed without it.
<a id="word-list--quota"></a>

**quota**
    In API contexts, often refers to API usage limits. Where possible, it's
    best to use a more specific term, such as *usage limit*; the word
    *quota* means many different things to many different people.
    In some contexts, such as Google Cloud documentation, the standard term is
    *quota*, so use that term.

<a id="word-list--letter-r"></a>

##### R

<a id="word-list--rdp"></a>

**RDP**
    Don't use as a verb. Instead, use *connect using RDP*. If it's
    clear from context that they're using RDP, it's OK to use *connect*.
<a id="word-list--re"></a>

**re***
    See [guidance about hyphens with prefixes](#hyphens--prefixes).
<a id="word-list--read-only"></a>

**read-only**
    Not *read only*. Always hyphenate *read-only*.
<a id="word-list--recents-screen"></a>

**(Android) recents screen**
    In Android contexts, use instead of *overview screen*.
<a id="word-list--redline"></a>

**Don't use: redline**
    Don't use as a verb. Instead, use precise terms appropriate to the
    context.
    In the context of editing or providing a review, refer to those actions or
    to *tracking changes*.
    In the context of setting priorities and planning work, refer to those
    actions or to *priority lining*.
<a id="word-list--regex"></a>

**Don't use: regex**
    Don't use. Instead, use *regular expression*.
<a id="word-list--rehost"></a>

**rehost**
    Use to describe the migration of an app or workload with no changes or
    minimal changes to that app or workload. Also known as *lift and shift*. For more
    information, see [Rehost: lift and shift](https://cloud.google.com/architecture/migration-to-gcp-getting-started#rehost_lift_and_shift) in the Cloud Architecture Center.
    On first mention, associate rehost with lift and shift. Okay to use *rehosting* as needed
    after first mention.
    Recommended: You can use this reference architecture to
    efficiently rehost (lift and shift) on-premises applications to the cloud.
    Recommended: The first step to modernization is to rehost
    your application in the cloud (also known as lift and shift).
    Don't use *the forklift approach*.
<a id="word-list--repo"></a>

**Don't use: repo**
    Don't use. Instead, use *repository*.
<a id="word-list--rest"></a>

**Don't use: Representational State Transfer**
    Don't use. To people unfamiliar with REST, this acronym expansion is
    meaningless; it's better to refer to it as REST and not explain what it
    stands for.
<a id="word-list--reservation"></a>

**Don't use: reservation, off the**
    Don't use.
<a id="word-list--resource-record-set"></a>

**resource record set**
    Not *resource recordset*.
<a id="word-list--retarded"></a>

**Don't use: retarded**
    Don't use. If you are referring to a system or component being slowed,
    use the word *slowed*.
<a id="word-list--retriable"></a>

**Don't use: retriable, triable**
    Don't use *retriable* or *triable*, unless a code item uses that
    spelling. Outside of code font, write around the term.
<a id="word-list--retryable"></a>

**Avoid: retryable, tryable**
    Where possible, write around *retryable* and *tryable*. For
    example, write out *you can try it again* or *can be tried
    again*.
<a id="word-list--review"></a>

**review**
    If you mean "read, potentially for the first time," then use *read*
    instead of *review*.
    If you mean "read critically, commenting on problems" (as in *code
    review*), then *review* is fine.
    Avoid using phrasing like "If you've never heard of OAuth, then review the
    OAuth documentation."
<a id="word-list--rfc"></a>

**RFC**
    When referencing an RFC specification, use a space between *RFC* and
    the number (for example, *RFC 2318*).
<a id="word-list--roll-out"></a>

**Avoid: roll out**
    Don't use to mean a sudden or instantaneous launch. If you use *roll
    out*, define what you mean. When possible, use a more precise,
    non-figurative term like *gradual*, *in stages*, *phases*,
    or *progressive*.
<a id="word-list--rtfm"></a>

**Don't use: RTFM**
    Don't use. Instead, use a more precise phrase like "For more information,
    see ...."
<a id="word-list--runbook"></a>

**runbook**
    Not *run book*.
<a id="word-list--runtime"></a>

**runtime, run time**
    Use the noun *runtime* when referring to the environment in which
    software runs, such as a Ruby or Java runtime.
    Use the noun phrase *run time* when referring to the time during
    program execution when something occurs, as contrasted with *compile
    time*, for example.
    Recommended: The profiler collects
    data at run time, and the scheduler uses this data at compile time to
    improve performance for subsequent runs.
    Recommended: The App Engine standard
    environment has two generations of runtime environments. The
    second-generation runtimes significantly improve the capabilities of App
    Engine.

<a id="word-list--letter-s"></a>

##### S

<a id="word-list--saas"></a>

**SaaS**
    Write out on first mention: *software as a service (SaaS)*.
<a id="word-list--sane"></a>

**Don't use: sane**
    Don't use. Instead use a word like *valid* or *sensible*.
<a id="word-list--sanity-check"></a>

**Don't use: sanity check**
    Don't use. Instead, use a term like *quick check*, *confidence
    check*, *preliminary check* or *coherence check*.
<a id="word-list--sap"></a>

**SAP**
    Pronounced as the individual letters *S*, *A*, *P*, so
    write *an SAP system*, not *a SAP system*. For more information, see
    [Indefinite articles before abbreviations](#abbreviations--articles).
<a id="word-list--scale"></a>

**scale**
    Don't use *scale* alone to say that something is large or increasing.
    Include supporting words to indicate magnitude or direction of change in
    magnitude, whether scaling up or down, such as when you change a machine
    type to add or remove CPUs or RAM, or scaling out or in, such as adding or
    removing instances from a group.
    Recommended: The system performs
    better at a larger scale.
    Not recommended: The system performs
    better at scale.
    Recommended: The system scales up
    quickly, but it scales down more slowly.
    Not recommended: The system scales
    quickly.
<a id="word-list--screenshot"></a>

**screenshot (noun)**
    Not *screen shot* or *screensnap*.
    Don't use as a verb; instead, use *take a screenshot*.
<a id="word-list--scroll"></a>

**scroll**
    OK to use *scroll* as a verb, but if possible, instead use a term
    that isn't specific to implementation. For example, write *go to the
    section*, instead of *scroll to the section*.
    If you use *scroll*, don't use directional language
    like *scroll up*. For more information, see
    [Accessibility](#accessibility--document-rendering).
<a id="word-list--search"></a>

**Search (as part of product name)**
    Capitalize *Search* when referring to a product like Google Search.
<a id="word-list--search-console"></a>

**Search Console**
    Capitalize each word in *Search Console*.
<a id="word-list--see"></a>

**see**
    OK as a general term and when referring to links and cross-references. Our
    research indicates that language relating to sight is OK for a wide range
    of readers. For more information, see
    [Cross-references and linking](#cross-references).
<a id="word-list--select"></a>

**select**
    Use to describe choosing an item from among multiple options, selecting
    text, or marking a checkbox.
    Recommended: Select **Automatically
    check for updates**.
    Not recommended: Check
    **Automatically check for updates**.
<a id="word-list--sensitive"></a>

**sensitive**
    *Sensitive* data is data for which the release might be harmful. See
    [confidential](#word-list--confidential).
<a id="word-list--service"></a>

**service**
    It's OK to refer to Google products, such as Google Kubernetes Engine or
    Compute Engine, as *services*. However, if the term *services*
    leads to ambiguity, then use the product names.
<a id="word-list--service-level-agreement"></a>

**service level agreement**
    Lowercase when referring to service level agreements in general.
    It's OK to use title case (*Service Level Agreement*) when referring
    to a specific document.
    OK to abbreviate as *SLA* after first use.
<a id="word-list--service-level-indicator"></a>

**service level indicator**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
    OK to abbreviate as *SLI* after first use.
<a id="word-list--service-level-objective"></a>

**service level objective**
    Lowercase except at the beginning of a sentence,
    heading, or list item.
    OK to abbreviate as *SLO* after first use.
<a id="word-list--setup"></a>

**setup (noun or adjective), set up (verb)**
<a id="word-list--sexy"></a>

**Don't use: sexy**
    Don't use. Instead, use precise, positive words, such as *fast*,
    *powerful*, or *elegant*.
<a id="word-list--sha-1"></a>

**SHA-1**
    Not *SHA1*, except in string literals/enums and in hyphenated phrases
    such as *HSA-SHA1*.
<a id="word-list--shall"></a>

**Avoid: shall**
    Avoid *shall* except under advice from a lawyer. For more
    information, see [should](#word-list--should).
<a id="word-list--she"></a>

**Avoid: she, her, hers**
    Don't use a gendered pronoun except for a specific individual of known
    gender. Use *they* and *their* for the general singular pronoun.
<a id="word-list--sherpa"></a>

**Don't use: sherpa**
    If possible, use a more precise term. For example, if you mean
    *guide*, use that term.
<a id="word-list--shift-left"></a>

**Avoid: shift left**
    In general, avoid using this term to mean moving something earlier in
    time. Instead, use a less figurative phrase, such as *shift earlier*
    or *move to an earlier phase*. This figurative term relies on the
    non-universal assumption that the natural flow is from left to right.
    It's OK to use *shift left* and *shift right* in the context of
    binary multiplication and division.
<a id="word-list--should"></a>

**Avoid: should, should be**
    Generally avoid.
    Because *should* is ambiguous by definition, it can be problematic. For more information
    and alternatives, see
    [Word choice for recommendations and requirements](#prescriptive-documentation--word-choice).
    See also [can](#word-list--can), [could](#word-list--could),
    [may](#word-list--may), [might](#word-list--might),
    [must](#word-list--must), and [would](#word-list--would).
<a id="word-list--sign-in"></a>

**sign-in (noun or adjective), sign in (verb)**
    Not *log in* or *signin*.
<a id="word-list--sign-into"></a>

**Don't use: sign into**
    Don't use. Instead, use *sign in to*.
<a id="word-list--sign-on"></a>

**Don't use: sign-on, sign on**
    Don't use either form on its own. Use the hyphenated version as part of
    *single sign-on*.
<a id="word-list--sign-out"></a>

**sign-out (noun or adjective), sign out (verb)**
    Not *log out* or *signout*.
<a id="word-list--simple"></a>

**Avoid: simple, simply**
    What might be simple for you might not be simple for others. Try
    eliminating this word from the sentence because usually the same meaning
    can be conveyed without it.
<a id="word-list--since"></a>

**since**
    If you mean *because*, then use *because* instead of
    *since*. *Since* is ambiguous; it can refer to the passage of
    time. *Because* refers to causation or the reason for something.
<a id="word-list--single-most"></a>

**single most**
    Not *singlemost*.
<a id="word-list--single-pane-of-glass"></a>

**single pane of glass**
    Avoid. This term is used to favorably compare a centralized control and
    monitoring interface against the alternative of several disparate
    interfaces. It can almost always be replaced by *single interface* or
    *unified interface*.
<a id="word-list--single-sign-on"></a>

**single sign-on (noun or adjective)**
<a id="word-list--slave"></a>

**Don't use: slave**
    Don't use. Instead, use alternative terms appropriate to your domain, such
    as *worker* or *replica*.
    If you're replacing the terms *master* and *slave* together,
    then consider such combinations as *primary*/*secondary*,
    *primary*/*replica*, *original*/*replica*,
    *controller*/*worker*, *initiator*/*responder*,
    *mixer*/*leaf*, *aggregator*/*collector*,
    *publisher*/*subscriber*, *leader*/*follower*, and
    *active*/*standby*.
    If the command or code that you're documenting uses the literal word
    *slave*, then use this word only in direct reference to the code item
    ([formatted as code](#code-in-text)), make it clear what
    you're referring to, and use the new term thereafter. For example, "Invoke
    the secondary (`slave`) process directly when debugging issues
    between the primary and secondary processes."
    See also [master](#word-list--master).
<a id="word-list--slice"></a>

**Don't use: slice and dice**
    Don't use the phrase *slice and dice*. Instead, use specific terms
    appropriate to the task that you're describing. Some possible options
    include: *segment data for analysis* or *break information into
    smaller parts*.
<a id="word-list--smartphone"></a>

**Don't use: smartphone, smart phone**
    Don't use. Instead, use [*mobile phone*](#word-list--mobile) or
    *phone*. If you're talking about more than phones, then use *mobile
    device*. It's OK to use *phone* (without *mobile*) when the
    context is clear.
<a id="word-list--soon"></a>

**Avoid: soon**
    Avoid in timeless documentation because this word can become outdated. The
    word can also prematurely disclose product or feature strategy or
    inappropriately imply that a product or feature might change.
    See also [eventually](#word-list--eventually) and
    [future](#word-list--future).
    Recommended: This setting is
    optional.
    Not recommended: This setting is
    optional for existing applications but will soon be required for all
    applications.
    For more information, see
    [Timeless documentation](#timeless-documentation).
<a id="word-list--spin-up"></a>

**Avoid: spin up**
    As in *spin up an instance*. Avoid using *spin up* unless you're
    referring to a hard disk; instead, use a less colloquial term like
    *create* or *start*.
<a id="word-list--sql"></a>

**SQL**
    Refer to *a SQL* (pronounced "a sequel"), not *an SQL*. For more
    information, see
    [Indefinite articles before abbreviations](#abbreviations--articles).
<a id="word-list--ssh"></a>

**ssh and SSH**
    Don't use `ssh` or SSH as a verb. SSH is a secure
    communications protocol; `ssh` is a utility.
    Recommended: To establish an SSH
    connection, use the `ssh` command.
    Recommended: Connect to the instance
    by using SSH.
        Not recommended: `ssh` into
        your remote shell.
<a id="word-list--sshing"></a>

**Don't use: ssh'ing**
    Don't use. See also [ssh and SSH](#word-list--ssh).
    Recommended: When you use
    `ssh` to log in ...
<a id="word-list--startup"></a>

**startup (noun or adjective), start up (verb)**
<a id="word-list--static-external-ip-address"></a>

**static external IP address**
    Don't use *static IP address* or *external IP address* to refer
    to static external IP addresses.
<a id="word-list--status-bar"></a>

**status bar**
    Not *statusbar* or *status-bar*.
    Lowercase except at the beginning of a sentence,
    heading, or list item.
<a id="word-list--stonith"></a>

**Avoid: STONITH, STOMITH**
    Avoid using
    [graphic or
    metaphorical language](#inclusive-documentation--graphic-language). Instead, explain the relevant feature, such as
    *fence failed nodes*.
<a id="word-list--style-sheet"></a>

**style sheet**
    *Style sheet* and *stylesheet* are both acceptable spellings. However, be consistent
    with your choice throughout a given document.
<a id="word-list--sub-command"></a>

**sub-command**
    Not *subcommand*.
<a id="word-list--subnet"></a>

**subnet**
    OK to use as a shortening of *subnetwork*. Use the same term consistently throughout your
    document. For more
    information, see [Subnets vs. subnetworks](https://cloud.google.com/compute/docs/vpc/#subnets_vs_subnetworks).
<a id="word-list--subtree"></a>

**subtree**
    Not *sub-tree*.
<a id="word-list--subzone"></a>

**subzone**
    Not *sub-zone* or *sub zone*.
<a id="word-list--such-as"></a>

**such as**
    Use *such as* to introduce examples or draw comparisons. Note that *such as*,
    *like*, and *include* introduce non-exhaustive lists, so it's redundant to combine
    them with *etc.*, *so forth*, or *and more*. See also [etc.](#word-list--etc),
    [like](#word-list--like). For more information, see [Format
    examples](#format-examples).
<a id="word-list--surface"></a>

**surface**
    Avoid as a transitive verb; instead, use a more specific term, such as
    *make people aware of* or *expose*.
    Recommended: To make the audit logs
    available, you must configure the monitoring system.
    Not recommended: To surface audit
    logs, you must configure the monitoring system.

<a id="word-list--letter-t"></a>

##### T

<a id="word-list--tab"></a>

**tab**
    When referring to the sub-pages of a [console](#word-list--console), use
    *page* instead of *tab*.
<a id="word-list--table-name"></a>

**table name**
    Two words. Set specific table names in code font.
<a id="word-list--tablet"></a>

**tablet**
    *Tablet* is OK. If you don't know whether it's a tablet or a phone,
    use *device*.
<a id="word-list--tag"></a>

**tag**
    See [element](#word-list--element).
<a id="word-list--tap"></a>

**(Android) tap**
    In Android documentation, use for on-screen and soft (capacitive)
    buttons.
        Use instead of *click* when the environment is definitely a
        touch device.
        Use instead of *touch*. However, *touch & hold* (not *touch
        and hold*) is OK to use.
        For mechanical buttons, use [*press*](#word-list--press).
<a id="word-list--tap-and-hold"></a>

**Don't use: (Android) tap & hold, tap and hold**
    In Android documentation, don't use. Instead, use *touch & hold*.
    (Not *touch and hold*.)
<a id="word-list--tarball"></a>

**Don't use: tarball**
    Don't use. Instead, use *tar file*.
<a id="word-list--target"></a>

**target**
    Avoid using as a verb when possible, especially in reference to people.
    For some readers, *target* has aggressive connotations. Instead of
    "targeting" audiences, we try to attract them or appeal to them or make
    their lives easier.
    It's OK to use *target* as an adjective, as in *target
    audience*, but consider rephrasing for clarity. Alternatives
    include phrases such as *intended for*, *looking for*,
    *focused on*, and *interacting with*.
<a id="word-list--terminate"></a>

**Avoid: terminate**
    Avoid using as a synonym for *stop*. Instead, use words like
    *stop*, *exit*, *cancel*, or *end*.
    For a specific context where you can use *terminate* as a synonym for
    *stop*, see [Documenting
    command-line syntax](#code-syntax--linux-signals).
        In some contexts, such as telephony and networking, *terminate* has
            specific technical meanings that aren't synonyms for *stop*; in those
            contexts, you can use *terminate*.
<a id="word-list--textbox"></a>

**Don't use: text box, textbox**
    Don't use. Instead, use *box*. For more information, see
    [Text box](#ui-elements--term-textbox).
    In Google Cloud documentation, use
    *field* instead of *box*. For example, "In the **Instance**
    field, specify a value less than 64 characters long."
    In Google Workspace documentation, use
    *field* instead of *box*. For example, "In the **Instance**
    field, specify a value less than 64 characters long."
<a id="word-list--their"></a>

**their (singular)**
    See [*they*](#word-list--they).
<a id="word-list--then"></a>

**then**
    Although it is common in casual usage to omit the word *then* in *if...then*
    statements, you should include helper words like *then* in technical documentation. For
    more information, see
    [Use clear, precise, and unambiguous language](https://developers.google.com/style/translation#clear-language).
<a id="word-list--they"></a>

**they (singular)**
    This is our preferred gender-neutral pronoun. Whether used as singular
    or plural, it always takes the plural verb. For example, "A user
    authenticates their identity by entering their password." See also [gender-neutral he](#word-list--gender).
<a id="word-list--third-party"></a>

**third party (noun), third-party (adjective)**
    Spell as *third party* when used as a noun and as *third-party* when used as an
    adjective.
    Avoid abbreviating to *3rd party* or *3rd-party*. For more information, see [Ordinal numbers](#numbers--ordinal-numbers).
<a id="word-list--this-that"></a>

**this, that**
    Where possible, put a noun after *this* or *that* for clarity.
    If doing so results in clunky prose, then don't do it; but even then, try
    thinking about what the noun would be. If you aren't sure what noun
    *this* or *that* refers to, then consider rephrasing—otherwise, your reader
    probably won't know what noun you're referring to, either.
<a id="word-list--time-frame"></a>

**timeframe**
    Not *time frame*. Avoid where possible, or use an alternative such as
    *period*, *schedule*, *deadline*, or *when*. But if
    you do use it, then write it as one word.
<a id="word-list--timeout"></a>

**timeout (noun), time out (verb)**
<a id="word-list--time-stamp"></a>

**timestamp**
    Not *time stamp*.
<a id="word-list--ttl"></a>

**time to live**
    Not *time-to-live*. Abbreviate as *TTL* after first use.
<a id="word-list--time-zone"></a>

**time zone (noun), time-zone (adjective)**
    Spell as *time zone* when used as a noun and as *time-zone* when used as an
    adjective. See also [wake lock (noun), wake-lock (adjective)](#word-list--wake-lock).
<a id="word-list--tldr"></a>

**Don't use: tl;dr**
    Don't use. Instead, use something like *To summarize*, or revise the
    sentence.
<a id="word-list--toolkit"></a>

**toolkit**
    Not *tool-kit* or *tool kit*.
<a id="word-list--touch"></a>

**Don't use: (Android) touch**
    In Android documentation, don't use. Instead, use *tap*. However,
    *touch & hold* is OK to use.
<a id="word-list--touch-and-hold"></a>

**(Android) "touch & hold"**
    Not *touch and hold*.
<a id="word-list--touchscreen"></a>

**touchscreen**
    Not *touch screen*
<a id="word-list--traditional"></a>

**Avoid: traditional**
    If possible, use a more precise term.
    Recommended: Conventionally, Python
    function names are lowercase, with words separated by underscores.
    Not recommended: Traditionally, Python
    function names are lowercase, with words separated by underscores.
    Recommended: This tutorial explains
    how to migrate from an on-premises data warehouse to BigQuery.
    Not recommended: This tutorial
    explains how to migrate from a traditional data warehouse to BigQuery.
<a id="word-list--transpile"></a>

**transpile**
    Not *transcompile*.
<a id="word-list--tribal-knowledge"></a>

**Don't use: tribal knowledge, tribal wisdom**
    Don't use. Instead, use a less figurative term to indicate knowledge held
    by a group of people.
<a id="word-list--trojan"></a>

**trojan**
    Lowercase when referring to malware.
<a id="word-list--turn-on"></a>

**Avoid: turn on**
    In procedures, use the appropriate label and action for the
    [UI element](#ui-elements) that the user interacts with.
    For turning on or activating an option or feature, use *turn on* or
    [enable](#word-list--enable) consistently. Use the same term consistently throughout your
    document.
    Recommended: To turn on Magic Mode,
    follow these steps.
    Recommended: In **Settings**, click
    the **Magic mode** toggle to the on position.
<a id="word-list--tutorial"></a>

**tutorial**
    OK to use. See [documentation](#word-list--documentation).
<a id="word-list--type"></a>

**Avoid: type**
    In general, use [enter](#word-list--enter) instead of *type* because
    there is typically more than one way to enter text than typing (such as
    pasting text or speaking).
<a id="word-list--typically"></a>

**typically**
    Use to describe what is usual or expected under normal circumstances.
    Don't use as the first word in a sentence, as doing so can leave the
    meaning open to misinterpretation.

<a id="word-list--letter-u"></a>

##### U

<a id="word-list--ui"></a>

**UI**
    Don't use generically to refer to a page or dashboard. Use a more specific
    term like [*page*](#word-list--page) or
    [*console*](#word-list--console). If a specific term is unavailable,
    use *web interface*.
    Recommended: In the Google Cloud
    console
    Recommended: On the **Cloud Tasks**
    page
    Recommended: In the Secure Source
    Manager web interface
    Not recommended: In the **Cloud
    Tasks** UI
<a id="word-list--unarchive"></a>

**Don't use: unarchive**
    Don't use. Instead, use *extract*.
<a id="word-list--uncheck"></a>

**Don't use: uncheck**
    Don't use to refer to clearing a check mark from a checkbox. Instead, use
    *clear*.
    Recommended: Clear **Automatically
    check for updates**.
    Not recommended: Uncheck
    **Automatically check for updates**.
    Not recommended: Deselect
    **Automatically check for updates**.
<a id="word-list--uncompress"></a>

**Don't use: uncompress**
    Don't use. Instead, use *extract*.
<a id="word-list--under"></a>

**Don't use: under**
    Don't use for a range of version numbers. Instead,
    use [*earlier*](#word-list--earlier).
    Don't use to refer to a position in the UI.
    Recommended: In the **Service account
    ID** field, enter a name.
    Recommended: For **Service account
    ID**, enter a name.
    Not recommended: Under **Service
    account ID**, enter a name.
<a id="word-list--unicode"></a>

**Unicode**
    Not *UNICODE*.
<a id="word-list--unix-like"></a>

**Unix-like**
    Not *Unixlike* or *Unix like*.
<a id="word-list--unix-epoch-time"></a>

**Unix epoch time**
    Use instead of *Unix time* or *epoch time* to refer to a
    point in time represented as a number of seconds since the Unix epoch
    (00:00:00 UTC on January 1, 1970), ignoring leap seconds.
<a id="word-list--unselect"></a>

**Don't use: unselect**
    Don't use. Instead, use *clear* for checkboxes, and *deselect*
    for other UI elements.
<a id="word-list--unsighted"></a>

**Don't use: unsighted**
    Don't use. See [blind](#word-list--blind).
<a id="word-list--untar"></a>

**Don't use: untar**
    Don't use. Instead, use *extract*.
<a id="word-list--unzip"></a>

**Don't use: unzip**
    Don't use. Instead, use *extract*.
<a id="word-list--us"></a>

**US**
    OK to use as an abbreviation for *United States*. Don't use
    *U.S.* or *U.S.A.* For more information, see [Periods with abbreviations](#abbreviations--periods).
<a id="word-list--user"></a>

**user**
    Use the word *user* only to refer to the user of the software that
    your reader is developing. Otherwise, address the reader as *you*
    and assume that they will complete the tasks that you're documenting. For
    more information, see [Second person and first
    person](#person).
<a id="word-list--user-base"></a>

**user base**
    Not *userbase*.
<a id="word-list--using"></a>

**using**
    Where *using* might have more than one interpretation, use *by
    using* to help clarify the logic of the sentence.
    Recommended: You can filter for data
    with specific attributes by using custom filters.
    Not recommended: You can filter for
    data with specific attributes using custom filters.
<a id="word-list--utf"></a>

**UTF**
    Include the hyphen in the names of Unicode encodings, such as
    *UTF-8*, *UTF-16*, and *UTF-32*.
<a id="word-list--utilize"></a>

**utilize, utilization**
    Use with caution. Don't use *utilize* when you mean *use*. It's
    OK to use *utilize* or *utilization* when referring to the
    quantity of a resource being used.
    Recommended: When CPU utilization
    exceeds 75%, the autoscaler adds more CPU resources.
    Recommended: To distribute network
    traffic, use a load balancer.
    Not recommended: To distribute network
    traffic, utilize a load balancer.

<a id="word-list--letter-v"></a>

##### V

<a id="word-list--v"></a>

**v (abbreviating *version*)**
    Use lowercase.
<a id="word-list--via"></a>

**Don't use: via**
    Don't use.
<a id="word-list--vice-versa"></a>

**Don't use: vice versa**
    Don't use. Instead, use a phrase like *the other way around*,
    *conversely*, or *otherwise*. In some contexts, vice versa is
    unclear or imprecise because in a complex sentence it's hard to know which
    two things are swapped with each other. In such cases, make it explicitly
    clear what two things are swapped.
<a id="word-list--virtual-machine-instance"></a>

**virtual machine (VM) instance**
    Use when first introducing virtual machines on a given page. For
    subsequent mentions, you can use *VM instance* or *VM*.
    For Google Cloud: on first mention of a Compute Engine VM,
    use *Compute Engine instance* and then use *compute instance*
    throughout the rest of the document. If you need to indicate other types of
    VMs, use *VM*, *VM instance*, or *bare metal instance*.
    See also [GKE node](#word-list--gke-node).
<a id="word-list--visually-challenged"></a>

**Don't use: visually challenged**
    See [blind](#word-list--blind).
<a id="word-list--vlan"></a>

**VLAN attachment**
    Don't use the following: *interconnect attachment (VLAN)*,
    *Interconnect attachment*, *Cloud Interconnect attachment*, or
    any variation thereof. See also
    [interconnectAttachment](#word-list--interconnect-attachment).
<a id="word-list--voila"></a>

**Don't use: voila**
    Don't use.
<a id="word-list--voodoo"></a>

**Don't use: voodoo**
    Don't use. Instead, use a term like *mysterious*, *complicated*,
    or *nondeterministic*.
<a id="word-list--vs"></a>

**Don't use: vs.**
    Don't use *vs.* as an abbreviation for *versus*; instead, use
    the unabbreviated *versus*.

<a id="word-list--letter-w"></a>

##### W

<a id="word-list--wake-lock"></a>

**wake lock (noun), wake-lock (adjective)**
    Spell as *wake lock* when used as a noun and as *wake-lock* when used as an
    adjective. See also [time zone (noun), time-zone (adjective)](#word-list--time-zone).
<a id="word-list--walkthrough"></a>

**walkthrough**
    Not *walk-through*.
<a id="word-list--war-room"></a>

**Don't use: war room, warroom, war-room**
    Don't use. Instead, use a more precise term to describe the activity or
    team. Depending on context, possible alternatives include *rapid
    response team*, *situation response team*, *situation room*,
    *incident-management team*, or *media monitoring room*.
<a id="word-list--warm"></a>

**warm**
    When possible, avoid [jargon](#jargon) like *warm
    failover*, *warm standby*, and *warm spare*. If you use one
    of these phrases, define it on first use and use it consistently
    throughout the document.
<a id="word-list--we"></a>

**we**
    Don't use *we* (or other first-person plural pronouns such as
    *our* or *us*) to address the reader who is performing the
    tasks that you're documenting. Instead, use *you*.
    It's OK to use *we* to refer to the organization that's represented
    as the author of the document as long as the antecedent is clear. For more
    information, see
    [Second person and first person](#person).
<a id="word-list--web"></a>

**web (lowercase)**
<a id="word-list--wasm"></a>

**WebAssembly, Wasm**
    Use the capitalization established in the
    [WebAssembly specification](https://webassembly.github.io/spec/core/intro/introduction.html#introduction).
<a id="word-list--web-application-firewall"></a>

**web application firewall (lowercase)**
<a id="word-list--webmaster"></a>

**Don't use: webmaster, web master**
    Don't use. Instead, use a more precise term to describe the specific role,
    such as *website owner*, *website administrator*, *web content
    manager*, *owner of a site*.
<a id="word-list--web-server"></a>

**web server**
    Not *webserver*.
<a id="word-list--whether"></a>

**whether**
    - To decide whether it's more appropriate to use *if* or
      *whether*, see [Grammar Girl's
      discussion of *if* and *whether*](http://www.quickanddirtytips.com/education/grammar/if-versus-whether).
    - To decide whether you need to add *or not* when using
      *whether*, see [the New York
      Times's blog post about whether (or not)](http://afterdeadline.blogs.nytimes.com/2010/03/01/whether-or-not/).
<a id="word-list--while"></a>

**while**
    Don't use to indicate a contrast. Instead, use a more precise term, such
    as *although*.
    OK to use to refer to a period of time.
<a id="word-list--white-box"></a>

**Avoid: white-box**
    Avoid using *white-box*, *whitebox*, or *white box* to
    describe monitoring and testing. Consider using a more precise term for
    clarity.

    - For monitoring, use *introspective monitoring*.
    - For testing, use *clear-box testing*.
<a id="word-list--white-glove"></a>

**Avoid: white glove, white-glove, whiteglove**
    Avoid using. Instead use terms like *high-touch*, *premium*, or
    *platinum-level*.
<a id="word-list--whitehat"></a>

**Don't use: whitehat, white hat, white-hat**
    Don't use. Instead, use precise terms for the kind of compliance, such as
    *legal*, *ethical*, or *following the rules*.
<a id="word-list--white-label"></a>

**Avoid: white label, whitelabel, white-label**
    Don't use. Instead, use a more precise term for your context, such as
    *unbranded*, *unlabeled*, or *blank label*.
<a id="word-list--whitelist"></a>

**Don't use: whitelist, white list, white-list**
    Don't use. See [blacklist](#word-list--blacklist).
<a id="word-list--whitelisted"></a>

**Don't use: whitelisted, white listed, white-listed**
    Don't use. See [blacklist](#word-list--blacklist).
<a id="word-list--whitelisting"></a>

**Don't use: whitelisting, white listing, white-listing**
    Don't use. See [blacklist](#word-list--blacklist).
<a id="word-list--whitepaper"></a>

**whitepaper**
    Not *white paper*.
    When possible, use a more precise term. The term *whitepaper* has a variety of
    meanings in various contexts. If you must use the term *whitepaper*, also use descriptive
    terms to provide context.
<a id="word-list--whitespace"></a>

**whitespace**
    Not *white space*.
<a id="word-list--wildcard"></a>

**wildcard**
    Not *wild card*.
<a id="word-list--will"></a>

**will**
    Avoid. Applies equally to its past tense, *would*. See also
    [Present tense](#tense) and
    [Documenting future features](#future).
<a id="word-list--wish"></a>

**Don't use: wish**
    Don't use. Instead, use a word like *want* or *need*.
<a id="word-list--with"></a>

**with**
    Don't use *with* when expressing ownership:
        Recommended: A handset that has 2 GB
        of RAM.
        Not recommended: A handset with 2 GB
        of RAM.
    Don't use *with* when expressing use:
        Recommended: Use the debugging tool
        to debug.
        Not recommended: Debug this tool with
        the debugging tool.
<a id="word-list--workload"></a>

**workload**
    The term *workload* might refer to software, like an app or
    a service; to app resources, like data and infrastructure; or to physical
    components that work together.
    Where possible, use a more precise term to describe what you mean. If you
    use the term *workload*, define your meaning on first use as you
    normally would with jargon and other ambiguous terms.
<a id="word-list--world-wide-web"></a>

**Don't use: World Wide Web**
    Don't use. Instead, use *web*.
<a id="word-list--would"></a>

**Avoid: would**
    Avoid using. Instead, use *can* where possible.
    See also [can](#word-list--can), [could](#word-list--could),
    [may](#word-list--may), [might](#word-list--might),
    [must](#word-list--must), and [should](#word-list--should).
    For information about clarifying who's performing an action, see
    [Active voice](#voice).
    For information about tenses, see [Present
    tense](#tense).

<a id="word-list--letter-y"></a>

##### Y

<a id="word-list--ymmv"></a>

**Don't use: ymmv**
    Don't use. Instead, use something like *Your results might vary*.
<a id="word-list--you"></a>

**you**
    Use *you* instead of [*user*](#word-list--user) to address the
    reader of your document. For more information, see
    [Second person and first person](#person).

<a id="word-list--letter-z"></a>

##### Z

<a id="word-list--zippy"></a>

**Avoid: zippy**
    Don't use to refer to [expander arrows](#word-list--expander-arrow),
    unless you're specifically referring to the [Zippy widget](https://google.github.io/closure-library/api/goog.ui.Zippy.html)
    in Closure.

---

<a id="product-names"></a>

### Product names

*Source: <https://developers.google.com/style/product-names>*

This page describes how to use product names.

<a id="product-names--capitalize"></a>

#### Capitalize product names

In general, Google product names are in *title case*, sometimes called
*init-capped*, which means that every word is capitalized except for
prepositions like *of* or *on* and articles like *a* or
*the*. When you refer to a Google product, use title case except
when you're matching a UI label. For information about how to refer to UI
labels, see
[UI elements and interaction](#ui-elements).

When you write about any product, follow the official capitalization for the
names of brands, companies, software, products, services, features, and
terms defined by companies and open source communities.

- For example, if you're using Kubernetes-related terms, then follow
  the capitalization that's shown in the Kubernetes [Concepts
  documentation](https://kubernetes.io/docs/concepts/).

  Recommended in a Kubernetes
  context: A Job creates one or more Pods.

  Recommended: The Cloud Scheduler
  job publishes a message to a Pub/Sub topic at one-minute intervals.
- If an official name begins with a lowercase letter, then put it in
  lowercase even at the start of a sentence. But it's better to revise
  the sentence to avoid putting a lowercase word at the start, if
  possible.

  Recommended: You can use macOS to
  run the app.

  Not recommended: macOS can run the
  app.

<a id="product-names--feature-names"></a>

##### Feature names

A *feature* is a distinctive attribute or capability of a product.
Features are usually described in terms of what they can do as part of a
product. In general, feature names are lowercase, although there are
exceptions.

When you write about a feature, don't capitalize it unless the name is
officially capitalized. If you're unsure, follow the precedent that's set
by other documents that describe the feature. As with products, match
the capitalization of a UI label if you're referring to one.

For more general information about capitalization, see
[Capitalization](#capitalization).

<a id="product-names--shortening"></a>

#### Shorten Google product names

When referring to a Google product, sometimes you might want to abbreviate
the product name. For example, when you're referring to Google
Spreadsheets, it can be awkward to refer to it as Google Spreadsheets
every time; sometimes you might want to call it Spreadsheets.

Use the full trademarked product name. Don't abbreviate product names,
except in cases where you're matching a UI label. In such cases, make it
clear that you're referring to the Google product and not some other thing
with a similar name.

Also consider whether you need to refer to a product name throughout a
document, or if you can use a more general term. For example, if you've
established that you're talking about *Anthos Service Mesh*, you can
probably frame your discussion around the concept of *a service mesh*
throughout much of the document.

<a id="product-names--possessives"></a>

<a id="product-names--possessives-of-product-names"></a>

#### Possessives of product names

For information about forming possessives with product names, see
[Product, feature, and company names](#possessives--productu002c-featureu002c-and-company-names).

<a id="product-names--the-with-names"></a>

<a id="product-names--articles-before-product-names"></a>

#### Articles before product names

Don't use *the* before a product name unless you're using the name to
modify something else. *Do* use *the* before tool and API names.

Recommended: Using Cloud Datastore with Cloud Dataproc

Recommended: The Cloud Datastore options page

Recommended: The Google Cloud console

Recommended: The Transcoder API

Recommended: The `gcloud` CLI

Not recommended: Using the Cloud Datastore with Cloud
Dataproc

If you use a product name as a modifier with an indefinite article (*a* or *an*), pay
close attention to which article precedes the product name.

Recommended: An Anthos Service Mesh environment

Recommended: A Service Mesh environment

For more information about using articles, see [Articles](#articles).

<a id="product-names--multiple-products"></a>

<a id="product-names--use-service-to-refer-to-multiple-products"></a>

#### Use "service" to refer to multiple products

It's OK to refer to Google products as services, such as *the Google Kubernetes Engine
service* or *the Compute Engine service*. However, if the term *services* leads to
ambiguity, use the product names.

<a id="product-names--product-names-as-verbs"></a>

<a id="product-names--dont-use-product-names-as-verbs"></a>

#### Don't use product names as verbs

Don't use product names or feature names as verbs.

---

<a id="text-formatting"></a>

### Text-formatting summary

*Source: <https://developers.google.com/style/text-formatting>*

The page summarizes, and provides a quick reference for, many of the general text-formatting
conventions covered elsewhere in the style guide. For more information, see
[Visual formatting](#semantic-tagging--visual-formatting).

<a id="text-formatting--bold"></a>

**Bold**
    Use bold formatting, `<b>` or `**`, only for
    [UI elements](#ui-elements--formatting) and
    [run-in headings](#lists--types-of-lists), including at the beginning of
    [notices](#notices).
    Although a double underscore, `__`, can also indicate bold styling in Markdown, it
    can be difficult to distinguish in a text editor. It's best to use the double asterisk for bold in
    Markdown.
<a id="text-formatting--italic"></a>

**Italic**
    In general, use italics sparingly.
    When you're discussing or introducing terms, such as when defining terms or using
    *words as words*, use italics formatting, `<i>` or `_`. For more
    information, see
    [Use italics to discuss terms](#italics-terms)
    and
    [Format abbreviation introductions](#abbreviations--format-abbreviations).
    When you need to add emphasis to indicate importance, use italics, not bold or underline. But
    usually, your words can carry the emphasis without adding italics. To indicate
    [semantic emphasis](#semantic-tagging) in HTML, use the `em` element,
    which renders as italics in most contexts. To indicate emphasis in Markdown, use underscores
    (`_`), which render as italics; you can't do semantic tagging in Markdown.
    Although an asterisk, `*`, can also indicate italics in Markdown, we recommend
    underscores to make it easier for humans to distinguish italics from bold in the Markdown file.
    Italicize titles of books, movies, web series, and other full-length works, unless they're part
    of a link. For more information, see
    [Cross-references and linking](#cross-references).
    Italicize mathematical variables—for example, *x* + *y* = 3.
    Don't italicize mathematical operators such as the plus sign. For more information about
    formatting mathematical notation, see
    [Mathematical notation](#mathematical-notation--format-mathematical-notation).
    Italicize version variables—for example, version 1.4.*x*.
<a id="text-formatting--underline"></a>

**Underline**
    Reserve underlining for link text. For more information, see
    [Style link text](https://developers.google.com/style/cross-references#style-link-text).
<a id="text-formatting--code-font"></a>

**Code font**
    Use `<code>` in HTML or `` ` `` in Markdown to apply a monospace font
    and other styling to [code in text](#code-in-text), inline code, and user
    input.
    Use code blocks, `<pre>` or `` \`\`\` ``, for
    [code samples](#code-samples) or other blocks of code.
    Do not override or modify font styles inline.
    Use code font to mark up code, such as filenames, class names, method names, HTTP status codes,
    console output, and placeholders. For more information, see
    [Some specific items to put
    in code font](#code-in-text--some-specific-items-to-put-in-code-font).
<a id="text-formatting--capitalization"></a>

**Capitalization**
    Use American English style for
    [general capitalization](#capitalization).
    Use sentence case in all [headings,
    titles, and navigation](#capitalization--capitalization-in-titles-and-headings).
    Use all-capitals for [placeholders](#placeholders--placeholder-text).
<a id="text-formatting--quotation-marks"></a>

**Quotation marks**
    In general, use American English style when [punctuating
    quotations](#quotation-marks).
    For titles of shorter works—such as articles or episodes in a web series—put titles in quotation
    marks, unless they're part of a link.
<a id="text-formatting--font-style"></a>

**Font type, size, and color**
    Do not override global styles for [font type, size, or
    color](https://developers.google.com/style/fonts).
    Use [semantic HTML](#semantic-tagging) or Markdown to
    control the style of text on a page—for example, code tags in HTML (`<code>`)
    or backticks in Markdown (`` ` ``)—instead of manually styling text with a monospace
    font.
<a id="text-formatting--other-punctuation"></a>

**Other punctuation conventions**
    Don't use [ampersands (&)](#word-list--ampersand) as conjunctions or
    shorthand for *and*. Use *and* instead. That includes headings and navigation.
    **Exception**: It's okay to use *&* in cases where you need to refer to a UI
    element or the name of a menu that uses *&*.
    Put quotation marks and end punctuation outside of link text. For more information, see
    the [Punctuation around link text](https://developers.google.com/style/cross-references#punctuation)
    and [Quotation marks and italics](https://developers.google.com/style/cross-references#quotation-marks-italics)
    sections of the "Cross-references and linking" page.

<a id="text-formatting--more-resources"></a>

#### More resources

- [Mathematical notation](#mathematical-notation)

---

## General principles

<a id="accessibility"></a>

### Accessibility

*Source: <https://developers.google.com/style/accessibility>*

We write our developer documentation with accessibility in mind. This page is not an exhaustive
reference, but describes some general guidelines and examples that illustrate best practices to
follow. The
[World Health Organization](https://www.who.int/en/news-room/fact-sheets/detail/disability-and-health)
estimates that 15% of the world's population (more than 1 billion people) have an accessibility
need. When documentation is written with accessibility in mind, it improves the overall
experience for all readers.

For other writing best practices, see the following resources:

- [Write for a global audience](#translation)
- [Write inclusive documentation](#inclusive-documentation)
- [Voice and tone](#tone)

<a id="accessibility--general-dos-and-donts"></a>

#### General dos and don'ts

- Don't use ableist language. Avoid bias and harm when discussing disability and accessibility.
  For more information, see
  [Writing inclusive documentation](#inclusive-documentation).
- Ensure that readers can reach all parts of the document (including
  tabs, form-submission buttons, and interactive elements) by using only a keyboard,
  without a mouse or trackpad.
- Use a screen reader to test your documentation. This test can help you find accessibility
  issues in your content and is a good way to self-edit your content. To try out a screen reader,
  see [List of screen readers](https://wikipedia.org/wiki/List_of_screen_readers).
- In HTML, use [semantic
  tagging](#semantic-tagging). For example, use the `em` element only to
  indicate emphasis, not to indicate italics.
- In HTML, prefer
  [native
  elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element) over custom styles.
- Avoid unnecessary font formatting. (Screen readers explicitly describe
  text modifications.)
- If you're documenting a product that includes specialized accessibility
  features, then explicitly document those features. For example, the Google Cloud
  CLI (`gcloud` CLI) includes togglable accessibility features
  such as percentage progress bars and ASCII box rendering.
- Don't force line breaks (hard returns) within sentences and paragraphs. Line breaks might not
  work well in resized windows or with enlarged text.
- Avoid when possible [camel case](https://wikipedia.org/wiki/Camel_case) and
  [all caps](https://wikipedia.org/wiki/All_caps). Some screen readers read
  capitalized letters individually, and some languages are
  [unicase](https://wikipedia.org/wiki/Unicase). Follow
  [capitalization](#capitalization) guidelines.
- Depending on the screen reader (or personal settings), not all punctuation marks are read. Make
  sure that the same meaning is conveyed to the reader without punctuation marks. For that reason, avoid
  when possible the use of exclamation marks, question marks, and semicolons.
- Don't use *&* instead of *and* in headings, text, navigation, or
  tables of contents. However, it's OK to use *&* when referencing UI
  elements that use *&*, or in table headings and diagram labels where space
  constraints require abbreviation. Of course, it's fine to use `&`
  for technical purposes in code.

<a id="accessibility--ease-of-reading"></a>

#### Ease of reading

- Break up walls of text to aid in scannability. For example, separate
  [paragraphs](#paragraph-structure),
  create
  [headings](#headings),
  and use
  [lists](#lists).
- Use shorter sentences. Try to use fewer than 26 words per sentence.
- Define acronyms and abbreviations on first usage and if they're used infrequently.
- Use parallel writing structures for similar things. For example, start each list in the same
  format.
- Place distinguishing and important information of a paragraph in the first sentence to aid in
  scannability.
- Use clear and direct language. Avoid the use of double negatives and exceptions for exceptions.

  Recommended: You can continue without a
  path.

  Not recommended: A missing path won't
  prevent you from continuing.
- Left-align text for readability. Don't center or full-justify text.

<a id="accessibility--headings-and-titles"></a>

#### Headings and titles

Use descriptive headings and titles because they help a reader navigate their browser and the
page. It's easier to jump between pages and sections of a page if the headings and titles are
unique.

- Use a heading hierarchy.
- Don't skip levels of the heading hierarchy. For example, put an `h3` element
  only after an `h2` element.
- To change the visual formatting of a heading, use CSS rather than using a heading level that
  doesn't fit the hierarchy.
- Don't have empty headings or headings with no associated content.
- Tag headings using heading elements. In HTML: `h1`,
  `h2`, and so on. In Markdown: `#`, `##`, and so on.
- Use a level-1 heading for the page title or main content heading.

For more information and examples, see [Headings and titles](#headings).

<a id="accessibility--links"></a>

#### Links

- Use [meaningful link text](#cross-references--descriptive-link-text).
  Links should make sense when read out of context.
- Don't use *click here* or *read this document*. Some people who use screen readers
  jump from link to link to scan a page and need to understand what a link contains.
- Use *see* to refer to links and cross-references. For more information, see
  [see](#word-list--see).
- When a link does anything that the reader might not expect, such as downloading a file,
  opening in a new tab, or jumping to another section on the same page, explain that behavior when
  you link. For more information, see
  [Explain unexpected link behavior](#cross-references--explain-behavior).
- When possible, avoid adjacent links. Instead, put a character in between to separate them.

<a id="accessibility--lists"></a>

#### Lists

- In a
  [procedure](#procedures),
  make each instruction a
  [list item](#lists).
- Use lists to make it easier for the reader to follow the steps.

<a id="accessibility--images"></a>

#### Images

- For every image, provide an alt attribute. For alt attributes that contain
  [alt text](#images--alt-text), use alt text that adequately summarizes the
  intent of each image. If the image is purely decorative, use empty alt text.
- Don't present new information in images. Always provide an equivalent text explanation with
  the image.
- Don't repeat images unless absolutely necessary.
- Don't use images of text, code samples, or terminal output. Use actual text.
- Use SVG instead of PNG if available. SVGs stay sharp when you zoom in on the image.

For more information, see
[Text associated with images](#images--text-associated-with-images).

<a id="accessibility--videosu002c-recordingsu002c-and-gifs"></a>

#### Videos, recordings, and GIFs

- Provide captions, transcripts, or descriptions of audio and video content. For example, you
  can use the
  [autocaption feature](https://support.google.com/youtube/answer/6373554)
  in YouTube.
- Ensure that captions can be translated into major languages.
- Don't use flickering or flashing elements. They can cause anything from motion sickness
  to a seizure.

<a id="accessibility--buttons-and-icons"></a>

#### Buttons and icons

- For form-submission buttons, use the native HTML `button` element.
- An icon is a symbol or image that represents an object or a function. For information
  about using icons, see the [Buttons and icons](#ui-elements--buttons) section
  of the "UI elements and interaction" page.

<a id="accessibility--ui-navigation"></a>

#### UI navigation

When you use angle brackets (`>`) to document menu paths, add an
[`aria-label` attribute](https://www.w3.org/TR/WCAG20-TECHS/ARIA14.html)
to help screen readers interpret the brackets as "and then" instead of as
"greater than" or "keyboard arrow right". For more information and examples, see
[Menu bar](#ui-elements--term-menus).

<a id="accessibility--tables"></a>

#### Tables

- Introduce tables in the text preceding the table because not all screen readers preannounce
  tables.
- Use table headings for the first column and the first row only. Use the
  [`th` element](https://www.w3.org/TR/html4/struct/tables.html#edef-TH).
- If your tables include both row and column headings, then mark heading cells with the
  [`scope`
  attribute](https://www.w3.org/WAI/tutorials/tables/two-headers/).
- If your tables have more than one row containing column headings, then use the
  [`headers`
  attribute](https://www.w3.org/WAI/tutorials/tables/multi-level/) and make sure that the headings have unique IDs.
- Avoid when possible tables in the middle of a numbered procedure.
- Don't merge cells. Don't use `colspan` or `rowspan` attributes.
- Don't use tables unless it's the best method to present your information. Tables are
  challenging for screen readers. For more information, see
  [List or table](#tables--list-or-table).
- Don't present new information in tables through images or symbols alone; always provide a
  descriptive `alt` attribute for the image or symbol. For more information, see
  [Alt text](#images--alt-text).

For more information, see [Tables](#tables).

<a id="accessibility--interactive-elements"></a>

#### Interactive elements

Introduce an interactive element (such as a button that expands and collapses) in the text
preceding the element.

Recommended if practical: To see a list of
requirements, expand the **Requirements** section.

Recommended: To see a list of requirements,
click the expander arrow.

<a id="accessibility--forms"></a>

#### Forms

- Label every input field by using a `label` element.
- Place labels outside of fields.
- When you're creating an error message for form validation, clearly state
  what went wrong and how to fix it—for example: "Name is a required field."

<a id="accessibility--custom-css-and-javascript"></a>

#### Custom CSS and JavaScript

Try to use your site's standard styles and standard JavaScript code as much
as possible. However, if you do use custom styles or code, then follow these guidelines:

- Pick colors that respect
  [accessible color contrast
  ratios](https://webaim.org/resources/contrastchecker/) (4.5:1 for text).
- Don't use `visibility:hidden` or `display:none`. Both
  styles hide information from screen readers.
- Avoid when possible using mouseover events. But if you do use them, then add alternate
  focus and blur events for keyboard users.
- Ensure that any ordering and positioning defined in styles reflects the
  DOM and the reading order (such as left to right and top to bottom) of your page.

<a id="accessibility--document-rendering"></a>

#### Document rendering

Make sure that your document conveys all the information that you intended when you
view it in the following contexts:

- Without sound
- Using only sound
- Without images, including animation
- [Without color](https://colororacle.org/)
- Using a keyboard
- With screen magnification
- Without punctuation

Don't use color, size, location, or other visual cues as the primary way
of communicating information.

- If you're using color, an icon, or outline thickness to convey state,
  then also provide a secondary cue, such as a change in the text label.
- Refer to buttons and other elements by their label. For visual elements
  that have no text, don't try to describe the element. Instead, use the element's
  `aria-label`
  attribute if possible.
  For example:

  Recommended: Click **Save**.

  Recommended: Click **Notifications**.

  Not recommended: Click the bell icon.
- Don't use directional language to orient the reader, such as *above*, *below*,
  or *right-hand side*. This type of language doesn't work well for accessibility or for
  localization reasons. For example, what's on the right side for left-to-right languages
  appears on the left side for right-to-left languages.

  Don't use directional language to refer to a position in a document. For example, the text
  isn't *below* if it's being read by a screen reader. Instead, use *earlier*,
  *preceding*, or *following*.

  Recommended:
  In the preceding diagram, clients run jobs on multi-team or single-team clusters.

  Not recommended: In the diagram above,
  clients run jobs on multi-team or single-team clusters.

  If a [UI element](#ui-elements) is hard to find,
  [provide a screenshot](#images).

  Recommended:
  Click **Menu**.

  Not recommended: In the left-side
  panel, click the button with three lines.

<a id="accessibility--more-resources"></a>

#### More resources

- [Google's main
  accessibility page](https://www.google.com/accessibility/)
- [Web Content Accessibility
  Guidelines (WCAG) 2.0](https://www.w3.org/WAI/WCAG20/glance/)
- [Web Accessibility Initiative
  (WAI)](https://www.w3.org/WAI/)
- [Using ARIA](https://www.w3.org/TR/using-aria/)
- [Web Accessibility
  Tutorials](https://www.w3.org/WAI/tutorials/)

---

<a id="excessive-claims"></a>

### Excessive claims

*Source: <https://developers.google.com/style/excessive-claims>*

In documentation, don't make excessive claims. An *excessive claim* is an assertion
in the documentation that does any of the following:

- Makes a statement about performance or cost that isn't easily verifiable with data
  that's available to the reader.
- Makes a statement about security that would be invalidated by a security incident.
- Makes a statement that might be interpreted as subjective or even disparaging,
  especially about third-party products.

When you're assessing whether some text makes an excessive claim, take into account
not just what's true today about a product's performance, cost, security, or
functionality, but what might be true in the future.

Consider the following guidelines:

- When you describe products, avoid superlatives like *best*, *simplest*,
  *fastest*, *never*, and *always*. Similarly, be
  careful about words like *ensure* and *guarantee* and use them only when
  something can truly be ensured or guaranteed.
- If you make specific performance claims—how fast a product is, how much storage
  it requires, and so on—make sure that you reference the source of your information.
- If documentation claims that a product is secure, the documentation
  is invalid (and not credible) if someone succeeds in compromising the product.
  It's safer to suggest that a feature "helps with security" or "is designed for
  security" because those statements are true even if a security incident occurs.
- A statement that you make about a competitive product might be untrue if you
  misinterpret how the product works, or later if the other company comes out with
  a new release.

The safest approach is always to write factually and objectively, limiting what you say to
verifiable information that will be true over the lifespan of your documentation.

Recommended: Our product
distributes datasets and computation in memory across a cluster, and
therefore it can be faster for this scenario than ExampleCorporation's product. For
more information, see [Performance comparison](https://www.google.com/).

Not recommended: Our product is
faster than ExampleCorp's product.

Recommended: Using our security product
is part of an overall strategy that helps prevent account takeovers from phishing attacks.

Not recommended: Our security product
prevents account takeovers from phishing attacks.

---

<a id="future"></a>

### Future features

*Source: <https://developers.google.com/style/future>*

Avoid documenting future features or products, even in innocuous
ways. Don't pre-announce anything in documentation unless it has been approved by your legal counsel.

See also [Present tense](#tense) and
[Timeless documentation](#timeless-documentation).

---

<a id="translation"></a>

### Global audience

*Source: <https://developers.google.com/style/translation>*

We write our developer documentation in US English, but some of it is
translated into languages other than English or is read by developers for whom
English is not their primary language.

Write with localization, translation, and
internationalization in mind. The following list defines these terms:

- *Localization:* Adapting a product and its associated documentation for a specific country.
  This process involves more than translation—for example, using local currencies or units of
  measurement.
- *Translation:* Translating one language to another language. This process might involve
  localization, but the two terms aren't synonymous with one another.
- *Internationalization:* Designing a product and its associated documentation to minimize
  the localization effort—for example, placing all UI strings in a separate file to simplify
  translation.

For more information, see
[Language localization](https://wikipedia.org/wiki/Language_localisation).

For other writing best practices, see the following resources:

- [Write accessible documentation](#accessibility)
- [Write inclusive documentation](#inclusive-documentation)
- [Voice and tone](#tone)

<a id="translation--use-clearu002c-conciseu002c-and-unambiguous-language"></a>

#### Use clear, concise, and unambiguous language

Consider global audiences and translation and write in a way that's clear, concise, and
unambiguous.

<a id="translation--use-simpler-words-and-shorter-sentences"></a>

##### Use simpler words and shorter sentences

- Use a simple word. For example, don't use words like *commence* when you mean *start*
  or *begin*. Don't use *consequently* when you mean *so*. Don't use words like
  *utilize* or *leverage* when you mean *use*. (It's fine to use these words when
  you're conveying a special sense—for example, *Cloud Spanner utilizes up to 100% of the available
  CPU resources.*)
- Use a single word when it conveys the same idea as a phrase. For example, don't
  use a phrase like *a number of* when you can use *some* or *many*.
- Write shorter sentences. The shorter the sentence, the easier it is to translate. English sentences can be
  shorter in length than some languages, so an English sentence of average length might result in a
  long sentence when translated. Longer sentences can impair understanding, cause rendering issues
  on the page or product interface, lengthen translation time, and increase translation and
  review costs.

<a id="translation--avoid-phrasal-verbs"></a>

##### Avoid phrasal verbs

- Avoid phrasal verbs when possible. A phrasal verb combines multiple words to form a single
  verb phrase. These verbs are also known as compound verbs. Try to substitute a simpler verb first.
  There might not be a better verb; for example, a few exceptions to this rule include *set up*,
  *log in*, and *sign in*.

  Recommended: This document uses the following
  terms:

  Not recommended: This document makes use of
  the following terms:

<a id="translation--use-modifiers-appropriately"></a>

##### Use modifiers appropriately

- Don't use too many modifiers. In particular, don't use more than two nouns as modifiers of
  another noun.

  Recommended: A cloud-native DevSecOps
  pipeline in a hybrid environment

  Not recommended: A hybrid cloud-native
  DevSecOps pipeline
- Don't misplace modifiers. For example, place a word like *only* immediately before the
  word or phrase that it relates to. If the meaning is still ambiguous, try rephrasing the sentence.

  Recommended: Request only one token.

  Recommended: Request no more than one token.

  Not recommended: Only request one token.

<a id="translation--use-active-voice-and-present-tense"></a>

##### Use active voice and present tense

- Use [present tense](#tense) and avoid complex or uncommon verb forms.
- Use active voice. The subject of the sentence is the person or thing performing the action.
  With passive voice, it's often hard for readers to figure out who's supposed to do something.
  For more information, see [Active voice](#voice).

<a id="translation--use-words-in-their-primary-sense"></a>

##### Use words in their primary sense

- Don't use the same word to mean different things. In particular, avoid using the same word as
  both a noun and a verb in close proximity. For examples of words that have multiple meanings, see the word
  list entries for [once](#word-list--once), [while](#word-list--while), [as](#word-list--as), and [since](#word-list--since).
- Avoid directional language (for example, *above* or *below*) in procedural
  documentation. For more information, see
  [UI elements and interaction](#ui-elements--buttons).

<a id="translation--use-helper-words-and-optional-words"></a>

##### Use helper words and optional words

- Use qualifying nouns for technical keywords. For example, when referring to a file called
  `example.yaml`, call it the *`example.yaml` file* and not
  *`example.yaml`* by itself. For more information, see
  [Grammatical treatment of code elements](#code-in-text--keywords).
- Repeat a word if the redundancy improves comprehension.

  | Recommended | Not recommended |
  | --- | --- |
  | If the VM has started and if you're able to connect... | If the VM has started and you're able to connect... |
  | The resource hierarchy design creates both IAM segmentation and network segmentation by default. | The resource hierarchy design creates both IAM and network segmentation by default. |
  | An egress rule whose action is `allow`, whose destination is `0.0.0.0/0`, and whose priority is the lowest possible (`65535`). | An egress rule whose action is `allow`, destination is `0.0.0.0/0`, and priority is the lowest possible (`65535`). |
- Use helper words. Helper words such as *then*, *that*, and *of*
  are frequently left out of conversational English. Use these words to avoid ambiguity.

  | Recommended | Not recommended |
  | --- | --- |
  | If the attribute key is not found, then the default value is returned. | If the attribute key is not found, the default value is returned. |
  | This document is intended for data engineers and assumes that you have the following knowledge: | This document is intended for data engineers and assumes you have the following knowledge: |
  | Identify all of the datasets. | Identify all the datasets. |
  | Start the profiler, and then run the app. | Start the profiler, then run the app. |

  See also [Optional pronouns](#pronouns--optional-pronouns).
- Don't omit relative pronouns. To provide clarity and to avoid ambiguity, use relative
  pronouns such as *that* and *which*. For more information, see
  [Relative pronouns](#pronouns--relative-pronouns).

  Recommended: You can programmatically update
  the rules that you previously defined.

  Not recommended: You can programmatically
  update the rules you previously defined.

<a id="translation--clarify-abbreviations-and-pronouns"></a>

##### Clarify abbreviations and pronouns

- Define abbreviations. Abbreviations can be confusing out of context, and they don't translate
  well. Spell things out whenever possible, at least the first time that you use
  a given term. For more information, see [Abbreviations](#abbreviations).
- Clarify antecedents. Using pronouns can get tricky when translators are working with small,
  unconnected strings of text. Help them out by making things as clear as
  possible. For example, if a pronoun is ambiguous, then replace it with the
  appropriate noun.

  Recommended: If you use the term
  *green beer* in an ad, then make sure that the ad is targeted.

  Not recommended: If you use the term
  *green beer* in an ad, then make sure that it's targeted.

<a id="translation--use-apostrophes-appropriately"></a>

##### Use apostrophes appropriately

Be careful with how you use plural and possessive forms. In general, don't form a plural with
*'s*, don't use the plural or possessive form with trademarks of company, product, and feature
names, and don't use uncommon contractions. For more information, see [Possessives](#possessives), [Pluralization](#pluralization), and [Contractions](#contractions).

<a id="translation--address-users-and-their-needs-directly"></a>

#### Address users and their needs directly

Address the user and their needs directly and avoid providing unnecessary information.

- Address the reader directly. Use *you*, instead of *the user* or *they*, unless
  you're referring to someone who uses the software that the reader is developing. For more
  information, see [Second person and first person](#person).
- Provide context. Don't assume that the reader already knows what you're talking about.
- Avoid negative constructions when possible. Consider whether it's necessary to tell the reader
  what they can't do instead of what they can.

<a id="translation--be-consistent"></a>

#### Be consistent

Use standard sentence structures, consistent terminology, and appropriate punctuation to avoid
creating barriers to understanding, ambiguity, and mistranslations.

<a id="translation--use-consistent-terminology"></a>

##### Use consistent terminology

If you use a particular term for a concept in one place, then use that exact same term
elsewhere, including the same capitalization. If you use different names for the same thing,
translators might think you're referring to different concepts, and thus might use different
translations. Inconsistency in terminology and phrasing can increase translation costs,
particularly when translation memory and machine translations are used as first steps in
translation.

<a id="translation--use-standard-sentence-structures-and-formatting"></a>

##### Use standard sentence structures and formatting

- Use standardized phrases for frequently used sentences, introductory phrases, and other common
  tasks. For examples, read about [introducing links](#cross-references--link-introductions),
  [introducing output](#placeholders--placeholders-in-output), and
  [introducing code samples](https://developers.google.com/style/code-samples#introductions).
- Use standard English word order. Sentences follow the *subject + verb + object* order.
- Try to keep the main subject and verb as close to the beginning of the sentence as possible.
- Use the conditional clause first. If you want to tell the audience to do something in a
  particular circumstance, mention the circumstance before you provide the instruction. For more
  information, see [Sentence structure](#sentence-structure).
- Make list items consistent. Make list items parallel in structure. Be consistent in your
  capitalization and punctuation. For more information, see [Lists](#lists).

<a id="translation--use-consistent-text-formatting"></a>

##### Use consistent text formatting

- Use consistent typographic formats. Use bold and italics consistently. Don't switch from
  using italics for emphasis to underlining. For more information, see
  [Text-formatting summary](#text-formatting).
- Use consistent capitalization. For more information, see
  [Capitalization](#capitalization).

<a id="translation--be-inclusive"></a>

#### Be inclusive

You're not writing for your culture. Write with inclusivity in mind. For more information, see [Writing inclusive documentation](#inclusive-documentation).

- Write [dates and times](#dates-times) in unambiguous and clear ways.
- Don't be too
  culturally specific. In particular, don't refer to specific holidays, cultural practices, or sports
  unless you're certain they're known worldwide.
- Use a diverse set of example names. If you
  need to use people's names (for example, as email addresses), use a diverse set of names. For more
  information, see [Example domains and names](#examples).
- Avoid
  colloquialisms, idioms, or slang. Phrases like *ballpark figure*, *back burner*, or
  *hang in there* can be confusing and difficult to translate.
- Avoid humor. Most humor
  is difficult to translate, and much humor is culturally specific.
- Avoid geographically
  specific references, like the seasons. Remember that August isn't summer in the southern hemisphere.
  For more information, see [Expressing divisions of the
  year](#dates-times--divisions-year).

<a id="translation--consider-accessibility-for-images"></a>

#### Consider accessibility for images

Use screenshots and text in figures sparingly. Images don't get translated. Any new information
should be conveyed through text and not introduced in a figure or image. For more information, see
[Figures and other images](#images).

---

<a id="inclusive-documentation"></a>

### Inclusive language

*Source: <https://developers.google.com/style/inclusive-documentation>*

> [!NOTE]
> **Note**: This document includes references to
> potentially disrespectful or offensive terms. These terms are listed here to
> provide usage guidance and alternative terms.

When you write developer documentation with inclusivity and diversity in mind,
you help ensure that the content is more precise and clear for all readers.
Avoid any kind of idiomatic or figurative language that can be misinterpreted or
distracting.

This page is not an exhaustive reference, but provides some general guidelines
and examples that illustrate some best practices for writing inclusive
documentation.

For other writing best practices, see the following resources:

- [Write for a global audience](#translation)
- [Write accessible documentation](#accessibility)
- [Voice and tone](#tone)

<a id="inclusive-documentation--gendered-language"></a>

#### Avoid unnecessarily gendered language

Be mindful of the
[pronouns](#pronouns--gender-neutral-pronouns)
that are used in narrative
examples, and be aware of other possible sources of gendered language.

| Recommended | Not recommended |
| --- | --- |
| Equipment installation takes around 16 person-hours to complete. | Equipment installation takes around 16 man-hours to complete. |
| Build AI that benefits humanity. | Build AI that benefits mankind. |

<a id="inclusive-documentation--figurative-language"></a>

#### Avoid figurative language

Use simple language and terminology that's precise and clear for all of your
audiences:

- Avoid idiomatic or figurative language that can be misunderstood,
  distracting, or difficult for translation.
- Avoid [jargon](#jargon).
- Use terms that are established industry standards and widely understood by
  the target audience.

When you try to achieve a [friendly and conversational
tone](#tone), you might mistakenly use figurative language. Figurative language can
come in the form of figures of speech and other turns of phrase. Be attentive to
your word choice, especially when you aim for an informal tone.

Don't use metaphors, and don't use a term in a metaphorical sense
([use words in their primary sense](#translation--use-words-in-their-primary-sense)).
For example, avoid using the metaphor of *pets versus cattle* when you
compare on-premises or stateful systems with stateless cloud systems.

For guidance about specific terms, see the
[Word list](#word-list).

<a id="inclusive-documentation--ableist-language"></a>

##### Avoid ableist language

Ableist language includes
words or phrases such as *crazy*, *insane*, *blind to* or
*blind eye to*, *cripple*, *dumb*, and others. Choose a more
accurate or alternative word, depending on the context.

| Recommended | Not recommended |
| --- | --- |
| Before launch, give everything a final check for completeness and clarity. | Before launch, give everything a final sanity-check. |
| There are some baffling outliers in the data. | There are some crazy outliers in the data. |
| It slows down the service, causing a poor user experience until the queue clears. | It cripples the service, causing a poor user experience until the queue clears. |
| Replace the placeholder in this example with the appropriate value. | Replace the [dummy variable](#word-list--dummy-variable) in this example with the appropriate value. |

<a id="inclusive-documentation--graphic-language"></a>

##### <a id="inclusive-documentation--violent-language"></a>Avoid graphic or metaphorical language

Avoid unnecessarily graphic or metaphorical language, when you can use a more
precise term.

For example, instead of
*[STONITH](#word-list--stonith)*, use specific terms to
describe the process that's used to stop an errant node. If you need to mention a term
such as *STONITH*, you can mention it once when you first explain the
relevant feature, and phrase it in a way that de-emphasizes the term.

Recommended:
This approach might require you to fence failed nodes.

Sometimes okay:
This approach might require you to fence failed nodes (sometimes referred to
as *STONITH*).

Always use the most precise and well-understood terms for your context.
In some contexts, an industry-established term has a specific technical meaning
that doesn't have an accurate synonym or alternative. For examples, see the word
list entries for [terminate](#word-list--terminate) and
[execute](#word-list--execute).

| Recommended | Not recommended |
| --- | --- |
| If the connection doesn't respond, check for errors. | If the connection hangs, check for errors. |
| Point to **File**, and then click **New**. | Hover over **File**, and hit **New**. |

For guidance about specific terms, see the
[Word list](#word-list).

<a id="inclusive-documentation--diverse-examples"></a>

#### Write diverse and inclusive examples

Write documentation for a
[global audience](#translation--be-inclusive).
Use diverse names, genders, ages, and locations in examples. Keep the following
advice in mind:

- Follow our [gender-neutral
  pronoun](#pronouns--gender-neutral-pronouns) guidance.
- Avoid being too culturally specific to the US. Be mindful when referring
  to specific holidays (see also the word list entry for [*the holidays*](#word-list--holiday)), cultural practices,
  sports, and figures of speech.
- In examples,
  [choose a diverse set of names](#examples--example-person-names)
  to help reflect our global audience. For guidelines about fictional people,
  see
  [Further notes about example people](#examples--further-notes-about-example-people).
- When writing about older adults, avoid terms and figures of speech such
  as *the elderly*, *the aged*, *seniors*,
  *senior citizens*, or *80 years young*. Instead, use terms such as
  *older adults* or *aging population*, or mention the person's
  relative age or relationship to the other people in your example when those
  details are relevant.

<a id="inclusive-documentation--features-and-users"></a>

#### Write about features and users in inclusive ways

Avoid referring to people in divisive ways. For example, instead of referring
to people as *native speakers* or *non-native speakers* of English, consider
whether your document needs to discuss this at all, and revise it
to discuss the feature in terms that are relevant to anyone regardless of what
languages they know.

Avoid using socially charged terms for technical concepts where possible. For
example, avoid terms such as [blacklist](#word-list--blacklist) and
[native](#word-list--native) feature, and don't use terms like
[first-class
citizen](https://wikipedia.org/wiki/First-class_citizen), even though such terms might still be widely used.

<a id="inclusive-documentation--replace-or-write-around-non-inclusive-terms"></a>

##### Replace or write around non-inclusive terms

This section contains guidance about how to replace or write around a non-inclusive term. If a
term is well established in the industry and replacing it could cause confusion, see
[Replace established terms](#inclusive-documentation--replace). If a term occurs in code samples or keywords, see
[Write around non-inclusive code terms](#inclusive-documentation--write-around). For information about avoiding
non-inclusive jargon, see [Jargon](#jargon).

<a id="inclusive-documentation--replace"></a>

###### Replace established terms

Many non-inclusive terms are in wide use in the industry, such as *whitelist*. If replacing
an established term could cause confusion for readers, you can directly refer to the non-inclusive
term on the first use, and put it in parentheses. Then use the inclusive, replacement term
throughout the rest of the document.

Recommended: To make sure that administrators
get the notification, add them to an allowlist (sometimes called a *whitelist*). Anyone who
isn't on the allowlist is blocked ...

Recommended: In this model, a Jenkins
controller (master) handles HTTP requests. The Jenkins controller is designed to ...

Recommended: In cloud architecture, servers
are treated as commodities (sometimes described by using the metaphor *cattle, not pets*).

In many cases, instead of directly replacing a word, you can rewrite to improve the clarity of a
sentence. For example, instead of replacing the verb *whitelist* with *allowlist*, try
rewriting the sentence.

Recommended: You can allow requests from a
range of IP addresses by entering a CIDR block instead of a single address in the field.

Not recommended: You can allowlist a range of
IP addresses by entering a CIDR block instead of a single address in the field.

<a id="inclusive-documentation--write-around"></a>

###### Write around non-inclusive code terms

In some cases, non-inclusive terms are embedded in code (or similar) as names or keywords, and
you can't simply ignore those terms and use different terminology. What you can do, however, is
*minimize* your use of the term (hence avoid propagating it as a term of art), while still
providing clear documentation to your readers. Don't use a non-inclusive name or keyword unless it's
in code font.

Following are scenarios for writing around non-inclusive terms that occur in code and keywords.

One scenario is if you're documenting an existing system in which an entity is already named
by using a non-inclusive term. For example, there might be a configuration file that includes the
following cluster name:

```
apiVersion: v1
kind: Config
preferences: {}

clusters:
- cluster:
  name: master
- cluster:
  name: replica-1
```

Another scenario is if your documentation includes a non-inclusive term that's an established
keyword, such as the keyword `SLAVE` in dialects of SQL:

```
START SLAVE UNTIL SQL_AFTER_MTS_GAPS;
```

The first time that you refer to a code item that uses a non-inclusive term, you can directly
refer to that term, but format it in code font, and put it in parentheses if possible.

Recommended: The configuration file helps you
create a parent node (which is named `master` in the file).

Recommended: Start the replica by using the
`START SLAVE` statement.

In subsequent mentions, use the preferred term (*parent node*, *replica*). If it's
necessary to refer to the entity name or keyword, continue doing so only with code formatting.

<a id="inclusive-documentation--about-disability-and-accessibility"></a>

#### Avoid bias and harm when discussing disability and accessibility

Many developers create products with accessibility and disability in mind.
When documenting these features, and when writing about people with
disabilities or about accessibility, work to eliminate unintentional bias and
harm. Take the time to educate yourself about the ways that the communities that you're
writing about prefer to be identified and described before writing about them in
your documentation.

Some general guidelines in this area include the following:

- Don't describe people without disabilities as *normal* or *healthy*. This
  contributes to othering and alienation of people with disabilities by implying that
  they are abnormal or sick. Instead, use terms such as *nondisabled person*,
  *sighted person*, *hearing person*,
  *person without disabilities*, or *neurotypical person*.
- Research the ways that the people in the communities that you're writing about
  prefer to be identified and use the terms that they prefer. In many cases, avoid
  terms that remove personhood or that define people by their disability. For
  example, avoid terms such as *the disabled* or *a quadriplegic*.
  Instead, use terms such as *people with disabilities* or *a quadriplegic person*.

  However, many members of some communities prefer *identity-first language*—for
  example, that preference is common in autistic, blind, and Deaf communities. Capitalization of
  identities also can vary (for some perspectives, visit
  [Identity-First Language](https://autisticadvocacy.org/about-asan/identity-first-language/)
  and
  [Self-Identification
  in the Deaf Community](https://www.verywellhealth.com/deaf-culture-big-d-small-d-1046233)). Whenever possible, research and choose terms
  that respect the ways that people in the communities identify.
- Use *see* to refer to links and cross-references. For more information, see
  [see](#word-list--see).
- Avoid terms that reflect or project feelings and judgments about a person's disability,
  such as *victim of*, *suffering from*, or *wheelchair-bound*. Instead, use neutral
  terms such as *experiencing*, *living with*, or *uses a wheelchair*.
- Avoid euphemisms or patronizing terms such as *physically challenged*, *special*,
  *differently abled*, or *handi-capable*.

---

<a id="jargon"></a>

### Jargon

*Source: <https://developers.google.com/style/jargon>*

Jargon is the specialized and often figurative terminology of a specific group to represent a
larger concept—for example, *camel case*, *swim lane*,
*break-glass procedure*, or *out-of-the-box*. Jargon can also include
vaguely defined or overloaded terms like *solution*, *support*, or
*workload*.

Typically, the meaning of jargon isn't understood except by the specific group. For this reason,
jargon can hamper our efforts to publish content that's clear, that reaches a
[global audience](#translation)
in multiple languages, that serves readers at various levels of product knowledge, and that's
inclusive of different groups and cultures. For more information about writing with
inclusivity and diversity in mind, see
[Write inclusive documentation](#inclusive-documentation).

However, some jargon is widely understood and accepted by our industry or by the intended
audience of a document. It can be valuable to include jargon in a document when you know that
readers search for those terms. If you're going to use jargon, consider the following questions:

- **Can you write around the term?** If you don't need the term for search engine
  optimization (SEO), try writing around it. For example, instead of writing *Hold a
  post-mortem*, write *When the project is finished, review what processes worked or didn't
  work*. Instead of writing *Create a back-of-the-envelope design*, write *Use an informal
  design process*.
- **Can you replace the term with a different, more specific term?** For example, the
  [word list](#word-list)
  for this style guide offers several replacement terms: *affected area* or *spatial
  impact* (for *blast radius*), *import* or *load* (for *ingest*), and
  *ready-made* or *pre-built* (for *off-the-shelf*). When a term on the word list is
  marked as "Don't use" (some jargon can be considered offensive, violent, or not inclusive),
  replace that term or write around it.
- **Are you using the term only once in your document?** If so, describe the term in plain
  language and refer to it in parentheses, or link to a trusted definition.

  Recommended: You then move the task to an
  earlier part of the process (also known as *shifting left*).

  Recommended: A
  [split-brain](https://en.wikipedia.org/wiki/Split-brain_(computing))
  situation can develop.
- **Are you using the term throughout your document?** If so, briefly describe the term in
  parentheses on first reference, or link to a trusted definition.

  Recommended: The application is in the
  same state as a *cold standby* (a backup or redundant system that's identical to a primary
  system).

  Recommended: A better approach is to use
  a pattern called a
  [*dead letter queue*](https://en.wikipedia.org/wiki/Dead_letter_queue).
- **Is the term used in a command or code sample?** If so, use the words only in direct reference to the code items
  ([formatted as code](#code-in-text)), and make it clear
  what you're referring to.

  Recommended: Add a user to the
  allowlist (`whitelist`) by entering the following:
  `whitelist adduser EMAIL_ADDRESS`.

  Not recommended: Add a user to the
  whitelist by entering the following: `whitelist adduser
  EMAIL_ADDRESS`.

---

<a id="prescriptive-documentation"></a>

### Prescriptive documentation

*Source: <https://developers.google.com/style/prescriptive-documentation>*

Write prescriptive documentation.

*Prescriptive* (or *opinionated*) documentation recommends a way to achieve tasks
and accomplish goals. It tells the reader what to do instead of giving them a list of options to
choose from. When a goal or task is complex and involves multiple approaches or products,
prescriptive documentation recommends a path.

Prescriptive writing affects several aspects of documentation:

- **The purpose and structure of a document**. Prescriptive documentation states a clear,
  specific purpose. Headings and content are written with that purpose in mind.
- **Example scenarios and procedures**. Scenarios and procedures reflect the use cases that
  are most likely relevant to the readers.
- **Sample commands**. Prescriptive documentation provides commands and arguments that
  accomplish the task for the most common use case. For more information about documenting
  command-line options, see
  [Optional arguments in click-to-copy commands](#code-syntax--click-to-copy-commands).

For instance, best practice documents are typically prescriptive documents. For an example, see
[Operations best practices](https://cloud.google.com/architecture/security-foundations/operation-best-practices).

<a id="prescriptive-documentation--word-choice"></a>

#### Word choice for recommendations and requirements

To indicate required or optional user actions or the outcomes of a process, select an appropriate
auxiliary verb—for example, *must*, *can*, or *might*. Generally avoid the word
*should*. The word can create ambiguity and uncertainty for readers and is thus problematic for
prescriptive documentation. For example, if you're telling the reader what to do, *should*
implies that the action is recommended but optional, which can leave the reader unsure about what to
do.

To clarify what you mean, determine if an action is *required* versus *optional*, an
outcome is *expected* versus *possible*, or a state is *actual* versus
*recommended*.

- **If an action is required**: use *must*, or rephrase
  the sentence so that it's a clear imperative instruction such as
  "Do the following before you continue."
- **If an action is recommended**: use *We recommend ...* or
  *Google recommends ...*. You can use *should* if a
  recommended action is generally recognized. For example, "You should
  use a strong password ..." or "You should follow the principle of
  least privilege ...."
- **If an action is optional**: use *can*. For example,
  "You can also use approach B to solve the same problem."
- **If an outcome is expected**: describe the outcome in terms of
  what is expected. For example: "The process returns 10 items."
- **If an outcome is possible**: use *might* or *can*.
  For example, "The process can take about 30 minutes."
- **If a state is actual**: when you're describing the state of
  something, such as the value of a variable, avoid writing "The value
  should be true." Instead, clarify which of the following you mean:
  - "You must set the value to true."
  - "The server sets the value to true."
  - "If the value is false, follow these steps to change it to true."

  For information about clarifying who's performing an action, see
  [Active voice](#voice).

Recommended: Ensure that the
Classroom Share Button conforms to our min-max size guidelines and related
color/button templates.

Recommended: The column of the data
table that the filter operates on.

Recommended: Whether it's a brand new
project or an existing one, perform the following steps.

Not recommended: The Classroom Share
Button should conform to our min-max size guidelines and related color and
button templates.

Not recommended: The column of the
data table that the filter should operate on.

Not recommended: Whether it's a brand
new project or an existing one, here's what you should do.

<a id="prescriptive-documentation--more-resources"></a>

#### More resources

- See also [can](#word-list--can), [could](#word-list--could),
  [may](#word-list--may), [might](#word-list--might),
  [must](#word-list--must), and [would](#word-list--would) in the
  word list.

---

<a id="other-sources"></a>

### Third-party content

*Source: <https://developers.google.com/style/other-sources>*

Don't copy content from another source because it might violate copyright. Instead, paraphrase
and link to their content.

Content includes the following types: text, images, code, logos, and speech.

Recommended: A
[recovery point objective (RPO)](https://en.wikipedia.org/wiki/Disaster_recovery#Recovery_Point_Objective),
which is the maximum acceptable length of time during which data might be lost from your app due to
a major incident.

Not recommended: Recovery Point Objective (RPO): "RPO is the
maximum targeted period in which data (transactions) might be lost from an IT service due to a major
incident" (<https://en.wikipedia.org/wiki/Disaster_recovery#Recovery_Point_Objective>).

<a id="other-sources--third-party"></a>

#### Avoid third-party content

Unless you are sure that your company owns the assets, avoid copying from these sources:

- Third-party sources: This list includes documentation, websites, books, blogs, videos, images,
  podcasts, and more.
- Reference sources: Avoid copying from dictionaries, encyclopedias, and Wikipedia.
- Open source product documentation: Open source software (OSS) has different license options,
  which can range from no reuse without attribution to complete freedom to use the material. It's
  not safe to assume that you can reuse this content freely. When in doubt, don't use their
  content.
- GitHub content: Different GitHub users might adopt different licenses for their content. It's
  not safe to assume that you can reuse this content freely. When in doubt, don't use their
  content.

---

<a id="timeless-documentation"></a>

### Timeless documentation

*Source: <https://developers.google.com/style/timeless-documentation>*

Timeless documentation is documentation that avoids words and phrases that anchor the
documentation to a point in time or assume knowledge of prior or future products and features. In
general, document the current version of a product or feature.

Timeless documentation is especially important for technical documents that might be read a long
time after they are written. Words like *now*, *new*, and *currently* can render
such documentation inaccurate, outdated, or unmeaningful. In contrast, timeless documentation
focuses on how the product works right now—not on how it has changed from previous versions,
and not how it might change in the future.

| Recommended | Not recommended |
| --- | --- |
| These subcommands let you interact with HTTP load balancing. | These new subcommands let you interact with HTTP load balancing. |
| The following command-line options aren't supported: | The following command-line options aren't currently supported: |
| The emulator supports the following filters: | The emulator now supports the following filters: |

If you're writing procedural or time-stamped content such as press releases, blog posts, or
release notes, such time-based words and phrases are okay. For example, *new* is okay in a blog
post that announces updates to a product: *Dataflow includes several new features.* Or,
*soon* is okay in procedural content to emphasize a change in state after a user performs a
step: *The VM goes offline soon after you send the shutdown command.* However, some of these
words can become outdated or incorrect when used in product documentation to refer to a product's
features and capabilities, so we recommend against using such words in that context.

Writing timeless product documentation has the following value:

- It reduces the maintenance required to keep documentation up to date.
- It avoids assuming the reader is familiar with earlier versions of the product.

<a id="timeless-documentation--words-and-phrases-to-avoid"></a>

#### Words and phrases to avoid

The following words and phrases can undermine timelessness in documentation:

- **Words and phrases that make promises or project plans and
  strategies**. In the context of describing product or feature capabilities, words and phrases such
  as *at present*, *as of this writing*, or *eventually* can prematurely disclose plans
  for a product or feature, or they can inappropriately imply that a product or feature might change.
  In those cases, don't use such words and phrases.

  For more information, see [Documenting future features](#future).
- **Words and phrases that are implied**. At Google, we assume our documentation is
  current unless a specific release version is specified. Thus, words and phrases such as
  *currently* and *as of this writing* are implied by the existence of the documentation
  itself.
- **Words and phrases that become outdated soon after publication**. Words such as *soon*
  and *latest* quickly become irrelevant.
- **Words and phrases that assume prior knowledge of a product or feature**. If you must use
  words like *new*, give a reference point such as a date or version release number—for
  example, *The January 14, 2021 release of BigQuery includes a new resource panel.*

When describing product or feature capabilities in product and reference documentation, avoid
the following words and phrases:

- as of this writing
- currently
- does not yet
- eventually
- existing
- future, in the future
- latest
- new, newer
- now
- old, older
- presently, at present
- soon

---

<a id="tone"></a>

### Voice and tone

*Source: <https://developers.google.com/style/tone>*

In your documents, aim for a voice and tone that's conversational, friendly,
and respectful without using slang or being overly colloquial or frivolous. Use
a voice that's casual, natural, and approachable, not pedantic or pushy. Try to
sound like a knowledgeable friend who understands what the developer wants to do.

Don't try to write exactly the way you speak; you probably speak more
colloquially and verbosely than you should write, at least for developer
documentation. But, aim for a conversational tone rather than a formal one.

Don't try to be super-entertaining, but also don't aim for super-dry. Be
human, let your personality show, and be memorable. But remember that the
primary purpose of the document is to provide information to someone who's
looking for it and may be in a hurry.

Consider that readers come from many different cultures and may have varying
levels of ability reading English. As much as possible, avoid culturally
specific references. Simple and consistent writing can also make it easier to
translate documents into other languages. For more information, see
[Writing for a global audience](#translation).

For other writing best practices, see the following resources:

- [Write accessible documentation](#accessibility)
- [Write inclusive documentation](#inclusive-documentation)

<a id="tone--avoid"></a>

<a id="tone--some-things-to-avoid-where-possible"></a>

#### Some things to avoid where possible

- Buzzwords or
  [technical jargon](#jargon).
- Being too cutesy.
- [Avoid figurative language](#inclusive-documentation--figurative-language),
  which includes metaphors and ableist language.
- Placeholder phrases like *please note* and *at this time.*
- Choppy or long-winded sentences.
- Starting all sentences with the same phrase (such as *You can* or *To
  do*).
- Current pop-culture references.
- Exclamation marks. In general, avoid exclamation points. See [Specific guidance on exclamation points](#periods--exclamation-points).
- Wackiness, zaniness, and goofiness.
- Phrasing that denigrates or insults any group of people.
- Phrasing in terms of *let's* do something.
- Using phrases like *simply*, *It's that simple*, *It's easy*, or *quickly* in a
  procedure.
- Internet slang, or other [internet
  abbreviations](#abbreviations--dont-use) such as *[tl;dr](#word-list--tldr)* or
  *[ymmv](#word-list--ymmv)*.

<a id="tone--techniques"></a>

<a id="tone--some-techniques-and-approaches-to-consider"></a>

#### Some techniques and approaches to consider

- If you're having trouble expressing something, step back and ask yourself,
  "What am I trying to say?" Often, the answer you give yourself reveals what you
  should be saying in the document.
- If you're uncertain about your phrasing or tone, ask a colleague to take a
  look.
- Try reading parts of your document out loud, or at least mouthing the
  words. Does it sound natural? Not every sentence has to sound natural when
  spoken; these are written documents. But if you come across a sentence that's
  awkward or confusing when spoken, consider whether you can make it more
  conversational.
- Use transitions between sentences. Phrases like *Though* or *This way* can
  make paragraphs less stilted. (Then again, sometimes transitions like *However*
  or *Nonetheless* can make paragraphs more stilted.)
- Even if you're having trouble hitting the right tone, make sure you're
  communicating useful information in a clear and direct way; that's the most
  important part.

<a id="tone--politeness"></a>

<a id="tone--politeness-and-use-of-please"></a>

#### Politeness and use of *please*

It's great to be polite, but using *please* in a set of instructions is
overdoing the politeness.

Recommended: To view the document, click
**View**.

Not recommended: To view the document,
please click **View**.

Recommended: For more information, see
[link to other document].

Not recommended: For more information,
please see [link to other document].

<a id="tone--examples"></a>

#### Examples

| Too informal | Just about right | Too formal |
| --- | --- | --- |
| Dude! This API is totally awesome! | This API lets you collect data about what your users like. | The API documented by this page may enable the acquisition of information pertaining to user preferences. |
| Just like a certain pop star, this call gets your *telephone* number. The easy way to ask for someone's digits! | To get the user's phone number, call `user.phoneNumber.get`. | The telephone number can be retrieved by the developer via the simple expedient of using the `get` method on the `user` object's `phoneNumber` property. |
| Then—BOOM—just garbage-collect, and you're golden. | To clean up, call the `collectGarbage` method. | Please note that completion of the task requires the following prerequisite: executing an automated memory management function. |

---

## Language and grammar

<a id="abbreviations"></a>

### Abbreviations

*Source: <https://developers.google.com/style/abbreviations>*

Abbreviations include acronyms, initialisms, shortened words, and
contractions.

In most contexts, the technical distinction between acronyms and initialisms
isn't relevant; it's fine to use the word *acronym* to refer to both.

- An acronym is formed from the first letters of words in a phrase, but is
  pronounced as if it were a word itself:
  - *NATO* for *North Atlantic Treaty Organization*
  - *scuba* for *self-contained underwater breathing
    apparatus*
- An initialism is also formed from the first letters of words in a phrase,
  but each letter is pronounced separately:
  - *CIA* for *Central Intelligence Agency*
  - *FYI* for *For Your Information*
  - *PR* for *Public Relations*
- A shortened word is just part of a word or phrase, sometimes with a
  period at the end:
  - *Dr.* for *doctor*
  - *etc.* for *et cetera*
  - *min* for *minutes*
  - *CA* for *California*
- [Contractions](#contractions) are discussed in a
  separate page of this style guide.

<a id="abbreviations--long-and-short-versions"></a>

#### Long and short versions of a word

Some words have a long version and a short version—for example:

- *application* and *app*
- *demonstration* and *demo*
- *synchronize* and *sync*

The short versions of the words are not abbreviations, and
if you use them, you don't need to put a period after them.

If you're not sure whether a word is an abbreviation or just a short version
of a longer word, look in our list of [resources](#style--editorial-resources).
If that doesn't settle the issue, use the speaking test: if you speak the short
version as a word (*This is a demo version of the product*), you can usually
treat it as a word and not an abbreviation.

<a id="abbreviations--creating-abbreviations"></a>

#### When to use abbreviations

Abbreviations are intended to save the writer and the reader time. If the reader has to
think about an abbreviation, it can slow down their reading comprehension.

<a id="abbreviations--general-dos-and-donts"></a>

##### General dos and don'ts

- Use standard acronyms and initialisms that will save the reader time.
- Spell out abbreviations on first reference. For more information,
  see [When to spell out a term](#abbreviations--spelling-out).
- Avoid using abbreviations for terms that aren't related to the main topic of the document.

In the following examples, the main topic of the document is the internet of things, so *low Earth orbit* should not be abbreviated.

Recommended: The internet of things (IoT)
service can even be used for connecting to sensors in low Earth orbit.

Not recommended: The IoT (internet of things)
service can even be used for connecting to sensors in LEO (low Earth orbit).

- Be wary of using specialized abbreviations that your readers might not understand. For more information about when to use such language, see [Jargon](#jargon).

<a id="abbreviations--spelling-out"></a>

#### When to spell out a term

In general, when an abbreviation is likely to be unfamiliar to the audience, spell it out upon
first mention and include the abbreviation in parentheses immediately following.

Recommended:  *Border Gateway Protocol* (*BGP*)

For all
subsequent mentions of the abbreviation, use the abbreviation by itself. If you use an abbreviation
only once, include it only if you think the abbreviation is as commonly used as the spelled-out
term. Otherwise, don't include the abbreviation.

If the first mention of
a term occurs in a [heading or title](#headings), you can use the abbreviation and
then spell out the abbreviation in the first paragraph that follows the heading or title.

When deciding to spell out a term, consider your audience. If your document is going to be
translated, spelling out a term can provide important context for both human and machine translation.
It can also be helpful for readers who aren't as familiar with English. If the
majority of your audience is likely to recognize and understand the term, then you don't need to
spell it out. For example, if you're writing documentation for developers that references an API,
you don't need to spell out *application programming interface*. However, if you're explaining
the general concept of an API to someone with no programming experience, spelling out the
abbreviation can be helpful.

In some cases, spelling out a term doesn't help the reader
understand the term. For example, writing out *portable document format* doesn't help the
reader understand what a *PDF* document is. In those cases, don't spell out the term.

The following abbreviations rarely need to be spelled out:

- AI
- API
- DVD
- File formats such as PDF or XML
- HTML
- PC
- RAM
- REST
- [Units of measurement](#units-of-measure--byte-units) such as
  MB, MiB, GB, or GiB
- URL
- USB

<a id="abbreviations--format-abbreviations"></a>

##### Format abbreviation introductions

When you spell out a term and include its abbreviation in parentheses, do the following:

- Italicize both the spelled-out term and its abbreviation.

In the following examples, the only difference is the italicization of *BGP*:

Recommended: Establish *Border Gateway Protocol* (*BGP*) sessions using a router on the peer network.

Not recommended: Establish *Border Gateway Protocol* (BGP) sessions using a router on the peer network.

- Capitalize the spelled-out version of the abbreviation only if the long form is a proper noun or is conventionally capitalized.

That is, don't capitalize the term only because the abbreviation includes capital letters.

Recommended: data manipulation language (DML)

Not recommended: Data Manipulation Language (DML)

- Include the abbreviation in [link text](#cross-references--abbreviations).

<a id="abbreviations--dont-use"></a>

#### Abbreviations not to use

Don't use *i.e.* or *e.g.*; instead, use *that is* or
*for example*, respectively. For more information, see
[e.g.](#word-list--eg) and
[i.e.](#word-list--ie)

It's [okay to use *etc.* in
some circumstances](#word-list--etc), but it's best to use different phrasing in most lists.
For more information, see
[Comma-separated lists](#lists--comma-separated-lists).

Don't use internet slang abbreviations such as
[*tl;dr*](#word-list--tldr),
[*ymmv*](#word-list--ymmv),
[*RTFM*](#word-list--rtfm), or others. Write out what you
mean in a non-figurative way.

Use the most common form of a word. If the spelled-out word is common
and easily understandable, use that rather than abbreviating. For example, write
*approximately* instead of *approx.*

Spell out shortened words or common symbols that are substitutions for words.

Recommended: Updating the software made
throughput 10 times faster.

Not recommended: Updating the software made
throughput 10x faster.

<a id="abbreviations--periods"></a>

#### Periods with abbreviations

Follow these guidelines:

- Don't use periods with acronyms or initialisms.
- Put a period at the end of a shortened word, except for
  [date and time](https://developers.google.com/style/dates) abbreviations.
- If you write or say an abbreviation as a word (for example, *app* or
  *sync*), don't put a period after it.
- Don't use a period with an abbreviation for the name of a country, US
  state, or the District of Columbia (DC).

<a id="abbreviations--making-abbreviations-plural"></a>

#### Plural abbreviations

For guidance about how to make abbreviations plural, see [Pluralization](#pluralization--making-abbreviations-plural).

<a id="abbreviations--verbs"></a>

#### Abbreviations as verbs

Don't use acronyms, initialisms, or shortened words as verbs.

Recommended: Use SSH to
log in to your remote shell.

Not recommended: Then ssh
into your remote shell.

<a id="abbreviations--articles"></a>

#### Indefinite articles before abbreviations

Whether to use *a* or *an* before a term depends on the pronunciation of the term:
use *a* before any consonant sound and *an* before any vowel sound. Pronunciation of
abbreviations can vary, so in general, base your decision on the pronunciation that's most common
for your audience.

In particular, our word list includes preferences for
"[a SQL](#word-list--sql)", "[a FHIR](#word-list--fhir)",
and "[an SAP](#word-list--sap)".

For more information about articles, see [Articles](#articles).

---

<a id="voice"></a>

### Active voice

*Source: <https://developers.google.com/style/voice>*

In general, use active voice (in which the grammatical subject of the
sentence is the person or thing performing the action) instead of passive voice
(in which the grammatical subject of the sentence is the person or thing being
acted upon), although there are exceptions. Make clear who's performing the
action.

In passive voice, it's easy to neglect to indicate who
or what is performing a particular action. In this kind of construction, it's
often hard for readers to figure out who's supposed to do something (such as the
reader, the computer, the server, an end user, or a visitor to a web page).

Recommended: Send a query to the service.
The server sends an acknowledgment.

Not recommended: The service is queried,
and an acknowledgment is sent.

It's possible to indicate who's performing the action in passive voice (using
*by*), but the resulting prose is generally not as good as if you were to recast
the sentence as active voice. So whenever possible, make the doer the subject of
the sentence.

Recommended: Send a query to the service.
The server sends an acknowledgment.

Not recommended: The service is queried by
you, and an acknowledgment is sent by the server.

For more information, see
[Active voice vs. passive voice](https://developers.google.com/tech-writing/one/active-voice)
in Google's Technical Writing One guide.

<a id="voice--exceptions"></a>

#### Exceptions

In certain cases, it's okay to use passive voice. For example, passive can be
okay in the following instances:

- To emphasize an object over an action.

Recommended: The file is saved.

- To de-emphasize a subject or actor.

Recommended: Over 50 conflicts were
found in the file.

Not recommended: You created over 50
conflicts in the file.

- If your readers don't need to know who's responsible for the action.

Recommended: The database was purged
in January.

---

<a id="anthropomorphism"></a>

### Anthropomorphism

*Source: <https://developers.google.com/style/anthropomorphism>*

Don't attribute human qualities to software or hardware.

Anthropomorphism is a category of figurative language, which is less precise and is often harder
to understand and translate than direct language. For more information, see
[Write for a global audience](#translation).

Recommended: A Delimiter object specifies
where to split a string.

Not recommended: A Delimiter object tells
the splitter where a string should be broken.

Recommended: The PC detects a new
device.

Not recommended: The PC sees a new
device.

---

<a id="articles"></a>

### Articles (a, an, the)

*Source: <https://developers.google.com/style/articles>*

For ease of comprehension and translation, include definite and indefinite
articles (*a*, *an*, and *the*) in your writing. Don't skip
articles for brevity, including in headings and titles.

Recommended: Create a VM instance

Not recommended: Create VM instance

For more information about using standard English word order and about writing
for a global audience in general, see
[Write for a global audience](#translation).

For more information about writing clear headings and titles, see
[Headings and titles](#headings).

For information about using articles before product names, see
[Articles before product names](#product-names--the-with-names).

For information about using *a* or *an* before an abbreviation when the pronunciation
of the abbreviation can vary, see
[Indefinite articles before abbreviations](#abbreviations--articles).

---

<a id="capitalization"></a>

### Capitalization

*Source: <https://developers.google.com/style/capitalization>*

Follow the standard [capitalization rules](https://owl.purdue.edu/owl/general_writing/mechanics/help_with_capitals.html) for American English. Additionally,
do the following:

- Don't use unnecessary capitalization; before you capitalize a word, think
  about why (and whether) it should be capitalized.
- Don't rely on a difference in capitalization to convey meaning. For example,
  although people who are familiar with Kubernetes probably understand that a
  capitalized *Pod* is a Kubernetes unit, and a lowercase *pod* is
  any other kind of pod, that distinction is likely lost on many casual
  readers or those who are new to the domain.
- Don't use all-uppercase, except in the following contexts: in official
  names, in [abbreviations](#abbreviations) that are always
  written in all-caps, or when referring to code that uses all-caps.
- Don't use
  [camel
  case](https://en.wikipedia.org/wiki/Camel_case), except in official names or when referring to code that uses camel
  case.

For information about how to capitalize specific words, see the
[word list](#word-list).

<a id="capitalization--capitalize-product-names"></a>

#### Capitalize product names

For information about how to capitalize product names, see
[Product names](#product-names).

<a id="capitalization--capitalization-in-titles-and-headings"></a>

#### Capitalization in titles and headings

In [document titles and headings](#headings), use sentence case. That is,
capitalize only the first word in the title, the first word in a subheading after a colon, and any
proper nouns or other terms that are always capitalized a certain way.

Even though you're using sentence case, don't put a period at the end of a title or
heading.

<a id="capitalization--capitalization-in-references-to-titles-and-headings"></a>

##### Capitalization in references to titles and headings

In references to any title or heading from a document that follows this guide, use sentence case
even if the title or heading itself uses title case. That way, when the title or heading is
eventually updated to sentence case, the reference will match.

When you reference the title of any work or source that doesn't follow this guide, retain the
original capitalization.

For more information about internal and external references, see
[Cross-references and linking](#cross-references).

For more information about formatting references to third-party sources,
see [HTML and semantic tagging](#semantic-tagging).

<a id="capitalization--capitalization-and-colons"></a>

#### Capitalization and colons

Use a lowercase letter to begin the first word of the text immediately
following a colon, unless the text is one of the following:

- A proper noun (*Open source software: Hadoop*)
- A heading; see also [Capitalization in titles
  and headings](#capitalization--capitalization-in-titles-and-headings)
- A quotation (*Arthurian wit: "Bring me yon sworde"*)
- Text that follows a label such as *Caution* or *Note*

<a id="capitalization--capitalization-and-figures"></a>

#### Capitalization and figures

Use sentence case for captions. Use sentence case for labels, callouts, and
other text in images and diagrams.

<a id="capitalization--capitalization-in-glossaries-and-indexes"></a>

#### Capitalization in glossaries and indexes

Use lowercase for glossary and index terms unless the term is a proper noun
or has another reason to require capitalization.

Use sentence case for glossary definitions.

<a id="capitalization--capitalization-and-hyphens"></a>

<a id="capitalization--capitalization-and-hyphenated-words"></a>

#### Capitalization and hyphenated words

When a hyphenated word is the first word in a sentence or in a heading,
capitalize only the first element in the word, unless a subsequent element is a
proper noun or proper adjective.

<a id="capitalization--capitalization-in-lists"></a>

#### Capitalization in lists

Use sentence case for items in all types of lists. For more information, see
[Capitalization and end punctuation](#lists--capitalization-and-end-punctuation).

<a id="capitalization--capitalization-for-tables-in-text"></a>

#### Capitalization for tables in text

Use sentence case for all the elements in a table: contents, headings,
labels, and captions.

<a id="capitalization--special-capitalization-style-names"></a>

#### Special capitalization style names

Don't use a casing style name, such as *camel case* or *snake case*, to describe a
casing style. These names don't localize well and they aren't standardized. Instead, explain what
the requirements are and provide an example.

Recommended: Enter the value for the
`attribute` field in the format where there are no spaces between words and the
first letter of each word is capitalized—for example, `AssertionAccount`.

---

<a id="contractions"></a>

### Contractions

*Source: <https://developers.google.com/style/contractions>*

In general, we write our documentation in an [informal tone](#tone), so we
recommend using common two-word contractions such as *you're*, *don't*, and
*there's*.

<a id="contractions--negation-contractions"></a>

#### Negation contractions

In particular, we recommend using negation contractions such as *isn't*, *don't*, and
*can't*. It's easy for a reader to miss the word *not* when they're scanning, whereas
it's harder to misread *don't* as *do*.

If you need to emphasize the negative, you can use text formatting such as `is
<em>not</em>`, which renders as "is *not*." But in most cases, you don't
need emphasis to make your point clear.

<a id="contractions--contractions-to-avoid"></a>

#### Contractions to avoid

Don't make up nonstandard contractions such as *guides're* or *browser's* (where
*'s* means *is*).

Don't use three-word contractions such as *mightn't've*.

---

<a id="pluralization"></a>

### Pluralization

*Source: <https://developers.google.com/style/pluralization>*

In general, follow the standard rules for pluralization in US English and use the regular
plural form of a word in most cases. Avoid using *'s* to form a plural to avoid confusing
a plural with a possessive or contraction.

For more information, see [Contractions](#contractions) and [Possessives](#possessives).

<a id="pluralization--singular-and-plural"></a>

#### Singular and plural

For sentences with long or complex subjects, make sure to use either a plural or singular
appropriately.

Recommended: Confirm that the number of
entries listed in the directory is accurate.

Recommended: The workloads with the
`app: backend` label represent the traffic source.

Not recommended: The efficiency of
algorithms that process data sets depend on memory allocation.

For sentences with more than one subject being connected by *and* or *or*, make sure
to use either a plural and singular appropriately.

Recommended: The request payload and
header information are logged for debugging.

Recommended: Either the API keys or
service account wasn't authenticated.

Not recommended: User authentication and
authorization is processed and handled by the security module.

For consistent style, use a plural after *one or more*, not a singular.

Because *one or more* can express the possibility of one or more outcomes, it's sometimes
helpful to reword the sentence for clarity.

Recommended: If one or more tests fail, a
system warning is triggered.

Recommended: If any one test fails, a
system warning is triggered.

See also [Plurals in parentheses](#pluralization--plurals-in-parentheses).

Use a singular after *more than one*, not a plural.

Recommended: You can create more than one
instance at a time.

<a id="pluralization--making-abbreviations-plural"></a>

#### Plural abbreviations

In general, treat acronyms, initialisms, and other abbreviations as regular words when making
them plural. Avoid using *'s* to form the plural to help distinguish the plural form from the
possessive. For more information, see [Possessives](#possessives).

Recommended: APIs, SKEs, and IDEs

Not recommended: API's, SKE's, and
IDE's

If the acronym, initialism, or abbreviation ends in *s*, *sh*, *ch*, or
*x*, then add *es*—for example, *OSes*, *DISHes*, *DCCHes*, and
*BMXes*.

> [!NOTE]
> **Note:** Forming a plural using *'s* can be ambiguous or confusing
> to readers and might cause issues in translation. For more information, see [Write for a global audience](#translation).

When spelling out a term, make sure that both the spelled-out term and abbreviation match,
with both either being a plural or singular.

Recommended: virtual machines (VMs)

Not recommended: virtual machines (VM)

When using numbers with units of measure, use the singular when spelling out the unit if the
number is one. Otherwise, use the plural form for all other numbers, including zero,
decimal numbers, and numbers greater than one.

Recommended: 0 degrees

Recommended: 0.5 degrees

Recommended: 1 degree

Recommended: 15 degrees

Don't make an abbreviation plural when used as a unit with a number.

Recommended: 64 GB

Not recommended: 64 GBs

> [!NOTE]
> **Note:** Sometimes it can be helpful to spell out *-bit* or
> *-byte* terms. However, in general, it's not necessary to spell out a unit when used in
> combination with a specific number.

Make sure to include a space, preferably a nonbreaking space, between the number and
abbreviation. For more information, see [Spaces in units of
measurement](#units-of-measure--spaces-in-units-of-measurement).

For more information, see [Abbreviations](#abbreviations).

<a id="pluralization--plural-product-and-feature-names"></a>

#### Plural product and feature names

In general, don't form a plural or possessive for the trademark of a product, feature, or
company name. For more information, see [Use trademarks only as modifiers](#trademarks--use-trademarks-only-as-modifiers) and
[Product, feature, and company
names](#possessives--productu002c-featureu002c-and-company-names).

In general, use singular class names. Don't manually make a singular class name plural. Doing
so might cause issues in translation. Instead, add a plural noun after the class name.

Recommended: `Intent` objects
and `Activity` instances

Not recommended: `Intent`s and
`Activity`s

Not recommended: `Intents` and
`Activities`

For more information, see [API reference code
comments](#api-reference-comments).

<a id="pluralization--plurals-in-parentheses"></a>

#### Plurals in parentheses

Don't put optional plurals in parentheses. Instead, use either a plural or singular
construction and keep things consistent throughout your documentation. Choose what is most
appropriate for your documentation and your audience. If it's important in a specific context to
indicate both, use *one or more*.

| Recommended | Not recommended |
| --- | --- |
| To find your API key, visit the **Credentials** page. | To find your API key(s), visit the **Credentials** page. |
| The value of the parent depends on the values of its children. | The value of the parent depends on the value(s) of its child(ren). |
| You can use a physical linecard, which can contain one or more ports. | You can use a physical linecard, which can contain port(s). |

<a id="pluralization--plural-pronouns"></a>

#### Plural pronouns

For information about plural pronouns like *we*, *you*, and *they*, see [Pronouns](#pronouns) and [Second person and first
person](#person).

---

<a id="possessives"></a>

### Possessives

*Source: <https://developers.google.com/style/possessives>*

In general, to form a possessive, follow these guidelines.

For singular nouns, including those that end in *s*, add *'s* to the end of the word.

Recommended: Modify each vector's record.

Recommended: Raise the storage class's quota.

For plural nouns that end in *s*, add only an apostrophe to the end of the word.

Recommended: Extend the models' capabilities.

Not recommended: Extend the models's
capabilities.

For plural nouns that don't end in *s*, add *'s* to the end of the word.

If a possessive seems awkward, rewrite the sentence to omit the possessive.

Recommended: Analyze the business data.

Not recommended: Analyze the businesses' data.

Recommended: The rule that the Federal Trade
Commission (FTC) issued.

Not recommended: The Federal Trade
Commission's (FTC's) rule.

Avoid using *'s* to form a plural noun. For more information, see [Pluralization](#pluralization).

<a id="possessives--productu002c-featureu002c-and-company-names"></a>

#### Product, feature, and company names

When describing function or performance, don't form a possessive from a
feature name, product name, or trademark, regardless of who owns it. Instead,
use the name as a modifier or rewrite to use a word like *of* to indicate
the relationship.

Recommended: You can use this template to
monitor Google Search performance.

Recommended: You can use this template to
monitor the performance of Google Search.

Not recommended: You can use this template to
monitor Google Search's performance.

To form the possessive of a company name, add *'s* to the end of the name. Don't form the
possessive of a company name when using it as a trademark.

Recommended: Google's new office is
nearby.

Not recommended: The capabilities of
Google's Search are vast.

For information about using trademarks as adjectives, not nouns, see
[Trademarks](https://developers.google.com/style/trademarks#use-trademarks-as-adjectives).
<a id="possessives--code-items"></a>

#### Code items

Don't form the possessive of a code item. Instead, form the possessive from the noun that
follows the code item or rewrite to avoid the possessive form.

Recommended: Compare the number to the
`wordCount` method's return value.

Recommended: Compare the number to the
value returned by the `wordCount` method.

Not recommended: Compare the number to
`wordCount`'s return value.

For more information, see [Grammatical treatment of code
elements](#code-in-text--grammatical-treatment-of-code-elements).

---

<a id="prepositions"></a>

### Prepositions

*Source: <https://developers.google.com/style/prepositions>*

There's no rule against placing a preposition at the end of a sentence.
Place the preposition where it makes the most sense and makes the sentence easiest
to read. Use prepositions as needed, even at the ends of sentences.

Recommended: For details, see the client
library documentation for the language you're interacting with.

Not recommended: For details, see the
client library documentation for the language with which you're interacting.

Include prepositions that increase clarity, omit unnecessary prepositions,
and don't clutter the sentence with too many prepositions.

Recommended: The icon for the connector
manager turns green within a few minutes, and the connector instance is
displayed shortly after.

For information about which preposition to use when referring to UI elements, see
[UI elements and interaction](#ui-elements--prepositions).

---

<a id="tense"></a>

### Present tense

*Source: <https://developers.google.com/style/tense>*

Use present tense for statements that describe general behavior that's not associated with
a particular time.

Recommended: Send a query to the service.
The server sends an acknowledgment.

Not recommended: Send a query to the
service. The server will send an acknowledgment.

However, it's fine to use future tense (*will*) to distinguish an action that will occur in
the future.

Recommended: Add the filename to the
backup list. The file will be archived the next time the backup process runs.

In the following example, future tense is appropriate because Pub/Sub sends
messages asynchronously; messages are not received immediately by subscribers.

Recommended: A message is sent that
will notify any Pub/Sub subscribers.

Not recommended: A message is sent
that notifies any Pub/Sub subscribers.

Don't use future tense to describe how a product or feature will work after the next release
or update. For more information, see [Document future features](#future).

Also avoid the hypothetical future *would*—for example:

Recommended: If you send an unsubscribe
message, the server removes you from the mailing list.

Not recommended: You can send an
unsubscribe message. The server would then remove you from the mailing list.

---

<a id="pronouns"></a>

### Pronouns

*Source: <https://developers.google.com/style/pronouns>*

Ensure that a pronoun clearly refers
to its antecedent (the noun that it's replacing).

<a id="pronouns--ambiguous-pronoun-references"></a>

#### Ambiguous pronoun references

Avoid vague and confusing references between a pronoun and its antecedent.

Recommended: If you type text in the
field, the text doesn't change.

Not recommended: If you type text in the
field, it doesn't change.

Recommended: The name of the function to
execute in the given script. The name does not include parentheses or
parameters.

Not recommended: The name of the function
to execute in the given script. It does not include parentheses or
parameters.

In many cases, it's best to follow a demonstrative pronoun (like *this* and *these*)
with a noun.

Recommended: Set this value to true.

Not recommended: Set this to true.

Recommended: These approaches are your
best options.

Not recommended: These are your best options.

<a id="pronouns--gender-neutral-pronouns"></a>

#### Gender-neutral pronouns

Don't use gender-specific pronouns unless the person you're referring to is
actually that gender.

In particular, don't use *he*, *him*, *his*, *she*, or *her* as
gender-neutral pronouns, and don't use *he/she* or *(s)he* or other such
punctuational approaches. Instead, use the singular *they*.

Singular *they* has been in use for a long time; for example, [Jane Austen used it](http://www.pemberley.com/janeinfo/austheir.html),
and in 2015 the Washington Post [adopted
it as part of their official style](https://www.washingtonpost.com/opinions/the-post-drops-the-mike--and-the-hyphen-in-e-mail/2015/12/04/ccd6e33a-98fa-11e5-8917-653b65c809eb_story.html).

For more suggestions, see
The Chicago Manual of Style, 16th edition, section 5.225,
"Nine techniques for achieving gender neutrality."

<a id="pronouns--optional-pronouns"></a>

#### Optional pronouns

To avoid ambiguity and clarify meaning in sentences, use optional pronouns such as
*that* and *which*.

| Recommended | Not recommended |
| --- | --- |
| Right-click the link that you want to open. | Right-click the link you want to open. |
| You can use other option parameters, which are described in the following section. | You can use other option parameters, described in the following section. |

For more information, see
[Relative pronouns](#pronouns--relative-pronouns).

<a id="pronouns--personal-pronouns"></a>

#### Personal pronouns

Avoid first-person pronouns (*I*, *we*, *us*, *our*, and *ours*) except
in the following contexts:

- The questions in FAQs.
- A document whose author makes comments in the first person.
- Using *we* to refer to your organization, after using your organization's
  name. For example, "Example Pet Store recommends that you feed your aardvark
  Standardized Aardvark Treats. We cannot guarantee the happiness of your aardvark
  otherwise."

Use the second-person pronoun (*you*) whenever possible. For more information about
second person, see [Second person and first person](#person).

<a id="pronouns--relative-pronouns"></a>

#### Relative pronouns

There are several relative pronouns. This section concerns only three of
them: *that*, *which*, and *who*.

*That* and *which* don't mean exactly the same thing, so don't substitute one
for the other:

- *That* introduces a restrictive clause. It isn't preceded by a comma.

  Recommended: The echidna that has a
  long snout is furry.

  This sentence describes a particular echidna, the one that has a long
  snout.
- *Which* introduces a nonrestrictive clause and is preceded by a comma.

  Recommended: The echidna, which has a
  long snout, is furry.

  This sentence describes all echidnas, and mentions in passing that they
  all have long snouts.

For more information about restrictive and nonrestrictive clauses and whether
to use *that* or *which*, read
[what
Grammar Girl has to say on the subject](https://www.quickanddirtytips.com/articles/which-versus-that/).

When you're referring to a person, you can use *who* instead of *that*. If you're not
sure which pronoun is appropriate in your context, then it's generally OK to use *that*.

You can use *whose* to refer to people, animals, and things. *Whose* is the possessive
form of both *who* and *which*.

Recommended: Examine the variables whose
values are set at compile time.

---

<a id="person"></a>

### Second person

*Source: <https://developers.google.com/style/person>*

<a id="person--address-the-reader-as-you"></a>

#### Address the reader as *you*

In general, address the reader of your documents
using the second person instead of the first person: use *you* or *your*
instead of *we*, *our*, or *us*.
Assume that the reader is the person who's doing the
tasks or making the decisions. Use the word *user* only to refer to the user
of the software that your reader is developing.

| Recommended | Not recommended |
| --- | --- |
| The following sections describe how you can create a website. | The following sections describe how we can create a website. |
| Consider adding a description to your table. | Let's add a description to our table. |
| This document shows you how to develop an app for your organization. | This document shows the user how to develop an app for their organization. |

If you're telling the reader to do something, then use the imperative (the *you* is
implied). For example:

Recommended: Click **Submit**.

It's OK to use the imperative in running text after you establish who is being addressed.
However, consider whether the imperative text needs to be formatted as as a procedure.

Recommended: You can obtain the IP address
for the appliance from your network administrator. Store the address in a variable for future
use in the runbook.

Not recommended: To hold the backup data,
create a storage bucket. In the Google Cloud console, go to the **Buckets** page. Click
**Create bucket**.

There are some situations in which using *you* might not be accurate or
appropriate. Use the second person to address what the reader does, but use the
third person for what the software or an end user does. For example, in API
documentation, you can use the third person when you state facts about programming
elements, but address the reader as *you* when you tell them what to do with
them.

<a id="person--use-first-person-plural-pronouns-carefully"></a>

#### Use first-person plural pronouns carefully

It's OK to use first-person plural pronouns (such as *we*, *our*, or *us*)
to refer to the organization that's represented as the author of the document. However, ensure
that the antecedent for the pronoun is clear.

Recommended: Example Organization provides
A and B, but we don't provide C and D.

Recommended: For more information, contact
our sales organization.

Recommended: The example.org support team
regularly reviews tickets. Expect to hear from us in 2-3 business days.

<a id="person--address-your-audience-consistently"></a>

#### Address your audience consistently

It's important to identify who the *you* is that you're addressing
(a developer? a sysadmin? someone else?) and to be consistent
about that. Make it clear to the reader who you expect them to be (sometimes
with an explicit *audience* sentence near the beginning of the document).

---

<a id="sentence-structure"></a>

### Sentence structure

*Source: <https://developers.google.com/style/sentence-structure>*

If you want to tell the reader to do something, try to mention the circumstance, conditions, or
goal before you provide the instruction. Mentioning the circumstance first lets the reader skip
the instruction if it doesn't apply. For information about how to apply this guideline to
procedural instructions, see [Procedures](#procedures).

| Recommended | Not recommended |
| --- | --- |
| For more information, see [link to other document]. | See [link to other document] for more information. |
| To delete the entire document, click **Delete**. | Click **Delete** if you want to delete the entire document. |
| If your app is located in one of the following regions, using custom domains might add noticeable latency to responses: | Using custom domains might add noticeable latency to responses if your app is located in one of the following regions: |

---

<a id="reference-verbs"></a>

### Verbs in reference documents

*Source: <https://developers.google.com/style/reference-verbs>*

When you're writing reference documentation for a method, phrase the main
method description in terms of what the method does (*gets*, *lists*, *creates*,
*searches*), rather than what the developer would use it to do (*get*, *list*,
*create*, *search*).

It's a subtle distinction that manifests mostly in whether the initial verb
in the description has an *-s* at the end or not.

Recommended: tasks.insert: Creates a new
task on the specified task list.

Not recommended: tasks.insert: Create a
new task on the specified task list.

For more information and examples, see the
[Google Cloud API design guide](https://cloud.google.com/apis/design/documentation#method_description).

---

## Punctuation

<a id="colons"></a>

### Colons

*Source: <https://developers.google.com/style/colons>*

A colon indicates that closely-related information follows.

For information about using colons with run-in headings, see
[Description lists that use
run-in headings](#lists--description-lists-that-use-run-in-headings).

<a id="colons--phrase-preceding-colon"></a>

<a id="colons--introductory-phrase-preceding-colon"></a>

#### Introductory phrase preceding colon

When a colon introduces a list, the text that precedes the colon must be able
to stand alone as a complete sentence.

Recommended: The fields are defined as
follows:

Not recommended: The fields are:

<a id="colons--colon-in-sentence"></a>

<a id="colons--colons-within-sentences"></a>

#### Colons within sentences

In general, the first word in the text that follows a colon should be in
lowercase. For exceptions, see
[Capitalization and colons](#capitalization--capitalization-and-colons).

Recommended: Tone: concise,
conversational, friendly, respectful

Recommended: When you add or update
content to an existing project, remember to take these steps: review the style
guide, use checklists, enlist a fellow writer or an editor to copyedit your
work, and request a developmental edit if you feel that it's warranted.

<a id="colons--see-also"></a>

#### See also

For more information about how to punctuate introductory material, see the
sections on [list introductions](#lists--intros) and [code-sample introductions](#code-samples--intros).

For information about when it's better to use colons than dashes, see [Dashes](#dashes--colons).

---

<a id="commas"></a>

### Commas

*Source: <https://developers.google.com/style/commas>*

Use commas to separate items in a series, and use commas to separate certain kinds of
clauses.
<a id="commas--serial-commas"></a>

#### Serial commas

In a series of three or more items, use a comma before the final *and* or
*or* to avoid potentially changing the meaning of the sentence. This comma is called a serial
comma or an Oxford comma.

Recommended: Locations are divided into
zones, regions, and multi-regions.

Not recommended: Locations are divided into
zones, regions and multi-regions.

<a id="commas--introductory-phrases"></a>

<a id="commas--commas-after-introductory-words-and-phrases"></a>

#### Commas after introductory words and phrases

In general, place a comma after an introductory word or phrase.

Recommended: Finally, only groups that
contain parameters appear in this list.

Recommended: Based on the requirements of
your game, you can implement this method to update game information.

<a id="commas--independent-clauses"></a>

<a id="commas--commas-separating-two-independent-clauses"></a>

#### Commas separating two independent clauses

When a coordinating conjunction (*and*, *but*, *or*,
*nor*, *for*, *so*, or *yet*) separates two independent
clauses, insert a comma after the first clause (before the conjunction) unless
both clauses are very short.

Recommended: The libraries make
feed creation easier, and they ensure that only valid feeds are produced.

Not recommended: The libraries make
feed creation easier and they ensure that only valid feeds are produced.

Recommended: Type your ID and click **OK**.

Not recommended: Type your ID, and click
**OK**.

<a id="commas--independent-dependent-clauses"></a>

<a id="commas--commas-separating-independent-from-dependent-clauses"></a>

#### Commas separating independent from dependent clauses

When an independent clause and a dependent clause are separated by a
coordinating conjunction, insert a comma *only if* the sentence could
be misunderstood without one.

Recommended: Direct-access flags are
plain variables and can be read directly.

Not recommended: Direct-access flags are
plain variables, and can be read directly.

Recommended: The manager acknowledged the
last team member who entered the room, and started the meeting.

Not recommended: The manager acknowledged
the last team member who entered the room and started the meeting.

<a id="commas--other-clauses"></a>

<a id="commas--set-off-other-kinds-of-clauses"></a>

#### Set off other kinds of clauses

It's often a good idea to set off certain kinds of clauses with a comma or
other punctuation for clarity.

A couple of specific places where commas are a good idea:

- In general, put a comma before the word *which* at the start of a
  nonrestrictive clause. For more information about this topic, see this guide's section on [relative pronouns](#pronouns--relative-pronouns) and Grammar
  Girl's page on
  [*which* versus *that*](https://www.quickanddirtytips.com/articles/which-versus-that/).
- In general, put a semicolon or a period or a dash before a conjunctive
  adverb, such as *otherwise*, *however*, or *therefore*, and put a comma after
  the conjunctive adverb.

In general, don't use a comma before the causal conjunction *because* unless it starts a nonrestrictive clause. For more information,
see the *Chicago Manual of Style* Q&A entry on
[using
commas with *because*](https://www.chicagomanualofstyle.org/qanda/data/faq/topics/Commas/faq0018.html).

| Recommended | Not recommended |
| --- | --- |
| Name of the group, which has a maximum length of 200 characters. | Name of the group which has a maximum length of 200 characters. |
| The variable must have a value; otherwise, the server returns an error. | The variable must have a value otherwise the server returns an error. |
| You can use the same key name in multiple backend services and backend buckets, because each set of keys is independent of the others. | You can use the same key name in multiple backend services and backend buckets because each set of keys is independent of the others. |

<a id="commas--numbers"></a>

<a id="commas--punctuate-numbers"></a>

#### Punctuate numbers

For information about punctuating numbers, see [Commas and decimal
points in numbers](#numbers--commas-and-decimal-points-in-numbers).

<a id="commas--punctuate-examples"></a>

#### Punctuate examples

For information about punctuating examples, see [Format examples](#format-examples).

---

<a id="dashes"></a>

### Dashes

*Source: <https://developers.google.com/style/dashes>*

This page explains when to use em dashes. For information about hyphens, see the following:

- [Hyphens](#hyphens)
- [Ranges of numbers](#numbers--ranges-of-numbers)
- [Ranges of numbers with units](#units-of-measure--ranges)

<a id="dashes--dashes"></a>

<a id="dashes--em-dashes"></a>

#### Em dashes

To indicate a break in the flow of a sentence—or an interruption—use an em
dash, also known as a long dash. Don't put a space before or after it.

You can type the em dash character in various ways:

**HTML**
    &mdash;

**macOS**
    Press `Option+Shift+hyphen`.

**Linux desktop environment**
    Enable the Compose key (instructions for doing that vary depending on
    your flavor of Linux—for examples, see [Linux Keyboard Shortcuts For
    Text Symbols](http://fsymbols.com/keyboard/linux/compose/)). After the Compose key is enabled, you can create an em dash
    by typing the Compose key followed by three hyphens.
    Alternatively, press `Control+Shift+U`. Let go of those keys, and then type
    `2014`. Then press `Return`.
    > [!NOTE]
    > **Note**: These Linux options don't work if
    > you're signed in to the Linux command line from a remote system using `ssh` or the
    > like; you have to be in a Linux desktop environment.

**Windows**
    Turn num lock on, and then hold down the left `Alt` key and type `0151`
    on the numeric keypad.

Don't use an en dash (the shorter dash) or a hyphen in place of an em dash.
The use of an en dash with spaces around it in place of
an em dash is gradually becoming more common, but it's still not very widespread
in the US in professional publishing; so far (as of early 2016), it's mostly
used in Canada and a few other places. For now, only use the em dash.

<a id="dashes--ndashes"></a>

<a id="dashes--en-dashes"></a>

#### En dashes

Don't use. Instead, use a hyphen or the word *to*. For more information, see
the following:

- [Ranges of numbers with units](#units-of-measure--ranges)
- [Range of numbers](#hyphens--number-range)

<a id="dashes--colons"></a>

<a id="dashes--colons-instead-of-dashes-in-description-lists"></a>

#### Colons instead of dashes in description lists

Another common but nonstandard construction is to use an em dash, an en dash, or a hyphen
surrounded by spaces to separate an item and its description. Instead, use
[a colon or a period](#lists--description-lists-that-use-run-in-headings).
For a series of items, use
[an HTML description list](#lists--description-lists) (`<dl>`).

Recommended: Example: This is an
example.

Not recommended: Example - This is
an example.

Recommended: Appendix A: My first
appendix

Not recommended: Appendix A—My first
appendix

Recommended:

```
    <dl>
      <dt>Example</dt>
      <dd>This is an example.</dd>
      <dt>Another example</dt>
      <dd>This is another example.</dd>
    </dl>
    
```

---

<a id="ellipses"></a>

### Ellipses

*Source: <https://developers.google.com/style/ellipses>*

In general, don't use ellipses. An ellipsis is made up of
three contiguous periods. Ellipses indicate the omission of part of a sentence, paragraph, or larger
block of text where the omission is not pertinent to the understanding of the subject at
hand.

<a id="ellipses--suspension-points"></a>

<a id="ellipses--ellipses-as-suspension-points"></a>

#### Ellipses as suspension points

When ellipses are used to indicate hesitation, they are called *suspension
points*. Don't use ellipses this way in our documentation.

Not recommended: The answer is ... wait
for it ... that you shouldn't do this.

<a id="ellipses--how-to-use-ellipses"></a>

<a id="ellipses--ellipses-in-a-user-interface"></a>

#### Ellipses in a user interface

When ellipses appear in a user interface, exclude them from the
documentation describing the user interface unless their omission could cause
confusion. For example, if the text on the button in the UI reads **Save ...**,
document it as *click **Save***.

<a id="ellipses--ellipses-in-text"></a>

#### Ellipses in text

Don't use ellipses in your written documentation; omit any unnecessary
information and include all necessary information.

However, it's acceptable to use ellipses in quoted text (to replace a
portion of the quoted text) except when they appear at the beginning or end of
the text.

Not recommended: My high school English
teacher made me learn that Shakespeare quote about all the world being a stage
and " ... all the men and women merely players."

Not recommended: My high school English
teacher made me learn that Shakespeare quote: "All the world's a stage, And all
the men and women merely players ...."

The previous example ended with four ellipsis points. The final
ellipsis point is, in fact, a period. So when the material that you're omitting
contains one or more sentence boundaries, use four dots instead of three.

Recommended: My high school English
teacher made me learn that Shakespeare quote: "All the world's a stage, ....
And one man in his time plays many parts."

<a id="ellipses--punctuation-and-spacing-of-ellipses"></a>

#### Punctuation and spacing of ellipses

Keep all three ellipsis points together. When creating an ellipsis,
instead of the ellipsis character, use three periods in a row. Insert one space
before and after the ellipsis unless a punctuation mark immediately follows the
ellipsis; in this case, don't insert a space after the ellipsis.

Recommended: You don't need to
understand all the other Python code in there ... we'll explain it all in class.

Also recommended: You don't need to
understand all the other Python code in there ...; we'll explain it all in class.

Not recommended: You don't need to
understand all the other Python code in there...we'll explain it all in class.

---

<a id="hyphens"></a>

### Hyphens

*Source: <https://developers.google.com/style/hyphens>*

Use a hyphen (-) when needed for clarity. A hyphen can separate parts of words to avoid
misreadings, and it can combine terms when they should be read as a unit.

<a id="hyphens--general-guidelines"></a>

#### General guidelines

Guidance for hyphenation isn't always straightforward because it depends on
the following circumstances:

- **Location**. For example, does a term precede a noun, or does it follow a
  verb?
- **Interpretation and readability**. Is a sentence ambiguous or unclear if a term is
  not hyphenated?
- **Convention**. For some terms, our guidance tells us to always hyphenate or
  never hyphenate, even if the convention seems to contradict other guidance.

In addition, there are many exceptions to general hyphenation guidance. If you're not
sure whether to hyphenate a term, in addition to reviewing the guidelines on this page, check the
following sources (in this order):

1. The documentation that you're working with. If there's an established
   convention for hyphenating a term in a particular documentation set, follow that
   convention.
2. The [word list](#word-list) in this style guide.
3. The [Merriam-Webster
   dictionary](https://www.merriam-webster.com/).

As always, deviate from our guidance when it serves your readers. For
more information, see [Break the rules](#style--rules).

> [!NOTE]
> **Note**: Don't use a hyphen (-) or a double
> hyphen (--) in place of a dash (—). The dash is a distinct punctuation mark
> that has different uses. For more information, see
> [Dashes](#dashes).

<a id="hyphens--prefixes"></a>

#### Prefixes

In general, don't use a hyphen between a prefix and the main noun.

Recommended: *infrastructure*,
*megabyte*, *metadata*, *preprocessing*, *pseudocode*,
*semiconductor*

<a id="hyphens--exceptions"></a>

##### Exceptions

Add a hyphen after a prefix in the following circumstances:

- If the prefix is *self* or *cross*: *self-managing*,
  *cross-region*
- If the noun is capitalized or is a number: *non-Google*,
  *post-2000*
- To avoid confusion or difficulty in reading: *de-energize*, *intra-index*,
  *re-mark*, *re-sign*
- If the prefix is for a term that already has hyphens or spaces:
  *un-Google-like*, *non-twentieth-century*
- To be consistent within a document: *pre-processing*,
  *post-processing*

<a id="hyphens--the-non-prefix"></a>

##### The *non* prefix

The *non* prefix follows the same guidelines, but because it
can easily form words that are hard to parse, it's often hyphenated. Use your
best judgment, taking into account consistency within your documentation. The following
recommendations show contrasting usages that you can use as examples.

Recommended: *noncurrent*,
*nonempty*, *noninteractive*, *nonpublic*

Recommended: *non-existence*,
*non-integer*, *non-key*, *non-managed*, *non-negative*

When using *non* as a prefix, add a hyphen before hyphenated compound words.

Recommended: *non-KSA-based*,
*non-self-sustaining*
<a id="hyphens--compounds"></a>

#### Compounds

A *compound* is a term that combines more than one word. Compounds can
be *closed* as one word with no spaces, *open* with spaces between
words, or hyphenated.

<a id="hyphens--compound-nouns"></a>

##### Compound nouns

In general, write compound nouns in their closed (one-word, unhyphenated)
form. If you see that
[Merriam-Webster.com](https://www.merriam-webster.com/) uses the
two-word or hyphenated form, but you see that the closed form is the
predominant convention in your context or trending in that direction (as
compounds often do), then use the closed form.

Recommended: webpage

Recommended: hostname

Recommended: tradeoff

Recommended: workaround

<a id="hyphens--exceptions_1"></a>

###### Exceptions

Our [word list](#word-list) includes exceptions for
well-established terms that commonly use a hyphen or a space, such as
*multi-region* and *style sheet*. In some cases, we note that noun,
verb, and adjective versions of a word are treated differently.

<a id="hyphens--multiplied-units"></a>

When the components of a unit of measurement are multiplied by each other,
hyphenate them.

Recommended: 5 vCPU-hours

Recommended: 40 person-hours

<a id="hyphens--compound-modifiers-before-a-noun"></a>

##### Compound modifiers before a noun

If needed for clarity, hyphenate compound modifiers that come before a noun.
This guideline can be subjective. However, except as noted in
this section, it's almost never wrong to hyphenate a compound before a
noun to ensure clarity.

Recommended: A well-designed app

Recommended: Android-specific
techniques

Use a hyphen after *more* or *most* if you need to clarify what
those words modify.

Recommended: The most common scenario

Recommended: Edge locations with
more-reliable internet links

In general, avoid writing compound modifiers that have more than two words.
Instead, move some words after the noun. If you must use this type of
compound, then use a hyphen between each word as needed for clarity.

Recommended: test cases
that are specific to the 2023 edition

Recommended:
cross-data-center replication

Not recommended:
edition-2023-specific test cases

<a id="hyphens--numbers-and-units-of-measurement"></a>

###### Numbers and units of measurement

Hyphenate a number and a spelled-out unit of measurement when they combine to modify a
noun.

Recommended: a 64-bit system

Recommended: 100,000-byte files

Recommended: a five-minute wait

Don't hyphenate if the unit of measurement is abbreviated unless the hyphen is needed for
clarity. Instead, use a nonbreaking space (`&nbsp;`) between the number and unit of
measurement.

Recommended: `200&nbsp;GB
disk` (200 GB disk)

Recommended:
`50&nbsp;Mbps connection` (50 Mbps connection)

For more information, see [Units of measurement](#units-of-measure).

<a id="hyphens--exceptions_2"></a>

###### Exceptions

Don't hyphenate adverbs that end in *-ly* except when needed for clarity.

Recommended: Publicly available
implementations

Not recommended: Publicly-available
implementations

Don't use hyphens in compounds that are conventionally not hyphenated. Follow the
guidance in the [word list](#word-list)
or check the convention in the documentation that you're working with.

Recommended: A managed
instance group (MIG)

Recommended: A machine
learning model

<a id="hyphens--compound-terms-after-a-verb"></a>

##### Compound terms after a verb

In general, you don't need to add a hyphen to a compound that follows a verb.

Recommended: The app is well
designed.

Recommended: The logs are written
in real time.

Recommended: The product supports
high availability.

Recommended: The app uses techniques
that are Android specific.

Recommended: Customers can use
the utility as is.

Recommended: Get profile information
for the currently authorized user.

<a id="hyphens--exceptions_3"></a>

###### Exceptions

Some compound terms are always hyphenated, even if they follow a verb. To
check, look the term up in the [word list](#word-list). If it isn't in the
list, check the [Merriam-Webster dictionary](https://www.merriam-webster.com/).
As always, follow the convention in the documentation that you're working with.

Recommended: You can deploy the app
on-premises.

Recommended: The docs describe how
to create an add-on.

Recommended: The utility works
with apps that are cloud-based and cloud-adjacent.

Recommended: This page is
customer-facing.

Recommended: The app is designed
to be user-friendly.

Recommended: The goal is to produce
an experience that's game-like.

<a id="hyphens--number-range"></a>

<a id="hyphens--range-of-numbers"></a>

#### Range of numbers

Use a hyphen, not an en dash (`&ndash;`),
to indicate a range of numbers. If a hyphen introduces ambiguity, use words such as
*from*, *to*, and *through* for clarity. Don't mix hyphens with words.
For information about how to represent a range of numbers that includes units, see
[Ranges of numbers with units](#units-of-measure--ranges).

Recommended: 8-20 files

Recommended: 5-10 minutes

Recommended: from 8 to 20 files

Not recommended: from 8-20 files

<a id="hyphens--spaces-around-hyphens"></a>

#### Spaces around hyphens

Never place a space on either side of a hyphen except when using a
[suspended hyphen](#hyphens--suspended-hyphens), in which case you can leave a space after
(but not before) the hyphen.

<a id="hyphens--suspended-hyphens"></a>

#### Suspended hyphens

When two or more compound modifiers have a common base, you can keep the
hyphens but leave out the base for all except the last modifier. In the
following examples, the base is *hour*.

Recommended: You can set up the system to
scan for new files at one- or two-hour intervals.

Recommended: You can set up the system to
scan for new files at one-, two-, or three-hour intervals.

---

<a id="parentheses"></a>

### Parentheses

*Source: <https://developers.google.com/style/parentheses>*

Some of us love to use parentheses. Unfortunately, some readers ignore
anything that appears in parentheses, so don't put important information in
parentheses if you can help it.

Even for less important information, whenever you're inclined to use
parentheses, consider whether they're necessary. Sometimes they are; however,
the sentence or paragraph might work just as well if you remove the
parentheses and set off the phrase or sentence by using commas, dashes, semicolons,
or periods.

If you need to include parentheses in the middle of a sentence, keep the parenthetical thought
short. Otherwise, consider using two sentences.

> [!NOTE]
> **Note**: If a full standalone sentence appears inside
> parentheses, the period also goes inside the parentheses, not outside.

Recommended: Enter a name for the instance—for example, `my-instance-99`.

Recommended: Enter a six-digit hex number (for example, `228B22`), and then click **OK**.

Recommended: Enter a six-digit hex number, and then click **OK**. For example, if you want the color forest
green, enter `228B22`.

Not recommended: Enter a name for the instance (for example, `my-instance-99`).

Not recommended: Enter a six-digit hex number (for example, if you want the color forest green, enter
`228B22`), and then click **OK**.

Don't use parentheses to indicate optional plurals. For more information, see [Plurals in parentheses](#pluralization--plurals-in-parentheses).

---

<a id="periods"></a>

### Periods and end punctuation

*Source: <https://developers.google.com/style/periods>*

End a complete sentence with a period, unless it's a question. There are
exceptions for working in lists.

<a id="periods--periods-with-lists"></a>

#### Periods with lists

Whether to end a list item with a period depends on several factors, including
the kind of list that the item appears in.

For details about how to use periods in lists, see the
[Capitalization and end punctuation](#lists--capitalization-and-end-punctuation)
section of the "Lists" page.

<a id="periods--periods-with-URLs"></a>

<a id="periods--periods-with-urls"></a>

#### Periods with URLs

When a period immediately follows a URL or a file path, it can be hard to
tell whether the period is part of the URL.

To indicate that the punctuating period isn't part of the URL, try one of the
following techniques:

- Whenever possible, avoid putting [URLs in text](#cross-references--urls).
- Rewrite the sentence so that the URL isn't at the end of the sentence.
- Put the URL on a separate line from the text, omitting the final period.

If the URL is a link, it generally looks different from the surrounding text. For
example, in most browsers, link text is blue by default. This formatting helps
distinguish the URL from the period.

Recommended:

We use your feedback to improve the Animals API, in accordance with Example
Pet Store's Privacy Policy:

http://www.examplepetstore.com/privacy/

Not recommended:

We use your feedback to improve the Animals API, in accordance with Example
Pet Store's Privacy Policy at http://www.examplepetstore.com/privacy/.

When you do put a period after a URL, don't leave any space between the last character of
the URL and the period.

<a id="periods--periods-with-quotation-marks"></a>

#### Periods with quotation marks

When a sentence ends with material inside quotation marks, place the period
inside the quotation marks even if the period isn't part of the material inside
the quotation marks. An exception to this guideline applies if you're using quotation marks around
a keyword or other literal string. For more information, see
[Commas and periods with quotation marks](#quotation-marks--commas-and-periods-with-quotation-marks).

Recommended: ... you might say "Fixed typo."

If the material inside the quotation marks ends with a question mark or an
exclamation point, don't use a period.

Recommended: Children always ask "Why?"

<a id="periods--periods-with-parentheses"></a>

#### Periods with parentheses

If the last part of a sentence is contained inside parentheses, put the
period after the closing parenthesis.

If the parentheses contain a complete sentence, put the period inside
the parentheses.

Recommended: Your application could show
a notification when a relevant file or folder has changed (even if that change
occurs while your application isn't running).

Recommended: App Engine applications are
easy to create, easy to maintain, and easy to scale. (With App Engine, there are
no servers for you to maintain.)

For more information, see [Parentheses](#parentheses).

<a id="periods--periods-with-headings"></a>

<a id="periods--periods_with_headings"></a>

#### Periods with headings

Don't end headings with periods.

For more information, see [Headings](#headings).

<a id="periods--periods-with-numbers"></a>

#### Periods with numbers

Use a period to represent a decimal point. (Using a comma to separate the decimal part
of a number is the editorial custom in some countries, but not in the US.)

For more information, see [Numbers](#numbers).

<a id="periods--periods-with-captions"></a>

#### Periods with captions

See [Figure captions](#images--figure-captions).

<a id="periods--periods-with-alt-text"></a>

#### Periods with alt text

See [Alt text](#images--alt-text).

<a id="periods--periods-with-abbreviations"></a>

#### Periods with abbreviations

Put a period after a shortened word.

Don't put periods after the letters of an acronym or initialism.

For more information, see [Abbreviations](#abbreviations).

<a id="periods--sentence-spacing"></a>

<a id="periods--spaces-between-sentences"></a>

#### Spaces between sentences

Leave only one space between sentences.

<a id="periods--exclamation-points"></a>

#### Exclamation points

In general, avoid exclamation points. They can appear unprofessional, alarming, or translate poorly into other languages. If you need to use an exclamation point, see the following guidance by content type:

- **Concept and reference docs.** Never use exclamation points. These sections should maintain a neutral, objective tone.
- **Procedural topics.** Avoid exclamation points. Use periods for completion steps—for example, "The VM is created."
- **Blog posts.** Exclamation points are acceptable to convey enthusiasm but shouldn't be used in every paragraph.

When exclamation points are acceptable:

- **Code examples.** Use when required by syntax—for example, the `!=` operator.
- **System literals.** Use when an exclamation point is part of a specific error code or log message that must be matched exactly.
- **Tutorials and learning modules.** Use sparingly to mark major milestones or achievements—for example, "Congratulations! You've completed the setup."

> [!NOTE]
> **Note:** For translation impact, be conservative with exclamation points in global documentation. In some languages, such as Japanese or Korean, exclamation marks can come across as overly emphatic or even shouting, which can alienate the reader.

---

<a id="quotation-marks"></a>

### Quotation marks

*Source: <https://developers.google.com/style/quotation-marks>*

Use straight double quotation marks and apostrophes.

<a id="quotation-marks--when-to-use-quotation-marks"></a>

#### When to use quotation marks

In technical writing, we don't use quotation marks much, aside from instances of code.

Generally, you can use quotation marks for
titles of shorter works such as articles or episodes in a web series, unless
they're part of a link. For more information, see [cross-references](#cross-references).

For most titles that are full-length works, we use italics.

For examples of when to use quotation marks in regular text, see the following table:

| Guidance | Example |
| --- | --- |
| Referring to a section of a larger document or piece, if you can't link to the section directly. | The technique is described in the section "Deploying containers" of the [Containers overview](https://www.youtube.com) video. |
| Referring to the title of a parent document when you're already linking to a section | The [machine learning (ML) workflow section](https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform#ml-workflow) of "Introduction to Vertex AI" describes the machine learning workflow for Vertex AI. |
| Directly citing a person or quoting a slogan or motto. | Martin Fowler has said, "We are still learning the techniques to write software effectively." |
| Using a term metaphorically, but only if it's not an established usage in the domain. | This configuration forms an "island" within the network that is not connected to the external network. |

For more information, see [Text-formatting summary](#text-formatting).
<a id="quotation-marks--commaquote"></a>

<a id="quotation-marks--commas-and-periods-with-quotation-marks"></a>

#### Commas and periods with quotation marks

Commas and periods go inside quotation marks.

Recommended: See the section
titled "Care and feeding of the emu."

Not recommended: See the section titled "Care
and feeding of the emu".

**Exception**: When you put a keyword or other literal string in quotation
marks, put any other punctuation outside the quotation marks. In those cases,
the quotation marks indicate an exact literal string, so don't add anything
extraneous inside the quotation marks. However, in general, don't put quotation marks
around an item that's in code font, unless the quotation marks are part of the
item.

Recommended: If you enter `escape`,
the program crashes.

Acceptable: If you enter "escape", the program
crashes.

Not recommended: If you enter "escape," the
program crashes.

<a id="quotation-marks--curly-and-straight-quotation-marks"></a>

<a id="quotation-marks--straight-and-curly-quotation-marks"></a>

#### Straight and curly quotation marks

Most typefaces support two forms of quotation marks and apostrophes:
straight marks and curly, or typographic, marks. Some tools, like
Google Docs, automatically convert straight quotation marks and
apostrophes to the curly versions as you type. However, our guidance is
to always use straight quotation marks and straight apostrophes in developer documentation, for
the following reasons:

- It makes writing documents easier.
  - Code *requires* straight marks, so it's simpler to use straight marks everywhere
    in developer documentation than to use them in code but not in text.
  - Tools that automatically change straight marks to curly marks (such as word processors)
    often make mistakes.
  - Humans who manually type curly marks also often make mistakes.
  - Manually typing curly marks can be difficult on some platforms.
- It makes reviewing documents easier.
  - When you're proofreading a document, it can be hard to see whether marks are straight or
    curly, and which direction they point in.

In the following examples, the first example uses straight quotation marks and the second example
uses curly quotation marks:

Recommended: The section's title is "Care
and feeding of the emu."

Not recommended: The section’s title
is “Care and feeding of the emu.”

<a id="quotation-marks--single-quotation-marks"></a>

#### Single quotation marks

The only times to use single quotation marks in our documentation are the following:

- In code examples, in languages that use single quotation marks.
- When nesting a quotation inside another quotation.

In the latter case, put the primary speaker's quote in double quotation marks and the quote inside
the primary speaker's quote in single quotation marks.

Recommended: She said, "I heard
him shout 'Help,' and saw him floundering in the water."

Not recommended: She said, 'I heard him shout
"Help", and saw him floundering in the water'.

> [!NOTE]
> **Note**: For information about how to use quotation marks with links, see
> [Quotation marks and italics](https://developers.google.com/style/cross-references#quotation-marks-italics).

---

<a id="semicolons"></a>

### Semicolons

*Source: <https://developers.google.com/style/semicolons>*

If possible, avoid using semicolons. In a few cases, a semicolon is preferred:

- When joining two closely related independent clauses where a period or a comma is not as
  effective.

  Recommended: You can easily test
  compatibility by computing the centroid; if it is on the opposite side of the
  planet, reverse the order of your vertices.
- When preceding a conjunctive adverb (like *therefore*) or a phrase
  (like *that is*) that joins two independent clauses.

  Recommended: This setup places the
  head-tracked node below the Main Camera; therefore, only the stereo cameras are
  affected by the user's head motion.

  Recommended: The URL from which a video
  ad loads; that is, the URL to use to fetch that video ad.
- When separating a series of long or complex items that contain their own punctuation.

  Recommended: If you don't have time,
  then focus on the improvements that will have the greatest benefit: what matters most
  to your users; what is most important to fix; and what is easy or feasible to
  fix in the available time.

  Recommended: Review your document one
  more time, checking for the following: present tense and active voice; typos,
  punctuation, and grammar; and whether you can shorten anything.

  Notice that in the final example, the second item in the list is itself a list.

---

<a id="slashes"></a>

### Slashes

*Source: <https://developers.google.com/style/slashes>*

Avoid using slashes, except in code.

<a id="slashes--slashes-dates"></a>

<a id="slashes--slashes-with-dates"></a>

#### Slashes with dates

Don't use date formats that rely on slashes.

For information about how to write dates, see
[Dates and times](#dates-times).

<a id="slashes--slashes-alternatives"></a>

<a id="slashes--slashes-with-alternatives"></a>

#### Slashes with alternatives

Don't use slashes to separate alternatives.

Recommended: For example, a disaster
relief map is not subject to the usage limits even if it has been developed and
is hosted by a commercial entity.

Recommended: For example, a disaster
relief map is not subject to the usage limits even if it has been developed or
is hosted by a commercial entity.

Not recommended: For example, a disaster
relief map is not subject to the usage limits even if it has been
developed/hosted by a commercial entity.

  

Recommended: Call this method five or six
times.

Not recommended: Call this method 5/6
times.

<a id="slashes--and-or"></a>

##### And/or

Often, *and* implies *or*, so you don't need to write both words.
If you need to specify both in your content, avoid writing *and/or* except
when space is limited, such as in tables.

Recommended: You can view
and edit your own data.

Not recommended: You can
view and/or edit your own data.

  

Recommended: You can
export raw events, processed events, or both.

Not recommended: You can
export raw and/or processed events.

<a id="slashes--slashes-file-paths-urls"></a>

<a id="slashes--slashes-with-file-paths-and-urls"></a>

#### Slashes with file paths and URLs

Use forward slashes, as appropriate, in computer file paths and URLs.

> [!NOTE]
> **Note**: If you're documenting a Windows path, use backslashes.

Recommended:
https://developers.google.com/cardboard/

Where very long URLs extend beyond a line, add a line break immediately after
a slash. Don't ever insert an extraneous hyphen into a URL to break it between two lines.

Recommended:
https://developers.google.com/
  
cardboard/

<a id="slashes--slashes-fractions"></a>

<a id="slashes--slashes-with-fractions"></a>

#### Slashes with fractions

Don't use slashes with fractions because they can be ambiguous.

In the following example, 3/4 could be interpreted either as three-quarters
or as stating that 4 is an alternative to 3.

Recommended: ¾

Recommended: 0.75

Recommended: 75%

Not recommended: 3/4

<a id="slashes--slashes-abbreviations"></a>

<a id="slashes--slashes-with-abbreviations"></a>

#### Slashes with abbreviations

Don't use abbreviations that rely on slashes. Instead, spell the words out.

Recommended: care of, with

Not recommended: c/o, w/

---

## Formatting and organization

<a id="dates-times"></a>

### Dates and times

*Source: <https://developers.google.com/style/dates-times>*

Expressing dates and times in a clear and unambiguous way helps support
[writing for a global audience](#translation) and reduces
confusion.

<a id="dates-times--expressing-times"></a>

#### Express times

In general, use the following guidelines to format expressions of time:

- Use the 12-hour clock, except if required to use a 24-hour time, such as
  when documenting features that use 24-hour time. If the UI, a command, or a code sample uses the
  24-hour format, use that format throughout the page for consistency.
- Use exact times when possible, but *noon* and *midnight* are OK.
- Use hyphens in time ranges. Don't add spaces before or after the hyphens.

  Recommended: 5-10 minutes ago.
- Capitalize AM and PM, and leave one space between it and the time.

  Recommended: 3:45 PM.
- Remove the minutes from round hours.

  Recommended: 3 PM.

<a id="dates-times--expressing-time-zones"></a>

##### Express time zones

Avoid using time zones unless absolutely necessary. In cases where you need to use a time
zone—such as describing real events at real times—use the following guidelines:

- Let the reader know if the time is local to their time—for example, *10 AM your local
  time*.
- If a time zone is necessary, use the timestamp format as seen in the user interface (if
  available).
- If using a specific time zone, spell out the region and include the
  [UTC or GMT label](https://www.worldtimeserver.com/learn/utc-vs-gmt/)
  as a parenthetical. For example:
  - US and Canadian Pacific Standard Time (UTC-8)
  - US and Canadian Pacific Daylight Time (UTC-7)
- Don't abbreviate the name of the time zone.
- In the rare event where the time of an event doesn't change for daylight saving time, use the
  specific time zone, without reference to UTC.

<a id="dates-times--expressing-dates"></a>

#### Express dates

In general, spell out the names of months and days of the week in full. Give
the full four-digit year, not a two-digit abbreviation.

Recommended: January 19, 2017

If including the day of the week, add it before the month as follows:
`DAY_OF_WEEK`, `MONTH` `DAY`,
`YEAR`.

Recommended: Tuesday, April 27, 2021

<a id="dates-times--partial-dates-abbreviations"></a>

##### Partial dates and abbreviations

When giving only the month and year, don't use a comma.

Recommended: She was hired in January
2017.

In most cases, don't abbreviate the day of the week or the month. However,
when conserving space, such as in a heading or table, it's okay to abbreviate
the month and the day of the week to their three-letter abbreviations.
Capitalize the first letter and do not add a period at the end of the abbreviation.

If you abbreviate, do so for the entire date. Don't mix written-out forms with
abbreviated forms in the same date.

Be consistent in where you apply abbreviations throughout your documentation. For
example, if you choose to abbreviate in table cells, do so in all table cells.

Recommended: Mon, Sep 3, 2018

Not recommended: Mon, September 3, 2018

<a id="dates-times--dates-mid-sentence"></a>

##### Dates in the middle of a sentence

When a `MONTH` `DAY`, `YEAR`
date appears in the middle of a sentence, add a comma after the year.

Recommended: The January 19, 2017,
release of ...

However, if the date in the middle of the sentence consists of the
month and year only, don't use a comma.

Recommended: The January 2017 release
of ...

<a id="dates-times--why-dates-written-out"></a>

##### Why we prefer dates written out

In general, don't express months as numbers unless you don't have the option
(in which case, see [numeric-only date
format](#dates-times--numeric-only-date-format)). Different regions of the world put parts of the date in a different
order for numeric dates. For example, a date written as 04/05/09 means different
things in different regions:

- In the UK, 04/05/09 means May 4, 2009, where the order is usually day,
  month, and then year.
- In the US, 04/05/09 means April 5, 2009, where the order is usually month,
  day, and then year.
- In some other parts of the world, 04/05/09 means May 9, 2004. Some
  regions write the year first, followed by the month and day.

For this reason, we recommend always using words to express dates. Expressing
dates in numbers only (using slashes, periods, or hyphens as separators) can be
confusing.

Recommended: February 12, 2017

Recommended: Sunday, February 12, 2017

Not recommended: 02.12.2017

Not recommended: 12/02/2017

<a id="dates-times--numeric-only-date-format"></a>

##### Numeric-only date format

If you must express a date in numerical date format, use the format
`YYYY-MM-DD`, and separate the elements by using hyphens. This conforms
to [ISO 8601 international
standards](https://wikipedia.org/wiki/ISO_8601) for numerical date format.

Additionally, if you have a choice of what date to write (such as in a
fictional example), then choose a calendar day greater than 12 to differentiate
it from the month.

Recommended: 2017-04-15

Not recommended: 04/06/2017

<a id="dates-times--express-dates-and-times-together"></a>

##### Express dates and times together

If you must express a date and a time together, then mention the date first and then the time.

Recommended: 2017-04-15 at 3 PM

Recommended: May 4, 2009, at 6 PM

<a id="dates-times--divisions-year"></a>

#### Express divisions of the year

Avoid referring to seasons. Spring in the northern hemisphere is fall (autumn) in the
southern hemisphere. Instead, use the month, quarter, or temperature (if relevant).

| Recommended | Not recommended |
| --- | --- |
| During warmer months, data centers face a higher risk of cooling failures. | During summer months, data centers face a higher risk of cooling failures. |
| In November and December, data centers experience higher traffic volume. | In winter, data centers experience higher traffic volume. |
| Changes are released in October of each year. | Changes are released in the Fall of each year. |

---

<a id="format-examples"></a>

### Examples

*Source: <https://developers.google.com/style/format-examples>*

To introduce an example in a sentence, use the guidance in the following table. You can introduce
examples using *such as*, *for example*, or *like* in various ways.

| Guidance | Recommended | Not recommended |
| --- | --- | --- |
| Introduce a short-to-medium-length example at the end of a sentence. For clarity, consider setting off the example using a comma, parentheses, or an em dash as appropriate. Avoid using a semicolon for this purpose. | Choose a strong encryption algorithm, such as AES-256.  You can monitor various metrics for your managed database instances—for example, CPU utilization, storage capacity, and active connections.  The API supports common image formats like PNG and JPEG. | Enter a name for the instance, for example, `my-instance-99`.  Specify the region for deployment; for example, `us-central1`.  Enter a name for the instance (for example, `my-instance-99`). |
| Introduce a short example in the middle of a sentence. Keep the example in the middle of a sentence relatively short and consider setting it off with dashes, commas, or parentheses as appropriate. | Enter a six-digit hex number (for example, `228B22`), and then click **OK**.  The virtual machine (VM) requires an operating system, such as Ubuntu 22.04, to be installed.  Some elements, like buttons and input fields, have default accessibility attributes. | Enter a six-digit hex number (for example, if you want the color forest green, enter `228B22`), and then click **OK**. |
| Introduce a longer example as a separate sentence. For a longer example, introduce it as a separate sentence using *for example* as an adverb in that sentence. | You can assign tags to your virtual machine instances to categorize them. For example, you could tag instances by environment with `env:prod` or `env:dev`. |  |

---

<a id="images"></a>

### Figures and other images

*Source: <https://developers.google.com/style/images>*

Use images only when they provide useful visual explanations of information
that is otherwise difficult to express with words. For screenshots, be discreet. Only capture UIs
that are important to the discussion.

<a id="images--creating"></a>

<a id="images--create-and-save-images"></a>

#### Create and save images

Consider the following guidelines for images:

- To create a diagram, use any drawing tool.
- To take a screenshot, use any screen capture tool.
- Don't use images of text, code samples, or terminal output. Use actual
  text.
- For diagrams (architectural drawings, flow diagrams, and so on, as
  distinct from screenshots), use the following guidelines:

- Use SVG files if possible because SVGs stay sharp when you zoom in on
  the image.
- If you don't have an SVG file, then
  save your image as a PNG file unless you have a good reason to use a
  different format.
- Regardless of the format, don't use a transparent background. In
  particular, a transparent background can cause issues if you use the
  Devsite lightbox widget.

- For animations and videos, don't use animated GIF. Instead, use a more resource-efficient
  format (such as MP4).
- Be consistent for a given document or doc set in what operating system you use for
  screenshots—for example, take all screenshots on macOS or on Linux. Similarly, be consistent
  in how your screenshots look. If you take screenshots that include drop shadows of the
  main window, make sure that similar screenshots are consistent.
- Crop screenshots to show the relevant information. For example, don't include the
  full window if you just want to show a single button or menu item. Cropping helps the
  reader focus on the information that you want to convey in the screenshot, and it can help
  future-proof the screenshot if other parts of the UI change.
- Don't include personally identifying information (PII) in
  screenshots.

  If a source screenshot includes PII, hide it with a solid-color overlay
  with 100% opacity. Don't rely on blurs, mosaic effects, or similar
  image-processing effects to obscure PII; such effects can be reversed to reveal
  the original information.

  If you're exporting an image to a format that can include information on
  separate layers (for example, PDF or TIFF), flatten the image on export.
- Don't use image maps. Instead, provide a list of text references following the image. Reasons
  to avoid image maps include the following:

- Image maps are problematic for accessibility.
- Browser implementation for image maps varies, and image maps might not function correctly on
  mobile devices due to scaling.
- The technical complexity of creating and maintaining a coordinates overlay is often
  prohibitive.
- Use descriptive filenames for your image files. For more information, see
  [Filenames and file types](#filenames).

<a id="images--text-with-images"></a>

<a id="images--text-associated-with-images"></a>

#### Text associated with images

There are differences between alt text, figure captions, and figure
descriptions. Independently of these elements, an introductory sentence should precede most images.
The sentence can end with a colon or a period; usually a colon if it immediately precedes the image,
usually a period if there's more material (such as a note paragraph) between the introduction and
the image. Always introduce an image with a complete sentence. You don't need to introduce
screenshots that immediately follow procedural text that describes a UI.

<a id="images--example"></a>

##### Example

The following diagram shows how you can apply bounded contexts to an existing
ecommerce application:

<a id="images--bounded"></a>
![Bounded contexts are applied to an application.](https://cloud.google.com/architecture/images/microservices-architecture-refactoring-monoliths-bounded-contexts.svg)


**Figure 1**. Application capabilities are separated into bounded contexts that
migrate to services.

<a id="images--descr-1"></a>

In figure 1, the ecommerce application's capabilities are separated into
bounded contexts and migrated to services as follows:

- Order management and fulfillment capabilities are bound into the
  following categories:
  - The order management capability migrates to the order service.
  - The logistics delivery management capability migrates to the
    delivery service.
  - The inventory capability migrates to the inventory service.
- Accounting capabilities are bound into a single category:
  - The consumer, sellers, and third-party capabilities are bound
    together and migrate to the account service.

<a id="images--html"></a>

##### HTML

```
      <p>The following diagram shows how you can apply bounded contexts to an existing ecommerce application:</p>
<figure id="bounded">
  <img src="https://cloud.google.com/architecture/images/microservices-architecture-refactoring-monoliths-bounded-contexts.svg"
    alt="Bounded contexts are applied to an application.">
  <figcaption><b>Figure 1.</b> Application capabilities are separated into bounded
  contexts that migrate to services.</figcaption>
</figure>
<div id="descr-1">
<p>In figure 1, the ecommerce application's capabilities are separated into
bounded contexts and migrated to services as follows:</p>
<ul>
  <li>Order management and fulfillment capabilities are bound into the
    following categories:
  <ul>
    <li>The order management capability migrates to the order service.</li>
    <li>The logistics delivery management capability migrates to the
        delivery service.</li>
    <li>The inventory capability migrates to the inventory service.</li>
  </ul>
  </li>
  <li>Accounting capabilities are bound into a single category:
  <ul>
  <li>The consumer, sellers, and third-party capabilities are bound
        together and migrate to the account service.</li>
  </ul>
  </li>
  </ul>
</div>
```

<a id="images--markdown"></a>

##### Markdown

```
The following diagram shows how you can apply bounded contexts to an existing ecommerce application:

![Bounded contexts are applied to an application.](https://cloud.google.com/architecture/images/microservices-architecture-refactoring-monoliths-bounded-contexts.svg)

**Figure 1.** Application capabilities are separated into bounded contexts that migrate to services.

In figure 1, the ecommerce application's capabilities are separated into bounded contexts and
migrated to services as follows:

-   Order management and fulfillment capabilities are bound into the following categories:

    -   The order management capability migrates to the order service.
    -   The logistics delivery management capability migrates to the delivery service.
    -   The inventory capability migrates to the inventory service.

-   Accounting capabilities are bound into a single category:

    -   The consumer, sellers, and third-party capabilities are bound together and migrate to the
        account service.
```

<a id="images--alt-text"></a>

##### Alt text

*Alt text* is a concise description of the image that can replace the image in
situations where the image isn't visible, such as people using screen
readers, people using text-only browsers, or people who have a low-bandwidth
internet connection. Alt text should consider the context of the image, not just its content.
The presence of `alt` attributes helps support
[navigability](https://web.dev/labels-and-text-alternatives/#include-text-alternatives-for-images-and-objects)
in screen readers, [markup validation](https://validator.w3.org/docs/help.html#validation_basics),
and [search engine optimization](https://support.google.com/webmasters/answer/7451184#usealtattribute).
For more information, see [alt attribute](https://wikipedia.org/wiki/Alt_attribute).

However, if the image is decorative (not informative) or it's
provided only as a visual aid for information that is already expressed in text,
then provide empty alternative text (`alt=""`) so it's ignored
by assistive technologies. Examples of decorative images include the following:

- A screenshot of the UI showing a user how to fill out fields.
- Icons in the UI.
- Images whose purpose is to make the page more visually appealing.

When using the `img` element, the `alt` attribute is required,
even if its assigned value is an empty string (`alt=""`). If you exclude the `alt`
attribute completely, then screen readers might instead read the filename aloud.

As per the [HTML
specification](https://html.spec.whatwg.org/dev/images.html#general-guidelines), "the most general rule to consider when writing alternative
text is the following: the intent is that replacing every image with the text of
its `alt` attribute does not change the meaning of the page." So if the
alternative text is redundant with surrounding text or it's not useful to
visually impaired readers, use the empty tag.

Consider the following when writing alt text:

- Don't include phrases like *Image of* or *Photo of*.
- Include punctuation. When screen readers encounter punctuation, they
  pause before continuing.
- Use consistent alt text for repeated instances of an image, such as
  controls, status indicators, or icons that appear multiple times in your
  document.
- When possible, avoid using all-caps in alt text. Some screen readers read
  capital letters as each letter individually.
- Introduce diagrams in the text, not in the alt text.
- Don't use figure captions to replace alt text.
- Use full sentences or a noun phrase.

  Recommended: `alt="Architecture of
  an app that's built with Apps Script."`

  Recommended: `alt="A card
  message."`
- Write short, descriptive alt text in 155 characters or less.
- If the image presents more useful information than you can fit in the 155 character limit,
  include a brief summary of the image in the `alt`attribute and also include a more
  extensive description of the image in the text.
- Alt text should consider the context of the image, not just its content.

<a id="images--figure-captions"></a>

##### Figure captions

*Figure captions* are concise and comprehensive summaries of a figure or image. Figure
captions (and figure numbers) are optional. When using the [`figcaption`
element](https://html.spec.whatwg.org/multipage/semantics.html#the-figcaption-element), you must wrap both the `figcaption` and `img`
elements in the [`figure`
element](https://html.spec.whatwg.org/multipage/semantics.html#the-figure-element) to ensure that the figure caption is properly associated with the image.

Consider the
following when writing figure captions:

- Figure numbers are optional. If you use figure numbers, use the form "<b>Figure
  NUMBER.</b> DESCRIPTION."

  Recommended: **Figure 1**. Application
  capabilities are separated into bounded contexts that migrate to services.

  Recommended: Application
  capabilities are separated into bounded contexts that migrate to services.

  Not recommended: Bounded contexts
- We recommend using complete sentences in figure captions.
- Always use end punctuation for captions.
- When you refer to a figure, don't use spatial descriptions such as "the image above."

  - If you used figure numbers, consistently refer to the figure by number. For example:
    "... as shown in figure 1." Don't capitalize the word *figure* in a reference to a figure,
    except at the start of a sentence.
  - If you can't use figure numbers, show the figure again, for accessibility and user experience
    reasons.
- Don't include the figure caption in a sentence referencing the
  figure.

<a id="images--figure-descriptions"></a>

##### Figure descriptions

A *figure description* is text that provides a more detailed explanation of information
represented by a figure. In other words, the information that is conveyed in the image is captured
in the text. Any new information should be conveyed through text and not introduced in
a figure or image.

Consider the following when writing figure descriptions:

- Create text that conveys the same information as the figure.
- Use when a figure caption doesn't convey the purpose or complete information of the figure.
- Use punctuation in figure descriptions.

<a id="images--text-in-figures"></a>

##### Text in figures

In most cases, avoid embedding explanatory text in screenshot graphics; text
that's incorporated into a graphic hurts accessibility and searchability, and
increases localization costs if figures are localized. If you must embed text in
an image, then be sure to also provide the same information in a form that
people with visual disabilities can use, such as a figure description.

When you must include text in figures and images, use the following
guidelines:

- Keep text brief. Avoid complete sentences and punctuation when
  possible.
- Don't embed figure descriptions or captions in the figure or image.
  Instead, put figure descriptions and captions in text following the figure.
- Don't create new abbreviations to condense text.
- Use sentence case. Follow guidelines for [capitalization
  for titles and headings](https://developers.google.com/style/capitalization#capitalization-in-titles-and-headings_1).
- Use numbered callouts in figures to help you write a figure description,
  but don't use callouts for detailed annotations in the image.
- Use full trademarked product names.

<a id="images--accessibility-resources"></a>

##### Accessibility resources

For more information about the accessibility of diagrams and screenshots, see the following
resources:

- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/standards-guidelines/wcag/glance/)
- [General text alternative guidelines from WCAG](https://www.w3.org/WAI/WCAG21/quickref/?showtechniques=111#text-alternatives)
- [Using `alt` attributes for `img` elements](https://www.w3.org/WAI/WCAG21/Techniques/html/H37.html)
- [Providing a long description in text near the non-text content](https://www.w3.org/WAI/WCAG21/Techniques/general/G74.html)
- [Complex images](https://www.w3.org/WAI/tutorials/images/complex/)

<a id="images--high-resolution"></a>

<a id="images--high-resolution-images"></a>

#### High-resolution images

Modern browsers can use high-resolution images if they are available; this
makes the images look better on high-resolution displays.

To provide a high-resolution image, use the `img`
element's `srcset` attribute in addition to the standard
`src` attribute. The `srcset` attribute lets you specify
different image assets for different screen resolutions. It accepts a
comma-delimited set of image URLs, with the target screen resolution specified
by a size qualifier: `1x` meaning the "standard" resolution,
`2x` meaning "double" the resolution, and so on.

If a web browser supports the `srcset` attribute, it selects an
image from the specified images that's an appropriate resolution for the current
display. If the browser doesn't support the `srcset` attribute, it
uses the image in the `src` attribute. Consequently, you must always
still include the `src` attribute.

For example, to provide both a standard resolution image and a
double-resolution image, add a `srcset` attribute and specify both
`1x` and `2x` image assets:

```
<img src="/assets/images/skateboard.png"
  srcset="/assets/images/skateboard.png 1x,
  /assets/images/skateboard_2x.png 2x"
  width="375" alt="" />
```

- The `width` attribute matches the CSS pixel size used for the
  page dimensions. (The height is automatically calculated based on the width and
  the image's proportions; *don't* state it explicitly.)
- Set the `src` attribute to point to the standard-resolution
  (`1x`) image, *not* the `2x` version. (Almost
  everyone who has a high-resolution screen also has a modern browser that can
  recognize the `srcset` attribute. The `src` attribute is
  mainly used by older browsers on low-resolution devices, which should download
  the smaller, low-resolution image.) Even if your original image is the
  higher-resolution image, set the `src` attribute to use the
  standard-resolution version; don't force a reader using a low-resolution screen
  to download a graphic that's higher-resolution than they can view.
- The filename for the double-resolution image (in this case,
  `skateboard_2x.png`) can be anything—it's the "`2x`"
  value following the filename that informs the browser which resolution the file
  is. But it's a good idea to use a filename of the form
  `BASENAME_2x.EXTENSION` to make clear to human
  readers that it's a double-resolution version of
  `BASENAME.EXTENSION`.
- The double-resolution image must be exactly twice the width and height of
  the standard image, give or take a pixel. (For example, it's okay for the
  double-resolution image to be 875x500 and the standard size to be 438x250.)
- Don't scale up an existing `1x` image to make the
  `2x` version. If all you have is the `1x` version, then
  use it alone. But if you're starting with a high-resolution image (at
  `2x` resolution or better), then you can scale it down to appropriate
  dimensions for `1x` and `2x`.
- Currently, only an additional `2x` image is necessary, but
  someday screen PPI may increase further.
  So the `srcset` attribute supports further alternative sizes, each
  specified by the appropriate multiplier, such as `3x` or
  `4x`.
- A browser that supports the `srcset` attribute uses only the
  images provided in that attribute—it ignores the `src` attribute. So
  specify all available image resolutions in the `srcset`
  attribute.

> [!NOTE]
> **Note**: If you frequently revise an image, then you can
> use the `2x` image for both the `src` and
> `srcset` attributes, rather than maintaining multiple sizes of the
> image. If things stabilize and you no longer need to revise the image, then you
> can add a `1x` version.

For more information, see the HTML specification for the `img`
element.

<a id="images--layout"></a>

<a id="images--layout-of-images-on-a-page"></a>

#### Layout of images on a page

Consider the following guidelines for adding images to pages:

- Don't try to place an image manually; for example, don't use a
  `style` attribute or other workarounds to control the image's
  left/right justification or the margins around the image. Instead, use
  your site's standard CSS image styles.
- Don't make your image too small. It's fine for an image to take up the
  full width of a page.
- Consider how the image will look when printed out.
- In general, don't use an image that's wider than the column it appears
  in. On [developer.android.com](https://d.android.com), for
  example, the main-body column is 856px wide, so use images that are no wider
  than that. In that context, the high-resolution 2x version of the image should
  be no wider than 1712px.

  - Screenshots at full resolution often take up too much space on the
    page, so you may have to resize them.
  - If the graphics were created by someone else (for example, a designer
    on the team you're supporting), it may be fairly trivial for them to provide you
    with images at the appropriate size. If the images they provide are wider than
    856px, ask the designer if they can provide the relevant graphics as
    856px/1712px pairs.
- Don't link to the figure from within the same page unless it's a very
  long page and you're linking to it from quite far away on the page.
- Don't center the image on the page.
- Don't put an `img` element inside a `p` element.

---

<a id="footnotes"></a>

### Footnotes

*Source: <https://developers.google.com/style/footnotes>*

A footnote is an annotation with additional information usually provided at the end of a page,
chapter, or book. We recommend avoiding footnotes because they aren't accessible and can present
challenges for localization efforts.

Instead of a footnote, consider using the following formats to convey information:

- [Add a cross-reference](#cross-references).
- [Use a note](#notices).
- [Put it in a parenthetical](#parentheses).

If the only way to convey this information is to use a footnote, then use a superscript
number—for example, `<sup>1</sup>`.

Recommended: You want to add a footnote to this sentence.1

1 Put this footnote at the bottom of the page.

---

<a id="headings"></a>

### Headings and titles

*Source: <https://developers.google.com/style/headings>*

Use sentence case for headings and titles. Use descriptive headings and titles because they help
a reader navigate their browser and the page. It's easier to jump between pages and sections of a
page if the headings and titles are unique.

<a id="headings--heading-and-title-text"></a>

#### Heading and title text

Write document titles based on the primary purpose of the document. If a
document is primarily a tutorial, but it has a conceptual introduction, write a
task-based title. Write section headings based on the type of content that's in
the section.

| Guidance | Recommended | Not recommended |
| --- | --- | --- |
| For a task-based heading, start with a [*bare infinitive*](https://wikipedia.org/wiki/Infinitive#English), also known as a *plain form* or [*base form*](https://wikipedia.org/wiki/English_verbs#Base_form) verb. In English, the *imperative mood* also uses the base form verb, so it looks the same as the bare infinitive.  Task-based headings are frequently used in quickstarts, how-to documents, and tutorials. | Create an instance | Creating an instance |
| For a conceptual or non-task-based heading, use a [*noun phrase*](https://wikipedia.org/wiki/Noun_phrase) that doesn't start with an *-ing* verb.  Noun-phrase headings are frequently used in concept documentation. | Migration to Google Cloud | Migrating to Google Cloud |
| If a section is not required for all users or scenarios, use the *Optional:* prefix in the heading. This prefix signals when the section information applies only to a specific configuration or use case.  For information about optional steps in a procedure, see [Optional steps](#procedures--optional-steps). | Optional: Customize your alias | Customize your alias (optional) |

<a id="headings--title-phrasing"></a>

##### Title phrasing

Use a unique level-1 heading (`h1`) for each page in a set of documents and only use
a level-1 heading once on a page.

Avoid repeating the exact page title in a heading on the page. For example, if you document
how to create a virtual machine and how to start a virtual machine on the same task-based
page, the page title might be *Create and start VM instances*, with section headings
*Create a VM* and *Start a VM*.

<a id="headings--mixed-heading-styles"></a>

##### Mixed heading styles

It's OK to use task-based and conceptual heading styles in the same document.
If a single document includes both task-based and conceptual sections, then use
the appropriate phrasing for each section's heading.

<a id="headings--use-of--ing-verb-forms"></a>

##### Use of *-ing* verb forms

When possible, avoid using *-ing* verb forms as the first word in any heading or
title.

Recommended:
Transfer data sets

Not recommended:
Transferring data sets

An *-ing* verb form is a present participle or gerund. These verb forms
are inconsistently translated when they're used as the first word in a title,
and they increase character count in limited spaces.

Sometimes, there might not be a better alternative to using a gerund, such as the following
examples:

- Billing
- Pricing

It's OK to use a gerund in these cases.

It's OK to use an *-ing* verb form later in a heading or title, such as
*Introduction to BigQuery monitoring*.

<a id="headings--example-headings"></a>

##### Example headings

The following example is a task-based document that includes a conceptual
heading and a task-based heading.

Recommended:

<a id="headings--html"></a>

##### HTML

```
<h1>Log serving requests by using AI Platform Prediction</h1>

<p>This task-based document shows how to monitor machine learning models. The
document title starts with a bare infinitive.</p>

<h2>ML model monitoring overview</h2>

<p>This section provides a conceptual overview of ML model monitoring. Its title is
a noun phrase.</p>

<h2>Configure notebook settings<h2>

<p>This task-based section provides a series of steps to set variables in a
notebook. Its title starts with a bare infinitive.</p>
```

<a id="headings--markdown"></a>

##### Markdown

```
# Log serving requests by using AI Platform Prediction

This task-based document shows how to monitor machine learning models. The
document title starts with a bare infinitive.

## ML model monitoring overview

This section provides a conceptual overview of ML model monitoring. Its title is
a noun phrase.

## Configure notebook settings

This task-based section provides a series of steps to set variables in a
notebook. Its title starts with a bare infinitive.

```

<a id="headings--capitalization"></a>

<a id="headings--heading-and-title-format"></a>

#### Heading and title format

The following sections list and define our writing standards for capitalization,
abbreviations, and technical elements in headings. In general, guidance
that applies to standard text also applies to headings—for example,
[contractions](#contractions) and [articles](#articles).

<a id="headings--syntax-and-capitalization"></a>

##### Syntax and capitalization

- **Use sentence case** for all headings and titles. For more information, see
  [Capitalization in titles and
  headings](#capitalization--capitalization-in-titles-and-headings).
- **Keep punctuation simple**. Punctuation can be a sign that your heading is too complicated. Consider rewriting.
- **Limit abbreviations**. Only use an abbreviation of a word in a page title or heading if it's the more commonly known
  version of the word. If you do so, define the abbreviation in the first instance of the word in a paragraph.
  You can define the abbreviation in the page title or heading, but consider if the additional
  length adds value. For SEO, use the more prominent version of a term in headings. For more information, see
  [Abbreviations](#abbreviations).

<a id="headings--formatting-and-code"></a>

##### Formatting and code

- **Don't use numbers in headings** to indicate a sequence of sections.
  Instead, rely on heading hierarchy and order to indicate sequence.
- **Avoid code items in headings**. If you must mention a code item in a heading,
  add a descriptive noun to the item in code font. For more information, see
  [Grammatical treatment of code elements](#code-in-text--grammatical-treatment-of-code-elements).
- **Don't put links in headings**. A link can easily be confused as a style applied to the
  heading instead of a link.

<a id="headings--hierarchy-and-structure"></a>

##### Hierarchy and structure

- **Don't use heading tags to change visual formatting**. Use CSS rather than a heading level
  that doesn't fit the hierarchy. Don't make up your own formatting for headings.
- **Apply proper heading tags**. Use heading tags to structure your content hierarchically—for example,
  `<h1>`, `<h2>`, and `<h3>` in HTML, or
  `#`, `##`, and `###` in Markdown.
- **Maintain logical order**. Don't skip levels of the heading hierarchy. For example, put an `<h3>` tag
  only under an `<h2>` tag.

  Recommended:

  <a id="headings--html_1"></a>

  ##### HTML

  ```
  <h1>Transfer data sets</h1>

  <p>This document provides a high-level overview of ways to transfer your data to Google
  Cloud.</p>

  <h2>Estimate costs</h2>
  ```

  <a id="headings--markdown_1"></a>

  ##### Markdown

  ```
  # Transfer data sets

  This document provides a high-level overview of ways to transfer your data to Google Cloud.

  ## Estimate costs
  ```

  Not recommended:

  <a id="headings--html_2"></a>

  ##### HTML

  ```
  <h1>Transfer data sets</h1>

  <p>This document provides a high-level overview of ways to transfer your data to Google
  Cloud.</p>

  <h3>Estimate costs</h3>
  ```

  <a id="headings--markdown_2"></a>

  ##### Markdown

  ```
  # Transfer data sets

  This document provides a high-level overview of ways to transfer your data to Google Cloud.

  ### Estimate costs
  ```
- **Don't use empty headings**. Make sure headings are followed by content.

  Recommended:

  <a id="headings--html_3"></a>

  ##### HTML

  ```
  <h2>Migrate VMs to Compute Engine</h2>

  <p>Migration is not just a single step. The following sections describe the recommended
  steps.</p>

  <h3>Design the migration</h3>
  ```

  <a id="headings--markdown_3"></a>

  ##### Markdown

  ```
  ## Migrate VMs to Compute Engine

  Migration is not just a single step. The following sections describe the recommended steps.

  ### Design the migration
  ```

  Not recommended:

  <a id="headings--html_4"></a>

  ##### HTML

  ```
  <h2>Migrate VMs to Compute Engine</h2>

  <h3>Design the migration</h3>
  ```

  <a id="headings--markdown_4"></a>

  ##### Markdown

  ```
  ## Migrate VMs to Compute Engine

  ### Design the migration
  ```

<a id="headings--introducing-multiple-sections"></a>

<a id="headings--refer-to-a-group-of-sections"></a>

#### Refer to a group of sections

If you introduce a group of related H3 or lower sections within a larger H2 section, use the
phrase *the following sections*. Don't refer to the group of sections using the phrases
*this section* or *these sections* because those phrases are ambiguous.

Recommended:

<a id="headings--html_5"></a>

##### HTML

```
<h2>Views in the data preparation editor</h2>

<p>The following sections describe the views in the data preparation editor.</p>

<h3>Data view</h3>

<p>...</p>

<h3>Graph view</h3>

<p>...</p>

<h3>Schema view</h3>

<p>...</p>
```

<a id="headings--markdown_5"></a>

##### Markdown

```
## Views in the data preparation editor

The following sections describe the views in the data preparation editor.

### Data view

...

### Graph view

...

### Schema view

...
```

---

<a id="italics-terms"></a>

### Italics with terms

*Source: <https://developers.google.com/style/italics-terms>*

This page describes two circumstances when we italicize terms that we're
introducing or discussing.

For more information about italics and other formatting, including HTML and
Markdown formatting for italics, see
[Text-formatting summary](#text-formatting).

<a id="italics-terms--new_terms"></a>

#### New terms

When you introduce a new term that you're defining immediately, use italics on
the first mention of the term. Don't use bold or quotation marks.

Recommended: A
*Clos network* is a kind of multistage circuit switching network.

<a id="italics-terms--words_as_words"></a>

#### Words as words

When you refer to a word, phrase, or letter in reference to the word, phrase,
or letter itself (sometimes called *words as words*) use italics. Don't use bold
or quotation marks.

Recommended: Don't use
*&* (ampersand) as a conjunction. Use the word *and* instead.

Recommended: To form a
possessive of a singular noun, add *'s* to the end of the word.

---

<a id="lists"></a>

### Lists

*Source: <https://developers.google.com/style/lists>*

<a id="lists--list-or-table"></a>

#### List or table?

Tables and lists are both ways to present a set of similarly structured
items. Sometimes it's not obvious when to choose one presentation over the
other. To decide which presentation to use, see
[List or table?](#tables--list-or-table)

**Note**: Don't use a list to show only one item; a single
item isn't really a list. If you want to set a single item off from surrounding
text, then use some other formatting.

<a id="lists--types"></a>

<a id="lists--types-of-lists"></a>

#### Types of lists

Choose one of the following list styles. The following table includes common ways to present
lists in our documentation:

| List type | Used for | HTML elements |
| --- | --- | --- |
| Numbered list | A set of items where the sequence is significant, such as ordered steps, phases, or priorities. The following is an example of a numbered list:  Here's a sequence of steps to follow:   1. Open the box. 2. Remove the bobcat from the box. 3. Feed the bobcat.  Nested sequential lists are labeled with lowercase letters or lowercase Roman numerals. The following is an example of a nested sequential list:  Here's a list of things to do after breakfast, in order:   1. Go shopping.    1. Buy groceries:       - Flour       - Eggs       - Sugar       - Butter    2. Go to mall:       1. Buy dress.       2. Buy shoes. 2. Make cake. 3. Build birthday present out of spare parts. 4. Clean house.  See also [Sub-steps in numbered procedures](#procedures--sublists). | `ol`, `li` |
| Bulleted list | A set of items that's not a sequence, such as a set of nonsequential options or examples. Make sure it's clear whether or not every item is required. The following is an example of a bulleted list:  Here's a list of things that can go wrong, in no particular order:   - Your bicycle might explode. - The sun might go out. - An ant might break its leg and require a tiny splint. | `ul`, `li` |
| Description list | A set of terms, each with a description, definition, or explanation. Use this type of list if you want to draw attention to two or more terms (such as a glossary). The following is an example of a description list:  Here are some descriptions of types of birds:  Emu  The best kind of bird.  Crow  The other best kind of bird.  Peacock  Also the best kind of bird.  Phoenix  An even better kind of bird. | `dl`, `dt`, `dd` |
| Description list that uses bulleted run-in headings | A set of introductory terms or phrases, each followed by a description, definition, or explanation. Use this type of list if you want to highlight and explain several concepts or save space. For information about how to format and punctuate run-in headings and their descriptions, see [Description lists that use run-in headings](#lists--description-lists-that-use-run-in-headings) in this document.  The following is an example of a description list that uses bulleted run-in headings:  Here are some descriptions of types of birds:   - **Emu**: the best kind of bird - **Crow**: the other best kind of bird - **Peacock**: also the best kind of bird - **Phoenix**: an even better kind of bird | `ul`, `li` |

<a id="lists--multiple-paragraphs"></a>

<a id="lists--multiple-paragraph-list-items"></a>

#### Multiple paragraph list items

Any list item can contain more than one paragraph.

To create multiple paragraphs, use the `p` element rather
than using the `br` element. (The HTML specification describes which uses of the
[`br`
element](https://html.spec.whatwg.org/multipage/semantics.html#the-br-element) are legitimate and which aren't.)

Example of a list item that contains more than one paragraph:

- This list item is a single paragraph.
- This list item contains multiple paragraphs.

  As you can see!
- This is another list item that's only one paragraph long.

<a id="lists--intros"></a>

<a id="lists--introductory-sentences-for-lists"></a>

#### Introductory sentences for lists

Introduce a list with the appropriate context. In most cases, precede a list
with an introductory sentence. The sentence can end with a colon or a period; usually a colon if it
immediately precedes the list, usually a period if there's more material (such as a note
paragraph) between the introduction and the list.

If the list doesn't need any additional context other than the heading that immediately precedes
the list, it's OK to not introduce a list with an introductory sentence.

Introduce a list with a complete sentence, not a partial one that's
completed by the list items. You can also use *the following* as a noun phrase (see
[following](#word-list--following) in the word list).

| Recommended | Not recommended |
| --- | --- |
| Use the **Submit** button for any of the following purposes:   - To submit the form. - To indicate that you're done. - To allow the next person to enter their data. | Use the **Submit** button to:   - Submit the form. - Indicate that you're done. - Allow the next person to enter their data. |
| To get the USB driver, follow these steps:   1. Click **Tools >    Android > SDK Manager**. 2. Select **Google USB Driver**, and then click **OK**. | To get the USB driver:   1. Click    **Tools > Android >    SDK Manager**. 2. Select **Google USB Driver**, and then click **OK**. |
| If you need to add an instance manually, do the following:   1. Click **Create instance**. 2. For **Name**, enter a name. | If you need to add an instance manually:   1. Click **Create instance**. 2. For **Name**, enter a name. |
| <a id="lists--objectives"></a>Objectives  - Create an instance - Snapshot an instance - Delete an instance | <a id="lists--objectives_1"></a>Objectives In the following tutorial, you will complete the following tasks:   - Create an instance - Snapshot an instance - Delete an instance |

For information about introducing sub-steps, see [Sub-steps in numbered procedures](#procedures--sublists).

For information about punctuation and capitalization of lists, see
[Capitalization and end punctuation](#lists--capitalization).

<a id="lists--numbering"></a>

<a id="lists--unusual-list-numbering"></a>

#### Unusual list numbering

Use nonstandard numbering in the following situations:

- To present a list in reverse-numerical order, use an
  `ol` element with a `reversed` attribute.
- To set a value manually, use the `value` attribute. In some cases, setting a
  value manually can be convenient. However, in most cases, it isn't a good idea to manually
  number a list item in a numbered list, because if the number of items changes later, you'll
  have to manually change the value.

<a id="lists--sublists"></a>

<a id="lists--sub-steps-in-a-numbered-procedure"></a>

#### Sub-steps in a numbered procedure

For information about sub-steps in a numbered procedure, see
[Procedures](#procedures--sublists).

<a id="lists--parallel"></a>

<a id="lists--parallel-syntax"></a>

#### Parallel syntax

Use the same syntax/structure for all list items in a given list, if
possible.

<a id="lists--capitalization"></a>

<a id="lists--capitalization-and-end-punctuation"></a>

#### Capitalization and end punctuation

Capitalization and end punctuation depend on the type of list and the
contents of the list.

<a id="lists--numbered-lettered-bulleted-lists"></a>

##### Numbered, lettered, and bulleted lists

Start each list item with a capital letter, unless case is an important part of
the information conveyed by the list—such as in a list of glossary terms.

End each list item with a period or other appropriate sentence-ending
punctuation, except in the following cases:

- If the item consists of a single word, don't add end punctuation.
- If the item doesn't include a verb, don't add end punctuation.
- If the item is entirely in code font, don't add end punctuation.
- If the item is entirely link text or a document title, don't add end punctuation.

If you end up with inconsistent punctuation in your list, then either rewrite your list to use
[parallel construction](#lists--parallel) or add end punctuation to every list item
for consistency.

Recommended:

The following words are adjectives:

- Big
- Small
- Gratuitous

Recommended:

The SDK supports the following UI elements:

- Text box
- Bulleted list
- Button

Recommended:

The API supports the following actions:

- Create
- Replace
- Update
- Delete

Recommended:

You can do any of the following by using the API:

- Create an item.
- Replace one item with another.
- Update an item.
- Delete an item.

<a id="lists--description-lists"></a>

##### Description lists

Sometimes it's useful to add an explanatory phrase to a list item, which can
affect the punctuation. In general, don't add an explanatory phrase to only a
single list item; instead, use a description list, and provide explanatory
phrases for all items.

In most contexts, start each term (`dt` element) with a capital letter.

Don't end the term with a period. Do generally put a period at the end of
each `dd` ("description") element.

| Recommended | Not recommended |
| --- | --- |
| The following words are adjectives:  Big  A short word.  Relevant  A fancy word.  Gratuitous  A long word.  Purple  A vibrant color. | The following words are adjectives:   - Big - Relevant - Gratuitous - Purple—this is a color. |

<a id="lists--description-lists-that-use-run-in-headings"></a>

##### Description lists that use run-in headings

In most contexts, format run-in headings as follows:

- Start the run-in heading with a capital letter.
- End the run-in heading with a period or a colon, but be consistent within the list.
- You can decide whether to bold the punctuation that ends the heading based on factors
  such as on-page consistency.

For the descriptions that follow the punctuation, capitalize the first letter as follows:

- If the text follows a period, start the text with a capital letter.
- If the text follows a colon, start the text with a lowercase letter.

To end the descriptive text, punctuate as follows:

- If the description follows a period, end the description with a period.
- If the description follows a colon, do one of the following:

- If the description is a list of items or short phrases without verbs, don't include a
  period.
- If the description includes a verb or expresses a standalone thought, end the
  description with a period.

Don't use a dash to set off a description from an item in a description list. For more
information, see
[Colons instead of dashes in
lists](#dashes--colons-instead-of-dashes-in-description-lists).

Recommended:

The following words are adjectives:

- **Big**: a short word
- **Relevant**: a fancy word
- **Gratuitous**: a long word
- **Purple**: a vibrant color

Recommended:

The coffee shop has several great choices:

- **Coffee**: latte, mocha, cappuccino, espresso, macchiato
- **Tea**: chai tea, chai latte, black tea, green tea, herbal tea

Recommended:

Budget Airlines reduces your ticket cost in several ways:

- **It increases fuel economy by reducing baggage weight**. By charging
  astronomical prices for anything larger than a wallet....
- **It carries more passengers per flight**. By reducing leg room to industry and
  medical minimums, it fits more seats....

> [!NOTE]
> **Note**: The guidelines here about list punctuation
> differ from the [Material
> Design guidelines](https://material.io/guidelines/style/writing.html#writing-capitalization-punctuation). If you're writing UI text rather than prose
> documentation, then follow the Material Design guidelines.

<a id="lists--comma-separated-lists"></a>

#### Comma-separated lists

When you write a list in a paragraph, use
[serial commas](#commas--serial-commas) to separate the items.

Avoid ending a list with *etc.* or phrases like *and so on*.
Instead, introduce the list in a way that makes it clear that the list isn't
all-inclusive.

Recommended: The service processes data
like event logs, clickstream data, social network interactions, and e-commerce
transactions.

Not recommended: The service processes
event logs, clickstream data, social network interactions, e-commerce
transactions, etc.

For more information, see [etc.](#word-list--etc)

---

<a id="mathematical-notation"></a>

### Mathematical notation

*Source: <https://developers.google.com/style/mathematical-notation>*

This page describes how to format common mathematical notation such as
exponents, expressions, equations, operators, and variables in
documentation. Formatting best practices can help ensure that your
documentation is compatible with assistive technologies and
renders accurately.

For general information about using and formatting numbers, see
[Numbers](#numbers).

**Note:** This page includes examples of formatting in HTML
and Markdown in standard text. If you're using a third-party tool to display
complex math, follow that tool's formatting guidance to ensure that your
mathematical markup displays correct.

<a id="mathematical-notation--html-entities"></a>

<a id="mathematical-notation--use-html-entities-for-mathematical-symbols"></a>

#### Use HTML entities for mathematical symbols

In general, use HTML entities for mathematical symbols instead of keyboard
symbols. The following table lists entities for symbols that are common in
arithmetic and algebra. For the plus sign (`+`), equals sign
(`=`), and division sign (`/`), you can use
their keyboard equivalents.

| Symbol | Markup | Description |
| --- | --- | --- |
| + | Use the keyboard symbol. | Plus sign |
| − | `&minus;` | Minus sign |
| × | `&times;` | Multiplication sign  Alternatively, you can use the dot operator `∙` (`&#8729;`) or asterisk operator `*` (`&#42;`) to match the UI. Don't use an asterisk (`*`) to indicate multiplication in text.  You can indicate multiplication by omitting the multiplication symbol if doing so doesn't create ambiguity—for example, instead of *a* × *b*, you can write *ab*. |
| / | Use the keyboard symbol. | Division sign |
| = | Use the keyboard symbol. | Equals sign |
| ≠ | `&ne;` | Not equal to |
| ± | `&plusmn;` | Plus-minus sign |
| ∓ | `&mnplus;` | Minus-plus sign |
| < | `&lt;` | Less than sign |
| > | `&gt;` | Greater than sign |
| ≈ | `&asymp;` | Approximately equal to |
| ≉ | `&nap;` | Not approximately equal to |
| ≅ | `&cong;` | Congruent to |
| ≤ | `&le;` | Less than or equal to |
| ≥ | `&ge;` | Greater than or equal to |
| ≡ | `&equiv;` | Identical to |
| ≢ | `&nequiv;` | Not identical to |
| √ | `&radic;` | Square root |
| ∑ | `&sum;` | N-ary summation |

<a id="mathematical-notation--format-mathematical-notation"></a>

#### Format mathematical notation

The following sections provide formatting for common math-related notation.

<a id="mathematical-notation--operators"></a>

##### Operators

To ensure accessibility and accurate HTML syntax, use
[HTML entities](#mathematical-notation--html-entities)
instead of keyboard symbols for operators. For example, use
`&minus;` instead of a hyphen (`-`).

Include a non-breaking space (`&nbsp;`) on both sides
of operators within a single expression, equation, or
statement.

Don't italicize operators.

Recommended: *a* − *b*

To render *a* − *b*, use the following markup:

- **HTML:** `<i>a</i>&nbsp;&minus;&nbsp;<i>b</i>`
- **Markdown:** `_a_&nbsp;&minus;&nbsp;_b_`

<a id="mathematical-notation--variables"></a>

##### Variables

Italicize variables.

Recommended: *x* ≠ *y*

Recommended: *x**y*

Recommended: *y**i*

To render *x* ≠ *y*, use the following markup:

- **HTML:** `<i>x</i>&nbsp;&ne;&nbsp;<i>y</i>`
- **Markdown:** `_x_&nbsp;&ne;&nbsp;_y_`

<a id="mathematical-notation--expressions-equations"></a>

##### Expressions and equations

Include short expressions and equations inline with your text.

Include a non-breaking space (`&nbsp;`) between components
such as operators and variables so that the expression or equation renders on
the same line.

When an expression or equation creates an awkward line break, consider
placing it on its own line.

Recommended: The equation
that describes a linear trend line is
*y* = *a* + *bx*.

Recommended: The equation
that describes a polynomial trend line, where the order is *o*, is the
following:
*y* = *a* + *b* × *x* + ... + *k* × *x**o*

To render *y* = *a* + *bx*, use the
following markup:

- **HTML:** `<i>y</i>&nbsp;&=&nbsp;<i>a</i>&nbsp;+&nbsp;<i>bx</i>`
- **Markdown:** `_y_&nbsp;&=&nbsp;_a_&nbsp;+&nbsp;_bx_`

<a id="mathematical-notation--fractions"></a>

##### Fractions

Express fractions as decimal numbers, when possible.

If you must express fractions as words, connect the numerator and
denominator with a hyphen unless one of them is already hyphenated.

Recommended: 0.02

Recommended: one and one-half

Recommended: three-sevenths

Recommended: three seventy-fourths

<a id="mathematical-notation--exponents-subscripts"></a>

##### Exponents and subscripts

Use
[standard mathematical notation](https://wikipedia.org/wiki/Exponentiation).
Don't put a space between the base and the exponent.

To render exponents, use the HTML `<sup>` tag. Don't use the
keyboard caret symbol (`^`) to indicate an exponent.

To render subscripts, use the HTML `<sub>` tag.

Recommended: 23

Recommended: *x**y*

Recommended: *y**i*

Not recommended: 2^3

To render 23, use the following markup in HTML and Markdown:
`2<sup>3</sup>`

<a id="mathematical-notation--expressions-as-words"></a>

<a id="mathematical-notation--notation-as-words"></a>

#### Notation as words

In general, you can use mathematical notation in place of words in running
text. For example, in a sentence, you might use the statement
*x* ≠ *y* instead of writing "*x* is not equal to
*y*." If the use of notation instead of words creates ambiguous, grammatically
incorrect, or difficult-to-read text, then use words to convey the
mathematical concept.

Recommended: Check
whether *a* > *b*.

Recommended: The area
is calculated by multiplying the length by the width.

Not recommended: Check
whether *a* is greater than *b*.

Not recommended: The
area is calculated by multiplying *l* × *w*.

<a id="mathematical-notation--math-concepts"></a>

<a id="mathematical-notation--tools-for-complex-or-multiline-equations"></a>

#### Tools for complex or multiline equations

The methods described on this page that use HTML entities and tags are suitable for most common
mathematical notation. However, for more complex, multiline equations, or formulas that are
difficult to represent clearly with standard HTML, consider using [diagrams,
other images](#images), or a dedicated math rendering tool to support comprehension. Images and diagrams
like pie charts or bar graphs, in particular, are especially helpful for comparing statistics and
illustrating percentages.

<a id="mathematical-notation--more-resources"></a>

#### More resources

- [Numbers](#numbers)
- [Units of measure](#units-of-measure)
- [Text-formatting summary](#text-formatting)

---

<a id="notices"></a>

### Notes and other notices

*Source: <https://developers.google.com/style/notices>*

To give the reader important or useful information that isn't part of the flow of the text, you
can offset the information with a notice. However, there's
[evidence](https://www.nngroup.com/articles/tunnel-vision-and-selective-attention/)
that readers skip elements on the page, including notices, that are outside their focus of
interest. If you're not sure whether something should be a notice, write it first in regular text
and then decide if a notice is needed.

Don't use too many notices. When you use multiple notices on a page, they begin to lose their
visual distinctiveness. See if you can convey the information in a different way. This is
especially true if you have two (or more) notices in a row.

Where possible, avoid grouping two or more notices together. If you find it
necessary to do so (for example, a *note* with a *caution* inside it, or several
*warnings* one after another), consider reorganizing the content.

<a id="notices--pick-a-notice-type"></a>

#### Pick a notice type

The following is a list of commonly used notices.

<a id="notices--note"></a>

**Note**
    An ordinary aside or tip. Provides information that is useful but not critical to the reader.
    For example, "Generating excessive amounts of traffic to external systems can resemble a
    denial-of-service attack." For more information, see
    [when to use](#notices--when-to-use-a-note-notice-type)
    and [when not to use](#notices--when-not-to-use-a-note-notice-type) a note notice type.
<a id="notices--caution"></a>

**Caution**
    Tells the reader to proceed carefully. For example, "We don't recommend using a
    broad `0.0.0.0/0` range that would allow all traffic."
<a id="notices--warning"></a>

**Warning**
    Stronger than a *caution* notice; it means "Don't do this" or that this step might be
    irreversible, such as leading to permanent data loss. If a reader doesn't heed the warning, they
    can lose money, lose work, or open themselves to a security breach. For example, "Don't put a
    password on the command line; doing so is a security risk."
<a id="notices--success"></a>

**Success**
    Describes a successful action or an error-free status. Used only in interactive or dynamic
    content; don't use this notice type in ordinary static pages. For example, "You've successfully
    deployed an application to GKE."

<a id="notices--when-to-use-a-note-notice-type"></a>

#### When to use a *note* notice type

Create a *note* when all of the following are true:

- The information you're sharing is *relevant* but not
  *necessary* to what the reader is doing right now. If the reader skips
  the information, they'll still succeed.
- Interrupting the reader at this point is not an obstacle to the reader. For example, your
  *note* isn't suggesting an alternative that leads the reader down a
  different path.
- The information is not part of the flow of what you're writing—it's not just
  a continuation, a result, or a pointer to additional information.

<a id="notices--when-not-to-use-a-note-notice-type"></a>

#### When not to use a *note* notice type

- Don't use *notes* for [cross-references](#cross-references).
- Don't use *notes* to tell the reader about prerequisites or about
  steps they should have taken earlier. Information like this should precede the
  step.
- Don't make a full procedural step into a *note*.
- Don't use *notes* to provide information that's necessary for the
  reader to succeed.
- Don't use *notes* for information that's in flow with the preceding
  text. For example, don't use a *note* to state expected results or to
  include information that simply describes what precedes.

<a id="notices--examples"></a>

#### Examples

Use whatever visual presentation for notices is standard for your site.

If you're writing in HTML and your site doesn't specify what HTML to use for
notices, we recommend using HTML code similar to the following example:

```
<aside class="note"><b>Note:</b> All VPC networks include firewall
rules.</aside>
```

> [!NOTE]
> **Note**: All VPC networks include firewall
> rules.



> [!CAUTION]
> **Caution**: We don't recommend using a subnet that's part of a dynamic
> route.



> [!WARNING]
> **Warning**: Do not manually edit or delete generated
> table entries.



> [!TIP]
> **Success**: You've successfully created a Compute Engine instance.

---

<a id="numbers"></a>

### Numbers

*Source: <https://developers.google.com/style/numbers>*

> [!NOTE]
> For information about formatting quantities like 10 MB, see
> [Units of measurement](#units-of-measure).

<a id="numbers--ordinal-numbers"></a>

#### Ordinal numbers

Spell out all ordinal numbers in text.

Recommended: first, fifth, twelfth,
forty-third

Not recommended: 1st, 5th, 12th, 43rd

<a id="numbers--numbers-as-words"></a>

#### Numbers as words

This section covers when to spell out numbers as words.

If it's important to have the number and associated noun together on the same line, use
a nonbreaking space between the number and the noun.

In general, spell out the following:

- Numbers from zero through nine, except as noted in
  [Numbers as numerals](#numbers--numbers-as-numerals).

  Recommended:
  two-day total

  Recommended: four options

  Recommended: five minutes

  Recommended: nine developers
- A number that starts a sentence.

  Recommended: Fifteen
  directories are created.

  In some cases it's better to rearrange the sentence so that the number
  appears later.

  Recommended: In
  general, avoid sending files larger than 164 MB as attachments.

  Not recommended: 164 MB
  is generally considered too large a file to send as an attachment.

  **Exception**: It's okay, but non-optimal, to begin a
  sentence with a four-digit year.
- A number that is followed by a numeral.

  Recommended: This
  procedure creates fifteen 100,000-byte files.

  *But*

  Recommended: This
  procedure creates 15 of the 100,000-byte files.
- Indefinite and casual numbers.

  Using words like *millions* or *billions* is fine for approximate numbers. For
  precise numbers, use numerals.

  Recommended: You
  can specify thousands of combinations.

  Recommended: The
  API might return a list of a million songs.

<a id="numbers--numbers-as-numerals"></a>

#### Numbers as numerals

This section covers when to use numerals to write numbers.

If it's important to have the number and associated noun together on the same line, use
a nonbreaking space between the number and the noun.

In general, use numerals for the following:

- Numbers 10 and greater.

  Recommended: The link expires in 24
  hours.

  Recommended: 18 years old

  Recommended: 27 minutes

  Recommended: 728 shipments

  Recommended: 18,000,000 users

  Recommended: 10 chapters

  Recommended: 102 degrees

  **Exceptions**: Always use numerals for the following items, even if
  they're less than 10:

  - Version numbers.

    Recommended:
    version 3
  - Technical quantities, such as amounts of memory, amounts of disk
    space, numbers of queries, or usage limits.

    Recommended: 6 queries per second

    Recommended: 50 Mbps

    Recommended: 128 bits
  - Page numbers.
  - Chapter numbers, sections, pages, and so on.
  - Step numbers. Avoid referring to step numbers whenever possible,
    but in edge cases where you have no choice or it makes the most sense,
    use the numeral.
  - Prices.
  - Numbers without units, such as numbers used in mathematical
    expressions.
  - Numbers less than 10 when they appear in the same sentence with
    numbers greater than 9.

    Recommended: The
    menu contains 15 options but 6 of them are deselected.
- Negative numbers.
- Most [fractions](#numbers--fractions).
- [Percentages](#numbers--percentages).
- [Dimensions](#numbers--dimensions).
- Numbers containing decimal points.
  - Treat decimal numbers as plural even when less than or equal to 1.0.

    Recommended: 1.0 inches
  - For decimal numbers less than one, place a zero in front of the decimal point.

    Recommended: 0.3 inches
- Measurements.

  Recommended: 8 pixels
- [Numbers in a range](#numbers--ranges-of-numbers).

<a id="numbers--numbers-as-roman-numerals"></a>

#### Numbers as Roman numerals

In general, avoid using Roman numerals when possible. Instead, use Arabic numerals because they
are easier to scan.

You can use Roman numerals for
[sub-steps in numbered procedures](#procedures--sub-steps-in-numbered-procedures).

<a id="numbers--fractions"></a>

#### Fractions

Express fractions as decimal numbers, when possible.

If you must express fractions as words, connect the numerator and
denominator with a hyphen unless one of them is already hyphenated.

Recommended: 0.75

Recommended: one and one-half

Recommended: two-fifths

Recommended: five sixty-fourths

<a id="numbers--percentages"></a>

#### Percentages

In general, use numerals and the percent sign (%), without a space between them.

Recommended: 40%

**Exception**: If the percentage starts the sentence, then spell out both
the number and the word *percent*.

Recommended: Forty
percent of the files

<a id="numbers--ranges-of-numbers"></a>

#### Ranges of numbers

Use a hyphen with no space on either side of it. Do not use an
en dash (`&ndash;`).

Recommended:
2012-2016

For more information, see the following:

- [Ranges of numbers with units](#units-of-measure--ranges)
- [Range of numbers](#hyphens--number-range)

<a id="numbers--suspended-hyphens"></a>

#### Suspended hyphens

When two or more hyphenated compounds that start with numbers modify the same
word, use [suspended hyphens](#hyphens--suspended-hyphens).

Recommended: You can set up the system to
scan for new files at one-, two-, or three-hour intervals.

<a id="numbers--currency"></a>

#### Currency

Make sure that it's clear what country's currency you are describing. For more information, see
the [currency](#units-of-measure--currency) section in Units of measurement.

For US dollars, use a comma to delineate the thousands place of whole
currency. Use a period to delineate whole currency and fractions of currency.
Always include the dollar sign ($) at the beginning of the currency. Do
not use any punctuation or spaces to the right of the decimal.

Recommended: The price is $0.006653 per
vCPU hour.

Not recommended: The price is $0.006,653
per vCPU hour.

Recommended: $10,000 in fees is out of
reach for many developers.

Not recommended: $10 000 in fees is out
of reach for many developers.

<a id="numbers--punctuating-numbers"></a>

<a id="numbers--commas-and-decimal-points-in-numbers"></a>

#### Commas and decimal points in numbers

Use commas and decimal points in accordance with standard American number-formatting.

Specifically: in numbers four or more digits long, use commas to set off
groups of three digits, counting leftward from the decimal point, in the
standard American style. For long decimal numbers, do not use any digit-group separators to the
right of the decimal point.

> [!NOTE]
> **Note**: Even though the
> [International
> System of Units](https://www.nist.gov/pml/weights-and-measures/metric-si/si-units) (SI) uses a thin space as a digit group separator, we use a comma, which is
> the most common digit group separator used in the US.

Use a period for a decimal point, also in the standard American style.

| Recommended | Not recommended |
| --- | --- |
| The limit is 1,532,784 bytes per day. | The limit is 1532784 bytes per day. |
| The API supports up to 2,000 vertices. | The API supports up to 2000 vertices. |
| $0.031611/vCPU hour | $0.031 611/vCPU hour |

> [!NOTE]
> **Note**: Even though in some scientific writing,
> four-digit numbers don't use commas, our style is to use a comma for a
> four-digit number.

For more information about decimal points and digit group separators, see Wikipedia's [decimal mark](http://wikipedia.org/wiki/Decimal_mark) entry.

<a id="numbers--dimensions"></a>

#### Dimensions

Use numerals for dimensions.

Use a lowercase *x* between the numerals in the dimensions, with no space between
the numerals and the *x*.

Recommended: 192x192

Not recommended: 192 x 192

<a id="numbers--exponents"></a>

#### Exponents

Use
[standard mathematical notation](https://wikipedia.org/wiki/Exponentiation).
Don't put a space between the base and the exponent.

Recommended: 23

<a id="numbers--real-world-implication"></a>

<a id="numbers--accompany-numerical-concepts-with-real-world-practical-implications"></a>

#### Accompany numerical concepts with real-world practical implications

Accompany numerical concepts with real-world practical implications to provide tangible meaning.
For example, if using a feature incurs additional fees, add a link to pricing calculator.

<a id="numbers--math-concepts"></a>

<a id="numbers--mathematical-notation-and-visuals"></a>

#### Mathematical notation and visuals

For general guidance on formatting mathematical notation, such as equations and variables, see
[Mathematical notation](#mathematical-notation).

---

<a id="paragraph-structure"></a>

### Paragraphs

*Source: <https://developers.google.com/style/paragraph-structure>*

Break up your paragraphs to aid in the scannability of the page and to avoid
walls of text. Readers scan for information and read on different devices with
different screen sizes. Each paragraph should address a single idea in the
fewest words and in the fewest sentences possible.

Don't make sentences longer in order to limit the number of sentences in a
paragraph. Use shorter sentences and paragraphs.

A paragraph longer than 5 or 6 sentences is often an indication that the
paragraph is trying to convey too much information. If so, break the paragraph
into smaller paragraphs or remove some content. However, don't break paragraphs
up if they contain a single idea. It's OK to have a paragraph with one sentence,
and it can be OK if it's longer than 6 sentences as long as it's still about one
idea.

<a id="paragraph-structure--put-critical-information-first"></a>

#### Put critical information first

Similarly to putting the most important information first in a sentence, put
the most important information first in a paragraph. Don't hide the key point of
a paragraph at the end of the paragraph. Readers don't read every word.

<a id="paragraph-structure--format-paragraphs"></a>

#### Format paragraphs

Left-align text for readability. Don't center, full-justify, or right-align
text.

Don't force line breaks (hard returns) within sentences and paragraphs. Line
breaks might not work well in resized windows, across different devices, or with
enlarged text.

---

<a id="phone-numbers"></a>

### Phone numbers

*Source: <https://developers.google.com/style/phone-numbers>*

This page describes how to use and format phone numbers in technical documentation. This page
doesn't provide guidance on how to enter or use phone numbers in Google or third-party products.
If you need information about entering phone numbers in a specific product, consult the
product documentation or contact product support.

<a id="phone-numbers--phone-numbers-in-examples"></a>

#### Use example phone numbers

Most phone numbers in our documentation are examples. To show an example phone number, use a US
number in the range 800‑555‑0100 through 800‑555‑0199. That range is
reserved for use in examples and in fiction.

Never use a real phone number in examples.

<a id="phone-numbers--format-phone-numbers"></a>

#### Format phone numbers in HTML or Markdown

To ensure that a phone number is displayed on the same line, use a nonbreaking hyphen
(`&#8209;`) where appropriate in HTML or Markdown.

<a id="phone-numbers--example"></a>

##### Example

415‑555‑0132

<a id="phone-numbers--html"></a>

##### HTML

`415&#8209;555&#8209;0132`

<a id="phone-numbers--markdown"></a>

##### Markdown

`415&#8209;555&#8209;0132`

<a id="phone-numbers--phone-numbers-america"></a>

#### Format North American phone numbers

To format a real phone number in the US, Canada, and other [NANP](https://wikipedia.org/wiki/North_American_Numbering_Plan)
(North American Numbering Plan) countries, use a nonbreaking hyphen to separate the area code,
three-digit exchange code, and four-digit number.

Recommended: 415‑555‑0132

<a id="phone-numbers--international-phone-numbers"></a>

#### Format international phone numbers

To format a real phone number in non-NANP countries, include the country and area
codes. Insert a plus sign
immediately before the country code (no space); the plus sign stands in for a
prefix known as an *exit code*, which lets you dial out of a country. Each
country has a different exit code.

For more information, see the [ITU document about
standardized formatting for phone numbers](https://www.itu.int/rec/T-REC-E.123-200102-I/en).

Recommended: +1‑415‑555‑0132

<a id="phone-numbers--extensions"></a>

#### Format phone numbers that include an extension

To specify a phone extension, follow the phone number with the word *extension*, and then
specify the extension number.

Recommended: 415‑555‑0132, extension 987

---

<a id="procedures"></a>

### Procedures

*Source: <https://developers.google.com/style/procedures>*

A procedure is a sequence of numbered steps for accomplishing a task. For information about
lists of items that aren't part of a procedure, see the
[Lists](#lists) page.

<a id="procedures--introductory-sentences"></a>

#### Introductory sentences

In most cases, introduce a procedure with an introductory sentence. This
introductory sentence should provide context to the reader that isn't part of
the section heading. Don't simply repeat the heading: if the heading explains
what the procedure is, and no additional context is needed, then don't
include an introductory statement.

The sentence can end with a colon or a period. Use a colon if it immediately
precedes the procedure. Use a period if there's more material (such as a
note paragraph) between the introduction and the procedure.

You can introduce a procedure with an imperative statement. Don't introduce a procedure with
a partial sentence that's completed by the numbered steps.

Recommended: To customize the buttons,
follow these steps:

Also recommended: Customize the buttons:

Also recommended: To customize the buttons, do the following:

Not recommended: To customize the
buttons:

For more information about introducing lists, see [Lists](#lists--introductory-sentences-for-lists).

<a id="procedures--single-step-procedures"></a>

#### Single-step procedures

When a procedure consists of only one step, write the step in one sentence and format it as a
[bulleted list](#lists--numbered-lettered-bulleted-lists).

Recommended:

- To clear (flush) the entire log, click **Clear logcat**.

Not recommended:

To clear (flush) the entire log, follow this step:

1. Click **Clear logcat**.

Also not recommended:

To clear (flush) the entire log, follow this step:

- Click **Clear logcat**.

<a id="procedures--sublists"></a>

<a id="procedures--sub-steps-in-numbered-procedures"></a>

#### Sub-steps in numbered procedures

In a numbered procedure, sub-steps are labeled with lowercase letters, and
sub-sub-steps get lowercase Roman numerals.

When a step has sub-steps, treat the step like an [introductory sentence](#procedures--introductory-sentences): put a colon or a
period at the end of the step, as appropriate.

For more information about lists, see [Lists](#lists--introductory-sentences-for-lists).

Recommended:

1. To add a VM instance, do the following:
   1. Click **Create instance**.
   2. For **Name**, enter a name for the VM instance, and then do the following:
      1. For **Region**, specify where you want to deploy the VM instance.
      2. For **Machine type**, select an option.
   3. Click **Create**.
2. To connect to the VM instance by using SSH, click **SSH**.

<a id="procedures--multiple-components"></a>

<a id="procedures--order-of-multiple-components-in-a-step"></a>

#### Order of multiple components in a step

To document a complex procedural step, use the following order:

1. Describe the action to take.
2. List a command, if necessary.
3. Explain any placeholders that are used in the command.

   For more information, see
   [Formatting placeholders](#placeholders).
4. Explain the command in more detail, if necessary.
5. List the output of the command, if necessary.

   For more information, see
   [Output from commands](#code-syntax--output).
6. In a separate paragraph, explain
   [the result of an
   action](#procedures--steps-with-results-or-justifications), or any output, if necessary.

The following example demonstrates the preceding order:

1. Plan the Terraform deployment:

   ```
   terraform plan -out=NAME
   ```

   Replace `NAME` with the name of your Terraform plan.

   The `terraform plan` command does the following:

   1. Parses the Terraform configuration, building a list of resources to provision.
   2. Refreshes the current state of resources already provisioned in Google Cloud.
   3. Creates a plan to make the currently provisioned resources match the parsed
      configuration.

   The output is similar to the following:

   ```
     Plan: 26 to add, 0 to change, 0 to destroy.
     ------------------------------------------------------------
     This plan was saved to: NAME
   ```

   The output shows what resources to add, change, or destroy.

<a id="procedures--multi"></a>

<a id="procedures--multi-action-procedures"></a>

#### Multi-action procedures

In general, use one step for each action. However, you can combine small actions
into one step [by using
angle brackets](#ui-elements--term-menus) (`>`) for sequential menu selections.

Recommended:

1. Click **Next > Finish**.

Also recommended:

1. Click
   **File > New > Document**.

Don't make the steps too long. If they feel too long, consider splitting them
into multiple steps.

<a id="procedures--same-task"></a>

<a id="procedures--multiple-procedures-for-the-same-task"></a>

#### Multiple procedures for the same task

In general, if there's more than one way to complete a task, then document
one procedure that's accessible for all readers. If all methods are accessible, pick the shortest
and simplest approach if possible. If you need to document multiple ways to complete a
task, then separate them in different pages, headings, or tabs.

The following guidelines can help you choose which procedure to document:

- Choose a procedure that lets readers do all the steps by using only a keyboard.
- Choose the shortest procedure.
- Choose a procedure that uses a programming language that most of your
  audience is familiar with.

<a id="procedures--repetitive"></a>

<a id="procedures--repetitive-procedures"></a>

#### Repetitive procedures

Avoid repeating procedures. Instead, reference those procedures and link to
them.

Recommended:

1. Create a user as you did in the previous step.

Also recommended:

1. [Create a user as you did in the previous step.](#)

<a id="procedures--optional-steps"></a>

#### Optional steps

For an optional step, at the beginning of the step, type *Optional*
followed by a colon.

Recommended:

1. Optional: Type an arbitrary string ...

Not recommended:

1. (Optional) Type an arbitrary string ...

For information about optional sections, see [Heading and title text](#headings--heading-and-title-text).

<a id="procedures--specify-context"></a>

<a id="procedures--steps-that-say-where-to-complete-a-task"></a>

#### Steps that say where to complete a task

Tell the reader where to complete an action—for example, in a
particular tool or UI field—before you state the action.

Recommended:

1. In Google Docs, click
   **File > New > Document**.
2. In the Google Cloud console, go to the **Monitoring** page.

Not recommended:

1. Click **File >
   New > Document** in Google
   Docs.
2. Go to the **Monitoring** page in the Google Cloud console.

If a set of procedures is split across multiple headings, then in each
procedure, restate where the reader completes the action. For example, if two
procedures in a document take place in the console, then start both
procedures with "In the console ..."

<a id="procedures--steps-with-goals"></a>

#### Steps with goals

For some steps, it's useful to state the goal
that the step accomplishes.

When a step includes a goal, state the goal before the action. This
structure helps readers understand and complete the step more easily.

Recommended:

1. To start a new document, click
   **File >
   New > Document**.

Not recommended:

1. Click **File >
   New > Document** to start a
   new document.

Sometimes, the preceding format can imply that the required step is
optional. In such cases, use the following format:

Recommended:

1. Start a new document: click
   **File >
   New > Document**.

It's usually clear within the context of a procedure whether a step is
required. In such cases, the "To ..." format is more natural than the colon
format.

To determine whether you need to use the colon format, consider how the
goal of the step relates to the goal of the procedure. For example, in a
procedure for creating a bar chart, a step with the goal "To create the
chart" is clearly required. A step with the goal "To enhance the chart" is
also unlikely to create confusion. But a step with the goal "To sort the
data by date" might or might not be necessary. To clarify that the step
isn't optional, use "Sort the data by date:" instead.

<a id="procedures--steps-with-results"></a>

<a id="procedures--steps-with-results-or-justifications"></a>

#### Steps with results or justifications

Some steps consist of an action along with a resulting reaction that helps
the reader navigate to the next step. State the action first and the result
second. Keep the result in the same paragraph as the action. But also consider whether you
can avoid repetitiveness and overwhelming the reader with too much bolding of UI elements.

Recommended:

1. Click **Run**. The query results appear after the query runs.

Recommended:

1. Click **Enter**.
2. In the **New file** dialog that appears, click **Next**.

Not recommended:

1. Click **Enter**. The **New file** dialog appears.
2. In the **New file** dialog, click **Next**.

For information about describing output, see
[Output from commands](#code-syntax--output).

Other steps benefit from including a justification for why the step is
important. State the action first and the justification second.

Recommended:

1. Store the private key in a secure location. You need it later.

<a id="procedures--more-guidelines-for-writing-procedures"></a>

<a id="procedures--summary-of-guidelines-for-writing-procedures"></a>

#### Summary of guidelines for writing procedures

| Guidance | Recommended | Not recommended |
| --- | --- | --- |
| Make sure that the first sentence in a procedural step includes an imperative verb. | Clone the repository that contains the sample data. | You need the project ID later in this document. Retrieve the project ID. |
| Use complete sentences. |  |  |
| Use parallel structure and consistent verb form. | Download the service account key to your local machine. Click **More**, and then click **Download**. | Download the service account key to your local machine by clicking **More** and then clicking **Download** file. |
| For an optional step, type *Optional:* as the first word of the step. | Optional: Type an arbitrary string... | (Optional) Type an arbitrary string... |
| Set the context (such as a tool or an environment) in which the reader performs a procedure.  If there are multiple headings associated with a set of procedures, restate the context of the procedure in the first step, even if the context is the same as in the previous procedure. | In Cloud Shell, connect to the development cluster.  In the Google Cloud console, go to the **BigQuery** page. |  |
| Write in the order that the reader needs to follow. State the location of the action before stating the action. | In Google Docs, click **File > New > Document**.  In the Google Cloud console, go to the **Monitoring** page. | Click **File > New > Document** in Google Docs.  Go to the **Monitoring** page in the Google Cloud console. |
| State the purpose or goal of the action before stating the action. | To start a new document, click **File > New > Document**. | Click **File > New > Document** to start a new document. |
| Don't use directional language to orient the reader, such as *above*, *below*, or *right-hand side*. This type of language doesn't work well for accessibility or for localization. If a UI element is hard to find, provide a screenshot.  For information about documenting icons, see [Buttons and icons](#ui-elements--buttons). | Click **Menu**.  In the preceding diagram,...  In the following diagram,... | Click the button with three lines.  In the above diagram, ...  In the diagram below, ... |
| Don't use *please*. | To open a document, click **File > Open**. | To open a document, please click **File > Open**. |
| Avoid using *run the following command* to introduce code. Instead, focus on what the command does. | In Cloud Shell, deploy the load generator:...  Define a firewall rule to allow internal traffic:... | In Cloud Shell, deploy the load generator by running the following command:...  Run the following command:... |
| If the reader must press **Enter** after a step, then include that instruction as part of the step. | Click the search box, type `custom function`, and then press **Enter**. | 1. Click the search box and type `custom function`. 2. Press **Enter**. |
| Don't include keyboard shortcuts. | Copy the command, and then paste it... | Press Ctrl+C, and then press Ctrl+V... |
| When there's more than one way to do something, give only the best way. Giving alternate ways can confuse readers. |  |  |
| If your procedure includes code samples, see how to format  [code samples](#code-samples). |  |  |
| If your procedure includes commands, see how to format  [commands](#code-syntax--formatting-a-command). |  |  |
| Ensure that the reader has the information that they need in order to prepare for the task ahead of time. Having information in advance supports task management, executive functioning, memory, and emotional regulation. | The following hardware and software are required:... |  |
| Include as few steps as possible to complete the task. Limit interruptions in the path. |  |  |
| Focus on one reader decision at a time. Separate each instruction by making each instruction a separate list item. |  |  |

---

<a id="tables"></a>

### Tables

*Source: <https://developers.google.com/style/tables>*

In many contexts, tables are the best way to represent sets of related pieces of data. However,
in some contexts, other approaches are better choices.

<a id="tables--list-or-table"></a>

#### List or table?

Tables and lists are both ways to present a set of similarly structured
items; sometimes it's not obvious when to choose one presentation over the
other. To decide which presentation to use, consult the following table:

| Item type | Example | How to present |
| --- | --- | --- |
| Each item is a single unit. | A list of programming language names, or a list of steps to follow. | Use a [numbered list, lettered list, or bulleted list](#lists--numbered-lettered-bulleted-lists). |
| Each item is a pair of pieces of related data. | A list of term/definition pairs. | Use a [description list](#lists--description-lists) (or, in some contexts, a table). |
| Each item is three or more pieces of related data. | A set of parameters, where each parameter has a name, a data type, and a description. | Use a table. |

<a id="tables--places-not-to-use-tables"></a>

##### Places not to use tables

- Don't use tables to lay out a page; use your site's standard CSS instead.
- Usually if you have only one row of material, a table isn't the best
  choice for how to present it. But in some contexts (especially for consistency
  of layout in reference documentation), it might be.
- If you have only one column in your table, turn the table into a list.
- Don't use tables to lay out code snippets.
- Don't use tables to lay out long one-dimensional lists in multiple
  columns. For example, if you have a long list of function names, don't try to
  save space by splitting the list in half and presenting the two halves as a
  two-column table. Use tables only to present two-dimensional data—that is,
  material that semantically makes sense to display in rows and columns.
- Avoid tables in the middle of a numbered procedure.

<a id="tables--multiple-paragraphs"></a>

<a id="tables--multi-paragraph-table-cells"></a>

#### Multi-paragraph table cells

Any table cell can contain more than one paragraph.

To create multiple paragraphs, use the `p` element rather
than using the `br` element. (The HTML specification
describes which uses of the [`br`
element](https://html.spec.whatwg.org/multipage/semantics.html#the-br-element) are legitimate and which aren't.)

Example of a table with some cells that contain more than one paragraph:

| Attribute name | Type | Description |
| --- | --- | --- |
| `href` | HTML | Defines the URL for a link.  For example, go to the `<a href="https://www.google.com">Google Search</a>` page. |
| `src` | HTML | Defines the path of the image to be displayed.  For example, `<img src="kitten.jpg">`. |

<a id="tables--table-introductions"></a>

<a id="tables--introductory-sentences-for-tables"></a>

#### Introductory sentences for tables

Introduce tables with a complete sentence that describes the purpose of the table because not all
screen readers preannounce tables. The introductory sentence can end with a colon or a period;
usually a colon if it immediately precedes the table, and usually a period if there's more material
(such as a note paragraph) between the introduction and the table.

Recommended: Change the environment variables
to values for your deployment, as listed in the following table:

For more information, see the
[Tables](#accessibility--tables) section of the "Accessibility" page.

<a id="tables--table-placement"></a>

#### Table placement

- When introducing a table, use a complete sentence and try to refer to the
  table's position, using a phrase like *the following table* or *the preceding table*.
- Don't put a table in the middle of a sentence.
- Avoid using footnotes when possible. If your table does refer to footnotes, place them
  immediately following the table. For more information, see
  [Footnotes](#footnotes).

<a id="tables--table-captions"></a>

#### Table captions

If your document contains only one table, the table doesn't need a caption.
However, be sure to place the table adjacent to the text that refers to it.

If your document contains more than one table in fairly close proximity to
each other, include a caption for each one, using a [`caption`
element](https://html.spec.whatwg.org/multipage/tables.html#the-caption-element) as the first child of the `table` element. Start the
caption with a number, in the form "<b>Table NUMBER.</b>
DESCRIPTION". Use sentence case for the caption, but don't place a
period at the end.

When referring to the table from text, refer to it by its number—for example,
*... as shown in table 2*. Do not capitalize *table* unless it starts a sentence.

Your site's CSS determines the styling and placement of the caption.

Recommended:

```
<table>
  <caption><b>Table 1.</b> Prehistoric birds</caption>
  ...
</table>
```

<a id="tables--table-formatting"></a>

#### Table formatting

- Don't add styling to the table element.
- Don't apply a visual style such as a different font, font color, or background color to convey a
  header row or column by itself. Use the `th` element to semantically mark up headers in
  tables.
- Don't merge cells. Don't use `colspan` or `rowspan` attributes.
- Sort rows in a logical order, or alphabetically if there is no logical order.
- If the table is long or complicated—for example, with multiple header rows or columns—consider
  splitting it into multiple tables.
- Don't present new information in tables through images or symbols alone; always provide a
  descriptive `alt` attribute for the image or symbol. For more information, see
  [Alt text](#images--alt-text).

<a id="tables--table-column-heads"></a>

#### Table column heads

- Use sentence case.
- Write concise headings.
- Don't end with punctuation, including a period, an ellipsis, or a colon.
- Use table headings for the first column and the first row only. Use the
  [`th` element](https://www.w3.org/TR/2014/REC-html5-20141028/tabular-data.html#the-th-element).
- Include the [`scope` attribute](https://www.w3.org/TR/WCAG20-TECHS/H63.html) as appropriate for accessibility.

<a id="tables--responsive-tables"></a>

#### Responsive tables

Where possible, use table CSS that adapts to different viewport sizes.

<a id="tables--table-linking"></a>

<a id="tables--link-to-tables"></a>

#### Link to tables

Where possible, avoid linking to tables; instead, refer to them by table number.

---

<a id="units-of-measure"></a>

### Units of measurement

*Source: <https://developers.google.com/style/units-of-measure>*

Put a nonbreaking space (`&nbsp;`) between the number and the unit.

<a id="units-of-measure--spaces"></a>

<a id="units-of-measure--spaces-in-units-of-measurement"></a>

#### Spaces in units of measurement

For most units of measurement, when you specify a number with the unit, use a
nonbreaking space between the number and the unit. This guidance applies in both
HTML and Markdown.

For guidance about when to spell out units, see the
[Abbreviations](#abbreviations--spelling-out) page.

For guidance about whether to hyphenate, see the [Hyphens](#hyphens--compounds)
page.

Recommended: `64&nbsp;GB` (64 GB)

Recommended: `25&nbsp;mm` (25 mm)

Recommended: a 128-bit system

Not recommended: `64 GB`

Not recommended: 64GB

For more information about making abbreviations plural, see [Plural abbreviations](#pluralization--making-abbreviations-plural).

However, when the unit of measure is money or percent or degrees of an angle,
don't use a space. For more information, see [Currency](#units-of-measure--currency).

Recommended: $10

Recommended: £25

Recommended: 65%

Recommended: 180°

For degrees of temperature, include a nonbreaking space between the number and the degree symbol.
Don't use a space between the degree symbol (`&deg;`) and the temperature scale
(*F* or *C*).

<a id="units-of-measure--example"></a>

##### Example

50 °C

<a id="units-of-measure--html"></a>

##### HTML

`50&nbsp;&deg;C`

<a id="units-of-measure--markdown"></a>

##### Markdown

`50&nbsp;&deg;C`

For Kelvin temperatures, leave out the degree symbol but use a nonbreaking space before the
*K*.

<a id="units-of-measure--example_1"></a>

##### Example

300 K

<a id="units-of-measure--html_1"></a>

##### HTML

`300&nbsp;K`

<a id="units-of-measure--markdown_1"></a>

##### Markdown

`300&nbsp;K`

When a number and unit of measurement combine to modify a noun, don't hyphenate unless
the hyphen is needed for clarity.

Recommended:
`200&nbsp;GB disk` (200 GB disk)

<a id="units-of-measure--ranges"></a>

<a id="units-of-measure--ranges-of-numbers-with-units"></a>

#### Ranges of numbers with units

In a range of numbers, repeat the unit for each number. *Unit* includes both symbols (like
the degree symbol (º)) and abbreviations (like *MB* for megabytes) but not nouns
(like *file*). For more information, see
[Range of numbers](#hyphens--number-range).

Use the word *to* between the numbers, rather than a hyphen. A hyphen
can be misinterpreted as a subtraction sign.

Recommended: -40 °C to 85 °C

Not recommended: -40-85 °C

<a id="units-of-measure--multiplied-units"></a>

<a id="units-of-measure--hyphens-with-multiplied-units"></a>

#### Hyphens with multiplied units

When the components of a unit of measurement are multiplied by each other,
hyphenate them.

Recommended: 5 vCPU-hours

Recommended: 40 person-hours

<a id="units-of-measure--using-k"></a>

<a id="units-of-measure--use-k-to-indicate-thousands"></a>

#### Use *k* to indicate thousands

In some contexts, it might be appropriate to indicate thousands of something by
following a number with a lowercase *k*. If you do that, then follow these
guidelines:

- Don't put a space between the number and *k*.
- Add a noun to indicate what the number measures, and to make clear that
  you're not using *k* as an abbreviation for *kilobytes*.

Recommended: On this plan, you are
limited to 55k download operations and 20k upload operations per day.

<a id="units-of-measure--currency"></a>

#### Currency

If you're writing about monetary amounts, make sure that the reader knows what
currency you're referring to. For example, the dollar sign—the *$*
symbol—can refer to US dollars, Canadian dollars, Mexican pesos, and several
other currencies.

If there's any possibility of ambiguity, use a currency indicator before
the amount. For details, see section 9.20 and following in the Chicago
Manual of Style, 17th edition.

Recommended: US$10

<a id="units-of-measure--rates"></a>

#### Rates

Use *per* instead of the division slash (/) when space permits.
It's OK to use the division slash when space is limited,
such as in a table with small cells.

Shorten *per* to *p* only for well-established abbreviations for
rate units, such as *Gbps* for *gigabits per second* or
*MBps* for *megabytes per second*.

Recommended: requests per day

Not recommended: requests/day

Recommended: Gbps

Not recommended: Gb/s

<a id="units-of-measure--byte-units"></a>

#### Decimal and binary units

Use the same system to measure bytes as the technology that you're documenting.
Don't use *MB* if you mean *MiB*, or *GB* if you mean *GiB*. The following
table lists common types of
[decimal and binary units](https://en.wikipedia.org/wiki/Byte#Multiple-byte_units):

| Decimal units | Binary units |
| --- | --- |
| kB (kilobyte, or 1000 bytes) | KiB (kibibyte, or 1024 bytes) |
| MB (megabyte, or 10002 bytes) | MiB (mebibyte, or 10242 bytes) |
| GB (gigabyte, or 10003 bytes) | GiB (gibibyte, or 10243 bytes) |

For more information about abbreviating measurement terms, see
[When to spell out a term](#abbreviations--spelling-out).

<a id="units-of-measure--more-resources"></a>

#### More resources

- [Mathematical notation](#mathematical-notation)
- [Numbers](#numbers)

---

## Linking

<a id="cross-references"></a>

### Cross-references and linking

*Source: <https://developers.google.com/style/cross-references>*

In general, cross-references link to nonessential information that adds to
the reader's understanding.

When used well, cross-references help readers navigate and understand
documentation. But cross-references can easily become disruptive. The guidelines
on this page help you to minimize disruption while providing cross-references
that help your readers.

<a id="cross-references--choose-links"></a>

#### Choose links selectively

Be selective about which links you include on a page. Each link creates a
decision for the reader, adding cognitive load. Each link is also a chance for
the reader to leave the page and lose their place. When you include links,
choose the most relevant destination.

<a id="cross-references--context-on-page"></a>

##### Provide context on the page

When possible, provide help in context rather than linking elsewhere. For
example, in the following situations, consider providing information on the
page instead of linking:

- Define a term.
- Briefly explain a concept.
- Provide a couple of steps.

As a specific example, if you need readers to understand another product's
software or standards, it's better to link to good documentation elsewhere
than to try to thoroughly document another product's standards in our
documentation. But if a few sentences of basic information is all your readers
need, then it's better to provide that context and save your readers the trip
outside of our documentation.

<a id="cross-references--avoid-duplicate-links"></a>

##### Avoid duplicate links

Generally, within a given page, don't provide duplicate links to the same
destination. Provide the link once in the location where it's most useful to
the reader.

It's OK to add a secondary link in situations such as the following:

- You're linking to a particular section of another page.
- Your page is very long and the duplicate links are far apart.
- There are multiple entry points to the document that you're linking from.
  For example, if a page contains a procedure section and a troubleshooting
  section, then you might need to provide the same link in both of those
  sections.

<a id="cross-references--relevant-links"></a>

##### Provide the most relevant link

When you link, link to the most relevant page on a site. Link to the most
relevant heading on a page. Avoid providing multiple links that do the same
job.

<a id="cross-references--third-party-sites"></a>

##### Link to third-party sites

Our documentation often relies on the reader knowing something about
third-party standards or software. In such cases, it's better to provide a
link rather than attempt to thoroughly document someone else's standards. But
as with all links, when possible, provide brief information on the page
instead of linking.

<a id="cross-references--descriptive-link-text"></a>

#### Write descriptive link text

For the link text itself, use short, unique, descriptive phrases that provide
context for the material that you're linking to.

Effective link text helps to improve accessibility and scannability. Different
readers experience links differently. For example, users of screen reader
software often jump from one link to the next without reading the words in
between. Other readers visually scan a document to find relevant links.

Sometimes you have to rework a sentence to include a phrase that makes good
link text.

<a id="cross-references--link-text-options"></a>

##### Two options for effective link text

For your link text, use either the exact page title or a descriptive phrase, as
described in the following sections.

<a id="cross-references--page-titles"></a>

###### Page titles as link text

One option for effective link text is to match the link text to the page
title or heading that you're referencing.

For more information about how to capitalize the page title in a
cross-reference, see
[Capitalization in references to titles and headings](#capitalization--capitalization-in-references-to-titles-and-headings).

Recommended: For more
information, see
[Load balancing and scaling](https://cloud.google.com/compute/docs/load-balancing-and-autoscaling).

<a id="cross-references--descriptive-phrases"></a>

###### Descriptive phrases as link text

Another option for effective link text is to use a description of the
destination page, capitalized as if it's part of the sentence.

When you write a descriptive phrase as link text, help readers quickly
determine whether the link is relevant to them:

- Place important words at the beginning of the link text.
- Don't use the same link text in the same document for different target
  pages.
- Keep link text short where possible.
  Don't write lengthy link text such as a sentence or short paragraph.

Recommended: You can use
Cloud Scheduler and Cloud Functions to manage
[task scheduling on Compute Engine](https://cloud.google.com/blog/products/gcp/reliable-task-scheduling-on-google-compute-engine).

Not recommended: See
[this blog post](https://www.blog.google/products/pixel/pixel-4/).

<a id="cross-references--vague-link-text"></a>

##### Avoid vague link text

Write link text that makes sense without the surrounding text.
Don't use phrases such as *this document*, *this article*, or *click here*.

Recommended:
For more information, see
[Make headings into link targets](#headings-targets).

Not recommended:
Want more? [Click here!](#headings-targets)

Not recommended:
For more information,
see [this document](#headings-targets).

<a id="cross-references--urls"></a>

##### Avoid URLs as link text

In general, don't use a URL as link text. Instead, use the page title or a
description of the page.

Recommended:

```
For more information about protocols, see <a href="http://www.w3.org/Protocols/rfc2616/rfc2616.html">HTTP/1.1 RFC</a>.
```

Not recommended:

```
  See the HTTP/1.1 RFC at <a href="http://www.w3.org/Protocols/rfc2616/rfc2616.html">http://www.w3.org/Protocols/rfc2616/rfc2616.html</a>.
```

**Exception**: In some legal documents (such as some Terms of Service documents), it's
okay to use URLs as link text.

<a id="cross-references--abbreviations"></a>

##### Include abbreviations in link text

If the text includes an abbreviation in parentheses, include the long form
and the abbreviation in the link text.

Recommended: [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine/docs)

Not recommended: [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/docs) (GKE)

<a id="cross-references--commands"></a>

##### Link to commands

If the text includes a command or another element usually conveyed with
code font, include the description of the code element with the link text,
unless doing so is awkward or redundant. For more information about elements
that appear in code font, see [Code in text](#code-in-text).

Recommended: To create an
instance with a custom hostname, run the `gcloud instances create`
command with the
[`--hostname` flag](https://cloud.google.com/compute/docs/instances/custom-hostname-vm#gcloud).

Not recommended: To create
an instance with a custom hostname, run the `gcloud instances create`
command with the
[`--hostname`](https://cloud.google.com/compute/docs/instances/custom-hostname-vm#gcloud)
flag.

Recommended: This service
supports the `GET`, `HEAD`,
and `OPTIONS` methods.

Not recommended: This
service supports the `GET` method,
`HEAD` method, and
`OPTIONS` method.

<a id="cross-references--link-introductions"></a>

#### Write link introductions ("For more information")

When you dedicate a separate sentence to a cross-reference, introduce the
cross-reference using consistent language—specifically, use the phrase "For more
information, see..." or "For more information about..., see... ."

Include the "about..." clause when the link text or surrounding context
doesn't clearly indicate why you're referring the reader to this information.
For more information, see the
[Clarify the purpose of a link](#cross-references--clarify-purpose)
section of this document.

Don't use *on* instead of *about*.

Use *see* to refer to links and cross-references. For more information, see
[see](#word-list--see).

Recommended: For more information, see
[Load balancing and scaling](https://cloud.google.com/compute/docs/load-balancing-and-autoscaling).

Recommended: For more information about
task scheduling, see
[Reliable task scheduling on Google Compute Engine](https://cloud.google.com/blog/products/gcp/reliable-task-scheduling-on-google-compute-engine).

Not recommended: For more information on
indexes, see [Manage indexes](https://cloud.google.com/firestore/docs/query-data/indexing).

<a id="cross-references--clarify-purpose"></a>

#### Clarify the purpose of a link

Make sure that the surrounding context or the link text itself clearly
indicates why you're referring the reader to this information. Make the
explanation specific, but don't repeat the link text.

If you're introducing a cross-reference with "For more information..."
phrasing, then you can do this by adding an "about..." phrase. For more
information, see the
[Write link introductions](#cross-references--link-introductions) section
of this document.

Recommended: For more
information about authentication and authorization, see
[Using OAuth 2.0 to access Google APIs](https://developers.google.com/identity/protocols/OAuth2).

Recommended: If your
sample dump file is in a CSV, Avro, or Parquet file format, then
[load the file to BigQuery and copy to Spanner](https://cloud.google.com/spanner/docs/load-sample-data) using reverse ETL.

<a id="cross-references--explain-behavior"></a>

#### Explain unexpected link behavior

If a link goes to an unexpected destination or behaves in an unexpected way,
then provide that context. The following are a few such situations:

- **Links that download files and open emails.** If a link
  downloads a file or opens an email, then make that clear in the link text, and
  mention the file type.

  Recommended: For more
  information,
  [download the security features PDF](https://www.example.com/security.pdf).

  Recommended:

  ```
    <a href="mailto:support@example.com">send email to Technical Support</a>
  ```
- **Links to sections on the same page.** When you're
  linking to another section on the same page, let the reader know that the link
  takes you to a different section of the same page. Use a standard phrase to clue
  readers in if you use an on-page link.

  Recommended: For more
  information, see the
  [Write descriptive link text](#cross-references--descriptive-link-text)
  section of this document.
- **Links to sections on another page.** When you're linking
  to a section heading on another page, use the same wording and formatting as you
  do in a regular cross-reference.

  If the title of the section that you're linking to is identical to a
  title on the source page, add context to the cross-reference.

  Recommended: For more information, see
  [Create a table](https://cloud.google.com/bigtable/docs/managing-tables#create-table).

  Recommended: For more information, see
  [Install libraries](https://developers.google.com/style/cross-references#different-page)
  in "Building new audiences based on existing customer lifetime value."
- **Links that open in a new tab.** For more information, see the
  [Open links in the current tab](#cross-references--current-tab) section of this
  document.
- **Links that go to a different domain or server.** For more
  information, see the
  [Don't use external link icons](https://developers.google.com/style/cross-references#external-link-icons) section
  of this document.

<a id="cross-references--current-tab"></a>

#### Open links in the current tab

Don't force links to open in a new tab or window. Let the reader decide how
to open links.

In the rare situation that a link needs to open in a new tab or window, let
the reader know that the link opens differently than expected.

Recommended:

```
<a href="/style/accessibility">Accessible content</a>
```

Recommended:

```
<a href="/style/accessibility" target="_blank">Accessible content (opens in a new tab)</a>
```

Not recommended:

```
<a href="/style/accessibility" target="_blank">Accessible content</a>
```

---

<a id="headings-targets"></a>

### Headings as link targets

*Source: <https://developers.google.com/style/headings-targets>*

This page discusses how to turn a heading into a link target by using an
`id` attribute. For more information about how to format headings, see
[Headings and titles](#headings).

In some content management systems, anchors are automatically created for headings. However, you
might want to add a *custom* anchor to a heading for several reasons:

- You want to use an anchor that's shorter than the automatically generated anchor.
- You want to use an anchor for content that might be frequently linked to. Adding a custom
  anchor reduces the likelihood of breaking existing links if the heading text changes later.
- You want to [revise a heading](#headings-targets--changing-an-anchor). If the
  anchor for the heading is generated automatically, then the anchor changes when you revise
  the heading, breaking existing links.

<a id="headings-targets--adding-an-anchor"></a>

<a id="headings-targets--add-a-custom-anchor"></a>

#### Add a custom anchor

<a id="headings-targets--html"></a>

##### HTML

To add an anchor to a heading in HTML, add a `section` element
with an `id` attribute, or use an `a` element with
a `name` attribute. For anchor text, use lowercase letters, and
put hyphens between words. In the following, replace
`ID_OF_ANCHOR` with your anchor text—for example,
`introduction-to-everything`.

```
    <section id="ID_OF_ANCHOR"></section>
  
```

Recommended:

```
  <section id="introduction-to-everything">
  <h2>Introduction to everything</h2>
  ...
  </section>
  
```

Recommended:

```
  <h2><a name="introduction-to-everything">Introduction to everything</a></h2>
  
```

Recommended:

```
  <a name="introduction-to-everything"></a>
  <h2>Introduction to everything</h2>
  
```

Acceptable:

```
  <h2 id="introduction-to-everything">Introduction to everything</h2>
  
```

<a id="headings-targets--markdown"></a>

##### Markdown

To add an anchor to a heading in Markdown, add the following code to the
end of the line that the heading is on. For anchor text, use lowercase
letters, and put hyphens between words. In the following, replace
`ID_OF_ANCHOR` with your anchor text—for example,
`conserve-habitat`.

```
{: #ID_OF_ANCHOR }
```

Recommended:

```
## Help conserve habitat for pollinators {: #help-conserve-habitat-for-pollinators }
```

Also recommended:

```
## Help conserve habitat for pollinators {: #conserve-habitat }
```

Acceptable:

```
## Help conserve habitat for pollinators {: id='conserve-habitat' }
```

Acceptable:

```
## Help conserve habitat for pollinators {: id="conserve-habitat" }
```

<a id="headings-targets--changing-an-anchor"></a>

<a id="headings-targets--revise-a-heading"></a>

#### Revise a heading

If you revise a heading in a content management system where anchors are automatically created,
you can create a custom anchor to avoid breaking existing links. If the heading already has a
custom anchor, don't change the anchor unless it contains a term that you want to remove (such as
a disrespectful term).

To create the custom anchor, use the older ID string for the heading. You can find the ID
string by inspecting the heading on the published page. For example, if you change a heading from
*Introduction to some things* to *Introduction to everything*, then add a custom anchor
that uses the older ID string and formatting.

<a id="headings-targets--html_1"></a>

##### HTML

```
<section id="introduction-to-some-things">
<h2>Introduction to everything</h2>
...
</section>
```

<a id="headings-targets--markdown_1"></a>

##### Markdown

```
## Introduction to everything {: #introduction-to-some-things }
```

If you need to change an existing custom anchor, you should check your content management
system to update any links that use the old anchor. Inbound links that use the old anchor still
reach the page but not the specific section or heading.

---

## Computer interfaces

<a id="api-reference-comments"></a>

### API reference code comments

*Source: <https://developers.google.com/style/api-reference-comments>*

When you're documenting an API, provide a complete API reference, typically
generated from source code using document comments that describe all public
classes, methods, constants, and other members.

Use the basic guidelines in this document as appropriate for a given programming
language. This document doesn't specify how to mark up document comments.

For more information, see the following resources:

- [AIP-192: Documentation](https://google.aip.dev/192)
  in Google's API standards
- [Inline API documentation](https://cloud.google.com/apis/design/documentation)
  in the Google Cloud API design guide
- The specific style guide for each programming language

<a id="api-reference-comments--documentation_basics"></a>

#### Documentation basics

The API reference **must** provide a description for each of the following:

- Every class, interface, struct, and any other similar member of the API (such
  as union types in C++).
- Every constant, field, enum, and typedef.
- Every method, with a description for each parameter, the return value, and any
  exceptions thrown.

The following are **extremely strong suggestions**. In some cases, they don't
make sense for a particular API or in a specific language, but in general,
follow these guidelines:

- On each unique page (for a class, interface, etc.), include a code sample
  (~5-20 lines) at the top.
- Put all API names, classes, methods, constants, and parameters in code font,
  and link each name to the corresponding reference page. Most document
  generators do this automatically for you.
- Put string literals in code font, and enclose them in double quotation marks.
  For example, XML attribute values might be `"wrap_content"` or `"true"`.
- Make sure that the spelling of a class name in documentation matches the
  spelling in code, with capital letters and no spaces (for example,
  `ActionBar`).

  - Don't make class names plural (`Intents`, `Activities`); instead, add a
    plural noun (`Intent` objects, `Activity` instances). For more
    information, see [Plural product and feature
    names](#pluralization--plural-product-and-feature-names).
  - However, if a class has a name that's a common term, you can refer to it
    with the corresponding English word, in lowercase and *not* in code font
    (activities, action bar).

<a id="api-reference-comments--classes_interfaces_structs"></a>

#### Classes, interfaces, structs

In the first sentence of a class description, briefly state the intended purpose
or function of the class or interface with information that can't be deduced
from the class name and signature. In additional documentation, elaborate on how
to use the API, including how to invoke or instantiate it, what some of the key
features are, and any best practices or pitfalls.

Many documentation tools automatically extract the first sentence of each class
description for use in a list of all classes, so make the first sentence unique
and descriptive, yet short. Additionally:

- Don't repeat the class name in the first sentence.
- Don't say "this class will/does ..."
- Don't use a period before the actual end of the sentence, because some
  document generators naively terminate the "short description" at the first
  period. For example, some generators terminate the sentence if they see
  *e.g.*, so use *for example* instead.

The following example is the first sentence of the description for Android's
[`ActionBar` class](http://developer.android.com/reference/android/app/ActionBar.html):

> *A primary toolbar within the activity that may display the activity title,
> application-level navigation affordances, and other interactive items.*

<a id="api-reference-comments--members"></a>

#### Members

Make descriptions for members (constants and fields) as brief as possible. Be
sure to link to relevant methods that use the constant or field.

For example, here's the description for the `ActionBar` class's
[`DISPLAY_SHOW_HOME`](http://developer.android.com/reference/android/app/ActionBar.html#DISPLAY_SHOW_HOME)
constant:

> *Show 'home' elements in this action bar, leaving more space for other
> navigation elements. This includes logo and icon.*

> *See also: `setDisplayOptions(int)`, `setDisplayOptions(int, int)`*

<a id="api-reference-comments--methods"></a>

#### Methods

In the first sentence for a method description, briefly state what action the
method performs. In subsequent sentences, explain why and how to use the method,
state any prerequisites that must be met before calling it, give details about
exceptions that may occur, and specify any related APIs.

Document any dependencies (such as
[Android permissions](http://developer.android.com/guide/topics/security/permissions.html))
that are needed to call the method, and how the method behaves if such a
dependency is missing (for example, "the method throws a
[SecurityException](http://developer.android.com/reference/java/lang/SecurityException.html)"
or "the method returns null").

For example, here's the description for Android's
[`Activity.isChangingConfigurations` method](http://developer.android.com/reference/android/app/Activity.html#isChangingConfigurations()):

> *Checks whether this activity is in the process of being destroyed in order to
> be recreated with a new configuration. This is often used in `onStop` to
> determine whether the state needs to be cleaned up or if it's passed on to the
> next instance of the activity using `onRetainNonConfigurationInstance`.*

Use present tense for all descriptions—for example:

- *Adds a new bird to the ornithology list.*
- *Returns a bird.*

<a id="api-reference-comments--description"></a>

##### Description

- If a method performs an operation and returns some data, start the description
  with a verb describing the operation—for example:

  - *Adds a new bird to the ornithology list and returns the ID of the new
    entry.*
- If it's a "getter" method and it returns a boolean, start with "Checks
  whether ...."
- If it's a "getter" method and it returns something other than a boolean,
  start with "Gets the ...."
- If it has no return value, start with a verb like one of the following:

  - Turning on an ability or setting: "Sets the ...."
  - Updating a property: "Updates the ...."
  - Deleting something: "Deletes the ...."
  - Registering a callback or other element for later reference:
    "Registers ...."
  - For a callback: "Called by ...." (Usually for a method that's named
    starting with "on", such as `onBufferingUpdate`.) For example, "Called by
    Android when ...." Then, later in the description: "Subclasses implement this
    method to ...."
- If it's a convenience method that constructs the class object, start with
  "Creates a ...."

<a id="api-reference-comments--parameters"></a>

##### Parameters

For parameter descriptions, follow these guidelines:

- Capitalize the first word, and end the sentence or phrase with a period.
- Begin descriptions of non-boolean parameters with "The" or "A" if possible:

  - *The ID of the bird you want to get.*
  - *A description of the bird.*
- For boolean parameters that tell the API to do or not do something, state
  what the API does if the parameter is true and if it's false. For example:

  - *`enableCertificateValidation`: If true, validates the SSL certificate
    before proceeding. If false, trusts the certificate without validating it.*
- For boolean parameters that declare the already-established state of something
  (rather than telling the API to do something), use the format "True if ...;
  false otherwise." For example:

  - *True if the zoom is set; false otherwise.*
- In this context, don't put the words "true" and "false" in code font or
  quotation marks.
- For parameters with default behavior, explain what the behavior is for each
  value or range of values, and then say what the default value is. Use the
  format *Default:* to explain the default value.

<a id="api-reference-comments--return_values"></a>

##### Return values

Be as brief as possible in the return value's description; put any detailed
information in the class description.

- If the return value is anything other than a boolean, start with "The ..."—for
  example:

  - *The bird specified by the given ID.*
- If the return value is a boolean, use the format "True if ...; false
  otherwise."—for example:

  - *True if the bird is in the sanctuary; false otherwise.*

<a id="api-reference-comments--exceptions"></a>

##### Exceptions

In languages where the reference generator automatically inserts the word
"Throws", begin your description with "If ...":

- *If no key is assigned.*

Otherwise, begin with "Thrown when ...":

- *Thrown when no key is assigned.*

<a id="api-reference-comments--deprecations"></a>

##### Deprecations

When something is deprecated, tell the user what to use as a replacement. (If
you track your API with version numbers, mention which version it was first
deprecated in.)

Only the first sentence of a description appears in the summary section and
index, so put the most important information there. Subsequent sentences can
explain why something is deprecated, along with any other information that's
useful for a developer using your API.

If a method is deprecated, tell the reader what to do to make their code work.

<a id="api-reference-comments--examples"></a>

###### Examples

> *Deprecated. Use #CameraPose instead.*

> *Deprecated. Access this field using the `getField` method.*

---

<a id="code-in-text"></a>

### Code in text

*Source: <https://developers.google.com/style/code-in-text>*

In ordinary text sentences (as opposed to, say, [code samples](#code-samples)),
use code font to mark up most things that have anything to do with code. Code
font helps to clarify for your reader which text refers to an entity in these
ways:

- Signals to your reader that the text is meant to be entered
  verbatim.
- Shows where the boundaries of the text to enter are.
- Clearly separates the entity from surrounding text.

To mark text as code font, use the following:

- In HTML, use the `code` element.
- In Markdown, use backticks (`` ` ``).

For information about choosing HTML or Markdown, see
[Markdown versus HTML](#markdown).

This page explains how to format code in ordinary text sentences. For more information about
formatting and explaining placeholders, command-line syntax, and code samples, see the following
resources:

- [Formatting placeholders](#placeholders)
- [Documenting command-line syntax](#code-syntax)
- [Code samples](#code-samples)
- [Code style guides](#code-samples--coding)
- [Formatting a heading or title](https://developers.google.com/style/headings#formatting-a-heading-or-title)

<a id="code-in-text--code"></a>

<a id="code-in-text--some-specific-items-to-put-in-code-font"></a>

#### Some specific items to put in code font

The following table includes items that should be in code font, but it's not an exhaustive
list:

| Item | Recommended |
| --- | --- |
| Attribute names and values | The `imageURL` attribute contains the path for the image file that you can open in a browser—for example, `https://www.example.com/images/product.jpg`.  You can create a VM instance using the `e2-highcpu-16` machine type in the `us-central1-a` region. |
| Class names | The `SnapshotDiskOperator` class includes the `generate_snapshot_name` method. |
| Command output | The output is similar to the following:     ```         Found sysprep-specialize-script-ps1 in metadata.         ...         Finished running specialize scripts.          ``` |
| [Command-line utility names](https://developers.google.com/style/code-in-text#tool-names), such as `gcloud`, `gsutil`, `kubectl`, and `bq` | You can use the `kubectl` tool to define a network policy. |
| Data types | Nested data is represented as a `STRUCT` type. |
| Database elements (such as row and column names) | The query extracts the `month`, `julianday`, and `dayofweek` values from the `datetime` and `timestamp` columns. |
| Defined (constant) values for an element or attribute | The constant `city` has the value `"San Francisco"`. |
| [DNS record types](https://wikipedia.org/wiki/List_of_DNS_record_types) | Create a DNS `AAAA` record in your public DNS zone that points to the IP address of the load balancer. |
| Element names (HTML and XML) | The `script` and `df-messenger` HTML elements should be in the `body` element of your page.  A C-CDA document contains a header and a body enclosed within a `ClinicalDocument` XML element.  When you refer to an element name, don't put angle brackets (`<>`) around the element name. |
| Enum (enumerator) names | Generated from the protobuf enum `BOOL = 1;`. |
| Environment variable names | Set the `CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES` environment variable to include the resolution of your monitor. |
| Filenames, [filename extensions](#filenames--file-type-names) (if used), and paths | Open the `pg_hba.conf` file, which is typically in the `/etc/postgresql/13/main` directory. |
| Folders and directories | The configuration information for the reader deployment is in the `opentsdb-read.yaml.tpl` file in the `deployments` folder of the guide repository. |
| [HTTP content-type](https://www.w3.org/Protocols/rfc1341/4_Content-Type.html) values | The value of the `Content-Type` header value is required and must be set to `application/fhir+json` as defined in the FHIR specification. |
| [HTTP status codes](#code-in-text--statuscodes) | The HTTP `500 Internal Server Error` status code indicates that the server encountered an unexpected condition that prevented it from fulfilling the request. |
| HTTP verbs | To specify image content directly using a local image file, you can use a `POST` request. |
| IAM role names | Grant the new service account the `roles/cloudfunctions.invoker` IAM role for the `trace` function. |
| IP addresses | The other nodes of the cluster should contact this host on IP address `10.10.10.10.` |
| Language keywords | The SQL statement contains the dataset table name after the `FROM` keyword in the format of `PROJECT_NAME.DATASET.TABLE_NAME`. |
| [Method and function names](#code-in-text--methods) | The `ST_GEOPOINT` function uses the longitude and latitude of the Colosseum in Rome.  To fetch the status of the job, call the `get_job_status` method. |
| Namespace aliases | Use Config Sync to apply the package only to the `default` namespace. |
| [Placeholder variables](#placeholders) | Replace `SUBNETWORK_NAME` with the resource ID of the private subnet that you want the blueprint to use. |
| Package names | The Beautiful Soup library for parsing web pages is distributed as the `beautifulsoup4` package. |
| Port numbers | Each member Pod must have a container that's listening on TCP port `50000`. |
| Query parameter names and values | If you want to return all contents under a directory, use the `recursive=true` query parameter with your request. |
| Strings (such as URLs or domain names) that are used in commands and code | In IAM, a condition can specify a page that only Human Resources admins can access—for example, `https://hr.example.com`.  The `logID` field includes the domain `corpaudits.example.com`. |
| Text input | In the **Key name** field, enter `config-management`. |
| [UI elements](#ui-elements) that are rendered based on previously entered text (such as a server or instance name) | From the **Server name** list, select **`my-sql-cluster1`**.  Click **`my-instance`**.  If a code-formatted element appears in UI, add bold as well. For more information, see [Code in UI elements](#code-in-text--code-in-ui). |

Generally, don't put quotation marks around code unless the quotation marks
are part of the code.

<a id="code-in-text--roman"></a>

<a id="code-in-text--items-to-put-in-ordinary-non-code-font"></a>

#### Items to put in ordinary (non-code) font

The following table includes items that should not be in code font, but it's
not an exhaustive list. If you're referring to any of these items as computer input or output,
or as a code entity like an attribute or value, then use code font.

| Item | Recommended |
| --- | --- |
| Domain names | The test environment is designed only for standard application offerings from example.com. |
|<a id="code-in-text--u0023tool-names"></a> Names of products, services, and organizations | Example Organization has current and former employees who use Google products such as Google Docs and Google Sheets. |
| URLs that the reader is supposed to follow in a browser | You can find support at https://support.example.com.  It's usually best to format a URL as a link and use descriptive link text instead of exposing the URL itself. For more information, see [Avoid URLs as link text](#cross-references--urls). |

<a id="code-in-text--code-in-ui"></a>

<a id="code-in-text--code-in-ui-elements"></a>

#### Code in UI elements

If a
[UI element](#ui-elements--formatting)
meets the
[requirements for code font](#code-in-text--code),
then use both code font and bold for that element.

Recommended: In the **Network** list, select
**`my-net-2`**.

Recommended: In the **Query results** pane,
the **`Store`** column is displayed.

<a id="code-in-text--sometimes"></a>

<a id="code-in-text--items-that-are-sometimes-in-code-font"></a>

#### Items that are sometimes in code font

The following list includes items that are sometimes in code font, but it's not an exhaustive
list.

- **Boolean values**. If you refer directly to a Boolean data type value (such
  as `true` or `false`, or `1` or `0`), then format
  the value as code. If you refer to the evaluation of a Boolean condition as true or
  false, then refer to the evaluation in non-code font.

  Recommended:

  - If the update succeeds, returns `true`.
  - `enableCertificateValidation`: If true, validates the SSL certificate
    before proceeding. If false, trusts the certificate without validating it.
- **Command-line utility names**. Often, command-line utility names are spelled the same
  as the software project or product with which they are associated, with only differences in
  capitalization. In such cases, use code font for the command and ordinary font for the name of
  the project or product.

  Recommended:

  - Invoke the GCC 8.3 compiler using `gcc` for C programs or
    `g++` for C++ programs.
  - To send the file over FTP with IPv6, use `ftp -6`.
  - The options for the `curl` command are explained on the
    curl project website.
  - The `apt` program includes commands from the `apt-get`
    and `apt-cache` programs for working with APT packages.
- **Email addresses as input or output**. If you want the reader to use the email address
  as computer input or output, use code font. If you want the reader to treat the email address as
  a way to contact someone or a reference to someone, use non-code font and hyperlink the email
  address.

  Recommended:

  - Enter the username, not the full email address. For example, enter `alex`,
    not `alex@example.com`.
  - For help, contact [support@example.com](mailto:support@example.com).

<a id="code-in-text--methods"></a>

<a id="code-in-text--method-names"></a>

#### Method names

When you refer to a method name in text, omit the class name except where
including it would prevent ambiguity.

Recommended: To retrieve the zebra's
metadata, call its `get` method.

Not recommended: To retrieve the zebra's
metadata, call its `animal.get` method.

<a id="code-in-text--statuscodes"></a>

<a id="code-in-text--http-status-codes"></a>

#### HTTP status codes

To refer to a single status code, use the following formatting and
phrasing:

an HTTP `400 Bad Request` status code

In particular, call it a *status code* instead of a *response
code* or *error code*, and put the number and the name in code font.
If the *HTTP* is implicit from context, you can leave it out.

To refer to a range of codes, use the following form:

an HTTP `2xx` or `400` status code

In particular, use *Nxx* (with a specific digit in place of
N) to indicate *anything in the N00-N99
range*, and put the status code number in code font even if you're leaving
out the code's name.

If you prefer to specify an exact range, you can do so:

an HTTP status code in the `200`-`299`
range

Here, too, put the numbers in code font.

<a id="code-in-text--keywords"></a>

<a id="code-in-text--grammatical-treatment-of-code-elements"></a>

#### Grammatical treatment of code elements

In general, don't use code elements such as keywords and filenames as if they were
English verbs or nouns. Don't inflect the name of a code element, such as to make it
plural or possessive. Instead, include a noun after the name of the code element, and
inflect that noun.

| Recommended | Not recommended |
| --- | --- |
| The `ADDRESS` constant's value is defined in the `settings.h` file. | `ADDRESS`'s value is defined in `settings.h`. |
| To add the data, send a `POST` request. | `POST` the data. |
| To retrieve the data, send a `GET` request. | Retrieve information by `GET`ting the data. |
| You can't close the file before opening it.  You can't call the `close` method for a file before you call `open`. | `Close`ing the file requires you to have `open`ed it first. |
| Takes an array of extended ASCII code points (an array of `INT64` values) and returns `BYTES` values.  For `STRING` arguments, returns the original string with all alphabetic characters in uppercase. | Takes an array of extended ASCII code points (ARRAY of INT64) and returns BYTES. |

<a id="code-in-text--android-linking-API-terms"></a>

<a id="code-in-text--linking-api-terms-in-android"></a>

#### Linking API terms in Android

When you're writing code comments that you'll turn into generated reference
documentation, link to the first instance of each element of Android APIs, such as classes, methods,
constants, and XML attributes. Use code font and regular HTML
`a` elements to link to this reference material.
For later uses of the same API element in the same section, use code font
but do not link to the reference documentation.

Link `AndroidManifest.xml` elements and attributes to the API
guide pages. Link the attribute for a particular widget or layout to its Javadoc
in the widget or layout's API reference entry.

Recommended:

```
<a href="/guide/topics/manifest/data-element.html">data</a>
```

Very common classes such as `Activity` and `Intent`
don't need to be linked every time. If you use a term as a concept rather than a
class, then don't put it in code font and don't capitalize it. Here are some
objects that do not always require Javadoc links or capitalization:

- activity, activities
- service
- fragment
- view
- loader
- action bar
- intent
- content provider
- broadcast receiver
- app widget

If you use one of these terms in the context of referring to an actual
instance, use the formal class name and link to its reference page. Here are two
examples:

Recommended: The [`Activity`
class](https://developer.android.com/reference/android/app/Activity.html) is an important part of an application's overall lifecycle...

Recommended: The user interface for an
activity is provided by a hierarchy of views—objects derived from the
[`View` class](https://developer.android.com/reference/android/view/View.html).

To link to a class or method:

- To link to a class, use the class name as link text—for example:

  ```
  <a href="/reference/android/widget/TextView">TextView</a>
  ```
- To link to a method, use the method name as a fragment identifier. If
  you're linking to a static method, also include the class name in the link
  text. If you need to distinguish between overloaded versions of a particular
  method, consider showing the full signature—for example:

  ```
  <a href="/reference/android/app/Activity.html#onCreate(android.os.Bundle)">onCreate(Bundle)</a>
  ```
- To link the attribute for a particular widget or layout to its Javadoc
  in the widget or layout's API reference entry, use the URL for the page, and
  then add the fragment identifier
  `#attr_android:ATTRIBUTE_NAME`. For example, to link to
  the XML attribute `android:inputType` for the `TextView`
  widget, add the following:

  ```
  <a href="/reference/android/widget/TextView.html#attr_android:inputType>inputType</a>
  ```

---

<a id="code-samples"></a>

### Code samples

*Source: <https://developers.google.com/style/code-samples>*

This page explains how to format code samples. For more information about formatting and
explaining code that appears in text, command-line syntax, and placeholders, see the following
resources:

- [Code in text](#code-in-text)
- [Documenting command-line syntax](#code-syntax)
- [Formatting placeholders](#placeholders)

<a id="code-samples--guidelines"></a>

<a id="code-samples--basic-guidelines"></a>

#### Basic guidelines

Follow these guidelines when formatting code samples:

- **Follow the indentation guidelines in the relevant
  [code style guide](#code-samples--coding)**. For most programming languages, this means using
  spaces instead of tabs and using two spaces for each indentation level. However, some contexts
  use four spaces for each indentation level, and some contexts use tabs. This guidance applies to
  formatting code samples, not to [formatting commands](#code-syntax--formatting-a-command).
- **Wrap lines** at 80 characters. If you expect readers to have a relatively narrow
  browser window or to print out your document, consider wrapping at a smaller number of
  characters for readability.
- **Mark code blocks as preformatted text**. In HTML, use a `pre` element;
  in Markdown, indent every line of the code block by four spaces.
- **Indicate omitted code by using a comment** in the syntax of the language of your code
  sample. Don't use three dots or the ellipsis character (`…`). If a code
  block contains an omission, don't format the block as click-to-copy.

Recommended:

```
<pre>
function helloWorld() {
  alert('Hello, world! This sentence is so long that it wraps onto a second
    line.');
}
</pre>
```

This renders the following code block:

```
function helloWorld() {
  alert('Hello, world! This sentence is so long that it wraps onto a second
    line.');
}
```

Recommended:

```
apiVersion: serving.knative.dev/v1
kind: Service
# Several lines of code are omitted here.
spec:
  template:
    spec:
      containers:
      - image: IMAGE_URL
        ports:
        - name: h2c
          containerPort: 8080
```

<a id="code-samples--intros"></a>

<a id="code-samples--introductory-statements"></a>

#### Introductory statements

In most cases, precede a code sample with an introductory sentence or
paragraph. The introduction can end with a colon or a period; usually a colon if it
immediately precedes the sample, usually a period if there's more material (such
as a note paragraph) between the introduction and the sample, or if the
introduction paragraph ends in a sentence that isn't directly related to the
sample.

Recommended (ending with a period): The
following code sample shows how to use the `get` method. For
information about other methods, see [link]. [sample]

Also recommended: The following code
sample shows how to use the `get` method: [sample] For information about
other methods, see [link].

Not recommended (ending with a colon): The
following code sample shows how to use the `get` method. For
information about other methods, see [link]: [sample]

For more information about how to introduce code samples, see
[Document command-line syntax](#code-syntax).

<a id="code-samples--coding"></a>

<a id="code-samples--code-style-guides"></a>

#### Code style guides

The following public Google coding-style guides are available on GitHub:

- [C++ style guide](https://google.github.io/styleguide/cppguide.html).
- [HTML/CSS style guide](https://google.github.io/styleguide/htmlcssguide.html).
- [Java style guide](https://google.github.io/styleguide/javaguide.html).
- [JavaScript style guide](https://google.github.io/styleguide/javascriptguide.xml).
- [Python style guide](https://google.github.io/styleguide/pyguide)
- [Full list of Google's programming style guides](https://google.github.io/styleguide/)

Some open source projects have their own overriding style guides. For
example, Java code in the Android Open Source Project follows the [AOSP Java Code
Style for Contributors](https://source.android.com/setup/contribute/code-style) guide.

---

<a id="code-syntax"></a>

### Command-line syntax

*Source: <https://developers.google.com/style/code-syntax>*

<a id="code-syntax--command-line-syntax"></a>

This page shows how to document command-line commands and their arguments. For more
information about formatting code that appears in text, placeholders, and code samples, see the
following links:

- [Code in text](#code-in-text)
- [Formatting placeholders](#placeholders)
- [Code samples](#code-samples)

<a id="code-syntax--best-practices"></a>

#### Best practices

When you write procedural or conceptual documentation for a command-line command, apply the
following best practices:

- **Provide an inline link to the command reference**. A good place for that link is in
  the text that introduces the command or a series of steps.

  Recommended:

  To connect to the instance, use the
  [`gcloud compute ssh` command](https://cloud.google.com/sdk/gcloud/reference/compute/ssh):

  ```
  gcloud compute ssh
  ```
- **Determine which arguments are needed to complete each task in the recommended way**.
  To minimize the number of options that you need to document in non-reference content, use as
  few optional arguments as possible. Rely on the command reference for the complete list of
  arguments.
- **Provide a click-to-copy command example that the reader doesn't need to edit after they
  copy it**. If possible, include only runnable code and placeholder variables in the
  click-to-copy example.

  Some command examples contain
  [optional arguments](#code-syntax--optional-arguments),
  [mutually exclusive arguments](#code-syntax--set-of-two-arguments), or
  [repeated arguments](#code-syntax--arguments-that-can-repeat)
  that are indicated by square brackets (`[]`), pipes (`|`),
  braces (`{}`), and ellipses (`...`). These characters can break
  commands if they're not first removed. For that reason, avoid using these
  arguments in click-to-copy examples.

  For more information, see the
  [Optional arguments in click-to-copy commands](#code-syntax--click-to-copy-commands)
  section of this document.

<a id="code-syntax--formatting-a-command"></a>

<a id="code-syntax--format-a-command"></a>

#### Format a command

To mark a block of code such as a lengthy command or a code sample, use the
following formatting:

- In HTML, use the `pre` element.
- In Markdown, use a code fence (`` \`\`\` ``).

To format a command with multiple elements, do the following:

- When a line exceeds 80 characters, you can safely add a line break before
  some characters, such as a single hyphen, double hyphen, underscore, or
  quotation marks. After the first line, indent each line by four spaces to vertically align each line
  that follows a line break.
- When you split a command line with a line break, each line except the
  last line must end with the command-continuation character. Commands that don't
  have the command-continuation character don't work.

  - Linux or Cloud Shell: A backslash typically preceded with a space
    ( `\`)
  - Windows: A caret preceded with a space ( `^`)
- Format placeholder text with [placeholders](#placeholders).
- Follow the command line with a descriptive list of the placeholders
  used in the command line. For more information, see [Explaining placeholders](#placeholders--explain-placeholders).
- When documenting a command-line option or argument, use end puctuation for complete
  sentences. Don't use end punctuation for single words or noun phrases, unless there is a mix of
  sentences and noun phrases. This guidance is similar to [end punctuation in lists](#lists--capitalization-and-end-punctuation).
  For more information, see [Google AIP guidelines for documentation](https://google.aip.dev/192#style).

When you're documenting a `bash` or `sh` command, follow the
[quotation mark style](https://google.github.io/styleguide/shellguide.html#s5.7-quoting)
in Google's shell style guide.

<a id="code-syntax--prompt"></a>

#### Command prompt

If your command-line instructions show multiple lines of input in one block, then start each line
of input with the prompt symbol. If you don't want users to copy the prompt symbol when they copy
the command, you might be able to turn off text selection for the symbol—for example, by using
CSS.

Don't show the current directory path before the prompt, even if
part of the instruction includes changing directories. However, if the overall
context of the command interface changes—such as from the local machine
to a remote machine—then add an additional prompt indicator, as appropriate, for
the new context.

Recommended:

Enter the following code into the terminal:

```
$ adb devices
```

The output is the following:

```
List of devices attached
emulator-5554  device
emulator-5556  device
```

Recommended:

```
$ adb shell
shell@ $ screencap /sdcard/screen.png
shell@ $ exit
$ adb pull /sdcard/screen.png
```

When you're showing a one-line command, the command prompt
(the `$` symbol) is optional. However, if your document includes both
multi-line and one-line commands, then we recommend using the command prompt
for all of the commands in the document for consistency.

If your command-line instructions include a combination of input and output
lines, we recommend using separate code blocks for input and output.

Recommended:

```
$ cat ~/.ssh/my-ssh-key.pub
```

The output is similar to the following:

```
ssh-rsa KEY_VALUE USERNAME
```

<a id="code-syntax--optional-arguments"></a>

#### Optional arguments

Use square brackets around an argument to indicate that it's optional. If there's more than one
optional argument, enclose each item in its own set of square brackets.

Avoid using optional arguments in click-to-copy code examples. For best practices on documenting
optional arguments with click-to-copy commands, see the
[Best practices](#code-syntax--best-practices) and
[Optional arguments in click-to-copy commands](#code-syntax--click-to-copy-commands)
sections of this document.

In the following example, `GROUP` is required, but
`GLOBAL_FLAG` and `FILENAME` are optional:

```
gcloud dns GROUP [GLOBAL_FLAG] [FILENAME]
```

<a id="code-syntax--set-of-two-arguments"></a>

#### Mutually exclusive arguments

Use curly braces to indicate that the reader must choose one—and only one—of the
items inside the braces. There can be more than two mutually exclusive choices. To separate each
choice, use a pipe (`|`).

Avoid using mutually exclusive arguments in click-to-copy code examples. For best practices on
documenting mutually exclusive arguments with click-to-copy commands, see the
[Best practices](#code-syntax--best-practices) and
[Optional arguments in click-to-copy commands](#code-syntax--click-to-copy-commands)
sections of this document.

In the following example, choose either `FILE_1` or `FILE_2`:

```
{FILE_1|FILE_2}
```

In the following example, there are also two options:

- Left side of pipe: If the source code is deployed from a cloud
  repository, the following is required:  
  `--source=CLOUD_SOURCE --source-url=SOURCE_URL`
- Right side of pipe: If the source code is in a local directory:
  - `--bucket=BUCKET` is required.
  - `--source=LOCAL_SOURCE` is optional, as specified by the square
    brackets.

```
{--source=CLOUD_SOURCE --source-url=SOURCE_URL | --bucket=BUCKET [--source=LOCAL_SOURCE]}
```

<a id="code-syntax--arguments-that-can-repeat"></a>

#### Arguments that can repeat

Use three dots and no spaces (`...`) to indicate that the reader can specify multiple
values for the argument.

Avoid using an ellipsis in click-to-copy code examples. For best practices on documenting optional
arguments with click-to-copy commands, see the
[Best practices](#code-syntax--best-practices) and
[Optional arguments in click-to-copy commands](#code-syntax--click-to-copy-commands)
sections of this document.

In this example, the reader can specify multiple instances of the optional
parameter `GLOBAL_FLAG`:

```
gcloud dns GROUP [GLOBAL_FLAG ...]
```

<a id="code-syntax--click-to-copy-commands"></a>

#### Optional arguments in click-to-copy commands

[Optional arguments](#code-syntax--optional-arguments),
[mutually exclusive arguments](#code-syntax--set-of-two-arguments), and
[repeated arguments](#code-syntax--arguments-that-can-repeat)
contain characters (such as square brackets, curly braces, pipes, and ellipses) that can break
commands if the reader doesn't remove them. Avoid using these types of arguments in click-to-copy
commands. Instead, choose one of the following approaches:

- **Remove the optional arguments**. As a best practice,
  [use only the necessary arguments](#code-syntax--best-practices)
  to complete the task for the most common use case. If possible, remove optional arguments from
  the command; always provide a link to the command reference for the command, where readers can
  find the full list of options. For more information, check with product management or a
  technical support specialist for the most relevant arguments.

  Recommended:

  To get an aggregate list of all virtual machine (VM) instances in all zones for a project,
  use the
  [`gcloud compute instances list` command](https://cloud.google.com/sdk/gcloud/reference/compute/instances/list):

  ```
  gcloud compute instances list
  ```

  If you want to narrow the list of VMs to a specific zone, use the previous command with the
  `--zones` flag.
- **Use separate code blocks for each option**. In some cases, it might be ideal to
  provide more than one click-to-copy code block within the same section.

  Recommended:

  To create a bootable Compute Engine image, use the
  [`gcloud compute images import` command](https://cloud.google.com/sdk/gcloud/reference/compute/images/import):

  ```
  gcloud compute images import IMAGE_NAME \
      --source-file=SOURCE_FILE
  ```

  If you're importing an image with an existing license, specify the
  `--byol` flag:

  ```
  gcloud compute images import IMAGE_NAME \
      --source-file=SOURCE_FILE \
      --byol
  ```
- **Document optional arguments in separate tasks**. In some cases, it might be best to
  treat different options in separate sections.

  Recommended:

  To create a bootable or non-bootable Compute Engine image based on an existing virtual
  disk, use the
  [`gcloud compute images import` command](https://cloud.google.com/sdk/gcloud/reference/compute/images/import).

  <a id="code-syntax--import-a-bootable-virtual-disk"></a>

  ##### Import a bootable virtual disk

  If your virtual disk has a bootable operating system installed on it, run the following
  command:

  ```
  gcloud compute images import IMAGE_NAME \
      --source-file=SOURCE_FILE
  ```

  <a id="code-syntax--import-a-non-bootable-virtual-disk"></a>

  ##### Import a non-bootable virtual disk

  If your virtual disk doesn't have a bootable operating system installed on it, include the
  `--data-disk` flag:

  ```
  gcloud compute images import IMAGE_NAME \
      --source-file=SOURCE_FILE \
      --data-disk
  ```
- **Let the reader know that the command contains optional arguments**. If you must
  include special characters to indicate optional arguments, indicate that fact when you
  introduce the command.

  Recommended:

  To create a VM with a custom name and attach one or more existing stateful disks to that VM,
  use the
  [`gcloud compute instance-groups managed create-instance` command](https://cloud.google.com/sdk/gcloud/reference/compute/instance-groups/managed/create-instance)
  with one or multiple `--stateful-disk` flags. In the following example, you
  optionally specify the `auto-delete` subflag to keep or discard each disk when the
  VM is permanently deleted:

  ```
  gcloud compute instance-groups managed create-instance NAME \
      --instance=VM_NAME \
      --stateful-disk=device-name=DEVICE_NAME,source=DISK[,auto-delete=DELETE_RULE]
  ```

  For example, the following command creates a managed instance that's named
  `db-instance` and attaches the persistent disk `db-data-disk-1` as a
  stateful disk that is detached and preserved if its VM is deleted:

  ```
  gcloud compute instance-groups managed create-instance example-database-mig \
      --instance=db-instance \
      --stateful-disk=device-name=data-disk,source=projects/example-project/zones/us-east1-c/disks/db-data-disk-1,auto-delete=never
  ```

<a id="code-syntax--output"></a>

#### Output from commands

You don't have to show output for every command. Add output only if it adds value—for
example, if the reader needs to copy a value from the output or if they need to verify a value
in the output.

If you are showing output, use one of the following introductory phrases to separate the command
from the output.

Recommended: The output is similar to the following:

Recommended: The output is the following:

If you want to explicitly call out something about the output, you can customize the introductory
phrase.

Recommended: The output is similar to the
following, in which the `IP` column shows the IP address for each resource:

To indicate that one or more lines of output are omitted from sample output, use three dots and
no spaces (`...`) on a separate line. Do not use the ellipsis character (`…`).
For example:

```
Reading file status
Upload done, resetting board...
...
Wakeup reason: 0
```

For more information about presenting output, also see the following:

- For more information about how to present output in procedures, see [Order of multiple
  components in a step](#procedures--order-of-multiple-components-in-a-step).
- For more information about using placeholders in output, see [Placeholders in output](#placeholders--placeholders-in-output).
- For more information about using examples such as domain names and IP addresses in output, see [Example domains and names](#examples).

<a id="code-syntax--command-line-terminology"></a>

#### Command-line terminology

When discussing commands and their constituent parts in the `gcloud` CLI
and in Linux commands, follow this guidance:

- Avoid mapping nomenclature of the `gcloud` CLI's commands to
  Linux commands.
- Linux commands can be complicated. It's wise to describe what the entire
  command does rather than what its individual elements are called.
- For Linux commands or commands in the `gcloud` CLI, ask yourself if the reader must
  know the name of the command-line element or if explaining the command is sufficient.

<a id="code-syntax--gcloud-commands"></a>

##### gcloud commands

```
gcloud GROUP | COMMAND [--account=ACCOUNT] [--configuration=CONFIGURATION] \
    [--flatten=[KEY,...]][--format=FORMAT] [--help] [--project=PROJECT_ID] \
    [--quiet, -q][--verbosity=VERBOSITY; default="warning"] [--version, -v] \
    [-h] [--log-http][--trace-token=TRACE_TOKEN] [--no-user-output-enabled]
```

For the sake of accurate classification, the `gcloud` CLI's
syntax distinguishes between a *command* and a *command group*. In
docs, however, command-line contents are generally referred to as commands.

You can use commands (and groups) alone or with one or more flags. A
*flag* is a Google Cloud-specific term for any element
other than the command or group name itself. A command or flag might also
take an *argument*, for example, a region value.

<a id="code-syntax--example-command"></a>

###### Example command

```
gcloud init
```

<a id="code-syntax--example-command-with-a-flag"></a>

###### Example command with a flag

```
gcloud init --skip-diagnostics
```

<a id="code-syntax--example-command-with-multiple-elements"></a>

###### Example command with multiple elements

```
gcloud ml-engine jobs submit training ${JOB_NAME} \
    --package-path=trainer \
    --module-name=trainer.task \
    --staging-bucket=gs://${BUCKET} \
    --job-dir=gs://${BUCKET}/${JOB_NAME} \
    --runtime-version=1.2 \
    --region=us-central1 \
    --config=config/config.yaml \
    -- \
    --data_dir=gs://${BUCKET}/data \
    --output_dir=gs://${BUCKET}/${JOB_NAME} \
    --train_steps=10000
```

The preceding command consists of the following elements:

- `ml-engine` is a `gcloud` command group.
- `jobs` is an `ml-engine` command group.
- `submit` is a `jobs` command group.
- `training` is a `submit` command.
- `${JOB_NAME}` is an argument that refers to an environment
  variable called `JOB_NAME` that was set earlier.
- `--package-path` is a flag set to a path to a Python package to build.
- `--` in isolation separates the `gcloud` arguments that precede it from
  the [user arguments](https://cloud.google.com/sdk/gcloud/reference/ml-engine/jobs/submit/training#USER_ARGS)
  that follow it.

In addition to the term flag, *option* is often used as a
catchall term when you don't want to mire the reader in specialized
nomenclature.

For more information, see the
[Cloud SDK: gcloud](https://cloud.google.com/sdk/gcloud/reference/)
topic.

<a id="code-syntax--linux-commands"></a>

##### Linux commands

> [!CAUTION]
> **Caution**: Linux command syntax is notoriously complex.
> This section covers only the most common elements. For a more detailed reference,
> see [The Linux Command Line](http://wiki.lib.sun.ac.za/images/c/ca/TLCL-13.07.pdf).

Where the `gcloud` CLI uses the catchall terms
flag and option, Linux commands use *options*, *parameters*,
*arguments*, and a host of specialized syntax elements. The following is an
example:

```
find /usr/src/linux -follow -type f -name '*.[ch]' | xargs grep -iHn pcnet
```

The preceding command consists of the following elements:

- `find` is the command name.
- `/usr/src/linux` is an argument that specifies the path to look
  in. Easier to refer to as only a path.
- `-follow` is an option. The hyphen (`-`), often called a *dash* in
  this context, is part of the option.
- `-type` is an option with a value of `f`.
- `-name` is an option with a value of `'*.[ch]'`, where
  the asterisk (`*`) is a *metacharacter* signifying a wildcard.
  Metacharacters are used in Linux shell commands for *globbing*, or filename
  expansion. In addition to the asterisk, metacharacters include the question mark
  (`?`) and caret (`^`).

The results of the first command are redirected by using a *pipe*
(`|`) to the `xargs grep -iHn pcnet` command. Other
redirection symbols include the greater than symbol (`>`), less than symbol
(`<`), left double angle quotation mark (`<<`), and right double
angle quotation mark (`>>`). Redirection means capturing
output from a file, command, program, script, or even code block within a script
and sending it as input to another file, command, program, or script.

<a id="code-syntax--linux-signals"></a>

##### Linux signals

Linux signals require vocabulary choices that
are generally discouraged elsewhere in documentation. We recommend using the terms in the
following table *only* in the context of process control:

| Signal | Description |
| --- | --- |
| `SIGKILL` | Signal sent to *kill* a specified process, all members of a specified process group, or all processes on the system. `SIGKILL` cannot be caught, blocked, or ignored. Do not substitute *cancel*, *end*, *exit*, *quit*, *stop*, or *terminate*. |
| `SIGTERM` | Signal sent as a request to *terminate* a process. Although similar to `SIGKILL`, this signal gives the process a chance to clean up any child processes that might be running. Do not substitute *cancel*, *end*, *exit*, *quit*, or *stop*. |
| `SIGQUIT` | Signal sent from a keyboard to *quit* a process. Some processes can catch, block, or ignore a quit signal. Do not substitute *cancel*, *end*, *exit*, *quit*, or *stop*. |
| `SIGINT` | Signal sent to *interrupt* a process immediately. The default action of this signal is to terminate a process gracefully. It can be handled, ignored, or caught. It can be sent from a terminal—for example, when a user presses `Control+C`. Do not substitute *suspend*, *end*, *exit*, *pause*, or *terminate*. |
| `SIGPAUSE` | Signal that tells a process to *pause*, or *sleep*, until any signal is delivered that either terminates the process or invokes a signal-catching function. Do not substitute *cancel* or *interrupt*. |
| `SIGSUSPEND` | Signal sent to temporarily *suspend* execution of a process. Used to prevent delivery of a particular signal during the execution of a critical code section. Do not substitute *pause* or *exit*. |
| `SIGSTOP` | Signal sent to *stop* execution of a process for later continuation (upon receiving a `SIGCONT` signal). `SIGSTOP` cannot be caught, blocked, or ignored. Do not substitute *cancel*, *end*, *exit*, *interrupt*, *quit*, or *terminate*. |

---

<a id="placeholders"></a>

### Placeholder formatting

*Source: <https://developers.google.com/style/placeholders>*

This page explains how to format placeholders in commands, code samples, and text
strings. This page doesn't explain how to implement visual styling for placeholders, but it does
show examples of how Google developer documentation style renders placeholders as visually
distinct from other text.

For more information about formatting code, command-line syntax, and code samples, see the
following links:

- [Code in text](#code-in-text)
- [Documenting command-line syntax](#code-syntax)
- [Code samples](#code-samples)

Placeholders in sample code and commands represent values that the reader must replace when they use
the sample input. Placeholders in example output can also represent other values that vary. In
general, a placeholder has a descriptive name as a default value.

For example, the placeholder `PROJECT_ID` represents a project ID in sample
code, commands, and example output.

In example output, the placeholder `HTTP_RESPONSE_CODE` represents an
HTTP response code; the reader isn't expected to set this to a specific value.

<a id="placeholders--placeholder-variables"></a>

<a id="placeholders--placeholders"></a>

#### Placeholders

When you create placeholders follow this general guidance around using the letter
*x*:

- In general, don't use a single *x* or a series of *x*'s as placeholders; use a more
  informative placeholder.
- In some contexts (such as HTTP status codes), a series of *x*'s is the standard,
  so it's OK to use (for example) *xx* in those cases.

There are several ways to format placeholders, depending on whether you're
working in HTML or Markdown, or whether the placeholder is inline, in a code block, or in a
paragraph. For details, see the following sections.

<a id="placeholders--placeholders-in-inline-text"></a>

##### Placeholders in inline text

If your sample code and command placeholders occur in a sentence, use the following formatting:

- In HTML, wrap variable placeholders by using the `var`
  element, like this:

  ```
  <code><var>PLACEHOLDER_NAME</var></code>
  ```
- In Markdown, wrap inline placeholders in backticks (`), and use an
  asterisk (*) before the first backtick and after the second one
  (`` *`PLACEHOLDER_NAME`* ``).

If your placeholder does not represent a code sample or command, use the following formatting:

- In HTML, wrap placeholders by using the `var`
  element, like this:

  ```
  <var>PLACEHOLDER_NAME</var>
  ```

<a id="placeholders--placeholders-in-code-blocks"></a>

##### Placeholders in code blocks

If your placeholders are in a block of code, use the following formatting:

- In HTML, wrap the code block in a `pre` element,
  and tag placeholders with `var` elements:

  ```
        <pre>
        gcloud compute forwarding-rules create <var>FORWARDING_RULE_NAME</var> \
            --global | --region=<var>REGION</var> \
            --load-balancing-scheme=<var>LOAD_BALANCING_SCHEME</var> \
            --network=<var>NETWORK</var> \
            ...
        </pre>
        
  ```
- In Markdown, wrap the code block in a code fence (\`\`\`). Inside a
  code fence, you can't apply formatting like bold or italic.

  ```
  ```
  PLACEHOLDER_NAME
  ```
  ```

<a id="placeholders--placeholder-text"></a>

##### Placeholder text

**Use uppercase characters with underscore delimiters.**

For example, in HTML:

Recommended:

- `.../<var>API_NAME</var>`
- `.../<var>METHOD_NAME</var>`

Not recommended:

- `.../<var>API-name</var>`
- `.../<var>API_name</var>`
- `.../<var>API name</var>`
- `.../<var>api_name</var>`
- `.../<var>api-name</var>`
- `.../<var>apiName</var>`

In Markdown:

Recommended:

- `.../*API_NAME*`
- `.../*METHOD_NAME*`

If the context in which your placeholders appear makes using
uppercase characters with underscore delimiters a bad idea, use something else
that makes sense to you, but be internally consistent.

**Don't include possessive adjectives in placeholders.**

Not recommended:

- `.../<var>MY_API_NAME</var>`
- `.../<var>YOUR_API_NAME</var>`

> [!NOTE]
> **Note**: You can mark up command-line syntax with [brackets](#code-syntax--optional-arguments), [braces](#code-syntax--set-of-two-arguments), and [ellipses](#code-syntax--arguments-that-can-repeat). Don't put the
> brackets, braces, or ellipses in the `var` element.

<a id="placeholders--explain-placeholders"></a>

#### Explain placeholders

When you use a placeholder in text or code, explain the placeholder the first time you use it.
It's not necessary to repeat the explanation in the document unless doing so might benefit the
reader—for example, in circumstances such as the following:

- Your document is lengthy.
- You've introduced several other placeholders in a long procedure.
- Your document isn't intended to be read from beginning to end.

The following is an example of a command that uses a placeholder with an explanation of that
placeholder:

```
<pre class="devsite-click-to-copy">
gcloud compute instances create <var>INSTANCE_NAME</var> \
    --metadata enable-guest-attributes=TRUE
</pre>

<p>Replace <code><var>INSTANCE_NAME</var></code> with the name that
you want your new VM instance to have.</p>
```

<a id="placeholders--single-placeholder"></a>

##### Single placeholder

Use the following format for a single placeholder:

- Replace PLACEHOLDER with a description of what
  the placeholder represents.

Recommended:

1. Stream the build logs to the Google Cloud console:

   ```
   gcloud builds log --stream=BUILD_ID
   ```

   Replace `BUILD_ID` with the ID of the `WORKING` build that
   you copied in the preceding step.

<a id="placeholders--two-or-more-placeholders"></a>

##### Two or more placeholders

Use the following format for two or more placeholders:

- Follow the command line with a descriptive list of the placeholders
  used in the command line. Explain what each placeholder represents
  even if the placeholder value is intuitive to you.
- Introduce this list with *Replace the following:*
- List the placeholders in the order in which they appear in the command line.
- Tag each placeholder in a code sample or command with `code` and
  `var` elements, followed by a
  [colon and a description that starts with a lowercase letter](#colons).
  For
  non-code samples, remove the `code` elements—for example:

  ```
  <li><code><var>INSTANCE_NAME</var></code>: description</li>
  ```
- If the description contains an example, introduce it with an *em dash* or
  *such as*—for example:

  ```
  <li><code><var>INSTANCE_NAME</var></code>: description&mdash;for example,...</li>
  ```

  ```
  <li><code><var>INSTANCE_NAME</var></code>: description, such as...</li>
  ```
- Each item in the list follows our [list style](#lists).

Recommended:

1. Set the maximum concurrency target for a new reservation:

   ```
       bq mk \
           --project_id=ADMIN_PROJECT_ID \
           --location=LOCATION \
           --target_job_concurrency=CONCURRENCY \
           --reservation \
           RESERVATION_NAME
   ```

   Replace the following:

   - `ADMIN_PROJECT_ID`: the project that owns the reservation
   - `LOCATION`: the location of the reservation
   - `CONCURRENCY`: the maximum concurrency target
   - `RESERVATION_NAME`: the name of the reservation

Recommended:

1. In Cloud Shell, set the environment variables:

   ```
   export ONPREM_PROJECT=ON_PREM_PROJECT_NAME \
       export ONPREM_ZONE=ZONE
   ```

   Replace the following:

   - `ON_PREM_PROJECT_NAME`: the Google Cloud project
     name for your on-premises project. You can find your project number on the
     [Dashboard](https://console.cloud.google.com/home/dashboard)
     page of the Google Cloud console.
   - `ZONE`: a [Google Cloud
     zone](https://developers.google.com/compute/docs/regions-zones#identifying_a_region_or_zone) that's close to your location—for example, `us-east1`.

<a id="placeholders--placeholders-in-output"></a>

##### Placeholders in output

If you provide a code output example, explain any placeholders that appear in
sample output:

- Use `var` elements to identify the placeholder text in
  the output.
- Follow the example output with a list of the placeholders used in the
  example.
- Introduce the list of placeholders with *This output includes the
  following values:*
- List the placeholders in the order in which they appear in the
  example.
- Tag each placeholder with a `var` element,
  followed by a colon and a description that starts with a lowercase letter—for example:

  ```
  <li><code><var>INSTANCE_NAME</var></code>: description</li>
  ```
- If the description contains an example, introduce it with an *em dash* or
  *such as*—for example:

  ```
  <li><code><var>INSTANCE_NAME</var></code>: description&mdash;for example,...</li>
  ```

  ```
  <li><code><var>INSTANCE_NAME</var></code>: description, such as...</li>
  ```

For more information, see [Output from commands](#code-syntax--output).

Recommended:

<a id="placeholders--response"></a>

###### Response

The output is similar to the following:

```
{
 "name": "operations/build/PROJECT_ID/OPERATION_ID",
 "metadata": {
  "@type": "type.googleapis.com/google.devtools.cloudbuild.v1.BuildOperationMetadata",
  "build": {
   "id": "BUILD_ID",
   "status": "QUEUED",
   "createTime": "2019-09-20T15:55:29.353258929Z",
   "steps": [
    {
     "name": "gcr.io/compute-image-tools/gce_vm_image_import:release",
     "env": [
      "BUILD_ID=BUILD_ID"
     ],
     "args": [
      "-timeout=7056s",
      "-image_name=IMAGE_NAME",
      "-client_id=api",
      "-data-disk",
      "-source_file=SOURCE_FILE"
     ]
    }
   ],
   "timeout": "7200s",
   "projectId": "PROJECT_ID",
   "logsBucket": "gs://PROJECT_NUMBER.cloudbuild-logs.googleusercontent.com",
   "options": {
    "logging": "LEGACY"
   },
   "logUrl": "https://console.cloud.google.com/gcr/builds/BUILD_ID?project=PROJECT_NUMBER"
  }
 }
}
```

This output includes the following values:

- `PROJECT_ID`: the project ID for the project that
  the image was imported into
- `OPERATION_ID`: the ID of the import operation
- `BUILD_ID`: the ID of the build for the import
  operation
- `IMAGE_NAME`: the name of the image to be
  imported
- `SOURCE_FILE`: the URI for the image in Cloud
  Storage—for example, `gs://my-bucket/my-image.vmdk`
- `PROJECT_NUMBER`: the number for the import
  project

---

<a id="ui-elements"></a>

### UI elements and interaction

*Source: <https://developers.google.com/style/ui-elements>*

<a id="ui-elements--task-focus"></a>

#### Focus on the task

When practical, state instructions in terms of what the reader
should accomplish, rather than focusing on the widgets and gestures.
By avoiding reference to UI elements, you help the reader understand
the purpose of an instruction, and it can help future-proof
procedures.

Recommended: Refresh the page.

Recommended: Expand the **Advanced options**
section.

However, know the audience and understand the context. In some cases, the point
of a procedure is to guide the reader through elements on the page. Or the UI might not be obvious,
and it's helpful to explain the gestures for completing a step. Provide the level of detail
that seems useful for the intended audience.

Recommended: Click **Refresh**.

Recommended: To expand the **Advanced
options** section, click the
expander arrow.

The rest of this page focuses on scenarios where you've decided it's
useful to explicitly discuss UI elements.

For information about writing procedures, see [Procedures](#procedures).

<a id="ui-elements--formatting"></a>

#### Format names of UI elements

When referring to any UI element by name, put its name in bold, using the
`b` element in HTML or `**` in Markdown. This
includes names for buttons, menus, dialogs, windows, list items, or any other
feature on the page that has a visible name. Don't use code font for UI elements,
unless it's an element that meets the [requirements for code font](#code-in-text).
In that case, use both code font and bold.

> [!NOTE]
> **Note**: The reason for using the [`b`
> element](https://html.spec.whatwg.org/multipage/semantics.html#the-b-element) is that in modern HTML, `b` connotes text to which
> you want to draw visual attention, whereas the [`strong`
> element](https://html.spec.whatwg.org/multipage/semantics.html#the-strong-element) indicates strong importance.

Don't make an official feature name or product name bold, except when it
directly refers to an element on the page that uses the name (such as a window
title or button name).

Recommended:
In the **New project** window, select the **New activity**
checkbox, and then click **Next**.

Not recommended:
In the New Project window, select "New Activity", and then click the
"Next" button.

If you document a UI element outside the context of a procedure, try to provide context for the
element.

Recommended: The service lets you check the status of all
jobs in the **Current jobs** section of the service console.

Not recommended: The service lets you check the status of
all jobs in the **Current jobs** section.

<a id="ui-elements--capitalization"></a>

#### Use appropriate capitalization

In most cases, follow the capitalization as it appears on the page. However,
if labels are inconsistent or they're all uppercase, use sentence case.

| Guidance | Recommended | Not recommended |
| --- | --- | --- |
| When a label is all uppercase, use sentence case. | Click **Refresh**. | Click **REFRESH**. |
| When referring to multiple labels that are inconsistently cased, use sentence case for all of the labels. | Click **New project**, and then click **New activity**. | Click **NEW PROJECT**, and then click **New Activity**. |

<a id="ui-elements--referring-to-ui"></a>

<a id="ui-elements--refer-to-ui-elements"></a>

#### Refer to UI elements

Don't use UI elements as if they were English verbs or nouns.

| Recommended | Not recommended |
| --- | --- |
| In the **Name** field, enter an account name. | **Name** the account. |
| To save the settings, click **Save**. | **Save** the settings. |
| In the **Service account ID** field, enter a name.  For **Service account ID**, enter a name. | Specify a **Service account ID**. |

<a id="ui-elements--ui-terms"></a>

#### Terminology and usage

A user interface can contain a variety of UI elements. In general, focus on
the feature and its functionality, not the UI element. If you think it adds
clarity for the reader, use the name of the UI element. For example, both of the
following sentences are valid:

Recommended:
Go to **File > Tools**.

Recommended:
In the **File** menu, click **Tools**.

Don't use slang terms for UI elements—for example,
*hamburger icon* or *zippy*. For more information, see
[Buttons and icons](#ui-elements--buttons).

Recommended:
To expand the **Advanced options** section, click the
expander arrow.

Recommended:
Expand **Advanced options**.

Not recommended:
To expand the **Advanced options** section, click the zippy.

The following sections define some terms to use when referring to UI
elements.

For prepositions to use with these elements, see the
[Prepositions](#ui-elements--prepositions) table.

<a id="ui-elements--term-windows"></a>

##### Windows, pages, dialogs, panes, and sections

Most often, a *window* is the entire application window in a desktop
environment. However, it can also refer to modular application elements that you
can open and close. For example, in Android Studio, several windows are
available in the **View > Tool Windows** menu.

Recommended:
In the **MyApp** window, click **Edit**.

Not recommended:
In the **MyApp** page, click **Edit**.

*Page* is the preferred term when referring to a web page in general and to a subpage
of a console in particular. For more information, see
[console](#word-list--console).

Recommended:
In the Google Cloud console, go to the **Deployments** page.

Not recommended:
In the Google Cloud console, go to the **Deployments** window.

A *dialog* is a smaller window that is usually detached from the
main application window and appears in front of the window.

Recommended:
In the **Welcome** dialog, click **OK**.

Not recommended:
In the **Welcome** pop-up window, click **OK**.

A *pane* (or *panel*) is typically a distinct rectangular region within a larger
browser or application window. A pane or panel can often be tightly coupled to surrounding UI
regions, whereas a window is distinctly separate and can be hidden. Do not use terms such as
*window*, *section*, *area*, or *column* to refer to a pane or panel.

Recommended:
In the **Create service account** pane, click **New**.

Not recommended:
In the **Create service account** section, click **New**.

A *section* is a labeled grouping of options and controls, usually within a window, pane, or
panel. Do not use terms such as *area* or *column* to refer to a section.

Recommended: In the **Create metric** pane, do the
following:

- In the **Metric type** section, select **Counter**.
- In the **Labels** section, click **Add label**.

<a id="ui-elements--term-menus"></a>

##### Menus and menu bars

In a desktop application, the *menu bar* appears at the top of the
window or at the top of the screen; it's a set of *menus* (such as
**File** or **Edit**), each of which is a set of related
*commands* and/or nested submenus.

To refer to an item in a menu, use the term *command*, not *choice*, *menu item*,
or *option*. Exception: if you're documenting how to build an interface,
you can use *menu item*.

To refer to a menu, use the form *the **LABEL_NAME** menu.*

To tell the reader where to find a command in a menu or submenu, use a phrase like
*In the **File** menu, select **Open**.*

Don't use *drop-down* as a synonym for *menu*. See
[drop-down](#word-list--drop-down).

<a id="ui-elements--angle-brackets"></a>

###### Use angle brackets

Another option is to use angle brackets (>). If you use angle brackets, follow these
guidelines:

- Put a nonbreaking space (`&nbsp;`) before each angle bracket.
- Don't bold each menu name separately; instead, enclose the entire sequence in a single bold
  tag (`<b>...</b>` or `**...**`).
- Wrap the angle bracket with a span tag and add an `aria-label` attribute with
  *and then* text
  (for example, `<span aria-label="and then">></span>`).
  Otherwise, some screen readers might read `>` as "greater than."

In the following example, the text renders as *Select **View >
Tools > Developer Tools***. A screen reader
interprets this as *Select View and then Tools and then Developer Tools*.

<a id="ui-elements--html"></a>

##### HTML

```
Select <b>View&nbsp;<span aria-label="and then">></span> Tools&nbsp;<span aria-label="and then">></span> Developer Tools</b>.
```

<a id="ui-elements--markdown"></a>

##### Markdown

```
Select **View&nbsp;<span aria-label="and then">></span> Tools <span aria-label="and then">></span> Developer Tools**.
```

This notation is useful for abbreviating a longer phrase like *In the
**File** menu, select **Open**.* However, this notation applies only to
menu items. Don't use it to describe a combination of different UI elements.

Recommended: Select
**MyApp > Preferences**, and then select the
**Languages** preference pane.

Not recommended:
Select **MyApp** > **Preferences** > **Languages** >
**+** > **CSS**.

<a id="ui-elements--term-navigation-menu"></a>

##### Navigation menu

A *navigation menu* is a control—usually a pane or window—that contains a list of items
that the user can click to go to pages in an application or website. Don't use the terms
*navigation bar*, *navigation pane*, *navigation panel*, or
*navigation window* for such a control.

Recommended:
In the BigQuery navigation menu, click **Scheduled queries**.

<a id="ui-elements--term-toolbars"></a>

##### Toolbar

A *toolbar* is a set of buttons for common user actions. A toolbar
button that includes a menu is called a *menu button*. Refer to the
toolbar by name if you think that the user needs help finding a button.

Recommended:
On the Google Cloud console toolbar, click
**Notifications**.

Recommended: Click
**Notifications**.

<a id="ui-elements--buttons"></a>

##### Buttons and icons

A *button* initiates an action when clicked (or tapped, in the case
of a touchscreen). To refer to a button, use the button's label.

Recommended: Click **OK**.

Not recommended: Click the "OK"
button.

An icon is a symbol or image that represents an object or a function. An icon
can be a button as well. If the button includes an icon, write the name of the
button as shown in the tooltip, and add the button icon before the
name. If you need to use a space between the icon and the name for readability,
use a nonbreaking space.

Recommended: Click
**Settings and utilities**.

Not recommended: Click
.

If the icon tooltip is identical to the name of the icon, use an
[empty `alt` attribute](#images--alt-text).

If you're unsure of the name of the icon, inspect the element using browser
tools. In many cases, a visual element like an icon has an ARIA attribute
that provides a textual description of the element for use by screen readers.
To inspect an element, right-click the element and select
**Inspect** or **Inspect element**, depending on your browser. Look for one of the following
types of labels: `aria-labelledby`, `aria-label`,
`aria-describedby`, `label`, `placeholder`, or `title`.
For more information, see
[Using aria-label](https://www.w3.org/TR/WCAG20-TECHS/ARIA14.html)
and
[Accessible Name and Description calculation](https://www.w3.org/TR/html-aapi/#accessible-name-and-description-calculation).

If a button with an icon doesn't include a tooltip, submit a bug report
requesting that a tooltip be added. Tooltips are crucial for accessibility, and
for documentation and discoverability in general.

Recommended: Click ![](https://developers.google.com/static/style/images/icon-add.png) **Add**.

Not recommended: Click the ![hammer icon](https://developers.google.com/static/style/images/icon-add.png) icon.

If a UI element name ends with an ellipsis (...), leave out the ellipsis.

Recommended: Click **Browse**.

Not recommended: Click
**Browse ...**.

Don't use directional language to orient the reader, such as *above*,
*below*, or *right-hand side*. Phrases like those don't work well for
accessibility or for localization. If a UI element is hard to find, provide a
screenshot.

Recommended: Click **Menu**.

Not recommended: In the left-side panel,
click the button with three lines.

<a id="ui-elements--difficult-to-find-ui-elements"></a>

###### Difficult-to-find UI elements

If you have UI elements that are difficult to find, consider one of the following options
as an alternative to using directional language, which can be problematic for
accessibility and localization reasons.

- Use the button icon along with its name as shown in the button tooltip.

  Recommended: Click
  **Refresh**.
- Add context to help the user find the element.

  Recommended: On the Cloud Run toolbar, click
  **Refresh**.
- Use a screenshot.

  Recommended: In the list of services, click
  **Column display options**.

  ![List of services.](https://developers.google.com/static/style/images/list-of-services.png)

  For more information about when and how to use screenshots, see
  [Diagrams, figures, and other images](#images).

<a id="ui-elements--term-tab"></a>

##### Tab

A *tab* is a navigation element that looks like a file tab. To refer
to a tab, use the form *the **LABEL_NAME** tab*.

Recommended: Select
**Tools > Options**, and then click the **Edit**
tab.

<a id="ui-elements--term-textbox"></a>

##### Text box

A *text box* is a box that the user can type in. Use
*box* and the form *the **LABEL_NAME** box*. Format the text
that the user types by using the `code` element in HTML, or by using code
formatting (monospace) in other markup.

Recommended: In the **Owner** box,
enter your name.

Recommended: In the **Name** box,
enter `wsfc-1`.

In Google Cloud, use
*field* instead of *box*.

In Google Workspace documentation, use
*field* instead of *box*.

Recommended: In the **Instance** field,
specify a value less than 64 characters long.

<a id="ui-elements--term-listbox"></a>

##### List box, combo box, and spin box

A *list box* is a box that offers the user a list of items. To refer to a list box, use
the form *the **LABEL_NAME** list* or
*the **LABEL_NAME** box*, whichever is clearer.

Recommended: In the **Item** list, select
**Desktop**.

A *combo box* is a combination of a text box and a list box. To
refer to a combo box, use the form *the **LABEL_NAME** box*. To refer to
entering a value into a combo box, use the verbs *type or select* or *enter*.

Recommended: In the **Font** box, type
or select the font that you want to use.

A *spin box* is a box that lets the user choose a value by clicking
arrows or by typing. To refer to a spin box, use the form *the
**LABEL_NAME** box*. To refer to entering a value into a spin
box, use the verb *enter*.

Recommended: In the **Font Size** box,
enter a font size.

<a id="ui-elements--term-checkbox"></a>

##### Checkbox

A *checkbox* is a small box that indicates whether an option is
on or off. To refer to a checkbox, use the form *the
**LABEL_NAME** checkbox*.

Be wary of using the verbs *check* and *uncheck*, which can be ambiguous; it's often
best to use *select* and *clear* instead.

Recommended: Select the **Automatically
check for updates** checkbox.

Recommended: Clear the
**Bookmarks** checkbox.

If you need to refer to the state of the checkbox, it's often best to refer to it as
*selected* or *not selected*.

Recommended: Make sure that the
**Bookmarks** checkbox is selected.

Recommended: Make sure that the
**Bookmarks** checkbox isn't selected.

<a id="ui-elements--term-radiobutton"></a>

##### Radio button

A *radio button* is a small button used to choose one item from a
group of mutually exclusive options. To refer to a radio button, use the radio
button's label, or refer to the group of buttons by its label.

Recommended: Select **Do not remember
passwords**.

Recommended: For **Startup mode**,
select an option.

<a id="ui-elements--term-expander"></a>

##### Expander arrow

An *expander arrow* is the UI element used to expand or collapse a section of
navigation or content. Avoid referring to these explicitly in documentation, but when you do, use
the terms *expander arrow* and *expandable section* rather than terms like
*expando* or *zippy*.

Recommended: To expand the
**Advanced options** section, click the
expander arrow.

Not recommended: To expand
the **Advanced options** section, click the zippy.

<a id="ui-elements--term-toggle"></a>

##### Toggle

A *toggle* is the UI element that switches back and forth between on and off
states. Don't use the word *toggle* as a verb. Describe the action that you want the
user to take.

Recommended: To turn on the setting, click
the **Wi-Fi** toggle.

In some cases, you might not know what state the toggle is in before the user interacts with it
so be clear what position the toggle should be in.

Recommended: In **Settings**, click
the **Magic mode** toggle to the on position.

<a id="ui-elements--keyboard"></a>

#### Press and type keyboard keys

To indicate that the user should press a given keyboard key or
combination, use the `kbd` element.

The following is an example of a `<kbd>` tag:

Recommended:
`Press <kbd>Control+C</kbd>.`

When rendered, the text appears as follows:

Recommended: Press `Control+C`.

If you're working with non-HTML markup, use monospace formatting, which is how the
`kbd` element renders.

To refer to a letter key, use uppercase instead of lowercase.

Recommended: To save, press
`Control+S`.

Not recommended: To save, press
`Control+s`.

To refer to a key that the user types to enter that key's value as text input,
use the `code` element, not the `kbd` element.
For more information, see [Code font](#text-formatting--code-font).

To refer to a keyboard key, use the key's name. If that's ambiguous, use the
form *the `KEY_NAME` key*.

Recommended: Press `Esc`.

Recommended: Press the `Esc` key.

Spell out the names of modifier keys such as Command, Control, Option, and
Shift. Don't use symbols for those keys. To refer to a key combination, use the
form *`MODIFIER+KEY_NAME`*.

Recommended: Press
`Control+V`.

When you provide shortcuts for multiple operating systems, put the macOS shortcut in
parentheses after the Windows and Linux shortcut.

Recommended: To copy, press
`Control+C` (or `Command+C` on macOS).

Not recommended: To copy, press
`Ctrl+C` (`⌘+C`).

To refer to a key or combination that uses the Shift key, use the form
*`MODIFIER+Shift+KEY_NAME`*.

Recommended: Press
`Control+Shift+?`.

Spell out the names of characters that could be confusing in a keyboard
shortcut, such as comma, hyphen, period, and plus.

To refer to a keyboard shortcut, use either *keyboard shortcut* or *key
combination*.

To refer to pressing a key or combination to cause an action to occur, use
the verb *press*. To refer to typing a key or combination as part of text, use
the verbs *enter* or *type*.

<a id="ui-elements--prepositions"></a>

#### Prepositions

When documenting the UI, use the following prepositions.

| Preposition | UI element | Recommended |
| --- | --- | --- |
| in | dialogs  fields  lists  menus  panes  windows | In the **Alert** dialog, click **OK**.  In the **Name** field, enter `wsfc-1`.  In the **Item** list, select **Desktop**.  In the **File** menu, click **Tools**.  In the **Metrics** pane, click **New**.  In the **Task** window, click **Start**. |
| on | pages  tabs  toolbars | On the **Create an instance** page, click **Add**.  On the **Edit** tab, click **Save**.  On the **Dashboard** toolbar, click **Edit**. |

<a id="ui-elements--verbs"></a>

#### Verbs in procedures

To describe an action on the page, use the following verbs. For more
information about each verb, see its corresponding entry on the
[word list](#word-list).

- [Click](#word-list--click)
- [Choose](#word-list--choose)
- [Drag](#word-list--drag)
- [Enable](#word-list--enable)
- [Enter, type](#word-list--enter)
- Go to (see [scroll](#word-list--scroll))
- [Hold the pointer over](#word-list--hold-the-pointer-over)
- [Press](#word-list--press)
- [Select](#word-list--select)
- [Tap](#word-list--tap)
- [Turn on, turn off](#word-list--turn-on)

For information about writing procedures, see [Procedures](#procedures).

---

## HTML and CSS

<a id="semantic-tagging"></a>

### HTML and semantic tagging

*Source: <https://developers.google.com/style/semantic-tagging>*

<a id="semantic-tagging--intro"></a>

Use HTML elements for the purposes that they were designed for. For example, when
you give the title of a standalone work (such as a book or a movie), mark it
with a [`cite`
element](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-cite-element). For more information about semantic tagging, see [Semantics in HTML](https://developer.mozilla.org/en-US/docs/Glossary/Semantics#Semantics_in_HTML)
on the MDN web documents site.

In situations where there are no semantically relevant HTML elements, use CSS
or the few HTML elements that convey visual style without semantics.

<a id="semantic-tagging--visual-formatting"></a>

#### Visual formatting

If you want to achieve specific visual results, don't use HTML elements that
convey different semantics.

In particular, follow these guidelines:

- Don't use frames or tables for layout; instead, use your site's CSS to lay out the page.
- Don't use the heading elements (such as `h1` and
  `h2`) to visually style text; instead, use those elements
  only for hierarchically structured headings, and use CSS for visual style.
- The [`em`
  element](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-em-element) indicates emphasis, not italics as such. Don't use it to italicize
  something that isn't meant to be emphasized; instead, use the [`i`
  element](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-i-element) for non-emphasis italics.
- The [`strong`
  element](https://html.spec.whatwg.org/multipage/semantics.html#the-strong-element) indicates strong importance, not bold as such. To bold a word that
  doesn't merit strong importance, use the [`b`
  element](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-b-element).
- The [`br`
  element](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-br-element) is intended "only for line breaks that are actually part of the content,
  as in poems or addresses." Don't use it to adjust the spacing between lines.
  Instead, use elements like `p` to semantically mark the
  text, and use CSS to adjust line spacing.

---

<a id="html-formatting"></a>

### HTML formatting

*Source: <https://developers.google.com/style/html-formatting>*

<a id="html-formatting--formatting"></a>

Follow Google's [HTML/CSS
Style Guide](https://google.github.io/styleguide/htmlcssguide.html). Exception: don't leave out optional elements.

In particular, following are some basic guidelines from that style guide,
which generally apply to other documentation source files, too (such as YAML and Markdown):

- **Don't use tabs** to indent text; use spaces only. Different text
  editors interpret tabs differently, and some Markdown features expect spaces
  and not tabs.
- **Indent by two spaces** per indentation level.
- **Use all-lowercase** for elements and attributes.
- **Don't leave trailing spaces** at the end of a line (except as
  needed for Markdown).

<a id="html-formatting--line-length"></a>

#### Line length

Break lines at 80 characters except in the following cases:

- Information in a `meta` element at the beginning of a file must be on a single line,
  so those lines can be as long as needed.
- If a URL in a link has a line break, the link won't work.
  If a URL is longer than 80 characters (quite common), you're stuck with it. In that case,
  put the URL on its own line with the `href` attribute to make it
  easier to review the text before and after, as the following example shows:

```
You can find more information in
<a href="https://example.com/long-url/johan-gambolputty-de-von-ausfern-…-von-hautkopf-of-ulm.html"
>his biography.</a>
```

Break code snippets (in `<pre>` blocks) at 80 characters:

- Older files might use different line lengths. If you're making small changes to a file that
  has a consistent line length other than 80 characters, then make your changes conform to that
  file's line length rather than reformatting the whole file.
- When adding line breaks, make sure that you don't change the meaning of the code! If you're
  not familiar with the programming language, ask for help from someone who is. But sometimes you
  just can't avoid a long line.

---

<a id="markdown"></a>

### Markdown versus HTML

*Source: <https://developers.google.com/style/markdown>*

<a id="markdown--html-markdown"></a>

Use either HTML or Markdown. Some of this style guide assumes that you're using HTML. If you're
using Markdown, details like what HTML elements to use in various contexts might be
irrelevant to you.

Markdown is easier to write than HTML, and it's easier for most humans to
read Markdown source than HTML source. However, HTML is more expressive
(particularly regarding [semantic tagging](#semantic-tagging))
and can achieve some specific effects that might be difficult or impossible in
Markdown. For example, you might have to switch to using the HTML `code` element
for special characters in code such as nonbreaking spaces.

In the end, which one to use is primarily a matter of personal preference;
however, if your team or your document template already uses one or the other,
it may be best to use whatever they use.

---

## Names and naming

<a id="examples"></a>

### Example domains and names

*Source: <https://developers.google.com/style/examples>*

Don't use real domain names, email addresses, or people's names in your examples. Don't reveal
personally identifiable information (PII), such as domain names, email addresses,
phone numbers, people's names, project names, or credit card numbers. You can
provide imaginary (fictitious) examples or use
[placeholders](#placeholders), like
`USER_ID` or `EMAIL_ADDRESS`.

<a id="examples--domains"></a>

<a id="examples--example-domain-names"></a>

#### Example domain names

When you need a generic domain name in an example, use example.com,
example.org, or example.net. These domains are reserved by the
[Internet Assigned Numbers Authority](https://www.iana.org/domains/reserved)
for use in documentation.

Alternatively, you can use any of the following domain names, which Google
owns specifically for use in documentation:

- altostrat.com
- examplepetstore.com
- example-pet-store.com
- myownpersonaldomain.com
- my-own-personal-domain.com
- cymbalgroup.com

If you need an example domain name for an internationalized domain name, use one of the
[IDN Test TLDs](https://en.wikipedia.org/wiki/IDN_Test_TLDs) and copy from the
"URL of the test site" column.

Recommended: Hostnames that include non-ASCII characters
are encoded using Punycode. For example, `http://مثال.إختبار` is encoded as
`xn--kgbechtv`.

<a id="examples--addresses"></a>

<a id="examples--example-email-addresses"></a>

#### Example email addresses

If you need a generic email address, use one of the domains listed
in
[Example domain names](#examples--example-domain-names)
and one of the names listed in [Example person names](#examples--example-person-names)—for
example, dana@example.com. It's OK to use generic addresses like support@example.net. Don't use
person names, product names, or made-up names in email addresses.

<a id="examples--names"></a>

<a id="examples--example-person-names"></a>

#### Example person names

When you need to include example given names in your documentation,
draw from the following list:

- Alex
- Amal
- Ariel
- Bola
- Charlie
- Cruz
- Dana
- Dani
- Hao
- Ira
- Izumi
- Jie
- Kai
- Kalani
- Kim
- Kiran
- Lee
- Lucian
- Luka
- Mahan
- Noam
- Nur
- Quinn
- Raha
- Rosario
- Sasha
- Tal
- Taylor
- Tristan
- Yuri

<a id="examples--example-person-surnames"></a>

##### Example person surnames

When you need to include example surnames in your documentation, use an initial
after the given first name—for example, Quinn N. or Dana A.

<a id="examples--further-notes-about-example-people"></a>

##### Further notes about example people

When you are writing about people, even fictitious or hypothetical people, it's important to
remember that your work will be read by real people whom we want to feel respected, valued, and
welcomed.

Your audience includes different kinds of people, including people with different jobs,
cultural contexts, and backgrounds, so strive to include a variety of people in your examples
as well.

Use the [gender-neutral singular pronouns](#pronouns--gender-neutral-pronouns)
*they*, *their*, and *theirs*
whenever possible, and avoid specifying gender unless it is integral to the information you
are communicating. Avoid examples that depend on a gender binary. However, if you do write an
example that requires specifying gender, consider that some of the names on this list may imply
a particular gender in a given language or culture, and check to ensure that any names you have
chosen do not carry a conflicting gender connotation.

Be mindful of assumptions and stereotypes that might be reinforced through hypothetical
examples, such as:

- Job roles and levels, such as executive, that might be disproportionately assigned
  particular gendered personas.
- Job roles, such as developer or engineer, that might be disproportionately assigned
  particular ethnic personas.

We recommend using names from the preceding list in most documentation. Some security
documentation uses the
[Alice and Bob](https://wikipedia.org/wiki/Alice_and_Bob#Cast_of_characters)
cast of characters. Don't use the Alice and Bob characters unless you're writing documentation that
refers to a technical specification that uses those characters. If you use the Alice and Bob
characters in a document, use only names from that cast of characters.

For further guidance, see the section of this guide on
[writing inclusive documentation](#inclusive-documentation).

<a id="examples--company"></a>

<a id="examples--example-company-names"></a>

#### Example company names

When you need a company name in an example, use Example Organization. If you need to
differentiate between two different fictional companies, you can add a description to the company
names. For example, you can use Enterprise Example Organization and Startup Example
Organization.

<a id="examples--phone-numbers"></a>

<a id="examples--example-phone-numbers"></a>

#### Example phone numbers

Most phone numbers in our documentation are examples. To show an example phone number, use a US
number in the range 800‑555‑0100 through 800‑555‑0199. That range is
reserved for use in examples and in fiction.

Never use a real phone number in examples.

For information about formatting, see
[Format phone numbers in HTML or Markdown](#phone-numbers--format-phone-numbers).

<a id="examples--ip-addresses"></a>

<a id="examples--example-ip-addresses"></a>

#### Example IP addresses

When you need an IPv4 address in an example, such as in a log, use one of the
[RFC 5737](https://tools.ietf.org/html/rfc5737) addresses that are
reserved for use in documentation:

- `192.0.2.0` through `192.0.2.255`
- `198.51.100.0` through `198.51.100.255`
- `203.0.113.0` through `203.0.113.255`

For IPv4 address ranges, use the following examples:

- `192.0.2.0/24`
- `198.51.100.0/24`
- `203.0.113.0/24`

When you need an IPv6 address, use values from the
[RFC 3849](https://tools.ietf.org/html/rfc3849) range. Example IPv6 addresses include
the following:

- `2001:db8::`
- `2001:db8:ffff:ffff:ffff:ffff:ffff:ffff`
- `2001:db8:1:1:1:1:1:1`
- `2001:db8:2:2:2:2:2:2`
- `2001:db8:3:3:3:3:3:3`
- `2001:db8:4:4:4:4:4:4`

For IPv6 address ranges, use the following example:

- `2001:db8::/32`

<a id="examples--street-addresses"></a>

<a id="examples--example-street-addresses"></a>

#### Example street addresses

Avoid using real street addresses in examples. Instead, use one of the following fictional
street addresses:

- 1800 Amphibious Blvd.  
  Mountain View, CA 94045
- Avenida da Pastelaria, 1903  
  Lisbon, 1229-076
- 8 Rue du Nom Fictif  
  341 Paris

<a id="examples--project-names"></a>

<a id="examples--example-project-names"></a>

#### Example project names

When you need an example project name, create a name that's meaningful or descriptive.

Ensure that the name is applicable to the reader's environment. Don't use unclear components like
`foo`, `bar`, and `baz` in names.

When necessary, use an appended numbering scheme. For example, `staging`,
`frontend-development`, `backend-development`, `production-1`,
`production-2`.

<a id="examples--service-account-ids"></a>

<a id="examples--example-service-account-ids"></a>

#### Example service account IDs

When you need a unique ID for a service account in an example, use the numeric ID
`123456789012345678901`.

Recommended: The allow policy shows the
identifier `deleted:serviceAccount:my-service-account@my-project.iam.gserviceaccount.com?uid=123456789012345678901`.

<a id="examples--data"></a>

---

<a id="filenames"></a>

### Filenames

*Source: <https://developers.google.com/style/filenames>*

<a id="filenames--naming-guidelines"></a>

#### Guidelines for names

Make file and directory names lowercase, with the occasional exception for consistency, to make file searches easier and search results more useful. For example, because most Unix-style operating systems are case sensitive, they can't find a file named `Impersonate-Service-Accounts.html` if you search for `impersonate-service-accounts.html`. Linux and macOS interpret these as two distinct files.

Use hyphens, not underscores, to separate words—for example,
`query-data.html`. Search engines interpret hyphens in file and directory names as spaces between words. Underscores are generally not recognized, meaning that their presence can negatively affect SEO.

Use only standard ASCII
alphanumeric characters in file and directory names.

Don't use generic page names such as `document1.html`.

<a id="filenames--exceptions-for-consistency"></a>

##### Exceptions for consistency

If you're adding to a directory where everything else already uses
underscores, and it's not feasible to change everything to hyphens, it's okay to
use underscores to stay consistent.

For example, if the directory already has `lesson_1.jd`,
`lesson_2.jd`, and `lesson_3.jd`, it's okay to add your
new file as `lesson_4.jd` instead of `lesson-4.jd`.
However, in all other situations, use hyphens.

Recommended: `avoiding-cliches.jd`

Sometimes OK: `avoiding_cliches.jd`

Not recommended: `avoidingcliches.jd`

Not recommended: `avoidingCliches.jd`

Not recommended: `avoiding-clichés.jd`

<a id="filenames--other-exceptions"></a>

##### Other exceptions

It's okay to have some inconsistency in filenames if it can't otherwise be
avoided. For example, sometimes tools that generate reference documentation
produce filenames based on different style requirements or based on the design
and naming conventions of the product or API itself. In those cases, it's okay
to make exceptions for those files.

<a id="filenames--referring-files"></a>

#### Refer to files

The following sections discuss how to reference files.

<a id="filenames--referring-filenames"></a>

##### Refer to filenames

When referring to a specific file, do the following:

- Use [code font](#code-in-text).
- Include the word *file* after the filename. For more information, see
  [Grammatical treatment of code elements](#code-in-text--grammatical-treatment-of-code-elements).
- Use the exact spelling of the filename even if it doesn't follow
  [naming guidelines](#filenames--naming-guidelines).
- If a sample of the file is included on the page, follow the
  [code sample](#code-samples)
  guidelines and precede a code sample with an introductory sentence or paragraph that includes the
  filename.

Recommended: In the following
`build.sh` file, modify the default values for all parameters:

<a id="filenames--file-type-interactions"></a>

##### Refer to file interactions

When interacting with files and file types, don't use the file types as a verb.

Recommended: Extract a zip file.

Not recommended: Unzip a zip file.

<a id="filenames--file-type-names"></a>

##### Refer to file types

When you're discussing a file type, use the formal name of the type, not the filename extension.
(The file type name is often in all caps because many file type names are acronyms
or initialisms.) Do not use the filename extension to refer generically to the
file type.

Recommended: a PNG file

Not recommended: a `.png`
file

Recommended: a Bash file

Not recommended: an `.sh`
file

The following table lists some examples of filename extensions and the
corresponding file type names to use.

| Extension | File type name |
| --- | --- |
| `.adoc` | AsciiDoc file |
| `.csv` | CSV file |
| `.exe` | executable file |
| `.gif` | GIF file |
| `.img` | disk image file |
| `.ipynb` | IPYNB file |
| `.jar` | JAR file |
| `.jpg`, `.jpeg` | JPEG file |
| `.json` | JSON file |
| `.md` | Markdown file |
| `.pdf` | PDF file |
| `.png` | PNG file |
| `.ps` | PowerShell file |
| `.py` | Python file |
| `.sh` | Bash file |
| `.sql` | SQL file |
| `.svg` | SVG file |
| `.tar` | tar file |
| `.tf` | Terraform file |
| `.tiff` | TIFF file |
| `.txt` | text file |
| `.wasm` | Wasm file |
| `.yaml` | YAML file |
| `.zip` | zip file |

---

<a id="trademarks"></a>

### Trademarks

*Source: <https://developers.google.com/style/trademarks>*

Follow any usage guidelines that trademark owners provide.
<a id="trademarks--labeling"></a>

<a id="trademarks--label-trademarked-terms"></a>

#### Label trademarked terms

For trademark marking or attribution in documentation, follow any usage
guidelines provided by the owners of the respective marks.

For more about Google trademarks in particular, see [About our trademarks and
how to use them](https://www.google.com/permissions/trademark/).

<a id="trademarks--adjectives"></a>

<a id="trademarks--use-trademarks-only-as-modifiers"></a>

#### Use trademarks only as modifiers

When you use a trademarked term, always use it to modify a noun, not as a noun
by itself. Don't use a trademark as a verb.

Never form a possessive or a plural from a trademark or change it in any way. For more
information, see [Possessives](#possessives).

Recommended: Another option is to use a Chromebook notebook computer.

Not recommended: Another option is to use a Chromebook.

Not recommended: Chromebook's features rely on an internet connection.

Not recommended: For information about Chromebook computers, google "notebook computers"

For more information about using Google trademarks, see [Rules for proper
usage](https://www.google.com/permissions/trademark/rules.html).
