# Volatenium

A simple algorithm-based python crypto trader

## Installation

1. Download the repo with either:
    * git:
        1. `git clone https://github.com/Aegeontis/Volatenium.git`
        2. `cd Volatenium`
    * as zip:
        1. Download https://github.com/Aegeontis/Volatenium/archive/refs/heads/main.zip
        2. `unzip Volatenium-main.zip`
        3. `cd Volatenium-main`
2. Initiate a python venv: `python -m venv venv`
3. Enter the python venv: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Create a settings.json file. Example below:

```
{
  "enabled_algorithms": [
    {
      "name": "SafeTrade",
      "enabled_exchanges": [
        {
          "Simulator": {
            "crypto_codename": "BTC-EUR",
            "exchange_fee": 0.001,
            "wallet_crypto_amount": 0,
            "wallet_fiat_amount": 100.0
          }
        },
        {
          "Simulator": {
            "crypto_codename": "SHIB-EUR",
            "exchange_fee": 0.001,
            "wallet_crypto_amount": 0,
            "wallet_fiat_amount": 100.0
          }
        }
      ]
    }
  ]
}
```

## Usage

##### Normal usage

1. Enter the python venv: `source venv/bin/activate`
2. Start the script: `python main.py`

##### Generate graph

1. Enter the python venv: `source venv/bin/activate`
2. Start the script: `python main.py --generate-graph`
