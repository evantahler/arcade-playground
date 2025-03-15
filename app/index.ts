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
If a tool call produces a response with multiple entries, format your response as a markdown table, with one row per entry.
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

const tables = await chat("Discover all the tables in the database");
const schemas = await chat(
  `Get the schemas of the tables in the database.  The tables are: ${tables}`,
  tables
);
await chat(
  `Get the first 10 user's names.  The database schema is: ${schemas}`,
  schemas
);
await chat(
  `Count how many users there are.  The database schema is: ${schemas}`,
  schemas
);
await chat(
  `How many messages has each user sent?  Group by user id and name.  The database schema is: ${schemas}`,
  schemas
);
await chat(
  `How many messages has each user sent?  Group by user id and name.  Respond not with text, but with an ascii-art bar chart representing this data. The database schema is: ${schemas}`,
  schemas
);

/* --- UTILITIES --- */

function buildPrompt(question: string) {
  return {
    messages: [
      {
        role: "system",
        content: SYSTEM_PROMPT,
      },
      {
        role: "user",
        content: question,
      },
    ],
    model: "gpt-4o",
    user: USER_ID,
    tools: ["Sql.ExecuteQuery"],
    tool_choice: "generate",
  };
}

async function chat(
  question: string,
  replace: string
): Promise<string | undefined> {
  console.log(`\r\n[❓] Asking: ${question.replace(replace, " {...}")}\r\n`);
  const response = await client.chat.completions.create(buildPrompt(question));
  displayResponse(response);
  return response.choices?.[0]?.message?.content;
}

function displayResponse(response: Arcade.Chat.ChatResponse) {
  console.log("--- response ---");
  console.log(response.choices?.[0]?.message?.content);
  console.log("\r\n--- tool calls ---");
  response.choices?.[0]?.message?.tool_calls?.map((tool) => {
    if (!tool || !tool.function) return;
    console.log(`${tool.function.name}: ${tool.function.arguments}`);
  });
  console.log("---");
}
