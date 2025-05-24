CREATE TABLE IF NOT EXISTS users(
    login VARCHAR(255) ,
    users_id BIGINT ,
    avatar_url VARCHAR(255) ,
    gravatar_id VARCHAR(255) ,
    url VARCHAR(255) ,
    html_url VARCHAR(255) ,
    followers_url VARCHAR(255) ,
    following_url VARCHAR(255) ,
    gists_url VARCHAR(255) ,
    starred_url VARCHAR(255) ,
    subscriptions_url VARCHAR(255) ,
    organizations_url VARCHAR(255) ,
    repos_url VARCHAR(255) ,
    events_url VARCHAR(255) ,
    received_events_url VARCHAR(255) ,
    type VARCHAR(255) ,
    site_admin BIT(1)
);
CREATE TABLE IF NOT EXISTS repositories(
    repositories_id BIGINT ,
    name VARCHAR(255) ,
    url VARCHAR(255)
);
