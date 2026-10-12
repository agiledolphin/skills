---
title: "Building a Search Assistant for Internal Docs"
author: "Eval Fixture"
tags:
  - "search"
---

# Building a Search Assistant for Internal Docs

Our team spent three months building a search assistant for internal documentation. It answers questions by combining a keyword index with retrieval-augmented generation. This post explains what worked and what did not.

## Why Keyword Search Was Not Enough

Engineers rarely remember the exact title of a page. They describe the problem instead, and keyword search returns nothing useful. *Retrieval-augmented generation* closes this gap by retrieving relevant passages first and then asking a language model to answer from them.

> The best search box is the one people stop noticing.

## Architecture

The system has three parts:

1. An ingestion job that splits each page into passages.
2. A vector database that stores an embedding for every passage.
3. A small API that receives a question and returns an answer with **citations**.

Every response is returned as JSON. Clients can show the answer text and link each citation back to its source page.

```python
# Retrieve the top passages for a question
def retrieve(question, k=5):
    vector = embed(question)  # convert the question into an embedding
    return index.search(vector, k)
```

## Results

| Metric | Before | After |
| --- | --- | --- |
| Questions answered | 41% | 78% |
| Median time to answer | 6 minutes | 40 seconds |

The biggest gain came from better passage splitting, not from a larger model. With retrieval-augmented generation, the quality of what you retrieve matters more than the model you generate with.

![Answer rate over twelve weeks](https://example.com/images/answer-rate.png)

## Further Reading

- [Our ingestion pipeline notes](https://example.com/notes/ingestion)
- ~~The old FAQ page~~ has been retired.
