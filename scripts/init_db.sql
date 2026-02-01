CREATE TABLE IF NOT EXISTS LanguagePreferences
(
    PreferenceID INTEGER PRIMARY KEY AUTOINCREMENT, -- SQLite auto-increment
    EntityID     INTEGER NOT NULL,                  -- ID of the entity
    EntityType   TEXT    NOT NULL,                  -- Type of the entity ('server', 'category', or 'channel')
    LanguageCode TEXT    NOT NULL,                  -- ISO 639 language code (e.g., 'en', 'fr')

    -- UNIQUE constraint to ensure no duplicate preferences per entity type and ID
    UNIQUE (EntityID, EntityType),

    -- CHECK constraint to ensure EntityType is valid
    CHECK (
        EntityType IN ('server', 'category', 'channel')
    )
);