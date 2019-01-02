# Discord bot of the Open Study Room
### Huge thanks to FluffM for coding it. Original code can be found [here](https://github.com/Thrillberg/looking-for-game-bot).

This bot has a variety of commands, and it is still in active development.
The most basic commands to get our users going are listed below:

```
!roles - Gives you information about the available roles in our OSR Discord Channel

!league - Contains information about OSR Leagues, rules and participation

!sensei [term] - Displays the first paragraph for a specified term from Sensei's Library

!quote [id] [response] -  Quotes a message using a specific message ID and responds to the message author.

!info - Basic info about the bot.

!help - A more detailed list of commands.
```

To run it, you'll need to provide your own bot token, to be pulled from your shell's environment variables (`OSR_TOKEN`). Add `export OSR_TOKEN="my-token-here"` to `~/.zshenv` (if you use Z Shell), to `~/.bashrc` (if you use bash)  or simply add it to your Windows environment variables.
Same needs to be done for the KGS credentials (`KGS_USERNAME` and `KGS_PASSWORD`)
