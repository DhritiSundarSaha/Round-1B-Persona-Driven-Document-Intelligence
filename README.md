# Task 1B: Persona-Driven Document Intelligence

This project analyzes a collection of PDFs to find sections most relevant to a specific user persona and their job-to-be-done.

## Methodology
The system uses a two-stage process. First, it uses a copy of our robust structure extraction engine to identify all headings and their content. It then uses a `sentence-transformers` model (`all-MiniLM-L6-v2`) to find the sections whose content is most semantically similar to the user's query. The final refined analysis identifies the most relevant paragraph within those top sections.

## Offline Model Usage
The `sentence-transformers` model is saved to a local `./model` directory, which is included in the Docker image to ensure the container runs completely offline.

## How to Build and Run

### 1. Download Model
Run this command once in the project's root directory to download the model. This will create a `./model` folder.
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('./model')"


**2. Build the Docker Image **
```bash
docker build --platform linux/amd64 -t adobe-task1b .
```

**3. Setup the Test Environment**
Before running the container, you must create input and output folders in the project's root directory.
```bash
mkdir -p input output
```
# Place your test PDF files and a config.json file inside the newly created input folder.

**4. Run the Container**
# The container can be run with the following command. It will read the PDFs from the `input` folder and write the results to the `output` folder.
```bash
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none adobe-task1b

```
