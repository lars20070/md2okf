---
type: Website
title: "Google. Google Developer Documentation Style Guide."
description: "Style guide for Google developer documentation"
resource: https://developers.google.com/style
tags: [guide, Google]
timestamp: 2026-08-01T06:28:39Z
---

<!-- markdownlint-disable MD033 -->

<!-- markdownlint-disable-next-line MD025 -->
# Google Developer Documentation Style Guide

*Snapshot of [https://developers.google.com/style](https://developers.google.com/style) generated 2026-08-01.*

## Table of contents

### Introduction

- [About this guide](#style)
- [Highlights](#highlights)
- [What's new](#whats-new)
- [Philosophy of this guide](#philosophy)

### Key resources

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
- Use descriptive link text.
- [Write accessibly](#accessibility).
- [Write for a global audience](#translation).

<a id="highlights--language"></a>

<a id="highlights--language-and-grammar"></a>

#### Language and grammar

- Use second person: "you" rather than
  "we."
- Use active voice: make clear who's performing
  the action.
- [Use standard American spelling](https://developers.google.com/style/spelling) and
  punctuation.
- Put conditions before instructions,
  not after.
- [For usage and spelling of specific words, see
  the word list](https://developers.google.com/style/wordlist).

<a id="highlights--formatting"></a>

<a id="highlights--formattingu002c-punctuationu002c-and-organization"></a>

#### Formatting, punctuation, and organization

- Use sentence case for document
  titles and section headings.
- Use numbered lists for sequences.
- Use bulleted lists for most other lists.
- Use description lists for pairs of related
  pieces of data.
- [Use serial commas](https://developers.google.com/style/commas-serial).
- Put code-related text in code font.
- Put UI elements in bold.
- Use unambiguous date formatting.

<a id="highlights--images"></a>

#### Images

- Provide alt
  text.
- Provide high-resolution or vector
  images when practical.

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
| Added cross-references between guidance about optional procedure steps and guidance about optional headings. | Headings and titles,  Procedures |
| Clarified that much of our guidance about writing inclusive documentation relates to the broader principle of avoiding figurative language, which can be ableist or unnecessarily graphic. Instead, we use literal, precise terms in their primary sense. | [Write inclusive documentation](#inclusive-documentation),  [Voice and tone](#tone),  [Word list](#word-list) |
| Updated guidance about creating custom heading targets, making anchor (`<a>`) elements equally as acceptable as section (`<section>`) elements. | Make headings into link targets |
| Added guidance about ensuring that you contextualize UI elements when you document them outside of a numbered procedure. | UI elements and interaction |
| Added word list entry: *managed instance group (MIG)* | [Word list](#word-list) |

<a id="whats-new--20260407"></a>

<a id="whats-new--april-7u002c-2026"></a>

#### April 7, 2026

| New guidance or change | Page |
| --- | --- |
| Added guidance about avoiding inconsistent end punctuation in list items. | [Lists](#lists) |
| Added *do the following* as a recommended phrase for introducing lists in procedures. | Procedures |
| Clarified that ordered lists are appropriate for any list where sequence is significant. Added guidance about ensuring that it's clear whether the items in an unordered list are required or optional. | [Lists](#lists) |
| Added guidance that if you must refer to a step number, use the numeral. | Numbers |
| Added guidance to use italics sparingly, and consolidated italics guidance into a new page. | Use italics to discuss terms,  [Text-formatting summary](#text-formatting) |
| Added guidance recommending the terms *selected* and *not selected* to refer to the state of a checkbox. | UI elements and interaction |
| Changed guidance to recommend using code font for IP addresses and port numbers. Added package names to the list of items to place in code font. | Code in text |
| Updated UI elements guidance with expanded definitions for *pane*, *panel*, and *section*. Added guidance about how to identify difficult-to-find UI elements without using directional language. | UI elements and interaction |
| Added `.wasm` (Wasm file) to the table of file extensions and corresponding file type names. | Filenames and file types |
| Reorganized and extended guidance about formatting abbreviation introductions. | Abbreviations,  [Text-formatting summary](#text-formatting) |
| Consolidated pluralization guidance into a new page, including guidance about abbreviations, product names, and code elements. | Pluralization |
| Restructured guidance about writing for a global audience to make it easier to navigate. | [Write for a global audience](#translation) |
| Expanded guidance about exclamation marks to clarify that we avoid them except in rare cases. | Periods and other end punctuation,  [Voice and tone](#tone) |
| Created a page about how to format common mathematical notation. | Mathematical notation,  Numbers,  [Text-formatting summary](#text-formatting),  Units of measurement |
| Changed guidance for temperatures to recommend a nonbreaking space between a numeral and the degree symbol instead of between the degree symbol and the temperature scale. | Units of measurement |
| Added guidance about marking headings as optional. Restructured headings guidance to make it easier to navigate. | Headings and titles |
| Added an entry for *AI*, specifying that it rarely needs to be spelled out. | [Word list](#word-list),  Abbreviations |
| Clarified that the word *can* can be used to convey both permission and ability. | [Word list](#word-list) |
| Clarified that when we mark a term "Use with caution" in the word list, we recommend following our standard jargon guidance. | [Word list](#word-list) |
| Clarified how we prefer to distinguish between a *page* (the whole web page) and a *document* (the text on a page that explains a product, feature, or service). | [Word list](#word-list) |
| Revised the entry for *style sheet* to also allow for *stylesheet*, prioritizing consistency in a document. | [Word list](#word-list) |
| Added explanations to several existing word list items regarding compound word usage: *clickthrough*, *hardcode*, *high availability*, *load balancing*, *plugin*, *third-party*, *time zone*, and *wake lock*. | [Word list](#word-list) |
| Expanded the entry for *first class*, *first-class*, *first-class citizen*, providing new recommended alternatives with examples. | [Word list](#word-list),  [Write inclusive documentation](#inclusive-documentation) |
| Expanded or added entries for *like*, *such as*, *for example*, and *for instance*. Made corresponding updates to the page about writing examples. | [Word list](#word-list),  Format examples |
| Added guidance to the *virtual machine (VM) instance* entry regarding Compute Engine instances. | [Word list](#word-list) |

<a id="whats-new--20250508"></a>

<a id="whats-new--may-8u002c-2025"></a>

#### May 8, 2025

| New guidance or change | Page |
| --- | --- |
| Removed outdated language that indicated that a list of options is treated differently than other unordered lists. | [Lists](#lists) |
| Added a page about writing prescriptive documentation. | [Prescriptive documentation](#prescriptive-documentation), Word list |
| Removed guidance that said to include empty parentheses after method names. | Code in text |
| Changed footnotes guidance to recommend using numbers instead of symbols. | Footnotes |
| Simplified contractions guidance, removing excess explanations and examples. | Contractions |
| Added examples to guidance about introducing sections of a document. | Headings and titles |
| Added an example service account ID. | [Example domains and names](#examples) |
| Simplified and clarified guidance about articles, including using articles before abbreviations and product names. | Abbreviations, Articles (a, an, the), [Product names](#product-names), [Word list](#word-list) |
| Included a general explanation of why we don't document future features. | [Document future features](#future) |
| Revised guidance to recommend using an abbreviation in a title or heading only if the abbreviation is the more commonly known version of the word. | Headings and titles |
| Added a suggestion that when you use an imperative in running text, consider whether to write a procedure instead. | Second person and first person |
| Generalized existing guidance on what to do when jargon is part of a command or code sample. | [Jargon](#jargon) |
| Consolidated guidance about cross-references and linking into one page. | Cross-references and linking |
| Added some specific reasons why we avoid directional language when orienting the reader to information on a page. | [Write accessible documentation](#accessibility) |
| Clarified that spacing around icons is a judgment call based on readability. | UI elements and interaction |
| Removed an example phone number. | [Example domains and names](#examples) |
| Removed the word list entry for *property* because its usage heavily depends on the technical context. | [Word list](#word-list) |
| New word list entries: *choose*, *confidential*, *sensitive*, *image*, *Fast Healthcare Interoperability Resources (FHIR)* | [Word list](#word-list) |

<a id="whats-new--20250117"></a>

<a id="whats-new--january-17u002c-2025"></a>

#### January 17, 2025

| New guidance or change | Page |
| --- | --- |
| Consolidated spelling guidance into the introduction to the word list. Extended guidance about how to use the preferred dictionary to determine which spelling to use for a word with multiple spellings. | [Word list](#word-list) |
| Generalized guidance about when to use spaces or tabs for indentation in code samples. | Code samples |
| Changed guidance for formatting telephone numbers to recommend using dashes instead of parentheses to set the area code off from the rest of the number. | Format phone numbers |
| Extended and clarified recommendation to avoid the abbreviations *i.e.*, *e.g.*, and *etc.* in most cases. | Abbreviations, Comma-separated lists |

<a id="whats-new--20241029"></a>

<a id="whats-new--october-29u002c-2024"></a>

#### October 29, 2024

| New guidance or change | Page |
| --- | --- |
| Consolidated and expanded guidance about hyphens and closed compounds. | Hyphens |
| Added *hotspot* to the word list. | Word list |

<a id="whats-new--20240815"></a>

<a id="whats-new--august-15u002c-2024"></a>

#### August 15, 2024

| New guidance or change | Page |
| --- | --- |
| Added guidance for distinguishing between binary and decimal units, such as gibibytes (GiB) and gigabytes (GB). Also corrected abbreviation of *kilobyte* to *kB*. | Decimal and binary units |
| Expanded guidance for referring to figures and other images in text. Clarified that figure numbers are not required. | Figure captions |
| Added word list entries: *curl*, *whitepaper*, *long-running operation* | [Word list](#word-list) |
| Updated word list entries: *ingest*, *execute*, *content type*, *media type*, *MIME* | [Word list](#word-list) |

<a id="whats-new--20240516"></a>

<a id="whats-new--may-16u002c-2024"></a>

#### May 16, 2024

| New guidance or change | Page |
| --- | --- |
| Added the term *generative AI*. | Word list |
| Added the term *rehost*. Redirected the definition for *lift and shift* to *rehost*. | Word list |
| Clarified that the style guide shows examples of how placeholders render but doesn't explain how to implement this visual styling. | Format placeholders |
| Added an example to the guidance showing how to use site-root-relative URLs to link to another page on the same server. | [Cross-references](https://developers.google.com/style/cross-references#same-server) |
| Clarified guidance about how to format anchor text. | Make headings into link targets |

<a id="whats-new--20240321"></a>

<a id="whats-new--march-21u002c-2024"></a>

#### March 21, 2024

| New guidance or change | Page |
| --- | --- |
| Expanded guidance about avoidance of the term *drop-down*. | Word list |
| Added examples to guidance about writing documentation that focuses on the present state of the software. | [Timeless documentation](#timeless-documentation) |
| Added recommendation to use a more precise term than *workload* when possible, or to define what the term means in the specific context.  Added related guidance about avoiding ambiguous or overloaded words like *workload*, *solution*, and *support*, or defining them in each context. | Word list,  [Jargon](#jargon) |
| Aligned guidance with XML and HTML specifications to recommend against the use of angle brackets as part of an element name, but instead to only use angle brackets as part of a tag. | Code in text |

<a id="whats-new--20240122"></a>

<a id="whats-new--january-22u002c-2024"></a>

#### January 22, 2024

| New guidance or change | Page |
| --- | --- |
| Cleaned up word list by removing entries that only provided hyphenation, [spelling](https://developers.google.com/style/spelling), or abbreviation guidance that followed directly from our general guidance. | [Word list](https://developers.google.com/style/style/word-list) |
| Consolidated and clarified guidance regarding alt text, figure captions, and figure descriptions. | [Diagrams, figures, and other images](#images)  [Write accessible documentation](#accessibility) |
| Added recommendation to avoid linking to other document sets from navigation controls such as a table of contents. | [Links to other sites](https://developers.google.com/style/links-external) |
| Clarified guidance about avoiding words such as *above* and *below* in references to documentation and user interfaces for accessibility reasons, and provided example of appropriate non-directional usage. | Word list |
| Removed prohibition against hyphenation of the phrase *open source*, so this term now follows our general guidance for hyphenation, which allows for hyphenation of an adjectival phrase to add clarity and remove ambiguity. | [Word list](https://developers.google.com/style/word-list#open-source) |
| Changed guidance for indicating the omission of code from an instructional code snippet to recommend the use of an explanatory comment instead of a mere ellipsis. | Code samples |

<a id="whats-new--20231108"></a>

<a id="whats-new--november-8u002c-2023"></a>

#### November 8, 2023

| New guidance or change | Page |
| --- | --- |
| Changed guidance regarding run-in headings in description lists to recommend that the punctuation (such as a colon) is not formatted as bold. Making the punctuation bold caused the punctuation to seem to be part of the heading string, which caused confusion in cases such as UI labels. | Lists |
| Removed the recommendation to use a special *external* icon (indicated by `class="external"`) for links. Readers and writers have expressed confusion about the meaning and usage of this icon. We strengthened guidance about using other, explicit means to inform the reader about the destination and behavior of a link. | [Link text](https://developers.google.com/style/link-text#write-link-text) |

<a id="whats-new--20231024"></a>

<a id="whats-new--october-24u002c-2023"></a>

#### October 24, 2023

| New guidance or change | Page |
| --- | --- |
| Removed page about custom font styling, which only said to use styles defined in the style sheet for the website. Redirected link to page about HTML formatting and semantic tagging. | [HTML and semantic tagging](https://developers.google.com/style/fonts) |
| Added word-list entry for *then* and expanded entry for *if* to recommend the use of the optional helper word *then* in many cases in which it might be omitted in casual usage. | Word list |
| Simplified and unified guidance for *jank* and *janky* to recommend that these terms only be used for specific graphics issues. | Word list |
| Strengthened guidance against the use of *and/or* except in cases where space is limited. | Slashes |

<a id="whats-new--20230929"></a>

<a id="whats-new--september-29u002c-2023"></a>

#### September 29, 2023

| New guidance or change | Page |
| --- | --- |
| Added several examples of when and how to use quotation marks. | Quotation marks |
| Added explanation of guidance against anthropomorphism. | Anthropomorphism |
| Added guidance about using a hyphen with the prefix *non* before hyphenated compounds. | Hyphens |

<a id="whats-new--20230824"></a>

<a id="whats-new--august-24u002c-2023"></a>

#### August 24, 2023

| New guidance or change | Page |
| --- | --- |
| Added link buttons to each entry in the word list to make deep-linking to individual entries easier. | [Word list](#word-list) |
| Extended guidance about example names to recommend using an initial to represent a person's surname. | Example person surnames |
| Clarified guidance about when to use present tense and when to use future tense. | Present tense |
| Extended link text guidance to include an example for `mailto` links. | [Link text](https://developers.google.com/style/link-text) |

<a id="whats-new--20230726"></a>

<a id="whats-new--july-26u002c-2023"></a>

#### July 26, 2023

| New guidance or change | Page |
| --- | --- |
| Added link to [Google API guidelines](https://google.aip.dev/192) for information about code comments. | API reference code comments |
| Revised guidance for the word *toggle* to recommend against use as a verb. | UI elements and interaction |
| Extended and clarified guidance for names for directories and files. | Filenames and file types |
| Added explanation for why to use code format for code items. | Code in text |

<a id="whats-new--20230615"></a>

<a id="whats-new--june-15u002c-2023"></a>

#### June 15, 2023

| New guidance or change | Page |
| --- | --- |
| Consolidated guidance about periods and end punctuation. Also removed standalone pages about exclamation points and about spacing after periods. | Periods and other end punctuation |
| Revised guidance about hyphens to suggest a lookup strategy, categorize uses, and note exceptions. | Hyphens |
| Created firmer guidance about punctuation in lists for run-in headings and at the end of list items. | [Lists](#lists) |
| Strengthened capitalization guidance: when *not* to use capitalization, and how to use capitalization with product names. | Capitalization, [Product names](#product-names) |
| Added guidance about using end punctuation when documenting a command-line option or argument. | Document command-line syntax |
| Improved description and examples for using first-person pronouns (*we*, *our*). | Second person and first person |
| Updated word list entries: *etc.*, *OK*, *user*, *we*, *you* | [Word list](#word-list) |

<a id="whats-new--20230509"></a>

<a id="whats-new--may-9u002c-2023"></a>

#### May 9, 2023

| New guidance or change | Page |
| --- | --- |
| Softened guidance regarding the choice between the pronouns *who* and *that*. | Pronouns |
| Added *web interface* as an alternative to *console* and *UI* in general references to a browser-based interface. | Word list |
| Clarified the purpose of the page about phone number formats. | Format phone numbers in text |

<a id="whats-new--20230331"></a>

<a id="whats-new--march-31u002c-2023"></a>

#### March 31, 2023

| New guidance or change | Page |
| --- | --- |
| Expanded and clarified guidance about using trademarks only as modifiers. This guidance emphasizes that you should never modify a trademark, such as by creating a possessive or plural form. | Use trademarks only as modifiers |
| Strengthened guidance against shortening product names to anything other than an approved alternative name. | [Google product names](#product-names--shortening) |
| Expanded guidance about using ARIA labels in text that describes icons in graphical user interfaces. This improves accessibility and increases consistency in terminology used to refer to visual elements in text. | Buttons and icons, [Accessibility](#accessibility) |
| New word list entry: *toolkit* | [Word list](#word-list) |

<a id="whats-new--20230213"></a>

<a id="whats-new--february-13u002c-2023"></a>

#### February 13, 2023

| New guidance or change | Page |
| --- | --- |
| Added a page about paragraph structure, which provides guidance about recommended paragraph length and order of information. | Paragraph structure |
| Expanded accessibility guidance to say that a document should convey its information when you use it without images or animation. | [Write accessible documentation](#accessibility) |
| Clarified that letter keys should be represented with uppercase letters. | Press and type keyboard keys |
| Added *existing* to list of examples of potentially problematic words in timeless documentation. | [Timeless documentation](#timeless-documentation) |
| Recommended using an empty `alt` attribute for icons that include a text label. | Buttons and icons |
| Strengthened and clarified guidance about avoiding culturally specific references and about using simple and consistent language. | [Voice and tone](#tone) |
| Created section about items that are sometimes—but not always—formatted in code font, such as email addresses. | Items that are sometimes in code font |
| Added information about example internationalized domain names. | Example domain names |
| Expanded guidance about choosing example email addresses. | Example email addresses |
| Expanded guidance about using second-person *you* to refer to the reader of a document and, generally, using third-person *user* to refer to the intended user of the software that the reader is developing. | Second person |

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
| To emphasize a negative, use `<em>`not`</em>`. | Contractions |

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
| Added guidance about how to document optional arguments for commands.  Special characters that indicate optional and mutually exclusive arguments in commands—such as brackets, braces, and pipes—break commands if the user doesn't edit them first. The new guidance offers several approaches for avoiding these problems. | Code in text, Code samples, Document command-line syntax |
| Clarified that contractions are recommended in general, but not required in all cases. | Contractions |

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
| Added guidance to multiple pages about ways to make documentation more inclusive for readers who have a variety of cognitive patterns. | [Write accessible documentation](#accessibility), Cross-references, Numbers, Procedures |

<a id="whats-new--20220912"></a>

<a id="whats-new--september-12u002c-2022"></a>

#### September 12, 2022

| New guidance or change | Page |
| --- | --- |
| Don't present new information in tables through images or symbols alone. | [Tables](#tables) |
| Clarified guidance about using footnotes in tables. | [Tables](#tables) |
| Added instructions for how to look up a UI element's `aria-label` attribute. | UI elements and interaction |

<a id="whats-new--20220905"></a>

<a id="whats-new--september-5u002c-2022"></a>

#### September 5, 2022

| New guidance or change | Page |
| --- | --- |
| Strengthened recommendation to avoid using semicolons where possible, and removed basic information about semicolons.  Our [accessibility guidance](#accessibility) recommends against using semicolons where possible, because screen readers may not clearly indicate them. So we changed our semicolon guidance to be more in line with our accessibility guidance. | Semicolons |
| Expanded and clarified guidance about what to put in code font. | Code in text |

<a id="whats-new--20220829"></a>

<a id="whats-new--august-29u002c-2022"></a>

#### August 29, 2022

| New guidance or change | Page |
| --- | --- |
| Changed and clarified recommended phrasing for describing boolean parameters in reference docs. | API reference code comments |
| Expanded and clarified explanation of why we use straight quotation marks and apostrophes. | Quotation marks |
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
| Write *a SQL* rather than *an SQL*.  Both are in use, but *a SQL* is significantly more common. | Articles (a, an, the) |
| Added information about our distinction between *don't use* and *avoid*. | [Word list](#word-list) |
| New word list entries: *nonce*, *SQL* | [Word list](#word-list) |

<a id="whats-new--20220801"></a>

<a id="whats-new--august-1u002c-2022"></a>

#### August 1, 2022

| New guidance or change | Page |
| --- | --- |
| Expanded guidance about *mobile* and related terms. | [Word list](#word-list) |
| It's OK to use *below* in set phrases such as *below (the) average*. | [Word list](#word-list) |
| Expanded our information about serial commas. | Commas |
| To refer to a file with the `.tiff` extension, use the phrase *TIFF file*. | Filenames and file types |
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
| Revised and expanded guidance about how to form possessives. | Possessives |
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
| Offset footnote symbols using superscript. | Footnotes |
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
| Expanded guidance about when to use the various notice types. | Notes, cautions, warnings, and other notices |
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
| In code samples, indicate omitted code using three dots and no spaces (`...`) | Code samples |
| New word list entries: *+* (appended to numbers in text) | [Word list](#word-list) |

<a id="whats-new--20220404"></a>

<a id="whats-new--april-4u002c-2022"></a>

#### April 4, 2022

| New guidance or change | Page |
| --- | --- |
| Removed guidance about using lettered lists for mutually exclusive options.  The semantic distinction that we were making isn't in wide use, and lettered lists aren't supported in standard Markdown, so we no longer recommend using lettered lists. | [Lists](#lists) |
| Clarified recommendation about how to italicize in Markdown. | [Text-formatting summary](#text-formatting) |
| Changed guidance about *dead-letter queue* and *hold the pointer over*. | [Word list](#word-list) |
| New word list entry: *break-glass* | Word list |

<a id="whats-new--20220328"></a>

<a id="whats-new--march-28u002c-2022"></a>

#### March 28, 2022

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about using an introductory phrase before the output of a command. | Document command-line syntax |
| New word list entry: *Unicode* | Word list |

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
| In general, don't use a single *x* or a series of *x*'s as placeholders; instead, use a more informative placeholder. | Formatting placeholders |
| New word list entry: *GBps* | [Word list](#word-list) |

<a id="whats-new--20220131"></a>

<a id="whats-new--january-31u002c-2022"></a>

#### January 31, 2022

| New guidance or change | Page |
| --- | --- |
| Avoid repeating the exact page title as a heading on the page. | Headings and titles |
| Expanded guidance about *runtime* and *run time*. | [Word list](#word-list) |
| Added *.adoc* and *.md* to the list of examples of filename extensions. | Filenames and file types |

<a id="whats-new--20220124"></a>

<a id="whats-new--january-24u002c-2022"></a>

#### January 24, 2022

| New guidance or change | Page |
| --- | --- |
| Clarified guidance about video formats.  The main reason to avoid using animated GIF is that it's resource-inefficient. | [Figures and other images](#images) |
| Clarified guidance about changing an existing custom anchor for a heading. | Making headings into link targets |

<a id="whats-new--20220118"></a>

<a id="whats-new--january-18u002c-2022"></a>

#### January 18, 2022

| New guidance or change | Page |
| --- | --- |
| For animations and videos, use a compressed format (such as MP4), not animated GIF. | [Figures and other images](#images) |
| Don't use *email* as a verb. | [Word list](#word-list) |
| New word list entry: *healthcare* | [Word list](#word-list) |

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
>
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
- Hyphens
- Capitalization

As always, it's fine to deviate from our guidance if that serves your readers
better. For more information, see [Break the rules](#style--rules).

<a id="word-list--word-list"></a>

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
UI elements and interaction.

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
Capitalization.

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
Product, feature, and company names.

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

For more information about using articles, see Articles.

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
Visual formatting.

<a id="text-formatting--bold"></a>

**Bold**
    Use bold formatting, `<b>` or `**`, only for
    UI elements and
    run-in headings, including at the beginning of
    notices.
    Although a double underscore, `__`, can also indicate bold styling in Markdown, it
    can be difficult to distinguish in a text editor. It's best to use the double asterisk for bold in
    Markdown.
<a id="text-formatting--italic"></a>

**Italic**
    In general, use italics sparingly.
    When you're discussing or introducing terms, such as when defining terms or using
    *words as words*, use italics formatting, `<i>` or `_`. For more
    information, see
    Use italics to discuss terms
    and
    Format abbreviation introductions.
    When you need to add emphasis to indicate importance, use italics, not bold or underline. But
    usually, your words can carry the emphasis without adding italics. To indicate
    semantic emphasis in HTML, use the `em` element,
    which renders as italics in most contexts. To indicate emphasis in Markdown, use underscores
    (`_`), which render as italics; you can't do semantic tagging in Markdown.
    Although an asterisk, `*`, can also indicate italics in Markdown, we recommend
    underscores to make it easier for humans to distinguish italics from bold in the Markdown file.
    Italicize titles of books, movies, web series, and other full-length works, unless they're part
    of a link. For more information, see
    Cross-references and linking.
    Italicize mathematical variables—for example, *x* + *y* = 3.
    Don't italicize mathematical operators such as the plus sign. For more information about
    formatting mathematical notation, see
    Mathematical notation.
    Italicize version variables—for example, version 1.4.*x*.
<a id="text-formatting--underline"></a>

**Underline**
    Reserve underlining for link text. For more information, see
    [Style link text](https://developers.google.com/style/cross-references#style-link-text).
<a id="text-formatting--code-font"></a>

**Code font**
    Use `<code>` in HTML or `` ` `` in Markdown to apply a monospace font
    and other styling to code in text, inline code, and user
    input.
    Use code blocks, `<pre>` or `` \`\`\` ``, for
    code samples or other blocks of code.
    Do not override or modify font styles inline.
    Use code font to mark up code, such as filenames, class names, method names, HTTP status codes,
    console output, and placeholders. For more information, see
    Some specific items to put
    in code font.
<a id="text-formatting--capitalization"></a>

**Capitalization**
    Use American English style for
    general capitalization.
    Use sentence case in all headings,
    titles, and navigation.
    Use all-capitals for placeholders.
<a id="text-formatting--quotation-marks"></a>

**Quotation marks**
    In general, use American English style when punctuating
    quotations.
    For titles of shorter works—such as articles or episodes in a web series—put titles in quotation
    marks, unless they're part of a link.
<a id="text-formatting--font-style"></a>

**Font type, size, and color**
    Do not override global styles for [font type, size, or
    color](https://developers.google.com/style/fonts).
    Use semantic HTML or Markdown to
    control the style of text on a page—for example, code tags in HTML (`<code>`)
    or backticks in Markdown (`` ` ``)—instead of manually styling text with a monospace
    font.
<a id="text-formatting--other-punctuation"></a>

**Other punctuation conventions**
    Don't use ampersands (&) as conjunctions or
    shorthand for *and*. Use *and* instead. That includes headings and navigation.
    **Exception**: It's okay to use *&* in cases where you need to refer to a UI
    element or the name of a menu that uses *&*.
    Put quotation marks and end punctuation outside of link text. For more information, see
    the [Punctuation around link text](https://developers.google.com/style/cross-references#punctuation)
    and [Quotation marks and italics](https://developers.google.com/style/cross-references#quotation-marks-italics)
    sections of the "Cross-references and linking" page.

<a id="text-formatting--more-resources"></a>

#### More resources

- Mathematical notation

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
- In HTML, use semantic
  tagging. For example, use the `em` element only to
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
  capitalization guidelines.
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
  paragraphs,
  create
  headings,
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

For more information and examples, see Headings and titles.

<a id="accessibility--links"></a>

#### Links

- Use meaningful link text.
  Links should make sense when read out of context.
- Don't use *click here* or *read this document*. Some people who use screen readers
  jump from link to link to scan a page and need to understand what a link contains.
- Use *see* to refer to links and cross-references. For more information, see
  see.
- When a link does anything that the reader might not expect, such as downloading a file,
  opening in a new tab, or jumping to another section on the same page, explain that behavior when
  you link. For more information, see
  Explain unexpected link behavior.
- When possible, avoid adjacent links. Instead, put a character in between to separate them.

<a id="accessibility--lists"></a>

#### Lists

- In a
  procedure,
  make each instruction a
  [list item](#lists).
- Use lists to make it easier for the reader to follow the steps.

<a id="accessibility--images"></a>

#### Images

- For every image, provide an alt attribute. For alt attributes that contain
  alt text, use alt text that adequately summarizes the
  intent of each image. If the image is purely decorative, use empty alt text.
- Don't present new information in images. Always provide an equivalent text explanation with
  the image.
- Don't repeat images unless absolutely necessary.
- Don't use images of text, code samples, or terminal output. Use actual text.
- Use SVG instead of PNG if available. SVGs stay sharp when you zoom in on the image.

For more information, see
Text associated with images.

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
  about using icons, see the Buttons and icons section
  of the "UI elements and interaction" page.

<a id="accessibility--ui-navigation"></a>

#### UI navigation

When you use angle brackets (`>`) to document menu paths, add an
[`aria-label` attribute](https://www.w3.org/TR/WCAG20-TECHS/ARIA14.html)
to help screen readers interpret the brackets as "and then" instead of as
"greater than" or "keyboard arrow right". For more information and examples, see
Menu bar.

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
  List or table.
- Don't present new information in tables through images or symbols alone; always provide a
  descriptive `alt` attribute for the image or symbol. For more information, see
  Alt text.

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

  If a UI element is hard to find,
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

See also Present tense and
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

- Use present tense and avoid complex or uncommon verb forms.
- Use active voice. The subject of the sentence is the person or thing performing the action.
  With passive voice, it's often hard for readers to figure out who's supposed to do something.
  For more information, see Active voice.

<a id="translation--use-words-in-their-primary-sense"></a>

##### Use words in their primary sense

- Don't use the same word to mean different things. In particular, avoid using the same word as
  both a noun and a verb in close proximity. For examples of words that have multiple meanings, see the word
  list entries for once, while, as, and since.
- Avoid directional language (for example, *above* or *below*) in procedural
  documentation. For more information, see
  UI elements and interaction.

<a id="translation--use-helper-words-and-optional-words"></a>

##### Use helper words and optional words

- Use qualifying nouns for technical keywords. For example, when referring to a file called
  `example.yaml`, call it the *`example.yaml` file* and not
  *`example.yaml`* by itself. For more information, see
  Grammatical treatment of code elements.
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

  See also Optional pronouns.
- Don't omit relative pronouns. To provide clarity and to avoid ambiguity, use relative
  pronouns such as *that* and *which*. For more information, see
  Relative pronouns.

  Recommended: You can programmatically update
  the rules that you previously defined.

  Not recommended: You can programmatically
  update the rules you previously defined.

<a id="translation--clarify-abbreviations-and-pronouns"></a>

##### Clarify abbreviations and pronouns

- Define abbreviations. Abbreviations can be confusing out of context, and they don't translate
  well. Spell things out whenever possible, at least the first time that you use
  a given term. For more information, see Abbreviations.
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
names, and don't use uncommon contractions. For more information, see Possessives, Pluralization, and Contractions.

<a id="translation--address-users-and-their-needs-directly"></a>

#### Address users and their needs directly

Address the user and their needs directly and avoid providing unnecessary information.

- Address the reader directly. Use *you*, instead of *the user* or *they*, unless
  you're referring to someone who uses the software that the reader is developing. For more
  information, see Second person and first person.
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
  tasks. For examples, read about introducing links,
  introducing output, and
  [introducing code samples](https://developers.google.com/style/code-samples#introductions).
- Use standard English word order. Sentences follow the *subject + verb + object* order.
- Try to keep the main subject and verb as close to the beginning of the sentence as possible.
- Use the conditional clause first. If you want to tell the audience to do something in a
  particular circumstance, mention the circumstance before you provide the instruction. For more
  information, see Sentence structure.
- Make list items consistent. Make list items parallel in structure. Be consistent in your
  capitalization and punctuation. For more information, see [Lists](#lists).

<a id="translation--use-consistent-text-formatting"></a>

##### Use consistent text formatting

- Use consistent typographic formats. Use bold and italics consistently. Don't switch from
  using italics for emphasis to underlining. For more information, see
  [Text-formatting summary](#text-formatting).
- Use consistent capitalization. For more information, see
  Capitalization.

<a id="translation--be-inclusive"></a>

#### Be inclusive

You're not writing for your culture. Write with inclusivity in mind. For more information, see [Writing inclusive documentation](#inclusive-documentation).

- Write dates and times in unambiguous and clear ways.
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
  For more information, see Expressing divisions of the
  year.

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
pronouns
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
| Replace the placeholder in this example with the appropriate value. | Replace the dummy variable in this example with the appropriate value. |

<a id="inclusive-documentation--graphic-language"></a>

##### <a id="inclusive-documentation--violent-language"></a>Avoid graphic or metaphorical language

Avoid unnecessarily graphic or metaphorical language, when you can use a more
precise term.

For example, instead of
*STONITH*, use specific terms to
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
list entries for terminate and
execute.

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

- Follow our gender-neutral
  pronoun guidance.
- Avoid being too culturally specific to the US. Be mindful when referring
  to specific holidays (see also the word list entry for *the holidays*), cultural practices,
  sports, and figures of speech.
- In examples,
  choose a diverse set of names
  to help reflect our global audience. For guidelines about fictional people,
  see
  Further notes about example people.
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
example, avoid terms such as blacklist and
native feature, and don't use terms like
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

```yaml
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

```sql
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
  see.
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
  (formatted as code), and make it clear
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
  Optional arguments in click-to-copy commands.

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
  Active voice.

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

- See also can, could,
  may, might,
  must, and would in the
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
- Exclamation marks. In general, avoid exclamation points. See Specific guidance on exclamation points.
- Wackiness, zaniness, and goofiness.
- Phrasing that denigrates or insults any group of people.
- Phrasing in terms of *let's* do something.
- Using phrases like *simply*, *It's that simple*, *It's easy*, or *quickly* in a
  procedure.
- Internet slang, or other internet
  abbreviations such as *tl;dr* or
  *ymmv*.

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
