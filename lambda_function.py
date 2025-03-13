import json
import quickstart

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    try:
        result = quickstart.main()
        return {
            'statusCode': 200,
            'body': json.dumps({"message": result})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
