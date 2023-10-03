# sipecam-deployments

A tool for deployment information merging based on a zendro/kobo database setting.

# Install

Navigate to repository directory then:
```
python -m pip install .
```
# Usage
For command line stdout ouput:
```
python fetch.py
```
For command line output to file:
```
python fetch.py --output=/path/to/destination.json
```
Using as a python module:
```
from sipecamDeployments.fetch import current_kobo_deployments

depls = current_kobo_deployments()
```



