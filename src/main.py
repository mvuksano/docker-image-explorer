import json
import requests

from collections.abc import Callable
from typing import Any

auth_url = "https://auth.docker.io"
registry_url = "https://registry-1.docker.io"
service_url = "registry.docker.io"
image = "golang"


def get_auth_token(auth_url: str, service_url: str, image: str) -> str:
    r = requests.get(
        "{}/token?service={}&scope=repository:library/{}:pull".format(
            auth_url, service_url, image
        )
    )
    try:
        data = r.json()
    except json.JSONDecodeError:
        return ""
    except ValueError:
        return ""

    return data["token"]


def get_image_data(
    registry_url: str, token: str, image: str, digest: str = "latest"
) -> dict[str, Any]:
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Accept": "application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.docker.distribution.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json",
    }
    r = requests.get(
        "{}/v2/library/{}/manifests/{}".format(registry_url, image, digest),
        headers=headers,
    )
    return r.json()


def filter_for_arch_and_os(
    arch: str, os: str
) -> Callable[[dict[str, Any]], bool]:
    def fn(d: dict[str, Any]):
        return (
            d["platform"] is not None
            and d["platform"]["architecture"] == arch
            and d["platform"]["os"] == os
        )

    return fn


def get_digest_from_manifests(
    arch: str, os: str, img_data: dict[str, Any]
) -> str:
    found_manifests = filter(
        filter_for_arch_and_os(arch, os), image_data["manifests"]
    )
    return next(found_manifests)["digest"]


def get_layer_digests(layers: dict[str, Any]) -> list[str]:
    return [layer_info["digest"] for layer_info in layers["layers"]]


def download_layer(
    registry_url: str,
    auth_token: str,
    image: str,
    layer_digest: str,
    filename: str,
) -> None:
    headers = {
        "Authorization": "Bearer {}".format(auth_token),
    }
    r = requests.get(
        "{}/v2/library/{}/blobs/{}".format(registry_url, image, layer_digest),
        headers=headers,
    )
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=512):
            f.write(chunk)


if __name__ == "__main__":
    token = get_auth_token(auth_url, service_url, image)
    image_data = get_image_data(registry_url, token, image)
    digest = get_digest_from_manifests("amd64", "linux", image_data)
    layers_data = get_image_data(registry_url, token, image, digest)
    digests_for_layers = get_layer_digests(layers_data)
    for (i, l) in enumerate(digests_for_layers):
        download_layer(
            registry_url, token, image, l, "layer_{}.tar.gz".format(i)
        )
