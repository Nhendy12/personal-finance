import json
import quickstart

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    try:
        # names = ["nick", "terra"]
        names = ["nick"]
        results = []

        for name in names:
            result = quickstart.main(name)
            results.append(result)

        return {
            'statusCode': 200,
            'body': json.dumps({"message": results})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
