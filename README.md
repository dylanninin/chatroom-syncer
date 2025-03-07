# Chatroom-Syncer

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/chatroom-syncer.svg)](https://pypi.org/project/chatroom-syncer/)
[![GitHub stars](https://img.shields.io/github/stars/wey-gu/chatroom-syncer.svg)](https://github.com/wey-gu/chatroom-syncer/stargazers)
[![Code size](https://img.shields.io/github/languages/code-size/wey-gu/chatroom-syncer.svg)](https://github.com/wey-gu/chatroom-syncer)
[![Actions Status](https://github.com/wey-gu/chatroom-syncer/workflows/Continuous%20Integration/badge.svg)](https://github.com/wey-gu/chatroom-syncer/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


Chatroom-Syncer is a project to sync IM Chat Room to the public domain like IRC in the old days, so that the information, context and history of communication could be discoverred, learnt from and referenced by others, anyware, anytime.

> https://user-images.githubusercontent.com/1651790/207810877-b86943fa-24b3-479c-ac25-d602a6c5d53c.mp4

**Supported Sinks**
- [x] Slack
- [x] GitHub
- [ ] IRC
- [ ] Telegram
- [ ] Discord

## Components and Flow

| Components        | Docker Images       | Image Comments |
| ----------------  | ------------------ | ------------- |
| `wechaty-gateway` | [![Docker Image docker:wechaty-gateway](https://img.shields.io/docker/v/weygu/wechaty-gateway?label=Latest%20Tag)](https://hub.docker.com/r/weygu/wechaty-gateway) | `"wechaty": "1.20.2"` <br/> `"wechaty-puppet-wechat": "1.18.4"` |
| `chatroom-syncer` | [![Docker Image docker:chatroom-syncer](https://img.shields.io/docker/v/weygu/chatroom-syncer?label=Latest%20Tag)](https://hub.docker.com/r/weygu/chatroom-syncer) | - tag: `dev` is the main branch head<br/> - `latest` is the latest release on [![PyPI](https://img.shields.io/pypi/v/chatroom-syncer.svg)](https://pypi.org/project/chatroom-syncer/) <br/> |


There are two processes in the system:
- Chatroom Syncer, current code base in Python as the WeChaty Client and the bot
- WeChaty Gateway, which leverages the Wechaty with UOS Wechat Client(also named as a puppet) to be called by the Chatroom Syncer due to WebChaty is not a native Python library, and the Wechaty Gateway is a gRPC server to manipulate and watch WeChat the puppet.

Thus, we need to start the WeChaty Gateway before the Chatroom Syncer.

```asciiarm
┌────────────────────────────┐        ┌────────┐     ┌────────┐
│                            │        │ Sink   │     │        │
│ Chatroom Syncer            │        │        │     │        │
│                            │        │ GitHub │     │        │
│ onMessage()                ├────────▶ Slack ─ ─ ─ ─▶ Linen* │
│   self.use(***SinkPlugin())│        │        │     │        │
│                            │        │        │     │        │
└──────────────▲─────────────┘        │        │     │        │
               │                      └────────┘     └────────┘
             gRPC
               │
┌──────────────▼──────────────┐
│                             │
│  Wechaty Gateway            │
│                             │
│                             │
│┌────────────────────────┐   │
││ Wechaty UOS puppet     │   │
│└────────────────────────┘   │
└─────────────────────────────┘

# * Linen.dev is a Open Source project and a SaaS/Cloud service to help sync slack/discord to a searchable and shareable public domain.

```

## Run

Before running, we need follow prerequisites:

- Configure WeChat Group Names and Sink Info in `config.yaml`, they should exist in both WeChat and Sink.
- Configure Sink API token(Slack API Token, GitHub Token etc) in `.env`.

### Run with Docker

Run it in background:

```bash
cp config-example.yaml config.yaml
cp env-example .env
docker-compose up -d
```

Check both containers are Up:

```bash
docker-compose ps
```

In case there are any `Exit 0` containers, give another try of starting up:

```bash
docker-compose up -d
```

Scan the QR code with your WeChat App, and you are ready to go!

```bash
docker logs chatroom-syncer_chatroom-syncer_1 2>/dev/null | grep -v Wechaty
```

Stop it:

```bash
docker-compose down
```

### Run from host

Run Webchaty gateway first:

```bash
export token="iwonttellyou"
docker run -d \
    --name=wechaty-gateway \
    --net=bridge \
    -p 9009:9009 \
    -e WECHATY_PUPPET_SERVICE_TOKEN="$token" \
    --restart=unless-stopped weygu/wechaty-gateway:latest
```

Run Chatroom-Syncer:

```bash
# install it
python3 -m pip install chatroom-syncer
# create config.yaml and change it
cp config-example.yaml config.yaml

# put tokens for sink according to your config.yaml
# i.e. if both slack and github discussion sinks were enabled
# we need token to send message to slack and github discussion
# as follow:
export SLACK_BOT_TOKEN="xoxb-1234567890-1234567890-1234567890-1234567890"
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxx

# run it
python3 -m chatroom_syncer
```

## Configuration

### WeChat

Copy the config-example.yaml to config.yaml

```bash
cp config-example.yaml config.yaml
```

And fill in the following fields in the table:

| Field | Description |
| ----  | ----------- |
| `enable_slack`                    | Switch of slack sink                                        |
| `group_channel_mapping`           | Mapping WeChat group name to Slack channel name             |
| `enable_avatar`                   | Switch to generate emoji-based avatar for Slack sink        |
| `enable_github_discussion`        | Switch of Github Discussion sink                            |
| `group_github_discussion_mapping` | Mapping WeChat group name to discussion:owner/repo/category |


## Contribute

### Build from host

```bash
git clone https://github.com/wey-gu/chatroom-syncer && cd chatroom-syncer
# install pdm
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
# install chatroom-syncer
pdm install
```

If dependencies are updated, run `pdm sync` to update the lock manifest.

```bash
pdm sync
```

### Build from docker

```bash
docker-compose -f docker-compose.dev.yaml build
docker-compose -f docker-compose.dev.yaml up -d

# get QR code to scan
docker logs chatroom-syncer_chatroom-syncer_1 2>/dev/null | grep -v Wechaty

# watch logs of the chatroom syncer
docker logs chatroom-syncer_chatroom-syncer_1 --follow

# stop the chatroom syncer and remove the container
docker-compose -f docker-compose.dev.yaml down
```

### linting

```bash
# install pre-commit
pip install pre-commit

# run pre-commit
pre-commit run --all-files
```
