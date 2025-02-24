# Video Games Copilot Architecture

This repository defines a **Video Games Copilot Architecture**, a flexible framework that enables shared control over a game instance.   
The architecture is built around a **Command Arbitrator**, which merges inputs from multiple **Actors** — either human 
players or software agents — into a single control stream.

## Project Structure

- **agents/** – Defines the core **Actor** classes, including **Human Actors** (physical controllers) and **Software Agent Actors** (extendable for AI-based control). Also contains an **observers/** submodule for tracking actor, controller, and game state inputs.

- **command\_arbitrators/** – Implements the **Command Arbitrator**, responsible for merging inputs from multiple Actors, and a **Policy Manager** that handles arbitration policies.

- **doom/** – Implements Doom-specific agents, including **Copilots** (extensions of the **Software Agent Actor**) and a **Doom State Listener** for game state monitoring.

- **sources/** – Manages physical and virtual input handling, including a **Physical Controller Listener**, a **Virtual Controller Provider**, and a **Game State Listener**.

This architecture is designed for flexibility, allowing seamless integration of multiple human and AI-controlled inputs 
to enhance accessibility and gameplay experiences.

![Copilot Architecture](assets/architecture.png)

