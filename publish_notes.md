* Update the version number to the setup.py-file.
* If there is no virtual environment, create it:
    ```
    virtualenv venv -p /usr/bin/python3
    source venv/bin/activate
    pip install twine
    ```
* Run following commands:

    ```
    rm -rf dist/
    ./setup.py sdist bdist_wheel
    twine upload dist/*
    ```    
