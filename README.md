# PDF Document Search Engine

A comprehensive PDF document search application built in Python that enables advanced full-text search with Boolean operators and document ranking capabilities.

## Overview

This application converts PDF documents into a searchable database, allowing users to query documents using keywords, phrases, and Boolean logic (AND, OR, NOT). The search results are ranked based on word frequency and cross-page references, with support for spell-checking and wildcard searches.

## How It Works

### 1. **PDF Processing** (`parse_txt_files.py`)
- Uses `pdfplumber` to extract text from PDF files
- Converts PDF pages into individual text files for efficient processing
- Extracts page numbers from document headers/footers
- Stores extracted text in the `txts/` directory with folder structure matching PDF names

### 2. **Data Structure: Trie** (`trie.py`)
- Implements a Trie (prefix tree) data structure for each document page
- Stores all words found on a page with their positions
- Enables efficient prefix-based searching and word suggestion features
- Each Trie node tracks:
  - Character representation
  - Child nodes for subsequent characters
  - Word frequency on the page
  - Word positions within the page text

### 3. **Graph-Based Ranking** (`graph.py`)
- Creates a directed graph representing document structure
- Each vertex represents a page and contains its Trie structure
- Edges connect pages that reference each other (e.g., "see page 5")
- Edges store reference counts between pages
- Supports custom queries for vertex retrieval by page number or index

### 4. **Core Search Logic** (`search.py`)

#### Graph Building
- Parses text content with regex patterns to identify page references
- Recognizes patterns like "see page X", "on pages X and Y"
- Creates edges representing page-to-page references
- Caches built graphs as pickle files for performance

#### Query Processing
- Transforms user queries from infix to postfix notation using the Shunting Yard algorithm
- Supports parentheses for grouping expressions
- Handles quotes for phrase searches
- Recognizes Boolean operators: AND, OR, NOT

#### Boolean Operations
- **AND**: Returns intersection of results (pages containing all terms)
- **OR**: Returns union of results (pages containing any term)
- **NOT**: Returns set difference (pages without specified term)
- Phrase searches: Find consecutive words in exact order

#### Ranking Algorithm
- Accumulates word frequency scores for each page
- Propagates scores through the referential graph
- Referenced pages boost the score of referring pages (2x multiplier)
- Results sorted by final computed score

#### Additional Features
- **Spell Checking**: Uses `SpellChecker` library for "did you mean" suggestions
- **Prefix Matching**: Wildcard searches using `*` (e.g., "hello*" finds all words starting with "hello")
- **Text Snippets**: Displays context around found words
- **PDF Export**: Generates PDF documents with highlighted search terms

### 5. **User Interface** (`main_menu.py`)

The main menu provides:
- Interactive PDF selection with automatic conversion handling
- Query input with Boolean operators and phrase support
- Paginated result display (10 results per page)
- Context snippets showing words in their surrounding text
- Spell-check suggestions when results are scarce (<5 results)
- PDF export of top 10 results with highlighted search terms

## Directory Structure

```
Search/
├── code/
│   ├── main_menu.py       # Entry point and user interaction
│   ├── search.py          # Core search algorithms
│   ├── trie.py            # Trie data structure
│   ├── graph.py           # Graph data structure
│   └── parse_txt_files.py # PDF to text conversion
├── pdf/                   # Input PDF files
├── txts/                  # Extracted text files (organized by PDF name)
├── graphs/                # Cached graph objects (serialized as .pkl)
├── results/               # Exported PDF search results
└── README.md
```

## Usage Example

1. Run the program: `python main_menu.py`
2. Enter PDF filename (e.g., `example` for `pdf/example.pdf`)
3. Enter search query with optional Boolean operators:
   - Simple search: `database`
   - Phrase search: `"data structure"`
   - Boolean search: `machine AND learning NOT supervised`
   - Wildcard search: `algo*`
4. Review results with page numbers and text snippets
5. Export results to PDF if desired

## Key Algorithms

- **Shunting Yard Algorithm**: Converts infix Boolean queries to postfix notation
- **PageRank-inspired Scoring**: Considers word frequency and document structure
- **Trie-based Search**: O(m) search complexity where m is query length (independent of document size)
- **Set Operations**: Efficient AND/OR/NOT operations on result sets
