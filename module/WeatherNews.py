import requests
import os
from dotenv import load_dotenv

class WeatherNews:
    def get_weather(self):
        """
        天候取得
        参考:
            https://openweathermap.org/current
            https://note.com/python_lab/n/ndc72bf889683
        """
        api_key = os.getenv('WEATHER_API_KEY')

        # 東京の緯度と経度
        lat = 35.6895
        lon = 139.6917

        # OpenWeatherMapのエンドポイント
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ja"

        # APIリクエストを送信
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            # 天気情報を抽出
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            news_text = f"{weather_description}, 気温{temperature}°C"
        else:
            news_text = f"なんともいえない天気, 気温はふつー"
        return news_text
