import argparse
import subprocess
import yaml
import tempfile
import os

parser = argparse.ArgumentParser(description="VectorSpace CLI")
subparsers = parser.add_subparsers(dest="command", required=True)

create_parser = subparsers.add_parser("create")
create_parser.add_argument("--name", required=True)
create_parser.add_argument("--db", required=True, choices=["qdrant", "chromadb", "milvus-lite"])
create_parser.add_argument("--ttl", required=True)
create_parser.add_argument("--persistent", action="store_true")
create_parser.add_argument("--embeddings", default="")
create_parser.add_argument("--user", default="")
create_parser.add_argument("--password", default="")

delete_parser = subparsers.add_parser("delete")
delete_parser.add_argument("--name", required=True)

list_parser = subparsers.add_parser("list")

start_parser = subparsers.add_parser("start")
start_parser.add_argument("--crd-file", default="VectorDBAgent.yaml", help="Path to the CRD YAML")

args = parser.parse_args()

def kubectl_apply(obj):
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".yaml") as f:
        yaml.dump(obj, f)
        f.flush()
        subprocess.run(["kubectl", "apply", "-f", f.name], check=True)

def kubectl_delete(kind, name, group="vectorspace.ai", version="v1"):
    subprocess.run([
        "kubectl", "delete", kind,
        name,
        f"--api-version={group}/{version}"
    ], check=True)

def kubectl_list(kind, group="vectorspace.ai", version="v1"):
    result = subprocess.run([
        "kubectl", "get", kind,
        f"--api-version={group}/{version}",
        "-o", "yaml"
    ], capture_output=True, text=True)
    return yaml.safe_load(result.stdout)

def kubectl_apply_file(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)

if args.command == "create":
    cr = {
        "apiVersion": "vectorspace.ai/v1",
        "kind": "VectorDBAgent",
        "metadata": {"name": args.name},
        "spec": {
            "dbType": args.db,
            "ttl": args.ttl,
            "persistent": args.persistent,
            "embeddings": args.embeddings,
            "credentials": {"user": args.user, "password": args.password}
        }
    }
    kubectl_apply(cr)

elif args.command == "delete":
    kubectl_delete("vectordbagent", args.name)

elif args.command == "list":
    crs = kubectl_list("vectordbagents")
    items = crs.get("items", [])
    if not items:
        print("No VectorDB agents found.")
    else:
        for item in items:
            spec = item.get("spec", {})
            print(f"- {item['metadata']['name']}: {spec.get('dbType')} TTL={spec.get('ttl')} Persistent={spec.get('persistent')}")

elif args.command == "start":
    if os.path.exists(args.crd_file):
        kubectl_apply_file(args.crd_file)
    else:
        print(f"CRD file not found: {args.crd_file}")
        exit(1)

    subprocess.Popen(["nohup","kopf", "run", "vcontroller.py", "--all-namespaces"])
    print("Operator started. You can now create VectorDBAgent CRs.")
