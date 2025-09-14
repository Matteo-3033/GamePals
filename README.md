# GamePals Framework

This repository defines **GamePals**, a flexible framework that enables shared control over a game instance.
The architecture is built around a **Command Arbitrator**, which merges inputs from multiple **Actors** — either human
players or software agents — into a single control stream.

## Project Structure

-   [**agents/**](gamepals/agents) – Defines the core **Actor** classes, including **Human Actors** (physical controllers) and **Software Agent Actors** (extendable for AI-based control).

-   [**command_arbitrators/**](gamepals/command_arbitrators) – Implements the **Command Arbitrator**, responsible for merging inputs from multiple Actors, and a **Policy Manager** that handles arbitration policies.

-   [**sources/**](gamepals/sources) – Manages physical and virtual input handling, including a **Physical Controller Listener**, a **Virtual Controller Provider**, and a **Game State Listener**.

-   [**utils/**](gamepals/utils)– Contains utility functions, such as an **argument parser**.

This architecture is designed for flexibility, allowing seamless integration of multiple human and AI-controlled inputs
to enhance accessibility and gameplay experiences.

![Framework architecture](assets/gamepals.png)

## Requirements and Setup

To run the architecture successfully, the following tools and packages are required:

-   **Windows OS** - The architecture is currently only available for Windows.

-   A **Physical GamePad** - This can either be an Xbox Controller or a DualShock Controller (for the latter, [**DS4Windows**](https://ds4-windows.com/) is also a requirement).

-   [**HidHide**](https://ds4-windows.com/download/hidhide/) - A tool used to hide the physical controller from the game, ensuring the game receives only inputs from a Virtual Controller.

-   [**Python 3.13**](https://www.python.org/downloads/release/python-3130/) - The latest Python version as of February 2025.

-   `requirements.txt` - The required Python packages can be installed using:
    ```bash
    pip install -r requirements.txt
    ```

## Arbitrator's Configuration

The infrastructure's configuration requires 3 different configuration files:

1. [`game.toml`](config.example/game.toml.example), which contains all the information about the game for which the infrastructure is being used.
   In particular, in this file are stored the inputs that the game recognizes and to which actions they are mapped. What is written in this file should match what the game settings look like.
2. [`agents.toml`](config.example/agents.toml.example), which contains all the information about the known software agents for the game. Each declared agent should explicitly report what game actions they are able to control and which parameters and commands they are able to understand.
3. [`assistance.toml`](config.example/assistance.toml.example), which contains all the information about how the arbitration should actually happen. In particular, this file contains:
    - For every game action, which Human Actors and Software Agent Actors are allowed to execute it and to what extent.
    - For every game action, which arbitration policy should be used to merge the actor inputs.
    - Which inputs are associated with the agent's meta-commands.
    - Eventually, special Software Agent Actors that don't handle any action.

An example for each of these files can be found in the [config](config.example) folder.

## Command Line Arguments

The infrastructure requires, as command line arguments, the paths to the 3 configuration files specified in the section above.
When writing your own implementation of the infrastructure, it's suggested to create an argument parser that extends the `ArgParser` class from the infrastructure itself.
By overriding the method `_add_arguments` you can easily introduce new command line arguments for your specific use cases.

Executing the program implementing the infrastructure will look something like this:

```bash
python main.py -gc ./config/game.toml -agc ./config/agents.toml -asc ./config/assistance.toml # your args here...
```

## Build and Installation

To build the project, you will first need to install the build package:

```bash
pip install build
```

Once the build package is installed, run the following command to generate the build artifacts:

```bash
python -m build
```

This will create two folders: `dist/` and `GamePals.egg-info/`. Inside the dist folder, you will find a file named `gamepals-<version>-py3-none-any.whl`, which can be used to install the package locally using pip:

```bash
pip install <path to the whl file>
```
