# mbti-type-from-text
## Installation
1. Create an Anaconda environment with Python 3.9:
```
conda create --name mbti-type-from-text python=3.9
```

2. Activate the environment:
```
conda activate mbti-type-from-text
```

3. Install the requirements:
```
pip install -r requirements.txt
```

4. If you are a developer, enable automatic code formatting with:
```
pre-commit install
```

## Download data
This project uses [DVC](https://dvc.org/) to manage data. The data is stored on a Google Drive remote. You need to ask for access.

To download the data, run: 
```
dvc pull
```
