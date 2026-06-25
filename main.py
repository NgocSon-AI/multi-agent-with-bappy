from src.tools.tools import web_search
from src.tools.tools import scrape_url
from src.pipelines.pipelines import run_research_pipeline

def main():
    # query = input("Enter your search query: ")
    # results = web_search(query)
    # print("Search Results:")
    # print(results)

    # results_scrape = scrape_url.invoke(
    #     {"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}
    # )
    # print(results_scrape)

    topic = "The impact of AI on the job market in 2024"
    run_research_pipeline(topic)



if __name__ == "__main__":
    main()