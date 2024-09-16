# MarCNoWA Flask App

This project is a Flask-based application for the MarCNoWA initiative. Follow the instructions below to set up your development environment and install the necessary dependencies.

## Project Setup

### Create an Environment

To get started, you need to create a project folder and a virtual environment. 

#### macOS/Linux

1. Open your terminal.
2. Run the following commands:

    ```bash
    mkdir myproject
    cd myproject
    python3 -m venv .venv
    ```

#### Windows

1. Open Command Prompt or PowerShell.
2. Run the following commands:

    ```cmd
    mkdir myproject
    cd myproject
    py -3 -m venv .venv
    ```

### Activate the Environment

Activate the virtual environment to ensure that you're working within the correct environment.

#### macOS/Linux

1. In your terminal, run:

    ```bash
    . .venv/bin/activate
    ```

#### Windows

1. In Command Prompt or PowerShell, run:

    ```cmd
    .venv\Scripts\activate
    ```

Your shell prompt will change to show the name of the activated environment.

### Install Flask

With the environment activated, install Flask by running:

```bash
pip install Flask
