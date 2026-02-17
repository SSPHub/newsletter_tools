
def fetch_grist_table_as_pl(doc_grist_id, table_id):
    """
    Get a grist table as a polar dataframe. It transforms Grist records :
    - If the value is a list (not a tuple) and the first element is 'L', we want an
      array of all elements 1...end

    Args:
        doc_grist_id : id of the grist document
        table_id (string) : id of the Grist table

    Return:
        A pl dataframe
    """
    grist_api = get_dinum_grist_login(doc_grist_id)
    table_grist_records = grist_api.fetch_table(table_id)
    table_dict = [record._asdict() for record in table_grist_records]

    # Cleaning Grist lists - causes a pb with polars. from
    # https://github.com/uaw-union/sheets-parquet-server/blob/19acaa3ef9ab65f9229b3df5e7007b8cc1fffca0/src/main.py#L4
    transformed_records = [
        {
            k: (
                ";".join([str(s) for s in v])
                if isinstance(v, list) and len(v) > 0
                else v
            )
            for k, v in d.items()
        }
        for d in table_dict
    ]

    return pl.DataFrame(transformed_records, infer_schema_length=None)


def get_dinum_grist_login(doc_grist_id):
    """
    Send back GRIST API login details

    Args:
        None

    Returns:
        A GristDocAPI object
    """
    # Log in to GRIST API
    SERVER = "https://grist.numerique.gouv.fr/"

    if "GRIST_API_KEY" not in os.environ:
        raise ValueError("The GRIST_API_KEY environment variable does not exist.")

    # Returning API details connection
    return GristDocAPI(doc_grist_id, server=SERVER)

