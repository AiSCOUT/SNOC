"""
Initialise the API client
"""
import os, sys
import logging
import requests
import json

from supporting_files.player_drill_entry_endpoints import (
    get_presigned_upload_url,
    app_login,
    put_presigned_upload_url,
    submit_drill_entry,
    get_drill_entry
)

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

STAGE_URL = "http://stage.aiscout.io"
PROD_URL = "https://secure.aiscout.io"

class PlayerAPIClient:
    """A class for interacting with the player API pipelines."""

    def __init__(self,
                 email: str | None = None,
                 password: str | None = None,
                 env: str = "stage"
        ):
        """Initializes the class. If email and password are provided, the player will be logged in.

        Args:
            email (str, optional): Email of the player to be logged in. Defaults to None.
            password (str, optional): Password of the player to be logged in. Defaults to None.
            env (str, optional): Enviroment to target. Defaults to "stage".

        Raises:
            ValueError: If env is not "stage" or "prod".
        """
        if env not in ["stage", "prod"]:
            raise ValueError(f"env must be 'stage' or 'prod', not {env}")
        self.env = env
        if email is not None and password is not None:
            self.email = email
            self.password = password
            response = app_login(email, password, "player", env).json()
            self.access_token = response["accessToken"]
            self.player_id = response["playerId"]
        else:
            self.email = None
            self.password = None
            self.person = None
            self.access_token = None
            self.player_id = None

    def app_login(self, email: str,  password: str, env="stage"):
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

        user_login = "players"

        if env not in ["stage", "prod"]:
            raise ValueError(f"env must be 'stage' or 'prod', not {env}")
        
        # Define the base URL based on the environment
        base_url = STAGE_URL if env == "stage" else PROD_URL

        body = {"email": email, "password": password, "fcmToken": "fcmToken"}
        logger.debug(f"Request BODY: {body}")

        response = requests.post(
            f"{base_url}/api/v2/{user_login}/login",
            json=body
        )
        logger.debug(f"JSON Body from login: {response.json()}")
        
        return response

    def drill_submission_full(self, path_to_upload_video: str, trail_id: int, ball_size: int = 4):
        """Full pipeline for submitting a local video as a drill entry for the logged in player.

        Args:
            path_to_upload_video (str): Path to the video to be uploaded.
            trail_id (int): ID of the trail to submit the drill entry to.
            ball_size (int, optional): Size of the ball. Defaults to 4.

        Raises:
            ValueError: If the player is not logged in.

        Returns:
            response: Response from the API.
        """
        if self.access_token is None:
            raise ValueError("You must login first")

        logger.debug(f"Path for the video to upload {path_to_upload_video}")

        video_extensions = {
            "mp4": "video/mp4",
            "mpeg": "video/mpeg",
            "mov": "video/quicktime"
        }

        file_extension = os.path.splitext(path_to_upload_video.lower())[1][1:]
        video_content_type = video_extensions.get(file_extension)

        response = get_presigned_upload_url(bearer_token=self.access_token, mime_type=str(video_content_type), env=self.env).json()
        logger.debug("Response from get_presigned_upload_url: " + str(response))

        s3_object_key = response["s3ObjectKey"]
        response = put_presigned_upload_url(response["preSignedUrl"], path_to_upload_video, video_content_type)
        logger.debug("put_presigned_upload_url status code: " + str(response.status_code))

        response = submit_drill_entry(int(self.player_id), trail_id, self.access_token, s3_object_key, ball_size=ball_size, env=self.env).json()  # type: ignore

        try:
            logger.debug(f"Response from submit_drill_entry: {json.dumps(response, indent=2)}")
            if not response.get("id"):
                print("Response from submit_drill_entry: ", response)  
                return response
        except json.JSONDecodeError as e:
            logger.debug(f"Response from submit_drill_entry: {response}")
            pass
        response["s3_object_key"] = s3_object_key

        try:
            response = get_drill_entry(self.player_id, trail_id, response["id"], bearer_token=self.access_token, env=self.env)
            logger.debug(f"Response from get_drill_entry: {response.text}")
        except KeyError:
            logger.debug(f"Response ID not found from submit_drill_entry: {response}")
            return None
        return response.text