import os
import json
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from azure.functions import HttpRequest, HttpResponse

from .run import run
from .config import Conf

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数から設定値を取得
conf = Conf(
    confluence_user_name=os.environ['CONFLUENCE_USER_NAME'],
    confluence_api_key=os.environ['CONFLUENCE_API_KEY'],
    openai_api_key=os.environ['OPENAI_API_KEY'],
    slack_outh_token=os.environ['SLACK_OAUTH_TOKEN'],
)


def main(req: HttpRequest) -> HttpResponse:
    """
    main関数

    Args:
        req (HttpRequest): HTTPリクエスト
    """
    logging.info("Python HTTP trigger function processed a request.")
    req_body = req.get_json()
    logging.info(req_body)

    if req_body["type"] == "url_verification":
        # challenge認証コード
        return req_body.get("challenge")
    elif req_body["type"] == "event_callback":
        try:
            # 実行
            run(req_body, conf)

            return HttpResponse(
                "Connection Confirmed.",
                status_code=200,
            )
        except SlackApiError as e:
            logger.error(f"Error sending message: {e}")

        except Exception as e:
            logger.error(e)
    else:
        return "bad"
