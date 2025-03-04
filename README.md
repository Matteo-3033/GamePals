# Video Games Copilot Architecture

This repository defines a **Video Games Copilot Architecture**, a flexible framework that enables shared control over a game instance.
The architecture is built around a **Command Arbitrator**, which merges inputs from multiple **Actors** — either human
players or software agents — into a single control stream.

## Project Structure

- **agents/** – Defines the core **Actor** classes, including **Human Actors** (physical controllers) and **Software Agent Actors** (extendable for AI-based control).

- **command\_arbitrators/** – Implements the **Command Arbitrator**, responsible for merging inputs from multiple Actors, and a **Policy Manager** that handles arbitration policies.

- **sources/** – Manages physical and virtual input handling, including a **Physical Controller Listener**, a **Virtual Controller Provider**, and a **Game State Listener**.

- **utils/** – Contains utility functions, such as an **argument parser**.

This architecture is designed for flexibility, allowing seamless integration of multiple human and AI-controlled inputs
to enhance accessibility and gameplay experiences.

![Copilot Architecture](assets/architecture.png)

## Requirements and Setup

To run the architecture successfully, the following tools and packages are required:

- **Windows OS** - The architecture is currently only available for Windows.

- A **Physical GamePad** - This can either be an XBOX Controller or a DualShock Controller (for the latter, [**DS4Windows**](https://ds4-windows.com/) is also a requirement).

- [**HidHide**](https://ds4-windows.com/download/hidhide/) - A tool used to hide the physical controller from the game, ensuring the game receives only inputs from a Virtual Controller.

- [**Python 3.13**](https://www.python.org/downloads/release/python-3130/) - The latest Python version as of February 2025.

- ```requirements.txt``` - The required Python packages can be installed using:
    ```bash
    pip install -r requirements.txt
    ```

## Arbitrator's Configuration

TODO: Specify how do build a config.toml
Give a look at config.toml.example