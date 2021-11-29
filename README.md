# Towards Automation of Topic Taxonomy Construction

This repository contains the code and the data used for the submission 58 of IDA 22

## Data

### S2ORC

The S2ORC dataset used in this paper in the `20200705v1` version. 
Because even the parsed are too large to be stored on this repository, please refer to the [S2ORC repository](https://github.com/allenai/s2orc) to download the dataset. 

#### Pre-processing

To preprocess the S2ORC dataset, you can use the cells of the `Extract S2ORC data` section in the [s2orc_preprocess notebook](preprocess/s2orc_preprocess.ipynb) in the `preprocess` repository by modifying the filenames to your system. 
The folder of interest will remain `full/metadata` in the S2ORC folder hierarchy.  

It will generate you two files, the first one to represent the abstracts + titles of the paper and the second to represent their metadata. 

### Classifications

The original ACM classification can be found at [https://cran.r-project.org/web/classifications/ACM-2012.html](https://cran.r-project.org/web/classifications/ACM-2012.html) while the Europa classification can be found at [https://ec.europa.eu/research/participants/data/call/trees/portal_keyword_tree.json](https://ec.europa.eu/research/participants/data/call/trees/portal_keyword_tree.json). 

The preprocessed networkx graph pickles representing both classifications without the "X and Y" topics are found in the [data](data) folder. 

### Matrix generation

The topic subsumption matrix can be generated using the script [knowledge/subsumption.py](knowledge/subsumption.py). 

It's usage is `py subsumption.py --data [paper data] --topics [topic list] --out [path and prefix of the ouput]`. 

The `data` argument is for the file containing on each line the titles + abstracts and correspond to the file generated by S2ORC preprocess. 
The `topics` argument is for the file listing the different topics to use it corresponds to the ACM and Europa topic files or our generated topics that are in the `data` folder. 
The output will generate two files, one with the suffix `_subsumption.pickle` containing the `Subsumption` object and one with the suffix `_vectorizer.pickle` containing the `CountVectorizer` used to process the abstracts. 

After that you can use the rest of the [s2orc_preprocess notebook](preprocess/s2orc_preprocess.ipynb) to generate the rest of the matrices. 

### Evaluation

TBW