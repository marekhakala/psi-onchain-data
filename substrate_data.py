import json
import pandas as pd
from typing import Optional
from decimal import Decimal
from sqlalchemy import create_engine
from substrateinterface import SubstrateInterface


class SubstrateBlockData:
    def __init__(self, data: dict):
        self.values = {}
        self._data = data

        self.header_fields = ["hash", "parentHash", "number",
                              "stateRoot", "extrinsicsRoot"]
        self.fields_list = ["extrinsics", "events", "logs"]

        self._extract_header()
        if "extrinsics" in self._data:
            self._set_value("extrinsics", self._extract_list(self._data["extrinsics"]))

    def _extract_header(self):
        if "header" in self._data:
            for field in self.header_fields:
                if field in self._data["header"]:
                    self._set_value(f"header_{field}", self._data["header"][field])

            if "digest" in self._data["header"] \
                    and "logs" in self._data["header"]["digest"]:
                self._set_value("logs", self._extract_list(self._data["header"]["digest"]["logs"]))

        return None

    @staticmethod
    def _extract_list(data: list):
        results = []

        for record in data:
            results.append(record.value)

        return results

    def set_events(self, data: list):
        self._set_value("events", self._extract_list(data))

    def _set_value(self, name: str, value):
        self.values[name] = value

    def to_dict(self):
        results = {}

        for field in self.header_fields:
            results[f"header_{field}"] = self.values[f"header_{field}"]

        for field in self.fields_list:
            results[field] = json.dumps(self.values[field])

        return results


class SubstrateData:
    def __init__(self, config: dict):
        self._config = config

        self._url = config["url"]
        self._ss58_format = config["ss58_format"] if "ss58_format" in config else None
        self._chain = config["chain"] if "chain" in config else None
        self._type_registry = config["type_registry"] if "type_registry" in config else None
        self._client = None

    def client(self):
        if self._client is None:
            self._client = SubstrateInterface(
                url=self._url,
                ss58_format=self._ss58_format,
                type_registry_preset=self._chain,
                type_registry=self._type_registry)

        return self._client

    @staticmethod
    def to_sql(table_name: str, data: pd.DataFrame,
               connection_string: str = None, if_exists: str = "replace"):
        if connection_string is None:
            connection_string = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"

        engine = create_engine(connection_string)
        return data.to_sql(table_name, engine, index=False, if_exists=if_exists)

    @staticmethod
    def to_html(filename: str, data: pd.DataFrame, file_prefix: str = "./outputs"):
        return data.to_html(open("{}/{}.html".format(file_prefix, filename), "w"))

    def _get_query_map(self, module: str, storage_function: str, columns: list,
                       params: Optional[list] = None, block_hash: str = None):
        result = self.client().query_map(module=module, storage_function=storage_function,
                                         params=params, block_hash=block_hash)

        data = {}
        for res in result:
            if len(res) >= 2:
                record = {}
                for column in columns:
                    if column in res[1].value:
                        record[column] = res[1].value[column]

                data[res[0].value] = record

        return data

    @staticmethod
    def _merge_assets_data(supply: dict, metadata: dict) -> dict:
        results = {}
        for asset_id in metadata.keys():
            results[asset_id] = metadata[asset_id]

        for asset_id in supply.keys():
            for column in supply[asset_id].keys():
                results[asset_id][column] = supply[asset_id][column]

            divide = Decimal(10 ** results[asset_id]["decimals"])
            results[asset_id]["supply"] = Decimal(results[asset_id]["supply"]) / divide

        return results

    def get_assets(self, block_hash=None) -> pd.DataFrame:
        supply_columns = ["owner", "supply",
                          "min_balance", "is_frozen"]
        supply = self._get_query_map("Assets", "Asset",
                                     supply_columns, block_hash=block_hash)

        metadata_columns = ["deposit", "name", "symbol", "decimals"]
        metadata = self._get_query_map("Assets", "Metadata",
                                       metadata_columns, block_hash=block_hash)

        data = self._merge_assets_data(supply, metadata)

        output = []
        for key in data.keys():
            record = {"asset_id": key}
            record.update(data[key])
            output.append(record)

        return pd.DataFrame(output)

    def get_storage_functions_params(self, functions: list, block_hash=None) -> list:
        for func in functions:
            store_func = self._client.get_metadata_storage_function(func["module_name"],
                                                                    func["storage_name"],
                                                                    block_hash=block_hash)
            try:
                func["params"] = str(store_func.get_param_info())
            except TypeError:
                func["params"] = str([])

        return functions

    def get_modules(self, block_hash=None) -> pd.DataFrame:
        modules = self.client().get_metadata_modules(block_hash=block_hash)

        output = []
        for module in modules:
            output.append({"chain": self._config["name"], "module": module["name"]})

        df = pd.DataFrame(output)
        return df

    def get_constants(self, block_hash=None) -> pd.DataFrame:
        columns = ["module_name", "constant_name", "constant_value", "documentation"]
        functions = self.client().get_metadata_constants(block_hash=block_hash)

        df = pd.DataFrame(functions)
        df["constant_value"] = df["constant_value"].apply(lambda x: str(x))

        return df[columns]

    def get_storage_functions(self, params: bool = False, block_hash=None) -> pd.DataFrame:
        columns = ["module_name", "storage_name", "storage_modifier",
                   "storage_default", "documentation", "type_class"]

        functions = self.client().get_metadata_storage_functions(block_hash=block_hash)

        if params:
            columns.append("params")
            functions = self.get_storage_functions_params(functions, block_hash=block_hash)

        df = pd.DataFrame(functions)[columns]
        df["storage_default"] = df["storage_default"].apply(lambda value: str(value))
        df["storage_modifier"] = df["storage_modifier"].apply(lambda value: str(value))

        return df[columns]

    def get_call_functions(self, block_hash=None) -> pd.DataFrame:
        columns = ["module_name", "call_name", "call_args", "documentation"]
        functions = self.client().get_metadata_call_functions(block_hash=block_hash)

        df = pd.DataFrame(functions)
        df["call_args"] = df["call_args"].apply(lambda x: str(x))

        return df[columns]

    def get_finalized_head(self):
        block_number = None
        response = self.client().rpc_request("chain_getFinalizedHead", [])

        if response is not None:
            block_number = response.get("result")

        return block_number

    def get_finalized_block(self):
        block_hash = self.get_finalized_head()
        return self.client().get_block(block_hash=block_hash)

    def get_finalized_block_head_number(self):
        block_hash = self.get_finalized_head()
        block = self.client().get_block(block_hash=block_hash)

        if "header" in block and "number" in block["header"]:
            return block["header"]["number"]
        return None

    def get_last_finalized_blocks(self, count: int = 10):
        block_number_end = self.get_finalized_block_head_number()
        block_number_start = block_number_end - count + 1
        blocks = self.get_finalized_blocks(block_number_start, block_number_end)
        return blocks

    def get_finalized_blocks(self, block_number_start: int, block_number_end: int):
        results = []

        block_number_current = block_number_start
        while block_number_current <= block_number_end:
            block = self.client().get_block(block_number=block_number_current)
            block_data, block_events = SubstrateBlockData(block), []

            if "header_hash" in block_data.values:
                block_events = self.client().get_events(block_data.values["header_hash"])

            block_data.set_events(block_events)
            results.append(block_data)
            block_number_current += 1

        return pd.DataFrame([block.to_dict() for block in results])
