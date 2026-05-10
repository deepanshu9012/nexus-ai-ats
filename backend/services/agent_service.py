from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from services.qdrant_service import search_resumes
from services.vector_service import generate_embedding


@tool
def search_candidate_database(query: str, limit: int = 3) -> str:
    """Search the internal resume vector database using a query string to find relevant candidates.

    Use this tool whenever you need to retrieve potential candidates that match technical requirements,
    skill keywords, role expectations, or hiring constraints in a Job Description. The tool returns a
    readable candidate list extracted from the database so you can compare profiles against the role.

    Args:
        query: A natural-language search query describing the candidate profile to find.
        limit: Number of candidates to return from the database.

    Returns:
        A formatted text summary of candidate matches including Name, Experience, Education,
        and Skills for each candidate. Returns "No matching candidates found." when there are no hits.
    """
    query_vector = generate_embedding(query)
    safe_limit = max(1, int(limit))
    matches = search_resumes(query_vector, limit=safe_limit)

    if not matches:
        return "No matching candidates found."

    lines: list[str] = []
    for index, match in enumerate(matches, start=1):
        profile = match.get("profile", {}) if isinstance(match, dict) else {}
        skills = profile.get("skills", [])
        skills_text = ", ".join(skills) if isinstance(skills, list) and skills else "N/A"
        lines.extend(
            [
                f"Candidate {index}",
                f"Name: {profile.get('name', 'N/A')}",
                f"Email: {profile.get('email', 'N/A')}",
                f"Experience: {profile.get('years_experience', 'N/A')} years",
                f"Education: {profile.get('education', 'N/A')}",
                f"Skills: {skills_text}",
                "",
            ]
        )

    return "\n".join(lines).strip()


async def run_hiring_agent(job_description: str, num_candidates: int = 3) -> str:
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    safe_num_candidates = max(1, int(num_candidates))

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an Expert Technical Recruiter. You are given a Job Description. "
                "You MUST use the 'search_candidate_database' tool to query the database "
                "for candidates that match the technical requirements, and you MUST pass "
                "limit={num_candidates} in that tool call. Once you have the "
                "candidates, evaluate them against the Job Description. "
                "Find the top {num_candidates} candidates for this role. "
                "Write a structured Markdown report highlighting the top {num_candidates} "
                "candidates to interview. You MUST format your analysis for EACH candidate "
                "as two completely separate blockquotes with a blank empty line between them. "
                "Do not merge them into one line. Follow this exact template:\n\n"
                "> **Why they are a good fit:** [reasoning]\n\n"
                "> **Missing skills:** [reasoning]",
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("human", "{input}"),
        ]
    )

    tools = [search_candidate_database]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = agent_executor.invoke(
        {
            "input": job_description,
            "num_candidates": safe_num_candidates,
        }
    )
    return str(result.get("output", ""))
