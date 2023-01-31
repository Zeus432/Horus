CREATE TABLE IF NOT EXISTS guilddata (
    guildid BIGINT PRIMARY KEY,
    prefix VARCHAR[] DEFAULT '{"h!"}'
);