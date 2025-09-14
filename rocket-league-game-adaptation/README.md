# GamePals Game Adaptation For Rocket League

This folder contains the game adaptation for the game **Rocket Leauge** built on top of the [GamePals Framework](../README.md).

## Requirements

To run the game adaptation, you need the following tools installed:

- [BakkesMod](https://www.bakkesmod.com/) with a specific mod used to interface with Rocket League.
  Refer to the [README in the mod folder](mod) for installation and setup instructions.

- [HidHide](https://github.com/nefarius/HidHide): this tool is required to hide all physical controllers from Rocket League, leaving only the virtual one created by this software visible.
  Install HidHide and configure it to exclude all controllers except the virtual controller from Rocket League.

## Usage

To run the full system, follow these steps in order:

- Start the GamePals software without connecting any controller.

- Launch HidHide and make sure only the virtual controller is visible to Rocket League (i.e., hide all physical controllers).

- Start BakkesMod, along with the Rocket League plugin provided in the [mod](mod) folder.

- Launch Rocket League.

- Once the game is running and the mod is loaded, plug in your controller.

- Confirm from the terminal that the controller is correctly recognized and mapped by the GamePals software.

To execute the software, you can also use the following command:

```bash
python main.py -gc ./config/game.toml -agc ./config/agents.toml -asc ./config/assistance.toml
```

The three configuration files in the command specify, respectively:

- The interface with the game (game.toml),
- The agent behaviors (agents.toml),
- The shared control setup (assistance.toml).

Refer to the [GamePals Framework README](https://gitlab.di.unimi.it/ewlab/accessibility/gamepals/gamepals-framework/-/blob/main/README.md) for more information on how to customize these configuration files.

For convenience, a [run.bat](run.bat) script is also provided. It accepts two command-line arguments:

```bash
run.bat path\to\assistance.toml [output_log_filename.ndjson]
```

- The first argument is the path to the assistance.toml file.
- The second argument is optional and defines the filename where logs will be saved.

This script simplifies launching the system with custom configurations.

## Acknowledgements

The software agents used in this adaptation are based on the Nexto bot: [https://github.com/Rolv-Arild/Necto](https://github.com/Rolv-Arild/Necto)
