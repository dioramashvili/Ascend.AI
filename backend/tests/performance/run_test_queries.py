#!/usr/bin/env python3
"""
Test script for Lab 9 - Runs 51 test queries and logs metrics.
Adapted for CareerSim API endpoints.

Usage: 
1. Ensure backend is running: uvicorn app.main:app --reload
2. Run: python tests/performance/run_test_queries.py
"""

import asyncio
import httpx
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

TEST_QUERIES = [
    {"career": "product manager", "focus": "sprint planning", "context": "Team velocity is 40 points, we have 60 points of backlog items requested by stakeholders"},
    {"career": "product manager", "focus": "sprint planning", "context": "Developer is on vacation for half the sprint, how to adjust capacity"},
    {"career": "product manager", "focus": "sprint planning", "context": "Product owner wants to add urgent feature mid-sprint"},
    {"career": "product manager", "focus": "sprint planning", "context": "Technical debt items keep getting deprioritized over features"},
    {"career": "product manager", "focus": "sprint planning", "context": "Team disagrees on story point estimates for complex backend task"},
    {"career": "product manager", "focus": "sprint planning", "context": "Stakeholder requests demo of incomplete feature"},
    {"career": "product manager", "focus": "sprint planning", "context": "Sprint goal conflicts with quarterly OKRs"},
    {"career": "product manager", "focus": "sprint planning", "context": "QA capacity is bottleneck for sprint completion"},
    {"career": "product manager", "focus": "sprint planning", "context": "Dependencies on external team blocking sprint items"},
    {"career": "product manager", "focus": "sprint planning", "context": "Team morale low after failed sprint delivery"},

    {"career": "software engineer", "focus": "code review", "context": "Senior developer consistently rejects junior's PRs with harsh feedback"},
    {"career": "software engineer", "focus": "code review", "context": "PR has been open for 5 days with no reviewers"},
    {"career": "software engineer", "focus": "code review", "context": "Reviewer requests complete rewrite of working solution"},
    {"career": "software engineer", "focus": "code review", "context": "Team lead merges own PRs without review"},
    {"career": "software engineer", "focus": "code review", "context": "Code coverage dropped from 80% to 60% after merge"},
    {"career": "software engineer", "focus": "code review", "context": "Security vulnerability found in approved PR after deployment"},
    {"career": "software engineer", "focus": "code review", "context": "Developer refuses to add unit tests citing time pressure"},
    {"career": "software engineer", "focus": "code review", "context": "Conflicting coding standards between team members"},
    {"career": "software engineer", "focus": "code review", "context": "Large PR with 2000+ lines of changes"},
    {"career": "software engineer", "focus": "code review", "context": "Legacy code modification without existing tests"},

    {"career": "engineering manager", "focus": "team conflict", "context": "Two senior developers disagree on microservices vs monolith architecture"},
    {"career": "engineering manager", "focus": "team conflict", "context": "Remote team member feels excluded from decisions"},
    {"career": "engineering manager", "focus": "team conflict", "context": "Engineer refuses to document their code"},
    {"career": "engineering manager", "focus": "team conflict", "context": "Team member takes credit for others' work in standup"},
    {"career": "engineering manager", "focus": "team conflict", "context": "Cross-functional blame game after production incident"},
    {"career": "engineering manager", "focus": "team conflict", "context": "New hire struggles to integrate with established team"},
    {"career": "engineering manager", "focus": "team conflict", "context": "Engineer wants to use new technology stack, team prefers stability"},
    {"career": "engineering manager", "focus": "team conflict", "context": "Disagreement over on-call rotation fairness"},
    {"career": "engineering manager", "focus": "team conflict", "context": "Tech lead micromanages junior developers"},
    {"career": "engineering manager", "focus": "team conflict", "context": "Communication breakdown between frontend and backend teams"},

    {"career": "tech lead", "focus": "technical decision", "context": "Choose between AWS Lambda vs ECS for new microservice"},
    {"career": "tech lead", "focus": "technical decision", "context": "Database migration from PostgreSQL to MongoDB proposed"},
    {"career": "tech lead", "focus": "technical decision", "context": "Build vs buy decision for authentication system"},
    {"career": "tech lead", "focus": "technical decision", "context": "Kubernetes adoption for small team of 5 developers"},
    {"career": "tech lead", "focus": "technical decision", "context": "GraphQL vs REST API for mobile app backend"},
    {"career": "tech lead", "focus": "technical decision", "context": "Monorepo vs polyrepo for growing engineering org"},
    {"career": "tech lead", "focus": "technical decision", "context": "Feature flags implementation strategy"},
    {"career": "tech lead", "focus": "technical decision", "context": "CI/CD pipeline taking 45 minutes to complete"},
    {"career": "tech lead", "focus": "technical decision", "context": "Technical debt payoff vs new feature development ratio"},
    {"career": "tech lead", "focus": "technical decision", "context": "Observability stack selection for distributed system"},
]

