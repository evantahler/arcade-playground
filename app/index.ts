import Arcade from "@arcadeai/arcadejs";

const ARCADE_API_KEY = Bun.env.ARCADE_API_KEY;
const ARCADE_URL = Bun.env.ARCADE_URL;
const USER_ID = Bun.env.USER_ID;
const DB_CONNECTION_STRING = Bun.env.DB_CONNECTION_STRING;
const DB_DIALECT = DB_CONNECTION_STRING?.split(":")[0];

const SYSTEM_PROMPT = `
You are an expert SQL analyst.
For all questions, you will use only the tools provided to you to answer the question, and no prior knowledge.
For all questions, your database connection string is: "${DB_CONNECTION_STRING}".
The SQL dialect is "${DB_DIALECT}".
If a tool call requires a schema, and one has not been provided, assume the schema is "public".
If a tool call produces a response with multiple entries, format your response as a markdown list, one per line.
`;

const client = new Arcade({
  baseURL: ARCADE_URL,
  apiKey: ARCADE_API_KEY,
});

const sqlTools = await client.tools.formatted.list({
  format: "openai",
  toolkit: "sql",
});

console.log("⚙️ Found the following tools:");
sqlTools.items.forEach((tool) => {
  // @ts-ignore
  console.log(`${tool.function.name}: ${tool.function.description}`);
});

let response: Arcade.Chat.ChatResponse | null = null;

console.log("\r\n⚙️ testing `Sql.DiscoverTables`\r\n");

response = await client.chat.completions.create({
  messages: [
    {
      role: "system",
      content: SYSTEM_PROMPT,
    },
    {
      role: "user",
      content: "Discover all the tables in the database",
    },
  ],
  model: "gpt-4o",
  user: USER_ID,
  tools: ["Sql.DiscoverTables"],
  tool_choice: "generate",
});
displayResponse(response);

console.log("\r\n⚙️ testing `Sql.GetTableSchema`\r\n");

response = await client.chat.completions.create({
  messages: [
    {
      role: "system",
      content: SYSTEM_PROMPT,
    },
    {
      role: "user",
      content: "Get the schema of the table `users`",
    },
  ],
  model: "gpt-4o",
  user: USER_ID,
  tools: ["Sql.GetTableSchema"],
  tool_choice: "generate",
});
displayResponse(response);
const userTableSchema = response.choices?.[0]?.message?.content;

response = await client.chat.completions.create({
  messages: [
    {
      role: "system",
      content: SYSTEM_PROMPT,
    },
    {
      role: "user",
      content: "Get the schema of the table `messages`",
    },
  ],
  model: "gpt-4o",
  user: USER_ID,
  tools: ["Sql.GetTableSchema"],
  tool_choice: "generate",
});
displayResponse(response);
const messagesTableSchema = response.choices?.[0]?.message?.content;

console.log("\r\n⚙️ testing `Sql.ExecuteQuery`\r\n");

response = await client.chat.completions.create({
  messages: [
    {
      role: "system",
      content: SYSTEM_PROMPT,
    },
    {
      role: "user",
      content: `Get the first 10 user's names.  Additional context about the user's table: ${userTableSchema}`,
    },
  ],
  model: "gpt-4o",
  user: USER_ID,
  tools: ["Sql.ExecuteQuery"],
  tool_choice: "generate",
});
displayResponse(response);

response = await client.chat.completions.create({
  messages: [
    {
      role: "system",
      content: SYSTEM_PROMPT,
    },
    {
      role: "user",
      content: `Count how many users there are.  Additional context about the user's table: ${userTableSchema}`,
    },
  ],
  model: "gpt-4o",
  user: USER_ID,
  tools: ["Sql.ExecuteQuery"],
  tool_choice: "generate",
});
displayResponse(response);

response = await client.chat.completions.create({
  messages: [
    {
      role: "system",
      content: SYSTEM_PROMPT,
    },
    {
      role: "user",
      content: `How many messages has each user sent?  Group by user id and name.  Additional context about the user's table: ${userTableSchema}.  Additional context about the messages table: ${messagesTableSchema}`,
    },
  ],
  model: "gpt-4o",
  user: USER_ID,
  tools: ["Sql.ExecuteQuery"],
  tool_choice: "generate",
});
displayResponse(response);
/* --- */

function displayResponse(response: Arcade.Chat.ChatResponse) {
  console.log("--- response ---");
  console.log(response.choices?.[0]?.message?.content);
  console.log("--- tool calls ---");
  response.choices?.[0]?.message?.tool_calls?.map((tool) => {
    if (!tool || !tool.function) return;
    console.log(`${tool.function.name}: ${tool.function.arguments}`);
  });
  console.log("---");
}
