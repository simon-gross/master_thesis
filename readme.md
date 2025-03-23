## Abstract
...

## Setup
Instructions for setting up the environment or installing necessary dependencies to run the project. The installation is base on the anaconda package manager

```bash
# Open anaconda prompt
...

# switch to a new folder
cd ./path/to/folder

# Create new conda environment with the provided dependencies
### conda create -n "spatial_rag_kg" 
conda activate spatial_rag_kg

# Clone the repository
git clone git@github.com:simon-gross/master_thesis.git
cd master_thesis

# Create conda environment

# Install dependencies
pip install -r requirements.txt
```

## Set up Environment Variables
Environment Variables should be set up for OpenAI. One for the token to access the API called "OPENAI1" and one for the fine-tuned model string called "FT_MODEL" specified in [Notebook 04](./01_gather_data_and_set_up_geosparql.ipynb).

They will be loaded using 
```python
token = os.environ.get('OPENAI1')
```

## Set up GraphDB
GraphDB is needed to run this experiment. They offer a free version of the database that can be downloaded [here](https://www.ontotext.com/products/graphdb/). After installing:

1. Set up a repository called "geonuts".
2. Import the NUTS.rdf file as specified in the [first Notebook](./01_gather_data_and_set_up_geosparql.ipynb).