async def run_single_query(client: httpx.AsyncClient, query: dict, index: int) -> dict:
    """Run a single test query and return results"""
    start_time = time.time()
    
    payload = {
        "career_title": query["career"],
        "focus_area": f"{query['focus']}: {query['context']}",
        "difficulty": "intermediate"
    }

    try:
        response = await client.post(
            f"{BASE_URL}/api/scenarios/generate",
            json=payload,
            timeout=60.0 
        )
        latency = time.time() - start_time
        
        # Initialize defaults for cost/tokens
        i_tokens = 0
        o_tokens = 0
        cost = 0.0
        error_msg = None

        if response.status_code == 200:
            data = response.json()
            i_tokens = data.get('input_tokens', 0)
            o_tokens = data.get('output_tokens', 0)
            # Gemini Flash Pricing
            cost = (i_tokens / 1_000_000 * 0.35) + (o_tokens / 1_000_000 * 1.05)
        else:
            error_msg = response.text[:200]
        
        return {
            "index": index + 1,
            "scenario": f"{query['career']} - {query['focus']}",
            "status": response.status_code,
            "latency": round(latency, 2),
            "success": response.status_code == 200,
            "error": error_msg,
            "cost": round(cost, 6), 
            "input_tokens": i_tokens,
            "output_tokens": o_tokens
        }
    except Exception as e:
        
        return {
            "index": index + 1,
            "scenario": f"{query['career']} - {query['focus']}",
            "status": 0,
            "latency": time.time() - start_time,
            "success": False,
            "error": str(e)[:200],
            "cost": 0.0,          
            "input_tokens": 0,
            "output_tokens": 0
        }

async def run_all_tests():
    """Run all test queries and save to file"""
    print(f"\n{'='*60}")
    print(f"Lab 9 Baseline Tests - {len(TEST_QUERIES)} Queries")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for i, query in enumerate(TEST_QUERIES):
            result = await run_single_query(client, query, i)
            results.append(result)
            
            # Print to Terminal
            status = "✓" if result["success"] else "✗"
            print(f"[{result['index']:02d}/{len(TEST_QUERIES)}] {status} {result['scenario']:<35} {result['latency']:.2f}s")
            
            await asyncio.sleep(1.0) 
    
    successful = sum(1 for r in results if r["success"])
    total_latency = sum(r["latency"] for r in results)
    avg_latency = total_latency / len(results) if results else 0

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(results),
        "successful": successful,
        "failed": len(results) - successful,
        "avg_latency_seconds": round(avg_latency, 4),
        "total_duration_seconds": round(total_latency, 4),
        "details": results
    }
    filename = "lab9_metrics.json"
    with open(filename, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Success Rate:     {successful/len(results)*100:.1f}%")
    print(f"Avg Latency:      {avg_latency:.2f}s")
    print(f"Total Time:       {total_latency:.1f}s")
    print(f"\n📄 Metrics saved to: {filename}") # Confirm file save
    print(f"{'='*60}")
    
    failures = [r for r in results if not r["success"]]
    if failures:
        print(f"\nFailed Queries:")
        for f in failures:
            print(f"  [{f['index']}] {f['scenario']}: {f['error']}")

if __name__ == "__main__":
    print(f"Targeting Backend at: {BASE_URL}")
    asyncio.run(run_all_tests())