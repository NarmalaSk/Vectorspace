### Vectorspace

Vector space allows ML Developers , Researchers to Run Ephermal Vector dbs . Helps in Also Exports of Indexes to cloud sources like s3 buckets.
Locally it can spin up docker containers or ephermal pods on k8s

##### Usecases:
* Testing Data with different vector dbs and perform benchmarks
* Export Indexes as HNSW/IVF/PQ
* Faster Vector Db Validation and Usecase Implementation

### MVP Support
This cli now supports k8s clusters locally and vectordbs like chromdb,qdrant

### Prerequisites

Before starting, make sure you have the following installed locally:

Minikube – Kubernetes local cluster
* Install from official docs: https://minikube.sigs.k8s.io/docs/start/

Kubectl – Kubernetes CLI tool
* Installation guide: https://kubernetes.io/docs/tasks/tools/

Docker – Required to build images
* https://docs.docker.com/get-docker/

### Setup

1.Clone The repo
```
git clone https://github.com/NarmalaSk/Vectorspace.git

```

2. Install requirements.txt 

```
pip install -r requirements.txt
```

3.Start the K8s crd 
```
python cli.py start
```

4.Create a db
```
python cli.py create --name mydb --db qdrant --ttl 1h
```



