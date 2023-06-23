from urllib.parse import urlparse
import logging

from slack_sdk import WebClient
from langchain.chat_models import ChatOpenAI

from .slacker import Slacker
from .confluencer import Confluencer
from .document_preprocessor import DocumentPreprocessor
from .config import Conf
from .question_generator import QuestionGenerator

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def run(req_body: dict, conf: Conf):
    event = req_body["event"]

    # メッセージの前処理
    message = Slacker.cleaninng_message(event["text"])
    urls = Slacker.find_urls(message)
    logging.info("urls: {}".format(urls))

    # 指示の分類
    message_type = classify_request(message)
    url_type = classify_source(urls[0])

    # 指示に応じて処理を実行
    if message_type == "question_generation":
        if url_type == "confluence":
            # Confluenceの文章から質問生成
            reply_text = run_confluence_question_generation(url=urls[0], conf=conf)
        else:
            reply_text = "現在Confluence効いの質問生成のみ対応しています。"
    elif message_type == "summarization":
        reply_text = "現在要約機能は対応していません。"
    else:
        reply_text = """以下のフォーマットにしたがって、質問文の生成または、記事の要約を指示してください
        
        質問文の生成：@b2b_bot 質問して https://~~~
        内容の要約：@b2b_bot 要約して https://~~~
        """

    
    # Slackに返信
    logging.info("slack replying...")
    slackClient = WebClient(token=conf.slack_outh_token)
    slackClient.chat_postMessage(
        channel=event["channel"],
        text=reply_text,
        thread_ts=event["ts"]
    )


def classify_request(message):
    """
    分類リクエストを送信する

    Args:
        message (str): メッセージ
    """
    if "質問" in message:
        return "question_generation"
    elif "要約" in message:
        return "summarization"
    else:
        return "other"
    
def classify_source(url):
    """
    分類リクエストを送信する

    Args:
        message (str): メッセージ
    """
    parsed_url = urlparse(url)
    if parsed_url.netloc == "brainpad.atlassian.net":
        return "confluence"
    elif parsed_url.netloc == "blog.brainpad.co.jp":
        return "platinum_data_blog"
    else:
        return "other"


def run_confluence_question_generation(url: str, conf: Conf):
    """
    Confluenceの質問を生成する"""
    # conflueceデータの読み込み
    logging.info("confluence data loading...")
    confulence_page = Confluencer(
        url=url, # 複数あった場合でも1つ目のURLだけを取得
    )
    html = confulence_page.get_html(
        user_name=conf.confluence_user_name,
        api_key=conf.confluence_api_key,
        )
    
    # ドキュメントの前処理
    logging.info("document preprocessing...")
    document_preprocessor = DocumentPreprocessor()
    docs = document_preprocessor.preprocess(html=html, url=url)

    # OpenAIの初期化
    logging.info("OpenAI initializing...")
    llm = ChatOpenAI(
        openai_api_key=conf.openai_api_key,
        model_name= "gpt-3.5-turbo",
        temperature=0.3
    )
    
    # OpenAIによる文章生成
    logging.info("question generating...")
    question_generator = QuestionGenerator(llm=llm)
    question = question_generator.generate(
        docs=docs,
    )
    logging.info("topics: {}".format(question_generator.topic))
    logging.info("issues: {}".format(question_generator.issues))
    logging.info("missing_issues: {}".format(question_generator.missing_issues))
    logging.info("question: {}".format(question_generator.question))

    return question

def run_open_post_question_generation():
    """
    Confluenceの質問を生成する"""
    pass
