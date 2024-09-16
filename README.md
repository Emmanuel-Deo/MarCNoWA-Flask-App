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

### Install Packages

If you have a `requirements.txt` file that lists all necessary packages, you can use it to install the dependencies in your virtual environment.

1. Ensure that your virtual environment is activated.
2. Run the following command to install the packages listed in `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

   This command will install all the packages and their specific versions as listed in the `requirements.txt` file.

### Install Flask

If you don’t have a `requirements.txt` file, you can manually install Flask by running:

```bash
pip install Flask
