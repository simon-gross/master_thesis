# Analyzing the Potential of Geographic Knowledge Graphs for Advancing Spatial Capabilities of RAG-based Large Language Model Applications
Master Thesis by Simon Groß

University of Vienna\
Department of Geography and Regional Research\
Spatial Data Science and Geoinformation

Supervisor: Univ.-Prof. Dr. Krzysztof Janowicz


This repository provides the code to reproduce the findings presented in the thesis under the title above.
## Abstract
Large Language Models (LLM) gained immense popularity during the last years. While
exhibiting impressive abilities, also within GIScience, they suffer from so called hallu-
cinations. Retrieval Augmented Generation (RAG) emerged as an approach to miti-
gate these by retrieving factual documents and giving them as context to the LLM.
GraphRAG is a recent variation the contextual information is retrieved from knowl-
edge graphs (KG) instead. This work assesses the potential of GraphRAG for spatially
explicit tasks. Three spatial concepts - topology, directionality and proximity - are an-
alyzed through targeted questions. A GraphRAG system is set up that autonomously
retrieves the answers to the questions from the KG. The question together with the
KGs ontology are given to a LLM with the instructions to generate a GeoSPARQL
query (including functions if applicable) that is executed automatically on a GraphDB
instance containing the needed data. During the experiment, multiple parameters
(model, temperature, etc.) are recorded and their effects on performance are evalu-
ated. This approach outperforms a non-RAG setup by a wide margin. Overall the f1
scores are 0.81 for RAG compared to 0.37 for non-RAG when using the best perform-
ing model-temperature combination. For easier questions the RAG approach reaches
f1 scores > 0.95. This study illustrates the potential of GraphRAG with the presented
retrieval approach for advancing spatial capabilities of LLMs.

## Setup
Instructions for setting up the environment or installing necessary dependencies to run the project. The installation is based on the anaconda package manager

```bash
# Open anaconda prompt
...

# switch to a new folder
cd ./path/to/folder

# Clone the repository
git clone git@github.com:simon-gross/master_thesis.git
cd master_thesis
```

### In the Anaconda Prompt Shell execute
```bash
cd ./path/to/folder/master_thesis
conda create --name spatial_rag_kg --file requirements.txt
conda activate spatial_rag_kg

# to open the notebooks run in the shell:
jupyter-notebook
```



### Set up Environment Variables
Environment Variables should be set up for OpenAI. One for the token to access the API called "OPENAI1" and one for the fine-tuned model string called "FT_MODEL" specified in [Notebook 04](./01_gather_data_and_set_up_geosparql.ipynb).

They will be loaded using 
```python
token = os.environ.get('OPENAI1')
```

### Set up GraphDB
GraphDB is needed to run this experiment. They offer a free version of the database that can be downloaded [here](https://www.ontotext.com/products/graphdb/). After installing:

1. Set up a repository called "geonuts".
2. Import the NUTS.rdf file as specified in the [first Notebook](./01_gather_data_and_set_up_geosparql.ipynb).

### Run the Notebooks
- [01Notebook](./01_gather_data_and_set_up_geosparql.ipynb): This Notebook describes where the data comes from, how it is transformed and how the knowledge graph is set up.
- [02Notebook](./02_define_spatial_tasks.ipynb): This Notebook defines the three spatial concepts that are analyzed in this study (Neighborhood, Directionality and Proximity).
- [03Notebook](./03_ontology.ipynb): This Notebooks sets up the ontology that is used for the RAG experiment.
- [04Notebook](./04_create_fine_tuning_dataset.ipynb): This Notebook describes the creation of the fine-tuning dataset that is used to build the custom mini-fine-tuned model.
- [05Notebook](./05_create_question_catalogue.ipynb): The 18 questions are presented and described.
- [06Notebook](./06_experiment_execution.ipynb): The Notebook executes the actual experiment sending requests to OpenAI and to the GraphDB instance.
- [07Notebook](./07_post_processing.ipynb): The resulting data is post-processed here, calculation quality metrics and preparing data for vizualization.
- [08Notebook](./08_results_non_rag.ipynb): The results for the non-RAG experiment **(RQ1)** are presented.
- [09Notebook](./09_results_RAG.ipynb): The results for the RAG experiment are presented **(RQ2)**.

# Run the demo
Make sure GraphDB is running on Port 7200 with the repository "geonuts" ready and the environment variable OPENAI1 is set.
```bash
cd ./path/to/folder/master_thesis
conda activate spatial_rag_kg
python demo.py
```

# Acknowledgement
OpenAI awarded a grant of 200 $ under the "OpenAI Researcher Access Program" for this thesis which covered all costs for the presented experiments.