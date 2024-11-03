# Volatenium

A simple algorithm-based python crypto trader

# Installation

1. Download the repo with either:
    * git: `git clone https://github.com/Aegeontis/Volatenium.git`
    * as zip: https://github.com/Aegeontis/Volatenium/archive/main.zip
2. Initiate a python venv: `python -m venv venv`
3. Enter the python venv: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Create a settings.json file. Example below:

```
{
  "enabled_algorithms": [
    {
      "name": "safe_sale",
      "enabled_exchanges": [
        "simulator"
      ]
    }
  ]
}
```

# Usage

##### Normal usage

1. Enter the python venv: `source venv/bin/activate`
2. Start the script: `python main.py`

##### Generate graph

1. Enter the python venv: `source venv/bin/activate`
2. Start the script: `python main.py --generate-graph`