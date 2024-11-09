# LLM-Twin

- This project was inspired by the book: [LLM Engineers's Handbook](https://subscription.packtpub.com/book/data/9781836200079/1). 
- LLM Twin is an AI character that incorporates your writing style, voice and personality into an LLM, which is a complex AI model.
- It helps you do the following:
  - Create your brand
  - Automate the writing process
  - Brainstorm new creative ideas

## Table of Contents

- [LLM-Twin](#llm-twin)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Building ML Systems With Feature | Training | Inference (FTI)Pipelines](#building-ml-systems-with-feature--training--inference-ftipipelines)
  - [Installation](#installation)
    - [UV](#uv)
    - [Poetry](#poetry)
    - [Poe The Poet: Task Exection Tool](#poe-the-poet-task-exection-tool)

## Overview

- This project contains the following stages:
  - **Data Collection**
    - Data Collection from different sources.
    - Standardize the crawled data and store it in a database.
    - Clean the data.
    - Create instruct datasets for fine-tuning the LLM.
    - Chunk and embed the cleaned data.
    - Create an index for the data in the vector database.
  - **Fintuning An LLM**
    - Finetune LLMs of different sizes. (7B, 13B, 30B, 70B parameters).
    - Finetune LLMs using the instruct datasets of different sizes.
    - Switch between different models. (Mistral, Llama, GPT-3.5, GPT-4, etc.)
    - Track and monitor the training process.
    - Evaluate the performance of the finetuned models before deploying them.
    - Automate the training process when new data is available.
  - **Inference Phase**
    - A REST API interface for interacting with the LLM.
    - Access to the vector DB in real-time for RAG.
    - Inference with LLMs of different sizes.
    - Autoscaling based on the number of requests.
    - Automatic deployment of models that pass the evaluation phase.
  - **Overall Features**
    - Dataset versioning, lineage and reusability.
    - Model versioning, lineage and reusability.
    - Experiment tracking and monitoring.
    - Continuous training (CT), continuous integration (CI) and continuous deployment (CD).
    - Prompt and system monitoring.

### Building ML Systems With Feature | Training | Inference (FTI)Pipelines

- **Feature Pipeline**:
  - It takes raw data as input and, processes it and outputs features and labels required by the model (for training or inference).
  - Instead of directly passing the features to the model, they are stored in a feature store.
  - The feature store is used to store, version and track the features and labels required by the model.
- **Training Pipeline**:
  - It takes the features and labels as input and outputs a trained model or models.
  - The trained models are stored in a model registry and it's features are similar to the feature store.
  - The model registry also contains the model's metadata such as the model's name, version, and other metadata.
- **Inference Pipeline**:
  - It takes as input the features and labels from the feature store and the trained model from the model registry.
  - It outputs the predictions from the model either in batch or real-time.

**Benefits of using FTI Pipelines**:

- It's intuitive and easy to understand.
- It's easy to maintain and update.
- Each component is independent and can be deployed, scaled, and managed separately.

<br>

[![image.png](https://i.postimg.cc/7ZvH3TWP/image.png)](https://postimg.cc/563W1jJD)

[Image Source](https://subscription.packtpub.com/book/data/9781836200079/1/ch01lvl1sec05/designing-the-system-architecture-of-the-llm-twin)

## Installation

- Install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) for managing Python versions.
- Install the required Python version using the following command:

```sh
pyenv install <your-version>

# E.g
pyenv install 3.11.8
```

- Check the installed version using the following command:

```sh
pyenv versions
```

- To make a specific version the default version, use the following command:

```sh
pyenv global <your-version>

# E.g
pyenv global 3.11.8
```

- To create a local Python version, use the following command [it should be run ONCE per project]:

```sh
pyenv local <your-version>

# E.g
pyenv local 3.11.8
```

### [UV](https://docs.astral.sh/uv/guides/projects/)

- Install UV for Python using the following command:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh 

# Install a specific version:
curl -LsSf https://astral.sh/uv/<your-version>/install.sh | sh

# E.g
curl -LsSf https://astral.sh/uv/0.5.1/install.sh | sh
```

- Add a dependency group  to the project using the following command:

```sh
uv add --group <group-name> <dependency-name>

# E.g
uv add --group aws sagemaker
```

### Poetry

- Install Poetry using the following command:

```sh
curl -sSL https://install.python-poetry.org | python3 - --version <your-version>

# E.g
curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3

# Or if you want to install the latest version:
curl -sSL https://install.python-poetry.org | python3 -
```

- Uninstall Poetry using the following command:

```sh
curl -sSL https://install.python-poetry.org | python3 - --uninstall
```

- To update Poetry, use the following command:

```sh
poetry self update
```

### Poe The Poet: Task Exection Tool

- Poe the Poet simplifies project management by integrating task automation into the Poetry configuration.
- It replaces the need for separate scripts, offering a streamlined approach to define and execute common project tasks, making it an efficient tool for Python developers.
- Consider the config file shown below:

```toml
[tool.poe.tasks]
# Example task
test = "pytest"
format = "black ."
start = "python main.py"
```

- To run these tasks, use the following command:

```sh
poetry run poe <task-name>

# E.g
poetry run poe test
poetry run poe format
poetry run poe start
```

- To list all available tasks, use the following command:

```sh
poetry run poe list
```

- To install Poe the Poet, use the following command:

```sh
poetry self add "poethepoet[poetry_plugin]"
```

- Add pre-commit hook to the project using the following command:

```sh
poetry run pip pre-commit install
```

- Update the `.lock` file using the following command:

```sh
poetry lock "--no-update"
```