import boto3
import pandas as pd
from itertools import zip_longest
from itertools import product


def get_profile():
    available_profiles = boto3.Session().available_profiles
    selected_profile = ""

    if not available_profiles:
        print("no avaible profile found")
    else:
        for i, profile in enumerate(available_profiles, start=0):
            print(f"{i}. {profile}")

        while True:
            selected_index = int(
                input("Select a profile by entering corresponding number: ")
            )
            if 0 <= selected_index < len(available_profiles):
                selected_profile = available_profiles[selected_index]
                break
            else:
                raise ValueError
    return selected_profile


def create_excel():
    selected_profile = get_profile()
    # input profile (needs to be in ~/.aws/config)
    session = boto3.Session(profile_name=selected_profile)
    iam_client = session.client("iam")

    # Get User in IAM #
    user_reponse = iam_client.list_users()
    users = user_reponse["Users"]

    # Set Array to be used as Pandas Dataframe
    user_data = []
    expanded_data = []

    for user in users:
        # Get Policy Directly attached to User from IAM
        user_name = user["UserName"]
        user_permissions_response = iam_client.list_attached_user_policies(
            UserName=user_name
        )
        attached_policies = user_permissions_response["AttachedPolicies"]
        user_permissions = [policy["PolicyName"] for policy in attached_policies]
        current_user = ""
        group_name = ""
        group_permission = ""

        # Get Groups attached to User
        groups_response = iam_client.list_groups_for_user(UserName=user_name)
        user_groups = groups_response["Groups"]

        # Get Groups permission attached to User
        if len(user_groups) > 0:
            group_permissions = []
            groups = [group["GroupName"] for group in user_groups]
            for group in user_groups:
                group_name = group["GroupName"]
                group_permission_response = iam_client.list_attached_group_policies(
                    GroupName=group_name
                )
                group_attached_policy = group_permission_response["AttachedPolicies"]
                group_permissions = [
                    policy["PolicyName"] for policy in group_attached_policy
                ]
                # Attached the result to Pandas Dataframe
                user_data.append(
                    {
                        "User": user_name,
                        "UserPermission": ", ".join(user_permissions),
                        "GroupName": ", ".join(groups),
                        "GroupPermission": ", ".join(group_permissions),
                    }
                )
        # If user doesn't have any group
        else:
            user_data.append(
                {
                    "User": user_name,
                    "UserPermission": ", ".join(user_permissions),
                    "GroupName": group_name,
                    "GroupPermission": group_permission,
                }
            )
# converting array into Pandas Dataframe
    df = pd.DataFrame(user_data)

    # Spliting by seperator
    df["GroupPermission"] = df["GroupPermission"].str.split(",")
    df["GroupName"] = df["GroupName"].str.split(",")
    df["UserPermission"] = df["UserPermission"].str.split(",")

    # exploding data by longest column
    df1 = (
        df.apply(
            lambda x: list(
                zip_longest(x["UserPermission"], x["GroupName"], x["GroupPermission"])
            ),
            axis=1,
        )
        .explode()
        .apply(
            lambda x: pd.Series(
                x,
                index=["UserPermission", "GroupName", "GroupPermission"],
            )
        )
        .groupby(level=0)
        .fillna("")
    )

    # join exploded data to User
    df = df[["User"]].join(df1)

    # return excel file
    excel_file = selected_profile + "_IAM_output.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"{excel_file} Created Successfully")

# Start Creation
create_excel()
