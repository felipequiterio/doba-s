# DOBA-S: Dynamic Orchestration of Behavior Agents System

DOBA-S is an intelligent task management system that dynamically routes user queries to appropriate agents for execution. It's designed to handle a variety of tasks, from simple to-do list management to complex multi-step processes.

## Features

- Dynamic task routing based on user queries
- Multiple specialized agents for different types of tasks
- Robust error handling and task validation
- Asynchronous task execution capability
- Extensible architecture for adding new agents and functionalities

## Prerequisites

- Windows Subsystem for Linux (WSL) installed and configured
- Docker installed and running

## Installation

1. Install the uv Python package manager:
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository:
   ```
   git clone https://github.com/yourusername/doba-s.git
   cd doba-s
   ```

3. Set up a virtual environment:
   ```
   uv venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

4. Install the required packages:
   ```
   uv sync
   ```

5. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   MODEL=your_model_name
   ```

## Adding new packages

To add new packages to the project, use:
