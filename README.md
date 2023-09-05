# Pandas_Explode
AWS IAM List UserPermission, GroupName and GroupPermission in Excel

## Iam_list.py
해당 Python code는 AWS IAM에서 사용자 이름을 list 해서, 
1. 해당 사용자에 직접 매핑되어 있는 policy
2. 사용자가 속해 있는 그룹명
3. 그룹이 소유하고 있는 policy
   를 excel로 출력해줍니다.

해당 파이썬 코드를 사용하실 때 주의하실 점은, profile 명이 로컬 ~/.aws/config 파일에 포함되어 있어야 합니다.
