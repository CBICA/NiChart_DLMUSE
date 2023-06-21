FROM tensorflow/tensorflow:2.9.0-gpu

LABEL IMAGE="niCHARTPipeline"
LABEL VERSION="0.1.0"
LABEL CI_IGNORE="True"

RUN apt-key del 3bf863cc
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub

RUN apt-get update && apt-get install -y \
    git \
    htop \
    zip \
    unzip \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN git clone  https://github.com/CBICA/niCHARTPipelines.git

RUN cd /niCHARTPipelines && pip install .

CMD ["niCHARTPipelines" ]
