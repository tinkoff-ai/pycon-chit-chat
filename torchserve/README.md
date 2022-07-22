# pycon-chit-chat
PyCon 2022, Мастер-класс "Как сделать свою генеративную болталку"

## Deploy to torchserve

Архивируем модель в `.mar` файл

```bash
export TS_MDIR=/path/to/trained/model
mkdir -p torchserve_registry
torch-model-archiver --model-name gpt --version 1.0 \
  --export-path ./torchserve_registry \
  --serialized-file ${TS_MDIR}/model.pt \
  --handler torchserve/handler.py \
  --extra-files "${TS_MDIR}/*"
```

Поднимаем модель через Docker

```bash
docker run --rm -d --shm-size=1g \
        --env LC_ALL="C.UTF-8" \
        --env LANG="C.UTF-8" \
        --ulimit memlock=-1 \
        --ulimit stack=67108864 \
        -p 8898:8080 \
        --name torchserve \
        --mount type=bind,source=$(pwd)/torchserve_registry,target=/tmp/models \
        pytorch/torchserve:0.4.2-cpu torchserve --start --model-store=/tmp/models --models gpt=gpt.mar --ncs
        
sudo bash -c 'echo "привет" >> data.txt'
# it will take up to 2 minutes (model needs to warm up)
curl -X POST http://localhost:8898/predictions/gpt -T data.txt
