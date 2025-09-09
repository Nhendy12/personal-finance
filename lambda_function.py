import json
import quickstart
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client("dynamodb")
TABLE_NAME = "DailyJobRuns"

def has_already_run(user, run_date):
    try:
        # fails if record already exists
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                "user_id": {"S": user},
                "run_date": {"S": run_date},
            },
            ConditionExpression="attribute_not_exists(user_id) AND attribute_not_exists(run_date)"
        )
        return False
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return True 
        else:
            raise

def lambda_handler(event, context):
    """AWS Lambda entry point"""

    names = ["nick", "terra"]
    results = []
    today = datetime.utcnow().strftime("%Y-%m-%d")

    try:
        for name in names:
            if has_already_run(name, today):
                results.append(f"Skipped {name}, already ran today")
                continue

            result = quickstart.main(name)
            results.append(result)

        print("****************")
        print(f"Finsished with results: {results}")
        print("****************")

        return {
            'statusCode': 200,
            'body': json.dumps({"message": results})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
