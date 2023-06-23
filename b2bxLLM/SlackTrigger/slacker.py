import re

class Slacker:
    """
    slackの各種制御を行う
    """
    def __init__(self):
        pass

    @staticmethod
    def cleaninng_message(message):
        """
        メッセージから不要な文字列を削除する
        
        Args:
            message (str): メッセージ
        """
        pattern_mention = r'<@\w+>'
        message_no_mention = re.sub(pattern_mention, '', message)
        pattern_synbol = r'[<>]'
        clean_message = re.sub(pattern_synbol, '', message_no_mention)
        return clean_message
    
    @staticmethod
    def find_urls(string):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-~_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        urls = re.findall(url_pattern, string)
        return urls