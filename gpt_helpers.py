
from openai import OpenAI
from uuid import uuid4
import time
import base64
import requests
from pathlib import Path
from typing import Literal
import json


class OpenAIHelper:
    """
    Helper class to interact with the OpenAI API.
    """

    def __init__(self, api_key, intent_message):
        """
        Initializes the OpenAIHelper with the provided API key and intent message.

        Args:
            api_key (str): The API key for OpenAI.
            intent_message (str): The initial intent message to be used in the chat.
        """
        self.api_key = api_key
        self.intent_message = intent_message
        self.messages = [
            {"role": "system", "content": f"{self.intent_message}"}
        ]

        self.connect_to_openai()

    def connect_to_openai(self):
        """
        Connects to the OpenAI API using the provided API key.
        """
        self.client = OpenAI(api_key=self.api_key)

    def reset_messages(self):
        """
        Resets the message history to the initial intent message.
        """
        self.messages = [{"role": "system", "content": f"{self.intent_message}"}]

    def gpt_3(self, prompt, max_retries=5):
        """
        Sends a prompt to the GPT-3 model and returns the response.

        Args:
            prompt (str): The prompt to send to GPT-3.
            max_retries (int): The maximum number of retry attempts in case of failure.

        Returns:
            str: The response from GPT-3.
        """
        query_wrapper = {"role": "user", "content": f"{prompt}"}
        self.messages.append(query_wrapper)
        data = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=self.messages
                )
                data = response.choices[0].message.content
                break
            except Exception as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_retries}.")
                time.sleep(1)
        
        return data

    def gpt_4(self, prompt, max_retries=5):
        """
        Sends a prompt to the GPT-4 model and returns the response.

        Args:
            prompt (str): The prompt to send to GPT-4.
            max_retries (int): The maximum number of retry attempts in case of failure.

        Returns:
            str: The response from GPT-4.
        """
        query_wrapper = {"role": "user", "content": f"{prompt}"}
        self.messages.append(query_wrapper)
        data = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4-0314",
                    messages=self.messages
                )
                data = response.choices[0].message.content
                break
            except Exception as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_retries}.")
                time.sleep(1)
        return data

    def gpt_json(self, prompt, data, example, model="gpt-3.5-turbo-0125", max_retries=5):
        """
        Sends a prompt to the GPT model and expects a JSON response.

        Args:
            prompt (str): The prompt to send to the GPT model.
            data (str): The data to include in the prompt.
            example (str): The example format for the JSON response.
            model (str): The model to use (default is "gpt-3.5-turbo-0125").
            max_retries (int): The maximum number of retry attempts in case of failure.

        Returns:
            dict: The parsed JSON response from the GPT model.
        """
        query_wrapper = {
            "role": "user",
            "content": f"{prompt}\n[data]```{data}\n This is the json format you will use\n[format]\n```{example}```"
        }
        self.messages.append(query_wrapper)
        data = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=self.messages,
                    response_format={"type": "json_object"}
                )
                response_content = response.choices[0].message.content
                data = json.loads(response_content)
                break
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}. Attempt {attempt + 1} of {max_retries}.")
            except Exception as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_retries}.")
                time.sleep(1)
        self.reset_messages()
        return data

    def gpt_url_vision(self, query, image_url, max_tokens=4096, max_retries=5):
        """
        Sends a query with an image URL to the GPT-4 vision model and returns the response.

        Args:
            query (str): The query to send to the GPT-4 vision model.
            image_url (str): The URL of the image to include in the query.
            max_tokens (int): The maximum number of tokens in the response.
            max_retries (int): The maximum number of retry attempts in case of failure.

        Returns:
            str: The response from the GPT-4 vision model.
        """
        data = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"{query}"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url,
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=max_tokens,
                )
                data = response.choices[0].message.content
                break
            except Exception as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_retries}.")
                time.sleep(1)
        self.reset_messages()
        return data

    def encode_image(self, image_path):
        """
        Encodes an image to a base64 string.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: The base64 encoded string of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def gpt_vision(self, query, image_path, max_tokens=4096, max_retries=5):
        """
        Sends a query with an image to the GPT-4 vision model and returns the response.

        Args:
            query (str): The query to send to the GPT-4 vision model.
            image_path (str): The path to the image file.
            max_tokens (int): The maximum number of tokens in the response.
            max_retries (int): The maximum number of retry attempts in case of failure.

        Returns:
            str: The response from the GPT-4 vision model.
        """
        base64_image = self.encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens
        }
        retry_counter = 0
        while True:
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                data = response.json()
                text = data['choices'][0]['message']['content']

                return text
            except Exception as e:
                retry_counter += 1
                if retry_counter > 4:
                    return data

                print("There was an error with GPT Vision")
                print(data)
                print(data['error']['code'])
                if 'rate limit' in data['error']['code']:
                    print("Waiting 30 seconds to retry against rate limit")
                    time.sleep(30)

    def transcribe_audio(self, audiofile):
        """
        Transcribes audio to text using the Whisper model.

        Args:
            audiofile (str): The path to the audio file.

        Returns:
            str: The transcribed text.
        """
        with open(audiofile, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format='text'
            )
        return transcript

    def speak(self, text, voice: Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'], filename="speech.mp3"):
        """
        Converts text to speech and saves it to a file.

        Args:
            text (str): The text to convert to speech.
            voice (Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']): The voice to use for the speech.
            filename (str): The name of the file to save the speech to (default is "speech.mp3").

        Returns:
            Path: The path to the saved speech file.
        """
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = self.client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text
        )

        response.stream_to_file(speech_file_path)

        return speech_file_path

    def get_embeddings(self, text):
        """
        Gets embeddings for the provided text using the text-embedding model.

        Args:
            text (str): The text to get embeddings for.

        Returns:
            list: The embeddings for the provided text.
        """
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding
        return embedding
