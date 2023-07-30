# Horus

<a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=yellow" alt="Python 3.10">
  </a>
  <a href="https://www.postgresql.org/">
     <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="Postgres">
  </a>
  <a href="https://redis.io">
     <img src="https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  </a>
  <a href="https://opensource.org/licenses/MPL-2.0">
     <img src="https://img.shields.io/badge/License-MPL_2.0-brightgreen?style=for-the-badge&logo=appveyor.svg" alt="License: MPL 2.0">
  </a>

A basic discord bot written with [discord.py](https://github.com/Rapptz/discord.py). It is an allpurpose bot with fun commands, utility, moderations, songs and so much more. Some of its major dependencies are:
- [Postgresql](https://www.postgresql.org)
- [Redis](https://redis.io)
- [Lavalink](https://github.com/freyacodes/Lavalink)

| **Warning** : Horus is still under development and this code is only for educational purposes so self hosting is not recommended. [Invite](https://discord.com/api/oauth2/authorize?client_id=858335663571992618&permissions=67420289&scope=bot+applications.commands) the bot instead! |
| --- |

### Installing
Should work if you have python >= `3.8` but for best results use version `3.10`.
1. Install [Postgresql](https://www.postgresql.org/download/), [Redis](https://redis.io/download/) and [Lavalink](https://github.com/freyacodes/Lavalink/releases/tag/3.4)

2. Clone the repository by running this command in your command line prompt / terminal :
```
git clone --branch v0.2 https://github.com/Zeus432/Horus
```

3. Create a virtual environment for your project with the following command :
```
python3 -m venv horus-env
```

4. Activate it using :
```
source horus-env/bin/activate
```

5. Now install python dependencies by:
```
pip install -U -r requirements.txt
```

6. Fill out the necessary details in the [config file](Core/config-sample.toml) and then rename the file to `config.toml`

7. For emojis you have to fill out the [emojis.json](Core/Assets/emojis.json) on your own, I have no other solution for that as of now

### Hosting the Bot
Now to host the bot make sure your postgresql, redis and lavalink servers are online.
Then make sure you're in the directory where [`__main__.py`](__main__.py) is in and then run this command
```
python3 .
```

#### **Note** : Horus is licensed under the [Mozilla Public License 2.0](LICENSE)