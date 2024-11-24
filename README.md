# Flow2Code

Flow2Code is a Python script designed to convert Draw.io diagrams into executable Python code. The purpose of the tool is to take visual flowcharts, parse them, and generate the corresponding code structure dynamically.

## Requirements

Before running Flow2Code, ensure you have the following requirements:

- Python 3.13.0 or later

Additionally, libraries listed in `requirements.txt` need to be installed. The script will handle the installation of these dependencies automatically.

## Installation

1. **Clone the repository**:
    ```sh
    git clone <repository_url>
    cd <repository_dir>
    ```

2. **Create and activate your virtual environment (optional but recommended)**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install required packages**:
   The script automatically installs required packages listed in the `requirements.txt`.

## Usage

1. **Prepare your Draw.io file**:
    - Create or obtain a Draw.io file representing the flowchart you wish to convert.

2. **Run the script**:
    ```sh
    python flow2code.py
    ```

3. **Input the path to your Draw.io file**:
    - You will be prompted to enter the path to your Draw.io file. Ensure the path is correctly formatted.

4. **Generate Python code**:
    - The script processes the input Draw.io file, maps the labels to edges, and generates the corresponding Python code blocks. The final code is printed to the console.

## Example

```sh
$ python flow2code.py
enter path to drawio file: path/to/your/diagram.drawio
```

The script will output the generated Python code based on the provided flowchart.


## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

---

Happy coding! 🚀

---
