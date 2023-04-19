from __future__ import annotations

import re

from EdgeGPT import Chatbot, ConversationStyle

from xiaogpt.utils import split_sentences

_reference_link_re = re.compile(r"\[\d+\]: .+?\n+")


class NewBingBot:
    def __init__(
        self,
        bing_cookie_path: str = "",
        bing_cookies: dict | None = None,
        proxy: str | None = None,
    ):
        self.history = []
        self._bot = Chatbot(
            cookiePath=bing_cookie_path, cookies=bing_cookies, proxy=proxy
        )

    @staticmethod
    def clean_text(s):
        s = s.replace("**", "")
        s = _reference_link_re.sub("", s)
        s = re.sub(r"\[[\^\d]+\]", "", s)
        return s.strip()

    async def ask(self, query, **options):
        kwargs = {"conversation_style": ConversationStyle.balanced, **options}
        completion = await self._bot.ask(prompt=query, **kwargs)
        text = self.clean_text(completion["item"]["messages"][1]["text"])
        print(text)
        return text

    async def ask_stream(self, query, **options):
        kwargs = {"conversation_style": ConversationStyle.balanced, **options}
        completion = self._bot.ask_stream(prompt=query, **kwargs)

        async def text_gen():
            current = ""
            async for final, resp in completion:
                if final:
                    break
                text = self.clean_text(resp)
                if text == current:
                    continue
                diff = text[len(current) :]
                print(diff, end="")
                yield diff
                current = text

        try:
            async for sentence in split_sentences(text_gen()):
                yield sentence
        finally:
            print()
