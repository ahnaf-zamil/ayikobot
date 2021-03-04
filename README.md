# Ayiko

![Ayiko banner](https://cdn.discordapp.com/attachments/783359069993435150/816651655470383104/ayiko_banner.png)

Ayiko is a general-purpose Discord bot written in Python.

## Status
This bot is currently under extensive development and considered as work-in-progress. 
If you are interested in contributing to the project, fell free to make an issue or a pull request.

## Invite
Right now, you cannot invite the bot to a server as it is not hosted. Mainly because the bot doesn't have any notable features for it to be hosted....yet.
The developer is working hard to get features out so it will be hosted soon ;)

## Contributing
If you are considering to contribute, thanks a lot! We welcome all contributors here and you can help out as well.
The bot is run inside a Docker container and that's what we recommend using for testing out the bot.

If you don't know how to use docker, we highly recommend that you check out this [tutorial.](https://www.youtube.com/watch?v=fqMOX6JJhGo)

## Running locally

Since this project uses Docker, it is highly recommended that you use it. But you can also find a way around 
it by hosting all the dependencies and services on your pc. But here's how you do it with Docker:

First of all, rename `.env.example` and `config.example.json` to `.env` and `config.json` respectively.
Then fill in all the configuration and credentials. Now you can start building the containers

To build the containers, just open your terminal in the folder and run

```bash
docker-compose up -d
```

This will build all the containers and run it.

To stop the bot, just run
```bash
docker-compose down
```

## Libraries
The open-source libraries and frameworks that we use to make Ayiko awesome are

```
hikari
hikari-lightbulb
asyncio
attrs
typing
aiohttp
colorama
pilutils
motor
pillow-simd
```

## License

This project is licensed under GPLv3. You can check out our copy [here.](./LICENSE)