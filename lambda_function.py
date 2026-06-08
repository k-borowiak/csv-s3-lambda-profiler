import boto3
import csv
import json
from urllib.parse import unquote_plus
from datetime import datetime

s3 = boto3.client("s3", region_name="eu-north-1")

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = unquote_plus(record["s3"]["object"]["key"])

    print("Bucket:", bucket, "Key:", key)

    obj = s3.get_object(Bucket=bucket, Key=key)
    content = obj["Body"].read().decode("utf-8").splitlines()

    reader = csv.DictReader(content)
    rows = list(reader)

    result = {
        "source_bucket": bucket,
        "source_key": key,
        "processed_at": datetime.utcnow().isoformat(),
        "rows": len(rows),
        "columns": reader.fieldnames,
        "sample_row": rows[0] if rows else None
    }

    #TEN SAM BUCKET, tylko inny folder
    output_key = key.replace("uploads/", "output/").replace(".csv", ".json")

    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(result, indent=2, ensure_ascii=False),
        ContentType="application/json"
    )

    print("Saved to:", output_key)

    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False)
    }
