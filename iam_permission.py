import boto3
import pandas as pd
from itertools import zip_longest

## Todo profile을 선택할 수 있도록 prompt를 구성

# input profile
profile_name = input("enter profile name: ")
session = boto3.Session(profile_name=profile_name)
iam_client = session.client("iam")

# Get User
user_reponse = iam_client.list_users()
users = user_reponse["Users"]

user_data = []
expanded_data = []

for user in users:
    # Get User in IAM #
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
            # for group_perm in group_permissions:
        user_data.append(
            {
                "User": user_name,
                "UserPermission": ", ".join(user_permissions),
                "GroupName": group_name,
                "GroupPermission": ", ".join(group_permissions),
            }
        )
    else:
        user_data.append(
            {
                "User": user_name,
                "UserPermission": ", ".join(user_permissions),
                "GroupName": group_name,
                "GroupPermission": group_permission,
            }
        )

# put array into pandas dataframe
df = pd.DataFrame(user_data)

# seperate string by ',' seperator
df["GroupPermission"] = df["GroupPermission"].str.split(",")
df["GroupName"] = df["GroupName"].str.split(",")
df["UserPermission"] = df["UserPermission"].str.split(",")

# multiline explode which are in different sizes
df1 = (
    df.apply(
        lambda x: list(
            zip_longest(x["UserPermission"], x["GroupName"], x["GroupPermission"])
        ),
        axis=1,
    )
    .explode()
    .apply(
        lambda x: pd.Series(x, index=["UserPermission", "GroupName", "GroupPermission"])
    )
    .groupby(level=0)
    .fillna("")
)

# join user with other exploded datas
df = df[["User"]].join(df1)

# save to excel
excel_file = profile_name + "_output.xlsx"
df.to_excel(excel_file, index=False)
