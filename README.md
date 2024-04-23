# NHL TV Downloader

NHL TV Downloader allows you to download NHL game videos from the NHL TV service. It automates the process of checking for new games and downloading them.

## About

The NHL TV Downloader is a Python script that interacts with the NHL TV API to find and download full game replays. It provides features such as:

- Checking for new games of your favorite team(s) at a configurable interval
- Downloading the full game replay videos
- Removing commercial breaks from the videos
- Obfuscating the true length of the video to avoid spoilers
- Keeping downloaded videos for a configurable retention period

## Installation

### With Docker

You have two options for running the NHL TV Downloader using Docker:

#### Option 1: Using the Pre-built Docker Image (easiest)

1. Install Docker on your system if you haven't already.

2. Run the Docker container using the pre-built image from GitHub Container Registry:

   ```bash
   docker run -d \
     --name dl-nhltv \
     -v /path/to/download/directory:/home/nhltv/media \
     -e NHLTV_USERNAME=your_username \
     -e NHLTV_PASSWORD=your_password \
     ghcr.io/pppontusw/dl-nhltv:latest \
     -t "Your Team Name" \
     -d media
   ```

   Replace `/path/to/download/directory` with the directory where you want the downloaded videos to be saved.

   There is also a [Docker compose example provided](Docker-compose.example)

#### Option 2: Building the Docker Image Locally

1. Install Docker on your system if you haven't already.

2. Clone this repository:

   ```bash
   git clone https://github.com/pppontusw/dl-nhltv
   ```

3. Navigate to the project directory:

   ```bash
   cd dl-nhltv
   ```

4. Build the Docker image:

   ```bash
   docker build -t nhltv .
   ```

5. Run the Docker container:

   ```bash
   docker run -d \
     --name nhltv \
     -v /path/to/download/directory:/home/nhltv/media \
     -e NHLTV_USERNAME=your_username \
     -e NHLTV_PASSWORD=your_password \
     nhltv-downloader \
     -t "Your Team" \
     -d media
   ```

   Replace `/path/to/download/directory` with the directory where you want the downloaded videos to be saved.

### With Python

You have two options for installing and running the NHL TV Downloader using Python:

#### Option 1: Installing from Wheel

1. Download the latest wheel (.whl) file from the [releases page](https://github.com/pppontusw/dl-nhltv/releases).

2. Install the wheel file using pip:

   ```bash
   pip install dl_nhltv-x.x.x-py3-none-any.whl
   ```

   Replace `x.x.x` with the version number of the downloaded wheel file.

3. Run the script:

   ```bash
   nhltv -u your_username -p your_password -t "Your Team Name"
   ```

   Provide your NHL TV username, password, and the name of your favorite team.

#### Option 2: Installing from Source

1. Clone this repository:

   ```bash
   git clone https://github.com/pppontusw/dl-nhltv
   ```

2. Navigate to the project directory:

   ```bash
   cd nhltv-downloader
   ```

3. (Optional) Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install the package using pip:

   ```bash
   pip install .
   ```

5. Run the script:

   ```bash
   nhltv -u your_username -p your_password -t "Your Team Name"
   ```

   Provide your NHL TV username, password, and the name of your favorite team.

## Usage

The NHL TV Downloader runs continuously, checking for new games at the configured interval. It will download any new full game replays it finds for the specified team(s).

You can customize the behavior using command-line arguments:

- `-u`, `--username`: Your NHL TV username (required)
- `-p`, `--password`: Your NHL TV password (required)
- `-t`, `--team`: The name or abbreviation of the team(s) you want to download games for (required, multiple teams separated by spaces)
- `-d`, `--download_folder`: The directory where downloaded videos will be saved (default: current directory)
- `-i`, `--checkinterval`: The interval in minutes to check for new games (default: 10)
- `-k`, `--keep`: The number of days to keep downloaded videos (default: forever)
- `--debug`: Enable debug mode for extra logging and debug dumps

## Developing

If you want to contribute to the development of the NHL TV Downloader or modify the code for your own purposes, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/pppontusw/dl-nhltv
   ```

2. Navigate to the project directory:

   ```bash
   cd dl-nhltv
   ```

3. Create and activate a virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install the development dependencies:

   ```bash
   pip install -r requirements.dev.txt
   ```

5. Make your desired changes to the codebase.

6. Use the provided Makefile for common development tasks:
   - Run tests:

     ```bash
     make test
     ```

   - Lint the code using pylint:

     ```bash
     make lint
     ```

   - Format the code using black:

     ```bash
     make format
     ```

   - Generate coverage report:

     ```bash
     make coverage
     ```

   - Run type checking using mypy:

     ```bash
     make type
     ```

7. Ensure that your changes pass all tests, linting, and formatting checks.

8. Submit a pull request with your changes.

The `requirements.dev.txt` file contains the additional development dependencies required for tasks such as testing, linting, and formatting. These dependencies are separate from the main project dependencies listed in `requirements.txt`.

The provided `Makefile` includes convenient targets for common development tasks, such as running tests, linting the code, formatting the code, generating coverage reports, and running type checking. You can use these targets to ensure code quality and consistency.

Feel free to explore the codebase, make improvements, and submit pull requests to contribute to the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.
