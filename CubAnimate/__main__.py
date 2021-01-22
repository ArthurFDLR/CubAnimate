## DO NOT USE RELATIVE IMPORTS HERE TO USE PYINSTALLER
## To compile use 'pyinstaller --onefile --windowed --noconsole --icon="resources/icon.ico" --name="CubAnimate" __main__.py'
from CubAnimate import app

if __name__ == '__main__':
    app.run()