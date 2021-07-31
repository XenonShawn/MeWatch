# MeWatch Remote Controller
A small project which helps my grandmother watch MeWatch shows using a phone application.

## Installation and requirements
This project uses Selenium python and FastAPI. Install the dependencies and run the program using
```bash
uvicorn main:app --host 0.0.0.0
```
Ensure that the chrome web driver is installed in the same directory.

## Usage
A phone application made using MIT App Inventor (currently not in the repository) interfaces with the web server to control Selenium.