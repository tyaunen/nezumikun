import anthropic
import module.Database
import os
from dotenv import load_dotenv


class ChatAi:
    """
    LLMへの入出力を扱うクラス
    """

    def __init__(self, database, charactor):
        load_dotenv()  # .env ファイルから環境変数を読み込む
        CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

        self.database = database
        self.charactor = charactor
        self.api_key = CLAUDE_API_KEY
        self.input_template = ("<rule>messageにロールプレイで返信せよ。返信内容は30～150文字かつ1～7行。空白行はなし。{additional_rule}</rule>"
                               "<message>{message}</message>")

    def chat(self, input_channel_id, input_user_text, additional_rule=""):
        """
        ユーザーの入力を受け取り、AIからの返答を返す
        """
        content = self.input_template.format(
            message=input_user_text,
            additional_rule=additional_rule)
        messages = self.database.load_message_history(input_channel_id)
        messages.append({"role": "user", "content": content}) # メッセージ履歴

        system_prompt_props = self.database.get_props(input_channel_id)

        system_prompt = self.charactor.get_system_role(
            system_prompt_props
        )
        sample_message = self.charactor.get_sample_message() # キャラクターのメッセージ形式のサンプル

        temp_messages = messages.copy()
        temp_messages.insert(0, {"role": "assistant", "content": sample_message}) # 会話履歴の先頭に会話サンプルを差し込むことで、返答形式を縛る力を加える
        ai_chat_client = anthropic.Anthropic(
            api_key=self.api_key
        )
        response = ai_chat_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            system=system_prompt,
            messages=temp_messages
        )
        output = response.content[0].text

        messages.append({"role": "assistant", "content": output})  # 会話履歴に、botの発言を追加
        self.database.add_message_history(input_channel_id, 'assistant', output)  # 会話履歴を保存

        return output
