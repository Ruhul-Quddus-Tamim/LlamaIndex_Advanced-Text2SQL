<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,sqlite" />
  </a>
</p>

---

# Advanced Text2SQL

### Introduction

This project showcases a Text-to-SQL system that can process natural language queries and retrieve information from a structured database. By utilizing LLMs, the system can understand user queries, generate SQL statements, and provide human-readable responses based on the data.

The project uses the ```WikiTableQuestions``` dataset, which contains various CSV files representing different tables. The system reads these CSV files, generates unique table names and summaries, creates a SQLite database, and indexes the tables for efficient query processing.

---

### Features

- Automated Table Name and Summary Generation: Uses LLMs to generate unique and descriptive table names and summaries from CSV files.
- Dynamic SQL Query Generation: Converts natural language queries into SQL statements using LLMs.
- Natural Language Response Synthesis: Generates human-readable responses from SQL query results.
- Efficient Data Retrieval: Utilizes vector indexes for quick retrieval of relevant table rows.
- Modular Code Structure: Organized into modules for better maintainability and readability.

---

### Prerequisites

- Python 3.8 or higher
- OpenAI API Key
- ```wget``` (for data download)

---

### Data Download

Download the WikiTableQuestions dataset using the following commands:

```
wget "https://github.com/ppasupat/WikiTableQuestions/releases/download/v1.0.2/WikiTableQuestions-1.0.2-compact.zip" -O data.zip
```

```
unzip data.zip
```

This will download and extract the dataset into the project directory.

---

### Usage

**1. Set Up Environment Variables**

Make sure to set your OpenAI API key as an environment variable. You can do this by creating a .env file or exporting it directly.

```
export OPENAI_API_KEY='your-openai-api-key'
```

**2. Run the Main Script**
```
python main.py
```

The script will process the CSV files, create the database, index the tables, and execute a sample query.

---

### Workflow Explanation

It operates in two main phases:

**1. Data Preparation and Indexing (Preprocessing Phase)**

**I.   Data Loading:** Reads CSV files into pandas DataFrames, handling data cleaning and column name sanitization.

**II.  Table Summary Generation:** Uses an LLM to generate unique table names and summaries.

**III. Database Creation:** Creates tables in a SQLite database using SQLAlchemy.

**IV.  Indexing:**

        a. Object Index: Indexes table schemas and summaries for quick retrieval.
        
        b. Vector Store Indexes: Indexes table rows to retrieve relevant data during queries.


**2. Query Processing (Runtime Phase)**

**I. User Query Input:** User submits a natural language query.

Text-to-SQL Workflow:

- Table Retrieval: Retrieves relevant tables using the Object Index.
  
- Context Generation: Gathers table schemas and relevant rows for context.
  
- SQL Generation: LLM generates an SQL query from the natural language query and table context.
  
- SQL Execution: Executes the generated SQL query against the SQLite database.
  
- Response Synthesis: LLM synthesizes a natural language response from the SQL results.
  
- Response Delivery: The system presents the final response to the user.

### Diagram

![Text2SQL drawio](https://github.com/user-attachments/assets/2fb868a0-212b-441c-81e4-a550fafdf9fc)


**NOTE:** Any Text-to-SQL application should be aware that executing 
arbitrary SQL queries can be a security risk. It is recommended to
take precautions as needed, such as using restricted roles, read-only
databases, sandboxing, etc.

---

### Acknowledgments

- LlamaIndex (GPT Index)
- OpenAI
- WikiTableQuestions Dataset


