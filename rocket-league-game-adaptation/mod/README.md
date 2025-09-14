# Rocket League Mod

This folder contains the source code for a custom [BakkesMod](https://www.bakkesmod.com) plugin used to extract game state information from Rocket League and send it to the GamePals Framework.

## Prerequisites

To compile this plugin, you need:

- Visual Studio 2022 with support for C++ development installed.
- Rocket League installed from the Epic Games Store.
- BakkesMod installed.

### What is BakkesMod?

BakkesMod is a community-created modding framework for Rocket League, widely used for plugin development and training tools.
Download it from the official website: [https://www.bakkesmod.com/](https://www.bakkesmod.com/)

### How to install Rocket League (Epic Games)

Download and install Rocket League via the Epic Games Store.

Once installed, open the Rocket League section in the Epic Games Store settings, check `Additional Command Line Arguments`, and add the following launch option:

```bash
-dev
```

This enables developer mode, which is necessary for the BakkesMod plugins to work correctly.

## Building the Plugin

1. Open the project in Visual Studio 2022.

2. Build the solution in Release x64 configuration.

3. After compilation, you will obtain a file called `RocketLeagueGameStateParser.dll`

## Installation

1. Open BakkesMod.
2. In the BakkesMod menu bar, go to `File > Open BakkesMod Folder`.
3. Navigate to the `bakkesmod/plugins/` directory.
4. Copy the compiled `RocketLeagueGameStateParser.dll` into that folder.

### Auto-load the Plugin on Startup

To ensure the plugin is loaded automatically every time you launch Rocket League:

1. Open the following file inside the BakkesMod folder:

```bash
bakkesmod/cfg/plugins.cfg
```

2. Add this line at the end:

```bash
plugin load rocketleaguegamestateparser
```

Make sure the filename is lowercase and matches the DLL name without the .dll extension.
