* Update the version number to the setup.py-file.
* Run following commands:

    ```
    rm -rf dist/
    python setup.py bdist_wheel
    twine upload dist/*
    ```    
