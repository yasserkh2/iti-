# DocGenAI
An assistant to help you build your dream app and generate SRS documents!
## How to use
1. Set up the API configurations (see below). 
2. To run the demo webapp:<br>
`gradio app.py`

## API configuration
### 1. VertexAI
1. Create credentials json file from GCP project
2. Save the json file on the environment the app will be run from (local machine, cloud VMs, etc)
3. export path to the credentials json file to **GOOGLE_APPLICATION_CREDENTIALS** environment variable. e.g. from terminal:
```
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your_credentials_file.json
```

## Python version: 3.10.6
