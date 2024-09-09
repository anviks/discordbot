import json
import os
from gettext import GNUTranslations, NullTranslations, translation as load_translation

__all__ = ['translator']

from typing import Literal, TypedDict

from discord import Interaction, Message

current_dir = os.path.dirname(__file__)
TRANSLATIONS_DIR = f'{current_dir}/translations/'
PREFERENCES_FILE = f'{current_dir}/language_preferences.json'

Id = int
OptionalId = Id | None


class Preferences(TypedDict):
    default: str
    servers: dict[str, str]
    categories: dict[str, str]
    channels: dict[str, str]


class Translator:
    def __init__(self):
        self._preferences: Preferences = dict()
        self._translations: dict[str, GNUTranslations] = {}

        self.load_preferences()
        self.load_translations()

    def load_preferences(self) -> None:
        try:
            with open(PREFERENCES_FILE, 'r') as file:
                self._preferences.update(json.load(file))
        except FileNotFoundError:
            self._preferences.update({
                'default': 'en',
                'servers': {},
                'categories': {},
                'channels': {}
            })

    def save_preferences(self) -> None:
        with open(PREFERENCES_FILE, 'w') as file:
            json.dump(self._preferences, file, indent=2)

    def load_translations(self) -> None:
        for language in os.listdir(TRANSLATIONS_DIR):
            translation = load_translation('messages', localedir=TRANSLATIONS_DIR, languages=[language])
            self._translations[language] = translation

    def get_translation(
            self,
            language: str,
            key: str,
            n: int | None = None
    ) -> str:
        translation: GNUTranslations = self._translations.get(language, NullTranslations())
        if n is None:
            return translation.gettext(key)
        return translation.ngettext(f'{key}.singular', f'{key}.plural', n)

    def get_language(
            self,
            server_id: OptionalId,
            category_id: OptionalId,
            channel_id: OptionalId
    ) -> str:
        for _id, entity in zip([channel_id, category_id, server_id], ('channels', 'categories', 'servers')):
            entity: Literal['servers', 'categories', 'channels']
            if _id and str(_id) in self._preferences[entity]:
                return self._preferences[entity][str(_id)]

        return self._preferences['default']

    def set_language(
            self,
            language: str,
            server_id: OptionalId = None,
            category_id: OptionalId = None,
            channel_id: OptionalId = None
    ) -> None:
        for _id, entity in zip([channel_id, category_id, server_id], ('channels', 'categories', 'servers')):
            entity: Literal['servers', 'categories', 'channels']
            if _id:
                self._preferences[entity][str(_id)] = language
                break
        else:
            return

        self.save_preferences()

    def translate(
            self,
            context: Interaction | Message,
            key: str,
            n: int | None = None,
            **format_kwargs
    ) -> str:
        if isinstance(context, Interaction):
            language = self.get_language(context.guild_id, context.channel.category_id, context.channel_id)
        else:
            language = self.get_language(context.guild.id, context.channel.category_id, context.channel.id)
        string = self.get_translation(language, key, n)
        return string.format(**format_kwargs)
