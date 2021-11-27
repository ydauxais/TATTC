# Towards Automation of Topic Taxonomy Construction

This repository contains the code and the data used for the submission 58 of IDA 22

## Data

### S2ORC

The S2ORC dataset used in this paper in the `20200705v1` version. 
Because even the parsed are too large to be stored on this repository, please refer to the [S2ORC repository](https://github.com/allenai/s2orc) to download the dataset. 

#### Pre-processing

To preprocess the S2ORC dataset, you can use the [s2orc_preprocess notebook](preprocess/s2orc_preprocess.ipynb) in the `preprocess` repository by modifying the filenames to your system. 
The folder of interest will remain `full/metadata` in the S2ORC folder hierarchy.  

It will generate you two files, the first one to represent the abstracts + titles of the paper and the second to represent their metadata. 

### Matrix generation

TBW

### Classifications

The original ACM classification can be found at [https://cran.r-project.org/web/classifications/ACM-2012.html](https://cran.r-project.org/web/classifications/ACM-2012.html) while the Europa classification can be found at [https://ec.europa.eu/research/participants/data/call/trees/portal_keyword_tree.json](https://ec.europa.eu/research/participants/data/call/trees/portal_keyword_tree.json). 

