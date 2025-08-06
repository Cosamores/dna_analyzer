# DNA Analyzer

## Purpose

This workflow aims to generate a rich analysis of DNA data, providing different tools with a modularized architecture.

## Expected input

The main pipeline expets a CSV file with SNP data as described:

```csv
RSID,CHROMOSOME,POSITION,RESULT
rs9651229,1,567667,CT
```

## Tools

### SNP Mapper (snp_mapper.py)

Maps the RSIDs from the CSV into JSON files, including available data from SNPedia and My Variants scrapping. 
Ouput = JSON with the following format:

```json
{
  "rsid": "Rs5400",
  "chromosome": "3",
  "position": "170732300",
  "alelo": "G;G",
  "alelo_clean": "GG",
  "genotipos": [
    {
      "genotipo": "(C;C)",
      "magnitude": "0.1",
      "resumo": "normal sugar consumption"
    },
    {
      "genotipo": "(C;T)",
      "magnitude": "1.7",
      "resumo": "significantly higher sugar consumption?"
    },
    {
      "genotipo": "(T;T)",
      "magnitude": "1.8",
      "resumo": "significantly higher sugar consumption"
    }
  ],
  "gmaf": "0.1873",
  "genes": [
    "SLC2A2"
  ],
  "descricao_livre": "[PMID 18349384]rs5400(T;T) carriers had a significantly higher intake of sugars",
  "trait": "normal sugar consumption",
  "resumo": "[PMID 18349384]rs5400(T;T) carriers had a significantly higher intake of sugars",
  "url": "https://www.snpedia.com/index.php/Rs5400",
  "found_snpedia_data": true,
  "found_myvariant_data": true,
  "gene": "SLC2A2",
  "significado_clinico": ""
}
```

### SNP Cleaner (snp_cleaner.py)

Filters the mapped SNPs and stores only the ones that "found_snpedia_data" OR "found_myvariant_data" equals to True.
Output = Stores the filtered JSONs in a new folder

### Genotype Matcher (genotype_matcher.py)

Matches the mapped genotypes with the alelo/alelo_clean fields in the SNP data.
Output = Stores the relevant genotypes in a new folder

### NLP Clustering (nlp_clustering.py)

Uses NLP through scikit-learn and matplotlib to generate a cluster graph and MD files with the clusters information on the pre-processed DNA data.


### LLM Queries

Currently implemented on V1 as dna_interpreter, it reads the CSV file and queries the LLM for each RSID  line.
Output =  incrementally saved MD file with the LLM answers 

## Current State

### Controlability and Orchestration

Currently the system lacks orchestration and integration with CLI. Future plans include a complete CLI system able to execute each tool separately or different workflows. At the moment only the SNP Mapper can be triggered from the main_pipeline.

### Genotype mapper

Curretly, the genotype mapper is quite strict, as it only matches genotypes that are already structured and mapped, but the descricao_livre, traits and resumo fields sometimes have useful genotypic data. Next steps is to include the mapping of relevant genotype data from tests.

### Embeddings

The plans include a embedding system that will allow an expanded analysis when later dealing with more complex models as LLMs. This step requires more understanding in Genetics than what I have at the moment, so I'll need quite some data exploration time before getting into this feature.

## Collaboration

Collaborations are more than welcome and appreciated. This project is not intended for commercial use.

Author: Diego Cosamores
Date: 08/06/2025


