Fossa allows you to download docker images and unpack them without using docker.

# Why?

Docker community has come up with a large number of useful images. These images are nothing more then a file system that contains useful userspace libraries. Besides docker there are other technologies that allow containerization of services / workloads. Fossa allows you to utilize what docker community has created and not have to reinvent the wheel. 

Specific use-case that motivated fossa is using docker images with systemd-nspawn. 

# How to use it?

First dicide what image you'd like to download (e.g. `golang`). Then run:

```
fossa fetch --dir=out golang
```

`fetch` command will download a number of docker layers into `out` directory.

Now unpack that image to create a flat file system:

```
fossa unpack --dir=out --dst=unpacked
```

Now you have a docker image (files that it has stored) in `unpacked` directory.


# Building from source
1. Clone this repository
2. Create a python venv for the project

```
python -m venv ~/.venv/fossa
```


# Limitations
1. At the moment supports only linux and amd64 (open an issue, or even better contribute a PR in case you'd like to see other architectures supported)
1. Losts of other stuff that I can't even think of. 
