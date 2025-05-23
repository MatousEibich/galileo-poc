# Data v2 Folder

This folder contains datasets related to the municipality of Horšovský Týn (CZ).

## Datasets

### editors_tyn.json

**Title:** Website Content of Horšovský Týn Municipality  
**Source:** Publicly available data from the official website of Horšovský Týn (CZ)  
**Format:** JSON → converted to CSV  
**Language:** Czech (cs)  

**Fields:**
- `title`: Title of the page
- `url`: Relative URL of the page on the municipality's website
- `language`: Content language (always "cs")
- `validityFrom` / `validityTo`: Content validity timeframe
- `content`: First 500 characters of the HTML-rich page content
- `meta_navigation`: Navigation section where the page is located
- `meta_title`: Meta title of the page
- `meta_description`: Meta description for SEO (if any)
- `meta_visibility`: Boolean flag for whether the page is publicly visible

**Record Count:** 79 records

### messages_tyn.json

**Title:** Website News and Notices of Horšovský Týn Municipality  
**Source:** Extracted from public municipal website of Horšovský Týn (CZ)  
**Format:** JSON → converted to CSV  
**Language:** Czech (cs)  

**Fields:**
- `title`: Headline of the message or announcement
- `url`: Relative web path to the message page
- `language`: Content language (always "cs")
- `validityFrom` / `validityTo`: When the message is considered valid
- `content`: HTML-rich text content of the message body
- `meta_navigation`: Where the message is placed in the navigation
- `meta_title`: Section title
- `meta_description`: Meta description for SEO (if any)
- `meta_visibility`: Boolean flag if the message is publicly visible

**Record Count:** 109 records

### official_boards_tyn.json

**Title:** Official Noticeboard Data from Horšovský Týn Municipality  
**Source:** JSON export from the official municipal website of Horšovský Týn (CZ)  
**Format:** JSON → CSV (truncated content)  
**Language:** Czech (cs)  

**Fields:**
- `title`: Name of the official notice
- `url`: Relative web address of the notice
- `language`: Content language (always "cs")
- `validityFrom` / `validityTo`: Date range for which the notice is valid
- `content`: HTML-rich published content
- `meta_navigation`: Website section where the notice appears
- `meta_title`: Meta title for the section
- `meta_description`: Description for SEO
- `meta_visibility`: Whether the notice is publicly visible

**Record Count:** 103 records 