#! /usr/bin/env python3
import logging
from substrate_data import SubstrateData


def store_metadata(client: SubstrateData, chain: str = "unknown"):
    modules = client.get_modules()
    name = "modules_{}".format(chain)
    logging.info(f"Storing file data {name} ...")
    SubstrateData.to_html(name, modules)

    storage_functions = client.get_storage_functions()
    name = "storage_functions_{}".format(chain)
    logging.info(f"Storing file data {name} ...")
    SubstrateData.to_html(name, storage_functions)

    call_functions = client.get_call_functions()
    name = "call_functions_{}".format(chain)
    logging.info(f"Storing file data {name} ...")
    SubstrateData.to_html(name, call_functions)

    constants = client.get_constants()
    name = "constants_{}".format(chain)
    logging.info(f"Storing file data {name} ...")
    SubstrateData.to_html(name, constants)

    assets = client.get_assets()
    name = "assets_{}".format(chain)
    logging.info(f"Storing file data {name} ...")
    SubstrateData.to_html(name, assets)


def store_metadata_sql(client: SubstrateData, chain: str = "unknown",
                       if_exists: str = "replace", block_hash=None):
    modules = client.get_modules(block_hash=block_hash)
    name = "modules_{}".format(chain)
    logging.info(f"Storing file data {name} ...")
    SubstrateData.to_sql(name, modules, if_exists=if_exists)

    storage_functions = client.get_storage_functions(block_hash=block_hash)
    name = "storage_functions_{}".format(chain)
    logging.info(f"Storing table data {name} ...")
    SubstrateData.to_sql(name, storage_functions, if_exists=if_exists)

    call_functions = client.get_call_functions(block_hash=block_hash)
    name = "call_functions_{}".format(chain)
    logging.info(f"Storing table data {name} ...")
    SubstrateData.to_sql(name, call_functions, if_exists=if_exists)

    constants = client.get_constants(block_hash=block_hash)
    name = "constants_{}".format(chain)
    logging.info(f"Storing table data {name} ...")
    SubstrateData.to_sql(name, constants, if_exists=if_exists)

    assets = client.get_assets(block_hash=block_hash)
    name = "assets_{}".format(chain)
    logging.info(f"Storing table data {name} ...")
    SubstrateData.to_sql(name, assets, if_exists=if_exists)


def store_last_finalized_blocks_sql(client: SubstrateData, chain: str = "unknown",
                                    if_exists: str = "replace", count: int = 10):

    blocks = client.get_last_finalized_blocks(count)
    name = "blocks_{}".format(chain)
    logging.info(f"Storing table data {name} ...")
    SubstrateData.to_sql(name, blocks, if_exists=if_exists)


def get_map_chains():
    return {
        "parallel-heiko": {
            "name": "Parallel-Heiko",
            "url": "wss://heiko-rpc.parallel.fi",
            "native_token": "HKO",
            "decimals": 12
        }
    }


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    chains = get_map_chains()
    for chain in chains.keys():
        client = SubstrateData(config=chains[chain])
        store_metadata(client, chain)
        store_metadata_sql(client, chain)
        store_last_finalized_blocks_sql(client, chain, count=15)

    exit(0)
