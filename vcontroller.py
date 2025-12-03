import kopf
import logging
from kubernetes import client, config
import asyncio

GROUP = "vectorspace.ai"
VERSION = "v1"
PLURAL = "vectordbagents"
NAMESPACE = "default"


try:
    config.load_kube_config()
except:
    config.load_incluster_config()

api = client.CustomObjectsApi()
apps_api = client.AppsV1Api()


def delete_cr(name):
    try:
        api.delete_namespaced_custom_object(GROUP, VERSION, NAMESPACE, PLURAL, name)
        logging.info(f"Deleted VectorDBAgent '{name}'")
    except client.exceptions.ApiException as e:
        logging.error(f"Error deleting {name}: {e}")

def parse_ttl(ttl_str):
    if ttl_str.endswith("m"):
        return int(ttl_str[:-1]) * 60
    elif ttl_str.endswith("h"):
        return int(ttl_str[:-1]) * 3600
    return int(ttl_str)

def create_deployment(name, db_type, credentials):
    container_image = {
        "qdrant": "qdrant/qdrant",
        "chromadb": "chromadb/chroma:latest",
        "milvus-lite": "milvusdb/milvus:v2.3.0"
    }.get(db_type)

    if not container_image:
        logging.error(f"No image defined for DB type: {db_type}")
        return

    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=f"{name}-deployment"),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector={"matchLabels": {"app": name}},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": name}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=db_type,
                            image=container_image,
                            ports=[client.V1ContainerPort(container_port=6333 if db_type=="qdrant" else 8000)],
                            env=[
                                client.V1EnvVar(name="DB_USER", value=credentials.get("user","")),
                                client.V1EnvVar(name="DB_PASSWORD", value=credentials.get("password",""))
                            ]
                        )
                    ]
                )
            )
        )
    )

    try:
        apps_api.create_namespaced_deployment(namespace=NAMESPACE, body=deployment)
        logging.info(f"Deployment created for {name}")
    except client.exceptions.ApiException as e:
        logging.error(f"Error creating deployment: {e}")

def delete_deployment(name):
    try:
        apps_api.delete_namespaced_deployment(name=f"{name}-deployment", namespace=NAMESPACE)
        logging.info(f"Deleted deployment {name}-deployment")
    except client.exceptions.ApiException as e:
        logging.error(f"Error deleting deployment: {e}")


@kopf.on.create(GROUP, VERSION, PLURAL)
async def create_fn(body, **kwargs):
    name = body['metadata']['name']
    spec = body.get("spec", {})
    db_type = spec.get("dbType", "qdrant")
    ttl = spec.get("ttl", "30m")
    persistent = spec.get("persistent", False)
    embeddings = spec.get("embeddings", "")
    credentials = spec.get("credentials", {})

    logging.info(f"Kopf create handler triggered for {name}, DB={db_type}")


    create_deployment(name, db_type, credentials)


    seconds = parse_ttl(ttl)
    await asyncio.sleep(seconds)
    logging.info(f"TTL expired for {name}, deleting CR")
    delete_cr(name)

@kopf.on.delete(GROUP, VERSION, PLURAL)
def delete_fn(body, **kwargs):
    name = body['metadata']['name']
    logging.info(f"Kopf delete handler triggered for {name}")
    delete_deployment(name)
