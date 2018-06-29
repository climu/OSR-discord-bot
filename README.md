# Discord bot of the Open Study Room
### Huge thanks to FluffM for coding it. Original code can be found [here](https://github.com/Thrillberg/looking-for-game-bot).

This bot so far has the following commands:

```
!LFG [minutes] - Adds the LFG role. If you are currently looking (and have the LFG role already), will remove the LFG role. Adding a number as the [minutes] will limit the number of minutes you will have the LFG role. Defaults to 1440 (1 day).

!whos_LFG - Tells you all the users who are currently looking for a game.

!info - Basic info about the bot.

!help - A list of commands.
```

To run it, you'll need to provide your own bot token, to be pulled from your shell's environment variables (`LFG_TOKEN`). In my case, I added `export LFG_TOKEN="my-token-here"` to `~/.zshenv` (since I use Z Shell).
