CREATE TABLE IF NOT EXISTS guilddata (
    guildid BIGINT PRIMARY KEY,
    prefix VARCHAR[] DEFAULT '{"h!"}',
    blacklists jsonb DEFAULT '{"prevbl": 0, "blacklisted": false}',
    serverbls jsonb DEFAULT '{"role": [], "user": [], "channel": []}'
);

CREATE TABLE IF NOT EXISTS userdata (
    userid BIGINT UNIQUE PRIMARY KEY,
    blacklists jsonb DEFAULT '{"prevbl": 0, "blacklisted": false}'
);

CREATE TABLE IF NOT EXISTS todo (
    userid BIGINT UNIQUE PRIMARY KEY,
    lastupdated BIGINT NOT NULL,
    data jsonb DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS tags (
    name VARCHAR NOT NULL,
    serverid BIGINT NOT NULL,
    content TEXT NOT NULL,
    usage BIGINT DEFAULT 0,
    info jsonb DEFAULT '{"owner": null, "created_at": null}',
    aliases VARCHAR[] DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS buttonroles (
    guildid BIGINT NOT NULL,
    messageid BIGINT PRIMARY KEY,
    channelid BIGINT NOT NULL,
    role_emoji jsonb DEFAULT '{}',
    config jsonb DEFAULT '{}'
);