# DNA Analyzer

## Purpose

This workflow aims to generate a rich analysis of DNA data, providing different tools with a modularized architecture.

## Project structure

The tools/ directory contains all the tools used in our workflow. They work as independent tools and are planned to be integrated in the main pipeline in the future.

```tree
|── main_pipeline
├── tools
│   ├── analyzer
│   │   ├── clusterers
│   │   │   ├── gene_clustering.py
│   │   │   ├── nlp_clustering.py
│   │   │   └── snp_clusterer.py
│   │   └── reporters
│   │       ├── detailed_risk__report.py
│   │       └── snp_reporter.py
│   ├── mapper
│   │   ├── dbsnp_local
│   │   │   └── snp_mapper_local.py
│   │   ├── filters
│   │   │   ├── genotype_matcher.py
│   │   │   └── snp_cleaner.py
│   │   └── scrapper
│   │       ├── helpers
│   │       │   ├── load_map_variants.py
│   │       │   └── snpedia_handler.py
│   │       ├── snp_locator.py
│   │       └── snp_mapper_web.py
│   ├── prompt_builder.py
│   └── query_llm.py
└── utils
    ├── __init__.py
    └── json_tools.py
```

Some tools are functional, some were just tests that are no longer being used, so don't expect the cleaner code now, but soon the tools will get more stabilized and I'll keep only the required files.

## Expected data input

The main_pipeline expets a CSV file with SNP data as described:

```csv
RSID,CHROMOSOME,POSITION,RESULT
rs9651229,1,567667,CT
```

The other tools expect a json with a mapped SNP.

## Tools

### SNP Mapper Web (_snp_mapper_web.py)

Maps the RSIDs from the CSV into JSON files, relying on available data from SNPedia, My Variants and Ensembl APIs to access useful SNP data.
Some of the SNPedia data look just like a LLM allucinating or repeating its prompt, so it's kind of a boring dataset.
Ouput = JSON with the following format:

```json
{
  "rsid": "Rs800292",
  "chromosome": "1",
  "position": "196642233",
  "alelo": "G;C",
  "alelo_clean": "GC",
  "genotipos": [
    {
      "genotipo": "(C;C)",
      "magnitude": "2",
      "resumo": "5% higher risk of Age related macular degeneration"
    },
    {
      "genotipo": "(C;T)",
      "magnitude": "1",
      "resumo": "1% decreased risk of macular degeneration"
    },
    {
      "genotipo": "(T;T)",
      "magnitude": "2",
      "resumo": "5% decreased risk of macular degeneration"
    }
  ],
  "gmaf": "0.4348",
  "genes": [
    "CFH"
  ],
  "descricao_livre": "rs800292is a SNP in the complement factor HCFHgene; it has been linked to blindness inage related macular degeneration. This SNP is also known as 184G>A, I62V, or Val62Ile.",
  "trait": "5% higher risk of Age related macular degeneration",
  "resumo": "rs800292is a SNP in the complement factor HCFHgene; it has been linked to blindness inage related macular degeneration. This SNP is also known as 184G>A, I62V, or Val62Ile.",
  "url": "https://www.snpedia.com/index.php/Rs800292",
  "found_snpedia_data": true,
  "found_myvariant_data": true,
  "gene": "CFH",
  "significado_clinico": "",
  "ref": "G",
  "alt": "A",
  "vartype": "snv",
  "myvariant_trait": "",
  "effect": "missense_variant",
  "putative_impact": "MODERATE",
  "location_type": "",
  "region": "",
  "impact": "MODERATE",
  "variant_consequence": "missense_variant",
  "regulatory_effect": "",
  "found_ensembl_data": true
}
```

### SNP Mapper Local (snp_mapper_local.py)

This is the new mapper developed to read a local copy of [sbSNP](https://www.ncbi.nlm.nih.gov/snp/) and map the inputted CSV file with DNA data into enriched JSONs for each rsid.
This method is supposed to be much faster than web scrapping or API fetching.  

This feature in being tested right now and I can't ensure the current code is functional, but below you can see the steps for fetching the dbSNP with FileZilla and enabling the execution of the SNP local mapping:

1. Conecte-se ao servidor com FilleZila usando as informações abaixo:

  ```terminal
    Host: ftp.ncbi.nlm.nih.gov
    Port: 21
    User: anonymous
    Password: <seu e-mail>
  ```

2. Navegue até o diretório /snp/latest_release/VCF/

3. Lá você encontrará os arquivos:

| Arquivo            | Tamanho  | Descrição |
|--------------------|----------|-----------|
|GCF_000001405.40.gz | ~29.5 GB |Arquivo VCF compactado contendo todos os SNPs anotados do genoma humano da referência GRCh38.p14 |
| GCF_000001405.40.gz.tbi	| ~3.14 GB | Arquivo de índice tabix, que permite acessar rapidamente regiões específicas do VCF |

4. O arquivo mais importante a ser baixado é o GCF_000001405.40.gz, que possui quase 30GB, então considere isso ao realizar este passo.

5. Agora basta adicionar os caminhos de input e output no mapper e rodar a feramenta.

### SNP Cleaner (snp_cleaner.py)

Filters the mapped SNPs and stores only the ones that "found_snpedia_data" OR "found_myvariant_data" equals to True.
Output = Stores the filtered JSONs in a new folder

### Genotype Matcher (genotype_matcher.py)

Matches the mapped genotypes with the alelo/alelo_clean fields in the SNP data.
Output = Stores the relevant genotypes in a new folder

### NLP Clustering (nlp_clustering.py) # Deprecated

Uses NLP through scikit-learn and matplotlib to generate a cluster graph and MD files with the clusters information on the pre-processed DNA data.

### LLM Queries

Currently implemented on V1 as dna_interpreter, it reads the CSV file and queries the LLM for each RSID  line.
Output =  incrementally saved MD file with the LLM answers

## Current State

### Controlability and Orchestration

Currently the system lacks orchestration and integration with CLI. Future plans include a complete CLI system able to execute each tool separately or different workflows. At the moment only the SNP Mapper can be triggered from the main_pipeline.

### Clesterization and analysis

Now with a more complete data we can find interesting ways to explore our data by gene location, RMAF, chromossomes, etc. So next steps definitely include different types of data eexploration.

### Embeddings

The plans include a embedding system that will allow an expanded analysis when later dealing with more complex models as LLMs. This step requires more understanding in Genetics than what I have at the moment, so I'll need quite some data exploration time before getting into this feature.

## Collaboration

Collaborations are more than welcome and appreciated. This project is not intended for commercial use.

- Author: Diego Cosamores
- Date: 08/06/2025
