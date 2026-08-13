import json
import os
import sqlite3
from pathlib import Path

from discord import Interaction, Message
from dotenv import load_dotenv

from .helpers import cache

__all__ = ['Translator']

PROJECT_ROOT = Path(__file__).parents[2]
TRANSLATIONS_DIR = PROJECT_ROOT / 'resources' / 'translations'
FALLBACK_LANGUAGE = 'en'

Id = int
OptionalId = Id | None


INIT_DB_SCRIPT = PROJECT_ROOT / 'scripts' / 'init_db.sql'


class Translator:
    def __init__(self):
        load_dotenv()
        configured_path = os.getenv('SQLITE_DB_PATH')
        if not configured_path:
            raise RuntimeError('SQLITE_DB_PATH is not set')

        db_path = PROJECT_ROOT / configured_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(db_path)
        self._init_db()
        self._translations: dict[str, dict[str, str]] = {}
        self.load_translations()

    def _init_db(self) -> None:
        with open(INIT_DB_SCRIPT) as f:
            self.connection.executescript(f.read())

    def load_translations(self) -> None:
        def read(path: Path) -> dict[str, str]:
            return json.loads(path.read_text(encoding='utf-8'))

        fallback = read(TRANSLATIONS_DIR / f'{FALLBACK_LANGUAGE}.json')
        for path in sorted(TRANSLATIONS_DIR.glob('*.json')):
            # Layered over English, so a key a translator hasn't got to yet renders in
            # English rather than leaking the raw identifier to users.
            self._translations[path.stem] = fallback | read(path)

    def get_translation(
            self,
            language: str,
            key: str,
            n: int | None = None
    ) -> str:
        strings = self._translations.get(language, self._translations[FALLBACK_LANGUAGE])
        if n is not None:
            key = f'{key}.one' if n == 1 else f'{key}.other'
        return strings.get(key, key)

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
