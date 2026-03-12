# Machine Learning Pipeline for Early FTD Detection from Brain MRI Scans

## Introduction

Frontotemporal Dementia (FTD) is a progressive neurodegenerative disorder that primarily affects the frontal and temporal lobes of the brain, leading to changes in behavior, language, and executive functions. The disease includes several clinical variants, each with distinct patterns of brain degeneration and symptoms. In this project, we develop a machine learning pipeline for detecting early signs of FTD from brain MRI images. Specifically, we analyze three main variants:
- Behavioral Variant FTD (bvFTD), which mainly affects personality, social behavior, and decision-making abilities.
- Semantic Variant Primary Progressive Aphasia (svPPA), characterized by a gradual loss of word meaning and object recognition.
- Nonfluent Variant Primary Progressive Aphasia (nfvPPA), marked by difficulties in speech production and grammatical expression.

## Repository Structure

This repository adopts a structure inspired to the [cookiecutter data science project template](https://cookiecutter-data-science.drivendata.org).

All data is stored in the `data` directory and managed using [DVC](https://dvc.org/).

The execution of data processing and model training is orchestrated via Nextflow. The Nextflow pipelines are defined in `nextflow/`.

Model training and usefull scripts are defined in `ftd_diagnosis/`.
Legacy original scripts are stored in the `references/shell` directory.
The analytical reports and traces are stored in the `reports/` directory.

## Usage

To ensure the reproducibility and scalability of the execution environment, this project uses Nextflow in combination with Docker. Nextflow manages the workflow orchestration and parallel execution, while Docker guarantees a consistent environment across different systems.


### Pre-requisites

Before running the containerized pipelines, we need to meet some pre-requisites.

1. The brain segmentation step in `preprocessing.nf` pipeline uses Freesurfer, a software package for analyzing and visualizing structural and functional neuroimaging data.
As Freesurfer is a licensed software, you need to obtain a Freesurfer license to use it (it can be easily requested from the [official website](https://surfer.nmr.mgh.harvard.edu/fswiki/License)).
The license file should be placed in the project root directory and named `license.txt`.
The same license can be used if the data processing pipeline is configured to work with Fastsurfer, a faster version of Freesurfer ([official website](https://deep-mi.org/research/fastsurfer/)).

2. You need to have Docker installed on your machine.
You can download Docker from the [official website](https://www.docker.com/get-started/).

3. You need to have Nextflow installed on your machine.
You can download Nextflow from the [official website](https://www.nextflow.io/).

4. You need to place the neuroimaging data in the `data/raw` directory.
   The data are organized as follows:

   ```text
    data
    └-- raw
      |-- bvFTD_T1
      |   |-- NIFD_1_S_0001_MR_t1_raw_00000.nii
      |   |-- NIFD_2_S_0002_MR_t1_raw_00027.nii
      |   └-- ...
      |
      |-- HC_T1
      |   |-- NIFD_1_S_0001_MR_t1_raw_00000.nii
      |   |-- NIFD_2_S_0002_MR_t1_raw_00027.nii
      |   └-- ...
      |
      |-- svPPA_T1
      |   |-- NIFD_1_S_0001_MR_t1_raw_00000.nii
      |   |-- NIFD_2_S_0002_MR_t1_raw_00027.nii
      |   └-- ...
      |
      └-- nfvPPA_T1
          |-- NIFD_1_S_0001_MR_t1_raw_00000.nii
          |-- NIFD_2_S_0002_MR_t1_raw_00027.nii
          └-- ...
   ```
   > **Note:**
   Subfolder's structure in `data/raw` is not important. You can organize neuroimages as you want, the same structure will be used by brain segmentation module to organize processed data. Please, report the same folder structure in the Nextflow parameter `params.dataset` defined in `nextflow/nextflow.config`. 

   Data is managed using DVC and stored on a local storage. To configure yours:
   ```bash
   dvc remote modify dvcstore url /your/path/to/store
   ```
   Once the store is set, add your data:
   ```bash
   dvc add your/data
   ```
   And push to the storage:
   ```bash
   dvc push
   ```

5. Machine Learning experiments are tracked with MLflow ([official website](https://mlflow.org/docs/latest/ml/)), and the experiment data is stored on the [Dagshub platform](https://dagshub.com/).  
To enable experiment tracking with MLflow you need to set three environment variables in the `.env` file, using your Dagshub credentials and repository: 
   ```
   MLFLOW_TRACKING_USERNAME=<your dagshub username>
   MLFLOW_TRACKING_PASSWORD=<your dagshub token>
   MLFLOW_TRACKING_URI=<your dagshub repository>
   ```
   If you are using a local setup or a platform other than Dagshub, simply configure the tracking URI, username, and password according to your environment.

6. Experiment parameters can be configured in the `nextflow/nextflow.config` file.
Model training hyperparameters are defined in `nextflow/configs/hyperparameters.yml`, while Pyradiomics parameters are specified in `nextflow/configs/pyradiomics.yml`.
> **Note:** Be sure to configure the parallel processing parameters based on your available hardware resources.

### Pipeline execution with Nextflow

Once all prerequisites are satisfied, you can build the containers using the docker compose file:

```bash
docker compose build
```

When you have done, you will be ready.
To run preprocessing pipeline throught Nextflow:

```bash
nextflow run nextflow/preprocessing.nf
```
> **Note:** You can choose which brain segmenter to use by modifying `params.brain_segmenter` in the nextflow.config file, default is Freesurfer.


And training pipeline:
```bash
nextflow run nextflow/training.nf
```
> **Note:** You can modify experiments params in the nextflow.config file to configure your experiments.

The pipeline will start running, and you can monitor its progress from the CLI.
