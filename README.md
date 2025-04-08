Arcade Playground

Testing out Arcade.dev tools.

## General Setup

- You will need bun, python3 + poetry installed
- copy `.env.example` to `.env` and fill out the info

## Tools

The "tools" are python projects and custom Arcade.dev tools. `cd tools/sql && poetry install` to install the deps.

Set up arcade to have a local worker: https://docs.arcade.dev/home/install/local

Then, run the local worker: `cd tools/sql && poetry run arcade dev`

## App

runThe "app" (user of the tools) is a bun project. `bun install` to install the deps, and run `bun run sql` to run the app. It's a little CLI test suite:

````
⚙️ Found the following tools:
Sql_DiscoverTables: Discover all the tables in the database
Sql_ExecuteQuery: Execute a query and return the results
Sql_GetTableSchema: Get the schema of a table

[❓] Asking: Discover all the tables in the database

--- response ---
The database contains the following tables:

- users
- messages

--- tool calls ---
Sql_ExecuteQuery: {"connection_string":"postgresql://evan@localhost:5432/bun","query":"SELECT table_name FROM information_schema.tables WHERE table_schema='public'"}
---

[❓] Asking: Get the schemas of the tables in the database.  The tables are:  {...}

--- response ---
Here are the schemas for the tables in the database:

### users
| Column Name  | Data Type                    |
|--------------|------------------------------|
| id           | integer                      |
| created_at   | timestamp without time zone  |
| updated_at   | timestamp without time zone  |
| name         | character varying            |
| email        | text                         |
| password_hash| text                         |

### messages
| Column Name  | Data Type                    |
|--------------|------------------------------|
| id           | integer                      |
| user_id      | integer                      |
| created_at   | timestamp without time zone  |
| updated_at   | timestamp without time zone  |
| body         | text                         |

--- tool calls ---
Sql_ExecuteQuery: {"connection_string": "postgresql://evan@localhost:5432/bun", "query": "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'"}
Sql_ExecuteQuery: {"connection_string": "postgresql://evan@localhost:5432/bun", "query": "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'messages'"}
---

[❓] Asking: Get the first 10 user's names.  The database schema is:  {...}

--- response ---
Here are the first 10 user names from the database:

| Name     |
|----------|
| new name |
| Evan     |
| Admin    |

--- tool calls ---
Sql_ExecuteQuery: {"connection_string":"postgresql://evan@localhost:5432/bun","query":"SELECT name FROM users LIMIT 10;"}
---

[❓] Asking: Count how many users there are.  The database schema is:  {...}

--- response ---
There are 3 users in the database.

--- tool calls ---
Sql_ExecuteQuery: {"connection_string":"postgresql://evan@localhost:5432/bun","query":"SELECT COUNT(*) AS user_count FROM users;"}
---

[❓] Asking: How many messages has each user sent?  Group by user id and name.  The database schema is:  {...}

--- response ---
Here is the number of messages sent by each user, grouped by user ID and name:

| User ID | User Name | Message Count |
|---------|-----------|---------------|
| 3       | Evan      | 0             |
| 12      | Admin     | 218           |
| 1       | new name  | 2             |

--- tool calls ---
Sql_ExecuteQuery: {"connection_string":"postgresql://evan@localhost:5432/bun","query":"SELECT users.id, users.name, COUNT(messages.id) AS message_count FROM users LEFT JOIN messages ON users.id = messages.user_id GROUP BY users.id, users.name;"}
---

[❓] Asking: How many messages has each user sent?  Group by user id and name.  Respond not with text, but with an ascii-art bar chart representing this data. The database schema is:  {...}

--- response ---
User       | Messages Sent
-----------+-------------------------------
Admin      | ██████████████████████████████ 218
new name   | ██ 2
Evan       |   0

--- tool calls ---
Sql_ExecuteQuery: {"connection_string":"postgresql://evan@localhost:5432/bun","query":"SELECT u.id, u.name, COUNT(m.id) as message_count FROM users u LEFT JOIN messages m ON u.id = m.user_id GROUP BY u.id, u.name ORDER BY message_count DESC"}

---

```

````
