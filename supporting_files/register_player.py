import sys
import logging
import random
import string

from supporting_files.registration_client import RegistrationClient, add_academy_team_to_player

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def create_tokens(env_variables, ENVIRONMENT):
    """
    Call various API functions and retrieve necessary information.

    Args:
    - api_client: An instance of the RegistrationClient class for API calls.
    - selected_env (dict): Selected environment variables.

    Returns:
    - admin_user_id (str): User ID of the admin.
    - admin_access_token (str): Access token for the admin.
    - admin_switch_user_id (str): User ID after admin switch.
    - admin_switch_access_token (str): Access token after admin switch.
    - coach_user_id (str): User ID of the coach.
    - coach_access_token (str): Access token for the coach.
    - coach_switch_user_id (str): User ID after coach switch.
    - coach_switch_access_token (str): Access token after coach switch.
    - coach_switch_coach_id (str): Coach ID after coach switch.
    - coach_switch_coach_pro_club_id (str): Coach Pro Club ID after coach switch.
    """
    selected_env = env_variables[ENVIRONMENT]
    api_client = RegistrationClient(env=ENVIRONMENT)
    admin_login_response = api_client.admin_login(
        selected_env['admin_username'],
        selected_env['admin_password']
    )
    admin_user_id = admin_login_response.json().get("userId")
    admin_access_token = admin_login_response.json().get("accessToken")
    admin_role_types = admin_login_response.json().get("roleTypes")
    logging.debug(f"Admin User ID: {admin_user_id}")
    logging.debug(f"Admin Token: {admin_access_token}")
    logging.debug(f"Admin Role Types: {admin_role_types} \n")

    admin_switch_response = api_client.admin_switch(admin_user_id, admin_access_token)
    admin_switch_user_id = admin_switch_response.json().get("userId")
    admin_switch_access_token = admin_switch_response.json().get("accessToken")
    logging.debug(f"Call Response for Admin Switch: {admin_switch_response}")
    logging.debug(f"Admin Switch User ID: {admin_switch_user_id}")
    logging.debug(f"Admin Switch Token: {admin_switch_access_token} \n")

    coach_login_response = api_client.coach_login(
        selected_env['coach_username'],
        selected_env['coach_password']
    )
    coach_user_id = coach_login_response.json().get("userId")
    coach_access_token = coach_login_response.json().get("accessToken")
    coach_role_types = coach_login_response.json().get("roleTypes")
    logging.debug(f"Coach User ID: {coach_user_id}")
    logging.debug(f"Coach Role Types: {coach_role_types}")
    logging.debug(f"Coach Token: {coach_access_token} \n")

    coach_switch_response = api_client.coach_switch(coach_user_id, coach_access_token)
    coach_switch_user_id = coach_switch_response.json().get("userId")
    coach_switch_access_token = coach_switch_response.json().get("accessToken")
    coach_switch_coach_id = coach_switch_response.json().get("coachId")
    coach_switch_coach_pro_club_id = coach_switch_response.json().get("coachProClubId")
    logging.debug(f"Coach Switch Response: {coach_switch_response}")
    logging.debug(f"Coach Switch User ID: {coach_switch_user_id}")
    logging.debug(f"Coach Switch Token: {coach_switch_access_token}")
    logging.debug(f"Coach ID: {coach_switch_coach_id}")
    logging.debug(f"Coach Pro Club ID: {coach_switch_coach_pro_club_id} \n")
    return api_client, admin_switch_access_token, coach_switch_access_token


def process_registration(
        api_client,
        admin_switch_access_token,
        coach_switch_access_token,
        player_detail,
        env_variables,
        ENVIRONMENT
):
    """
    Process player registration and related actions.

    Args:
    - api_client: An instance of the RegistrationClient class for API calls.
    - player_detail (dict): Details of the player to be registered.
    - selected_env (dict): Selected environment variables.
    - admin_switch_access_token (str): Access token for admin switch.
    - coach_switch_access_token (str): Access token for coach switch.
    """
    selected_env = env_variables[ENVIRONMENT]
    email_exists_response = api_client.check_email_exists(player_detail['email'])
    email_exists_value = email_exists_response.json().get("isExisting")
    logging.debug(f"Email Exists: {email_exists_value} \n")

    def add_email_alias(email: str) -> str:
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        username, domain = email.split('@')
        alias_email = f"{username}+{random_string}@{domain}"
        return alias_email

    previous_email_address = None
    if email_exists_value:
        logging.debug("!!!!! Email exists")
        print(player_detail['email'])
        previous_email_address = player_detail['email']
        logging.debug(f"Previous email exists: {previous_email_address}")
        player_detail['email'] = add_email_alias(player_detail['email'])
        logging.debug(f"New Player email: {player_detail['email']}")

    register_player_response = api_client.register_player(
        player_detail['email'],
        selected_env['player_password'],
        selected_env['player_fcm_token'],
        player_detail,
        selected_env["homeCountryId"],
        selected_env["terms_agreement_id"]
    )
    player_id = register_player_response.json().get("playerId")
    player_user_id = register_player_response.json().get("userId")
    player_access_token = register_player_response.json().get("accessToken")
    player_first_name = register_player_response.json().get("firstName")
    player_last_name = register_player_response.json().get("lastName")
    logging.debug(f"Player ID: {player_id}")
    logging.debug(f"Player User ID: {player_user_id}")
    logging.debug(f"Player Access Token: {player_access_token}")
    logging.debug(f"Player Firstname: {player_first_name}")
    logging.debug(f"Player Lastname: {player_last_name}")

    update_player_details_response = api_client.update_player_details(
        player_id, player_access_token,
        player_detail['height'],
        player_detail['weight']
    )
    logging.debug(f"Update Player Details Response: {update_player_details_response} \n")

    add_affiliation_code_response = api_client.add_affiliation_code(player_id, player_access_token, selected_env['affiliation_code'])
    logging.debug(f"Add Affiliation Code Response: {add_affiliation_code_response} \n")

    sign_player_response = api_client.sign_player(
        player_id,
        admin_switch_access_token,
        selected_env['pro_club_id'],
        selected_env['proClubSignedType']
    )
    logging.debug(f"Sign Player Response: {sign_player_response} \n")

    add_to_academy_analysis_response = api_client.add_to_academy_analysis(
        selected_env['training_session_id'],
        coach_switch_access_token,
        player_id,
        selected_env['trainingPlayerAvailabilityType']
    )
    logging.debug(f"Add to Academy Analysis Response: {add_to_academy_analysis_response} \n")

    print("player_id: ", player_id)
    print("selected_env['academy_team_id']: ", selected_env['academy_team_id'])
    print(selected_env)

    add_academy_team_to_player_response = add_academy_team_to_player(
        selected_env['academy_team_id'],
        player_id,
        ENVIRONMENT
    )

    logging.info(f"Add to Academy Team Player Response: {add_academy_team_to_player_response} \n")

    return previous_email_address, player_detail['email'], player_id
