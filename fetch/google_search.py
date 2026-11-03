import json
from logs.json_log import log
from typing import List, Dict
from orbitaim_data.api.wrapper import discovery_search
from config.settings import project_id, location, api_key, SPECIFIC_ENGINES

def run_search_and_save(
    query: str,
    total_results_per_engine: int = 100,
    fields: List[str] = None
) -> Dict:

    if not SPECIFIC_ENGINES:
        log.warning("No specific search engines configured (env vars missing).")
        return {"results": []}

    if fields is None:
        fields = ["title", "link", "description", "source", "pubDate"]

    all_results = []

    for source_name, engine_id in SPECIFIC_ENGINES.items():

        if not engine_id:
            log.warning(f"Skipping {source_name}: no engine ID configured.")
            continue

        log.info(f"Searching '{query}' on {source_name} (Engine ID: {engine_id})...")

        results = discovery_search(
            project_id=project_id,
            location=location,
            engine_id=engine_id,
            api_key=api_key,
            query=query,
            total_results=total_results_per_engine,
            fields=fields
        )

        extracted = results.get("results", [])

        for r in extracted:

            # Ensure source is present
            if "source" not in r or not r.get("source"):
                r["source"] = source_name

            # Inject required fields
            r["search_term"] = query
            r["source_type"] = "Google"     # your requirement

            # Default fallbacks
            r.setdefault("title", "")
            r.setdefault("description", "")
            r.setdefault("pubDate", "")
            r.setdefault("link", "")

        all_results.extend(extracted)

    log.info(f"Collected {len(all_results)} results from {len(SPECIFIC_ENGINES)} engines.")
    
    # Save to JSON
    save_json(all_results)
    
    return {"results": all_results}


import os

def save_json(data: List[Dict], output_file="data/search_results.json"):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ Saved JSON → {output_file}")
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")


# if __name__ == "__main__":
#     query = "new warehouse parks in india"

#     results = search_all_engines(query, total_results_per_engine=100)

#     print(f"\nCollected {len(results)} total results\n")

#     # Save the results into JSON file
#     save_json(results)

#     # Print sample
#     for idx, r in enumerate(results[:5], start=1):
#         print(f"\nResult #{idx}:")
#         print(f" Title      : {r.get('title')}")
#         print(f" Link       : {r.get('link')}")
#         print(f" Description: {r.get('description')}")
#         print(f" Source     : {r.get('source')}")
#         print(f" Published  : {r.get('pubDate')}")
#         print(f" SearchTerm : {r.get('search_term')}")
#         print(f" SourceType : {r.get('source_type')}")
#         print("-" * 60)
