### Vectorspace

Vector space allows ML Developers , Researchers to Run Ephermal Vector dbs . Helps in Also Exports of Indexes to cloud sources like s3 buckets.
Locally it can spin up docker containers or ephermal pods o k8s

##### Usecases:
* Testing Data with different vector dbs and perform benchmarks
* Export Indexes as HNSW/IVF/PQ
* Faster Vector Db Validation and Usecase Implementation

### MVP Support
This cli now supports k8s clusters locally and vectordbs like chromdb,qdrant

### Setup

1.Clone The repo
```
git clone https://github.com/NarmalaSk/Vectorspace.git

```

2.Start the K8s crd 
```
python cli.py start
```

3.Create a db
```
python cli.py create --name mydb --db qdrant --ttl 1h
```



