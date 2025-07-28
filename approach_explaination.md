### Persona-Driven Document Intelligence Engine

Our solution provides a highly relevant, persona-driven analysis of document collections by implementing an offline, CPU-based Retrieve-and-Rank pipeline. The system is designed to understand a user's specific role and task, and then intelligently extract and prioritize the most pertinent sections from a set of PDF documents, adhering strictly to all hackathon constraints.

**1. Content Retrieval and Structuring**

The pipeline begins by processing each PDF using the `PyMuPDF` library. Instead of a simple text dump, we perform a structured extraction by analyzing the document's layout. Text blocks are parsed along with their font metadata (size and style). A heuristic-based approach distinguishes potential headings from paragraphs: text with a larger or bolded font and a short word count is classified as a "title", while longer text blocks are treated as "paragraphs". This preserves the document's semantic structure. All extracted text undergoes a cleaning process to remove special characters and normalize whitespace, preparing it for the next stage.

**2. AI-Powered Relevance Ranking**

The core of our intelligence engine is the `all-MiniLM-L6-v2` sentence-transformer model. This model was specifically chosen for its excellent balance of performance, speed on CPU, and its small footprint (~86MB), which is well within the 1GB limit. It enables powerful semantic understanding without requiring an internet connection or GPU.

To rank the content, we first create a rich, contextual query by combining the user's `persona` and `job-to-be-done` from the input. This query is converted into a vector embedding. Concurrently, all extracted paragraphs from the documents are also converted into embeddings. We then calculate the cosine similarity between the query vector and every paragraph vector. This yields a relevance score for each paragraph, indicating how closely it matches the user's specific need.

**3. Final Output Generation**

The paragraphs are sorted in descending order of their relevance score. The final JSON output is constructed as follows:
*   **Sub-section Analysis:** The top 5 most relevant paragraphs, verbatim, are presented to give the user the most critical information directly.
*   **Extracted Section:** We identify the top 5 unique document pages containing the most relevant paragraphs. For each, we select a high-quality "Section title" by filtering the pre-identified titles from that page, rejecting generic headings (e.g., "Introduction"), and titles with disqualifying patterns. This ensures the final output is a concise, relevant, and actionable summary tailored to the user.