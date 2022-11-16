# PSI Onchain Data
This project focused on demonstrating how to interact with Substrate Blockchain nodes easily. 
The main aim is interaction with the Polkadot Defi Parachain project called Parallel Finance.

## SubstrateBlockData class 
This class provides a data model class for Substrate block data. 

## SubstrateData class
The primary purpose of this class is to provide an essential capability for blockchain data exports/imports into HTML files and relational databases.

| Method                        | Description                                        |
|-------------------------------|----------------------------------------------------| 
| **get_modules**               | Return list of Substrate Pallets (Modules)         |
| **get_storage_functions**     | Return list of available storage functions         |
| **get_call_functions**        | Return list of available call functions            |
| **get_assets**                | Return list of assets                              |
| **get_finalized_block**       | Return the last finalized Substrate block          |
| **get_last_finalized_blocks** | Return n last finalized Substrate blocks           |
| **to_html**                   | Export Pandas DataFrame into HTML file             |
| **to_sql**                    | Export Pandas DataFrame into a relational database |

## Requirements
 - Python >= 3.9
 - Psycopg2-binary >= 2.9
 - Docker Desktop >= 3.x

## Installation

- `pip install -r requirements.txt`
- `docker compose -f docker-compose.yml up -d`

## Run
- `./main.py`

## Libraries
- Pandas
  - https://pandas.pydata.org
- SQLAlchemy
  - https://www.sqlalchemy.org/
- Py-Substrate-Interface (Substrate Interface)
  - https://github.com/polkascan/py-substrate-interface
- Py-Scale-Codec 
  - https://github.com/polkascan/py-scale-codec

## Links
- Substrate - https://substrate.io/
- Polkadot - https://polkadot.network/
- Parallel Finance - https://parallel.fi/
