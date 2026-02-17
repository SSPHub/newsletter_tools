import os
# from grist_api import GristDocAPI
import requests
import polars as pl

class GristApi:
    def __init__(self, doc_id=os.environ["GRIST_VEILLE_DOC_ID"]):
        if "GRIST_API_KEY" not in os.environ:
            raise ValueError("The GRIST_API_KEY environment variable does not exist.")

        self.base_url = "https://grist.numerique.gouv.fr/api"

        self.doc_url = f"{self.base_url}/docs"

        self.table_url = f"{self.doc_url}/{doc_id}/tables"

        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {os.environ['GRIST_API_KEY']}",
            "Content-Type": "application/json",
        }

    def fetch_table(self, table_id, **kwarg):
        """
        Wrapper for a GET requests

        Args:
            The grist table id
            Additionnal arguments to pass on to requets.get()

        Returns:
            response from requests.get

        Example:
        >>> GristApi().fetch_table("Test")
        <Response [200]>
        """
        response = requests.get(
            f"{self.table_url}/{table_id}/records", headers=self.headers, **kwarg
        )
        return response

    def fetch_table_pl(self, table_id, **kwarg) -> pl.DataFrame:
        """
        Fetch data from a Grist table

        Args:
            The grist table id


        Returns:
            the table from Grist as a Polars DataFrame

        Example:
        >>> GristApi().fetch_table_pl("Test")
        """
        return (
            pl.DataFrame(
                self.fetch_table(table_id=table_id, **kwarg).json(),
                infer_schema_length=None,
                strict=False,
            )
            .unnest(columns="records")
            .unnest(columns="fields")
        )

    def add_records(self, table_id, **kwarg):
        """
        Wrapper for a POST requests to add records to a table.
        Records should have a particuliar format to get accepted by GRIST API

        Args:
            The grist table id
            Additionnal arguments to pass on to requets.post()

        Returns:
            response from requests.post

        Example:
        >>> GristApi().add_records("Test", json=data_json)
        <Response [200]>
        """
        response = requests.post(
            f"{self.table_url}/{table_id}/records", headers=self.headers, **kwarg
        )
        return response

    def delete_records(self, table_id, **kwarg):
        """
        Wrapper for a POST requests to delete records from a table.
        Records to delete should be identified by a list of their ids

        Args:
            The grist table id
            Additionnal arguments to pass on to requets.post()

        Returns:
            response from requests.post

        Example:
        >>> GristApi().delete_records("Test", json=data_json)
        <Response [200]>
        """
        response = requests.post(
            f"{self.table_url}/{table_id}/records/delete", headers=self.headers, **kwarg
        )
        return response

#     # Cleaning Grist lists - causes a pb with polars. from
#     # https://github.com/uaw-union/sheets-parquet-server/blob/19acaa3ef9ab65f9229b3df5e7007b8cc1fffca0/src/main.py#L4
#     transformed_records = [
#         {
#             k: (
#                 ";".join([str(s) for s in v])
#                 if isinstance(v, list) and len(v) > 0
#                 else v
#             )
#             for k, v in d.items()
#         }
#         for d in table_dict
#     ]

#     return pl.DataFrame(transformed_records, infer_schema_length=None)


# def get_dinum_grist_login(doc_grist_id):
#     """
#     Send back GRIST API login details

#     Args:
#         None

#     Returns:
#         A GristDocAPI object
#     """
#     # Log in to GRIST API
#     SERVER = "https://grist.numerique.gouv.fr/"

#     if "GRIST_API_KEY" not in os.environ:
#         raise ValueError("The GRIST_API_KEY environment variable does not exist.")

#     # Returning API details connection
#     return GristDocAPI(doc_grist_id, server=SERVER)

