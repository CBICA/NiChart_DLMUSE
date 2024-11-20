
## Suggested pull command (run from anywhere):
## CUDA_VERSION=11.8 docker pull cbica/nichart_dlmuse:1.0.1-cuda${CUDA_VERSION}
## OR
## docker pull cbica/nichart_dlmuse:1.0.1

## Suggested automatic inference run time command 
## Place input in /path/to/input/on/host.
## Replace -d cuda with -d mps or -d cpu as needed, or don't pass at all to automatically use CUDA.
## Each "/path/to/.../on/host" is a placeholder, use your actual paths!
## docker run -it --name DLMUSE_inference --rm 
##    --mount type=bind,source=/path/to/input/on/host,target=/input,readonly 
##    --mount type=bind,source=/path/to/output/on/host,target=/output
##    --gpus all cbica/nichart_dlmuse:1.0.1 -d cuda

## Suggested build command (run from the top-level repo directory):
## CUDA_VERSION=11.8 docker build --build-arg CUDA_VERSION=${CUDA_VERSION} 
##      -t cbica/nichart_dlmuse:1.0.1-cuda${CUDA_VERSION} .
## OR
## docker build -t cbica/nichart_dlmuse:1.0.1 .

ARG NICHART_DLMUSE_VERSION="1.0.1"
ARG CUDA_VERSION="11.8"
ARG TORCH_VERSION="2.4.1"
ARG CUDNN_VERSION="9"

## This base image is generally the smallest with all prereqs.
FROM pytorch/pytorch:${TORCH_VERSION}-cuda${CUDA_VERSION}-cudnn${CUDNN_VERSION}-runtime

WORKDIR /app
COPY . /app/ 

RUN pip install .
RUN mkdir /dummyinput && mkdir /dummyoutput
## Cache DLMUSE and DLICV models with an empty job so no download is needed later
RUN DLMUSE -i /dummyinput -o /dummyoutput && DLICV -i /dummyinput -o /dummyoutput
ENTRYPOINT ["NiChart_DLMUSE", "-i", "/input", "-o", "/output"]
CMD ["-d", "cuda"]
