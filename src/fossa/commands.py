import click
import tarfile
import pickle

import image_analyzer.docker as ia
from pathlib import Path

auth_url = "https://auth.docker.io"
registry_url = "https://registry-1.docker.io"
service_url = "registry.docker.io"


@click.group()
def cli1():
    pass


@cli1.command('fetch')
@click.option('--dir', default='tmp', help='Output directory.')
@click.argument('image_name')
def fetch_image(dir: str, image_name: str):
    token = ia.get_auth_token(auth_url, service_url, image_name)
    image_data = ia.get_image_data(registry_url, token, image_name)
    digest = ia.get_digest_from_manifests("amd64", "linux", image_data)
    layers_data = ia.get_image_data(registry_url, token, image_name, digest)
    digests_for_layers = ia.get_layer_digests(layers_data)

    tmp_dir = Path(dir)
    if not tmp_dir.exists():
        tmp_dir.mkdir()

    for (i, l) in enumerate(digests_for_layers):
        layer_path = tmp_dir / Path(f"{l}.tar.gz")
        ia.download_layer(
            registry_url, token, image_name, l, layer_path
        )

    layers_data_file = tmp_dir / 'layers_data'
    layers_data_file.write_bytes(pickle.dumps(layers_data))


@cli1.command('unpack')
@click.option('--dir', default='tmp', help='Output directory.')
@click.option('--dst', default='unpacked', help='Directory where layers will be unpacked.')
def unpack_layers(dir: str, dst: str):
    layers_dir = Path(dir)
    unpack_dir = Path(dst)

    files = set(layers_dir.glob('*.tar.gz'))

    layers_data_file = layers_dir / 'layers_data'
    layers_data_bytes = layers_data_file.read_bytes()
    layers_data = pickle.loads(layers_data_bytes)
    digests_for_layers = ia.get_layer_digests(layers_data)

    for d in digests_for_layers:
        with tarfile.open(layers_dir / f"{d}.tar.gz") as f:
            f.extractall(unpack_dir)

