#!/bin/bash

image="${1:-golang}"
registry_url="https://registry-1.docker.io"
auth_url="https://auth.docker.io"
svc_url="registry.docker.io"

function auth_token {
	curl -fsSL "${auth_url}/token?service=${svc_url}&scope=repository:library/${image}:pull" | jq --raw-output .token
}

function manifest {
	token="$1"
	image="$2"
	digest="${3:-latest}"

	curl -fsSL \
		-H "Authorization: Bearer $token" \
		-H "Accept: application/vnd.docker.distribution.manifest.list.v2+json" \
		-H "Accept: application/vnd.docker.distribution.manifest.v1+json" \
		-H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
		"${registry_url}/v2/library/${image}/manifests/${digest}"
}

function blob {
	token="$1"
	image="$2"
	digest="${3}"
	file="$4"

	curl -fsSL -o "$file" \
		-H "Authorization: Bearer $token" \
		"${registry_url}/v2/library/${image}/blobs/${digest}"
}

function layers {
	echo "$1" | jq -r '.layers[].digest'
}

token=$(auth_token)
image_data=$(manifest $token $image)
image_digest=$(jq -r '.manifests | map(select(.platform.architecture == "amd64" and .platform.os == "linux")) | first | .digest' <<< $image_data)
layer_data=$(manifest $token $image $image_digest)
i=0
for L in $(layers "$layer_data"); do
	echo "Layer:"
	echo $L
	blob "$token" "$image" "$L" "layer_${i}.tar.gz"
	i=$((i+1))
done
