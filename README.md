# ka-bosch
[Bosch Kaggle Competition](https://www.kaggle.com/c/bosch-production-line-performance)


## Downloading the data

The competition datasets can be downloaded with the DownloadData wrapper task, with train/test data switches being provided by the parameter `--Path-ENV=test`.

`python -m luigi --module train_cut DownloadData --local-scheduler`

The files download into:
```
|- data
    |- train
        |- train_categorical.csv.zip
        |- train_date.csv.zip
        |- train_numeric.csv.zip
    |- test
        |- test_categorical.csv.zip
        |- test_date.csv.zip
        |- test_numeric.csv.zip
```

## Separating analysis

The root data sets are shared by all runs within the environment, but multiple runs can be preserved using the `--Path-RUNTAG` parameter. By default, this is the date the pipeline is run, but any string value can be passed in.
