import os
import sqlite3
from gettext import GNUTranslations, NullTranslations, translation as load_translation

from discord import Interaction, Message
from dotenv import load_dotenv

from .helpers import cache

__all__ = ['Translator']

TRANSLATIONS_DIR = 'resources/translations/'

Id = int
OptionalId = Id | None


class Translator:
    def __init__(self):
        load_dotenv()
        self.connection = sqlite3.connect(os.getenv('SQLITE_DB_PATH'))
        self._translations: dict[str, GNUTranslations] = {}
        self.load_translations()

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

    @cache
    def get_language(
            self,
            server_id: OptionalId,
            category_id: OptionalId,
            channel_id: OptionalId
    ) -> str:
        query = """
        WITH Preferences AS (
            SELECT 
                LanguageCode,
                CASE 
                    WHEN EntityType = 'channel' THEN 1
                    WHEN EntityType = 'category' THEN 2
                    WHEN EntityType = 'server' THEN 3
                END AS Precedence
            FROM LanguagePreferences
            WHERE 
                (EntityType = 'channel' AND EntityID = ?)
                OR (EntityType = 'category' AND EntityID = ?)
                OR (EntityType = 'server' AND EntityID = ?)
        )
        SELECT LanguageCode
        FROM Preferences
        ORDER BY Precedence
        LIMIT 1;
        """

        cursor = self.connection.cursor()
        cursor.execute(query, (channel_id, category_id, server_id))
        result = cursor.fetchone()
        cursor.close()

        return result[0] if result is not None else 'en'

    @cache.clears(get_language)
    def set_language(
            self,
            language: str,
            server_id: OptionalId = None,
            category_id: OptionalId = None,
            channel_id: OptionalId = None
    ) -> None:
        query = """
        INSERT INTO LanguagePreferences (LanguageCode, EntityType, EntityID)
        VALUES (?, ?, ?)
        ON CONFLICT (EntityType, EntityID)
        DO UPDATE SET LanguageCode = ?;
        """

        cursor = self.connection.cursor()

        for entity_type, entity_id in [('channel', channel_id), ('category', category_id), ('server', server_id)]:
            if entity_id is not None:
                cursor.execute(query, (language, entity_type, entity_id, language))

        self.connection.commit()
        cursor.close()

    def get_translator(self, context: Interaction | Message):
        guild_id = getattr(context.guild, 'id', None)
        category_id = getattr(context.channel, 'category_id', None)
        channel_id = context.channel.id

        def translate(key: str, n: int | None = None, /, **format_kwargs):
            language = self.get_language(guild_id, category_id, channel_id)
            string = self.get_translation(language, key, n)
            return string.format(**format_kwargs)

        return translate
