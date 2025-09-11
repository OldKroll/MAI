FROM python:3.12-slim-bookworm

ENV UID=1000
ENV GID=1000
ENV USER_PASSWORD=user
ENV USER_NAME=user
ENV DEV_FOLDER=project

RUN apt-get update && apt-get install -y git vim sudo bash-completion tmux pip libaio1
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    unixodbc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r ${USER_NAME} && useradd -m -s /bin/bash -g ${USER_NAME} ${USER_NAME} -G adm,cdrom,sudo
RUN echo ${USER_NAME}:${USER_PASSWORD} | chpasswd
RUN usermod -u ${UID} ${USER_NAME} \
  && groupmod -g ${GID} ${USER_NAME}

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}
RUN mkdir ${DEV_FOLDER}
RUN mkdir -p .vscode-server/extensions
ENV PYTHONPATH="${PYTHONPATH}:/home/${USER_NAME}/${DEV_FOLDER}"

WORKDIR /home/${USER_NAME}/${DEV_FOLDER}
COPY --chown=${UID}:${GID} ./requirements.txt .
RUN pip3 install -r requirements.txt
