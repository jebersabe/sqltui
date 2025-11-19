import os
from odps import ODPS
from dotenv import load_dotenv


def odps_from_env(
    id_key="ODPS_ID",
    secret_key="ODPS_SECRET",
    project_key="ODPS_PROJECT",
    endpoint="https://service.ap-southeast-1.maxcompute.aliyun.com/api",
):
    """
    Create an ODPS instance from credentials stored
    in the environment variables.

    Parameters
    ----------
    id_key : str
        Environment variable key for ODPS access_id.
    secret_key : str
        Environment variable key for ODPS secret_access_key.
    project : str
        DaaS environment.
    endpoint : str
        Database endpoint.

    Returns
    -------
    ODPS
        An instance of ODPS.
    """
    load_dotenv()
    return ODPS(
        os.getenv(id_key),
        os.getenv(secret_key),
        os.getenv(project_key),
        endpoint=endpoint,
    )
