import logging
logger = logging.getLogger(__name__)

try:
    import requests
except:
    logger.info(
        "Did not import requests. This is expected if you are not using this module. If you want to make use of functions using this module please install the [video], [full] or [dev] extras."
    )
STAGE_URL = "http://stage.aiscout.io"
PROD_URL = "https://secure.aiscout.io"


def app_login(email: str,  password: str, person: str, env="stage"):
    """Logs in a player or coach (user) and returns the response object.

    Args:
        email (str): Email of the player.
        password (str): Password of the player.
        person (str): Type of user - player or coach
        env (str, optional): Enviroment to target. Defaults to "stage".

    Raises:
        ValueError: If env is not "stage" or "prod".

    Returns:
        response: Response object from the request.
    """

    if person == "player":
        user_login = "players"
    elif person == "user" or person == "coach":
        user_login = "users"

    if env not in ["stage", "prod"]:
        raise ValueError(f"env must be 'stage' or 'prod', not {env}")
    if env == "stage":
        data = {"email": email, "password": password, "fcmToken": "fcmToken"}
        logger.debug(f"Data for login request: {data}")
        response = requests.post(f"{STAGE_URL}/api/v2/{user_login}/login", json=data)
    else:
        response = requests.post(f"{PROD_URL}/api/v2/{user_login}/login", json={"email": email, "password": password, "fcmToken": "fcmToken"})
    logger.debug(f"Response from login: {response.json()}")
    return response


def refresh_tokens(user_id: int, env: str = "stage"):
    """Refreshes the tokens for a user.

    Args:
        user_id (int): ID of the user.
        bearer_token (str): Bearer token of the user.
        env (str, optional): The environment to target. Defaults to "stage".

    Raises:
        ValueError: If env is not "stage" or "prod".

    Returns:
        response: Response object from the request.
    """
    # headers = {"Authorization": f"Bearer {bearer_token}"}

    if env not in ["stage", "prod"]:
        raise ValueError(f"env must be 'stage' or 'prod', not {env}")

    url = f"{STAGE_URL if env == 'stage' else PROD_URL}/api/v2/users/{user_id}/refreshtokens"
    return requests.post(url, headers={})



def get_presigned_upload_url(
    bearer_token: str, file_entity_type: int = 30, file_media_type: int = 2, mime_type: str = "video/mp4", env: str = "stage"
):
    """Gets a presigned upload url for a video.

    Args:
        bearer_token (str): Bearer token of the player from login.
        file_entity_type (int, optional): Type of file entity. Defaults to 2.
        file_media_type (int, optional): The type of media. Defaults to 2.
        mime_type (str, optional): The mime type of the file. Defaults to "video/mp4".
        env (str, optional): The enviroment to target. Defaults to "stage".

    Raises:
        ValueError: If env is not "stage" or "prod".

    Returns:
        response: Response object from the request.
    """
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"fileEntityType": file_entity_type, "fileMediaType": file_media_type, "mimeType": mime_type}

    if env not in ["stage", "prod"]:
        raise ValueError(f"env must be 'stage' or 'prod', not {env}")

    stage = f"{STAGE_URL}/api/v2/files/uploadurl"
    prod = f"{PROD_URL}/api/v2/files/uploadurl"

    if env == "stage":
        return requests.get(stage, headers=headers, params=params)
    else:
        return requests.get(prod, headers=headers, params=params)


def put_presigned_upload_url(url: str, file_path: str, video_content_type: str):
    """Uploads a .mp4 file to a presigned url.

    Args:
        url (str): The presigned url.
        file_path (str): The path to the file to upload.

    Returns:
        response: Response object from the request.
    """
    headers = {"Content-Type": video_content_type}
    with open(file_path, "rb") as f:
        file = f.read()
    return requests.put(url, data=file, headers=headers)


def submit_drill_entry(
    player_id: int, trial_id: int, bearer_token: str, video_entry_relative_path: str, ball_size: int = 4, env: str = "stage"
):
    """Submits a drill entry.

    Args:
        player_id (int): Id of the player. Can be found in the response from player_login.
        trial_id (int): Id of the trial.
        bearer_token (str): Bearer token of the player from login.
        video_entry_relative_path (str): The relative path to the video entry. Can be found in the response from get_presigned_upload_url.
        ball_size (int, optional): Size of the ball. Defaults to 4.
        env (str, optional): The enviroment to target. Defaults to "stage".

    Raises:
        ValueError: If env is not "stage" or "prod".

    Returns:
        response: Response object from the request.
    """
    if env not in ["stage", "prod"]:
        raise ValueError(f"env must be 'stage' or 'prod', not {env}")
    if env == "stage":
        url = f"{STAGE_URL}/api/v2/players/{str(player_id)}/trials/{str(trial_id)}/entries"
    else:
        url = f"{PROD_URL}/api/v2/players/{str(player_id)}/trials/{str(trial_id)}/entries"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    body = {"videoEntryRelativePath": video_entry_relative_path, "measurementFactValue": ball_size}
    return requests.post(url, headers=headers, json=body)

def get_drill_entry(player_id: int, drill_id: int, entry_id: int, bearer_token: str, include_feedback: bool = True, env: str = "stage"):
    """Get a drill entry.

    Args:
        player_id (int): Id of the player.
        drill_id (int): Id of the drill.
        entry_id (int): Id of the entry.
        bearer_token (str): Bearer token of the player.
        include_feedback (bool, optional): Whether to include feedback. Defaults to True.
        env (str, optional): The environment to target. Defaults to "stage".

    Raises:
        ValueError: If env is not "stage" or "prod".

    Returns:
        response: Response object from the request.
    """

    if env not in ["stage", "prod"]:
        raise ValueError(f"env must be 'stage' or 'prod', not {env}")

    if env == "stage":
        url = f"{STAGE_URL}/api/v3/players/{player_id}/drills/{drill_id}/entries/{entry_id}"
    else:
        url = f"{PROD_URL}/api/v3/players/{player_id}/drills/{drill_id}/entries/{entry_id}"

    # Add the includeFeedback query parameter
    url += f"?includeFeedback={include_feedback}"

    logger.debug(f"URL for get drill entry: {url}")
    headers = {"Authorization": f"Bearer {bearer_token}"}
    return requests.get(url, headers=headers)
