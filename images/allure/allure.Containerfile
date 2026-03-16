ARG DOCKER_PROXY
FROM ${DOCKER_PROXY}node:25

RUN npm install -g allure
