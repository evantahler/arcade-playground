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

The "app" (user of the tools) is a bun project. `bun install` to install the deps, and run `bun start` to run the app. It's a little CLI test suite:

```
➜  app bun start
$ bun run --env-file=../.env index.ts
⚙️ Found the following tools:
Sql_DiscoverTables: Discover all the tables in the database
Sql_ExecuteQuery: Execute a query and return the results
Sql_GetTableSchema: Get the schema of a table

⚙️ testing `Sql.DiscoverTables`

--- response ---
The tables in the database are:

- users
- messages
--- tool calls ---
Sql_DiscoverTables: {"connection_string":"postgresql://evan@localhost:5432/bun","schema_name":"public"}
---

⚙️ testing `Sql.GetTableSchema`

--- response ---
The schema of the table `users` is:

- id: int
- name: str
- email: str
- password_hash: str
- created_at: datetime
- updated_at: datetime
--- tool calls ---
Sql_GetTableSchema: {"connection_string":"postgresql://evan@localhost:5432/bun","schema_name":"public","table_name":"users"}
---

⚙️ testing `Sql.ExecuteQuery`

--- response ---
Here are the first 10 user names:

- new name
- Evan
- Admin
--- tool calls ---
Sql_ExecuteQuery: {"connection_string":"postgresql://evan@localhost:5432/bun","query":"SELECT name FROM users LIMIT 10;"}
---
--- response ---
There are 3 users in the users table.
--- tool calls ---
Sql_ExecuteQuery: {"connection_string":"postgresql://evan@localhost:5432/bun","query":"SELECT COUNT(*) FROM users;"}
---
```
