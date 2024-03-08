import requests
import json
import logging

logger = logging.getLogger(__name__)

class RegistrationClient:
    def __init__(self, env: str = "stage"):
        self.base_url = "http://stage.aiscout.io" if env == "stage" else "https://secure.aiscout.io"
        self.env = env

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = method(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:

            # print(vars(err))
            if err.response:
                error_message = err.response.json().get("message")
                error_codes = err.response.json().get("codes")
                logger.error(f"Error message: {error_message}")
                logger.error(f"Error codes: {error_codes}")
            raise

    def admin_login(self, username: str, password: str) -> requests.Response:
        payload = {"email": username, "password": password}
        return self._request(requests.post, "/api/v3/users/login", json=payload)

    def admin_switch(self, user_id, access_token) -> requests.Response:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        return self._request(requests.post, f"/api/v3/users/{user_id}/switch/admins", headers=headers, json={})

    def coach_login(self, username: str, password: str) -> requests.Response:
        payload = {"email": username, "password": password}
        return self._request(requests.post, "/api/v3/users/login", json=payload)

    def coach_switch(self, user_id: int, access_token: str) -> requests.Response:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {"fcmToken": "string"}
        return self._request(requests.post, f"/api/v3/users/{user_id}/switch/coaches", headers=headers, json=data)

    def check_email_exists(self, email: str) -> requests.Response:
        url = "/api/v3/users/email/exists"
        headers = {"Content-Type": "application/json"}
        data = {"email": email}
        return self._request(requests.post, url, headers=headers, json=data)

    def register_player(self, username: str, password: str, player_fcm_token: str, player_detail: dict, homeCountryId: int, terms_agreement_id: int) -> requests.Response:
        user_settings = [
            {"key": "isNotificationOn", "isEnabled": True},
            {"key": "isReceiveMarketingOn", "isEnabled": True}
        ]
        payload = {
            "firstName": player_detail.get("firstName"),
            "lastName": player_detail.get("lastName"),
            "dateOfBirth": player_detail.get("dob"),
            "guardianName": player_detail.get("guardianName"),
            "guardianEmail": player_detail.get("guardianEmail"),
            "email": username,
            "password": password,
            "fcmToken": player_fcm_token,
            "gender": player_detail.get("gender"),
            "homeCountryId": homeCountryId,
            "userSettings": user_settings,
            "termsAgreementId": terms_agreement_id
        }

        headers = {
            "Content-Type": "application/json"
        }
        return self._request(requests.post, "/api/v3/players/register", headers=headers, json=payload)

    def update_player_details(self, player_id: int, access_token: str, height: float, weight: float) -> requests.Response:
            payload = {"height": height, "weight": weight}
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            return self._request(requests.patch, f"/api/v2/players/{player_id}/profile/footballdetails", headers=headers, json=payload)

    def add_affiliation_code(self, player_id: int, access_token: str, affiliation_code: str) -> requests.Response:
        payload = {"affiliationCode": affiliation_code, "uniqueEntryCode": "SenegalNOC"}
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        return self._request(requests.post, f"/api/v2/players/{player_id}/affiliations", headers=headers, json=payload)

    def sign_player(self, player_id: int, access_token: str, pro_club_id: int, proClubSignedType: int) -> requests.Response:
        payload = {"proClubSignedType": proClubSignedType, "signedProClubId": pro_club_id, "proClubSignedDate": "2024-02-28"}
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        return self._request(requests.put, f"/api/v2/players/{player_id}/signedproclub", headers=headers, json=payload)

    def add_to_academy_analysis(
        self,
        training_session_id: int,
        access_token: str,
        player_id: int,
        trainingPlayerAvailabilityType: int
    ) -> requests.Response:

        payload = {
            "preventMarkingMissingPlayersAsAway": True,
            "players": [
                {
                    "playerId": player_id,
                    "availabilityType": trainingPlayerAvailabilityType
                }
            ]
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = f"/api/v2/trainingsessions/{training_session_id}/trainingplayers/batch"
        logging.info(url)
        logging.info(payload)
        logging.info(headers)
        return self._request(requests.put, url, headers=headers, json=payload)

def add_academy_team_to_player(academy_team_id: int, player_id: int, env: str) -> requests.Response:

    if env == "stage":
        base_url = "https://stage.controlcentre.ai.io/api/trpc"
    else:
        base_url = "https://controlcentre.ai.io/api/trpc"
    endpoint = "/academyAnalysis.addAcademyTeamToPlayer?batch=1"
    payload = {
        "0": {
            "json": {
                "academyTeamId": academy_team_id,
                "playerId": player_id
            }
        }
    }

    headers = {"Content-Type": "application/json"}

    url = f"{base_url}{endpoint}"

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        return None