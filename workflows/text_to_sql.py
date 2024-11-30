import time
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Context,
    Event,
)
from llama_index.core.llms import ChatResponse
from utils.index_utils import get_table_context_and_rows_str

class TableRetrieveEvent(Event):
    """Result of running table retrieval."""
    table_context_str: str
    query: str

class TextToSQLEvent(Event):
    """Text-to-SQL event."""
    sql: str
    query: str

def parse_response_to_sql(chat_response: ChatResponse) -> str:
    """Parse response to SQL."""
    response = chat_response.message.content
    sql_query_start = response.find("SQLQuery:")
    if sql_query_start != -1:
        response = response[sql_query_start:]
        if response.startswith("SQLQuery:"):
            response = response[len("SQLQuery:") :]
    sql_result_start = response.find("SQLResult:")
    if sql_result_start != -1:
        response = response[:sql_result_start]
    return response.strip().strip("```").strip()

class TextToSQLWorkflow(Workflow):
    """Text-to-SQL Workflow that does query-time table retrieval."""
    def __init__(
        self,
        obj_retriever,
        text2sql_prompt,
        sql_retriever,
        response_synthesis_prompt,
        llm,
        vector_index_dict,
        sql_database,
        semantic_cache,  # Add semantic_cache parameter
        verbose=False,
        *args,
        **kwargs,
    ) -> None:
        """Initialize parameters."""
        super().__init__(*args, **kwargs)
        self.obj_retriever = obj_retriever
        self.text2sql_prompt = text2sql_prompt
        self.sql_retriever = sql_retriever
        self.response_synthesis_prompt = response_synthesis_prompt
        self.llm = llm
        self.vector_index_dict = vector_index_dict
        self.sql_database = sql_database
        self.semantic_cache = semantic_cache  # Store the cache
        self._verbose = verbose

    @step
    def retrieve_tables(self, ctx: Context, ev: StartEvent) -> TableRetrieveEvent:
        """Retrieve relevant tables and context."""
        table_schema_objs = self.obj_retriever.retrieve(ev.query)
        table_context_str = get_table_context_and_rows_str(
            ev.query,
            table_schema_objs,
            self.vector_index_dict,
            self.sql_database,
            verbose=self._verbose,
        )
        return TableRetrieveEvent(table_context_str=table_context_str, query=ev.query)

    @step
    def generate_sql(self, ctx: Context, ev: TableRetrieveEvent) -> TextToSQLEvent:
        """Generate SQL statement with caching."""
        # Construct the prompt
        fmt_messages = self.text2sql_prompt.format_messages(
            query_str=ev.query, schema=ev.table_context_str
        )
        prompt_text = fmt_messages[0].content

        # Check the cache
        cached_result = self.semantic_cache.check(
            prompt=prompt_text,
            distance_threshold=self.semantic_cache.distance_threshold
        )

        if cached_result:
            if self._verbose:
                print("Cache hit for SQL generation.")
            sql = cached_result[0]['response']
        else:
            if self._verbose:
                print("Cache miss for SQL generation. Generating SQL with LLM.")
            chat_response = self.llm.chat(fmt_messages)
            sql = parse_response_to_sql(chat_response)
            # Store in cache
            self.semantic_cache.store(
                prompt=prompt_text,
                response=sql,
                metadata={"generated_at": time.time()}
            )

        return TextToSQLEvent(sql=sql, query=ev.query)

    @step
    def generate_response(self, ctx: Context, ev: TextToSQLEvent) -> StopEvent:
        """Run SQL retrieval and generate final response with caching."""
        # Retrieve SQL query results
        retrieved_rows = self.sql_retriever.retrieve(ev.sql)

        # Construct the prompt
        fmt_messages = self.response_synthesis_prompt.format_messages(
            sql_query=ev.sql,
            context_str=str(retrieved_rows),
            query_str=ev.query,
        )
        prompt_text = fmt_messages[0].content

        # Check the cache
        cached_result = self.semantic_cache.check(
            prompt=prompt_text,
            distance_threshold=self.semantic_cache.distance_threshold
        )

        if cached_result:
            if self._verbose:
                print("Cache hit for response synthesis.")
            final_response = cached_result[0]['response']
        else:
            if self._verbose:
                print("Cache miss for response synthesis. Generating response with LLM.")
            chat_response = self.llm.chat(fmt_messages)
            final_response = chat_response.message.content
            # Store in cache
            self.semantic_cache.store(
                prompt=prompt_text,
                response=final_response,
                metadata={"generated_at": time.time()}
            )

        return StopEvent(result=final_response)
