# 📄 Persona-Driven Document Intelligence Engine

An **offline-first document analysis engine** designed to tackle information overload. It acts as an intelligent research assistant by analyzing a collection of PDF documents, understanding a user's specific **Persona** and **Job-to-be-Done**, and surfacing the most relevant sections and paragraphs.

> ✅ Entirely self-contained, CPU-optimized, and packaged in Docker for offline performance—perfect for hackathon constraints.

---

## ✨ Core Features

- **🧠 Intelligent Ranking**: Uses a state-of-the-art Sentence-Transformer model to semantically rank document content by relevance to the user’s intent.
- **📑 Structured Extraction**: Parses PDFs to identify headings and paragraphs by analyzing layout, font styles, and sizes—going far beyond simple text dumps.
- **🛡️ Offline-First & Secure**: Fully functional without internet access. All models and dependencies are pre-packaged inside the Docker image.
- **⚡ Lightweight & Efficient**: Runs smoothly on standard CPU hardware with a low memory footprint.

---

## 🚀 Why This Approach Excels

### 🖹 High-Performance PDF Parsing — *PyMuPDF*
We chose **PyMuPDF** for its ability to extract structured data with speed and precision. By analyzing font styles and sizes, we can distinguish section titles from paragraphs—something basic text extraction libraries can't do.

### 🔍 Efficient Semantic Search — *all-MiniLM-L6-v2*
This ~86MB Sentence-Transformer model offers a perfect trade-off between **accuracy, size, and speed**. It enables the system to **understand context and meaning**, not just keywords—while being lightweight enough for CPU-only environments.

### 📦 Guaranteed Portability — *Docker*
The entire application is containerized. Using `--network none`, we prove that the app works completely offline, adhering to strict data/privacy and hackathon guidelines. This also ensures consistent results across different environments.

---

## ⚙️ Setup & Usage

### 🔧 Prerequisites

- Git
- Docker Desktop

---

### 📁 1. Local Setup

Clone the repository and create the required folder structure:

```bash
# Clone the repository
git clone <your-repo-url>
cd persona-driven-document-intelligence-engine
```

Prepare the input directory:

```
persona-driven-document-intelligence-engine/
├── input/
│   ├── input.json
│   └── PDFs/
│       ├── doc1.pdf
│       └── doc2.pdf
└── ... (other project files)
```

Also, create an empty `output/` folder at the root for storing the results.

---

### 🏗️ 2. Build Docker Image

From the root directory, build the Docker image:

```bash
docker build -t doc-intel-engine .
```

---

### ▶️ 3. Run the Engine

#### For macOS / Linux:

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none doc-intel-engine
```

#### For Windows (PowerShell):

```bash
docker run --rm -v ${pwd}/input:/app/input -v ${pwd}/output:/app/output --network none doc-intel-engine
```

After execution, the results will be saved as `output/output.json`.

---

## 🛠️ Tech Stack

- **Backend**: Python  
- **AI/ML**: PyTorch, Sentence-Transformers (`all-MiniLM-L6-v2`)  
- **PDF Parsing**: PyMuPDF  
- **Containerization**: Docker  

---

## 📁 Project Structure

```
.
├── Dockerfile
├── README.md
├── approach_explanation.md
├── models/
│   └── all-MiniLM-L6-v2/
├── requirements.txt
└── src/
    ├── main.py
    ├── pdf_processor.py
    └── relevance_engine.py
```
