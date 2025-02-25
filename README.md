# image-rec

## development

### run tests
from `./app` directory:
```
poetry run pytest
```

## running locally

### prerequisites
install:
- docker
- kind
- kubectl

### build image-rec image
```
docker build -t local/image-rec:latest .
```

### create cluster
```
kind create cluster --name image-rec-demo
```

### load image on cluster
```
kind load docker-image local/image-rec:latest --name image-rec-demo
```

### install helm chart
```
helm upgrade --install image-rec . --namespace default
```

### forward service port
```
kubectl port-forward svc/image-rec 8080:80
```


## clean up
