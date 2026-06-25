from src.agents.agents import (
    build_reader_agent, build_search_agent, writer_chain, critic_chain
)


def step_search(topic: str) -> str:
    """Step 1 - Search agent gathers recent, reliable information."""
    search_agent = build_search_agent()
    result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    return result["messages"][-1].content


def step_read(topic: str, search_results: str) -> str:
    """Step 2 - Reader agent scrapes the most relevant source."""
    reader_agent = build_reader_agent()
    result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"Pick the most relevant URL and scape it for deeper content.\n\n"
            f"Search Results: \n{search_results[:8000]}"
        )]
    })
    return result["messages"][-1].content


def step_write(topic: str, search_results: str, scraped_content: str) -> str:
    """Step 3 - Writer drafts the structured report."""
    research_combined = (
        f"SEARCH RESULTS: \n {search_results} \n\n"
        f"DETAILED SCRAPED CONTENT: \n {scraped_content}"
    )
    return writer_chain.invoke({"topic": topic, "research": research_combined})


def step_critic(report: str) -> str:
    """Step 4 - Critic reviews and scores the report."""
    return critic_chain.invoke({"report": report})


def run_research_pipeline(topic: str) -> dict:
    state = {}

    print("\n" + "=" * 50)
    print("Step 1 - Search agent is working ...")
    print("=" * 50)
    state["search_results"] = step_search(topic)
    print("\n search results", state["search_results"])

    print("\n" + "=" * 50)
    print("Step 2 - Reader agent is scraping top resource ...")
    print("=" * 50)
    state["scaped_content"] = step_read(topic, state["search_results"])
    print("\n scraped content: \n", state["scaped_content"])

    print("\n" + "=" * 50)
    print("Step 3 - Writer is drafting the report ...")
    print("=" * 50)
    state["report"] = step_write(topic, state["search_results"], state["scaped_content"])
    print("\n Final Report \n", state["report"])

    print("\n" + "=" * 50)
    print("Step 4 - Critic is reviewing the report ...")
    print("=" * 50)
    state["feedback"] = step_critic(state["report"])
    print("\n Critic report \n", state["feedback"])

    return state
