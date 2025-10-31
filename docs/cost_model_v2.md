# Token Usage & Cost Model (Version 1.0)

**Project Name:** CareerSim – AI Career Experience Simulator
**Team Members:** Toma Danelia,Sopo Mrelashvili,Davit Ioramashvili,Temuri Mactchavariani
**Date:** 10/31/2025
**Version:** 1.0 (Initial Analysis & Optimization Plan)

---

## 📊 Executive Summary

**Current Cost Per Interaction:** **$0.00344**
**Projected Monthly Cost (10k interactions):** **$34.40**
**Optimization Potential:** **~95%** cost reduction identified
**Budget Status:** **Needs attention** (current model is not scalable)

**Key Insight:**

> The evaluation step, which re-sends the entire generated scenario to a premium model (Gemini Pro), accounts for **over 88% of the total cost**. Decoupling this step is the single most impactful optimization available.

---

## 1. Current Baseline (Analysis)

### Token Usage Breakdown

Based on the two-step process (Generation + Evaluation) for a single user interaction.

**Per Interaction Analysis (Generation + Evaluation):**

| Component                         | Model | Tokens         | Cost (Gemini) | % of Total |
| --------------------------------- | ----- | -------------- | ------------- | ---------- |
| **Generation Prompt**             | Flash | 70 (in)        | $0.00002      | 0.7%       |
| **Generation Output (Scenario)**  | Flash | 350 (out)      | $0.00037      | 10.7%      |
| **Evaluation Prompt**             | Pro   | 60 (in)        | $0.00021      | 6.1%       |
| **Evaluation Context (Scenario)** | Pro   | 350 (in)       | $0.00123      | 35.7%      |
| **Evaluation Output (Feedback)**  | Pro   | 150 (out)      | $0.00158      | 45.8%      |
| **TOTAL PER INTERACTION**         | **-** | **980 tokens** | **$0.00344**  | **100%**   |

**Key Findings:**

- The Evaluation step costs **$0.00302**, representing **88% of the total cost**.
- Sending the scenario context back to Gemini Pro (`Evaluation Context`) is the single most expensive input component.
- The premium model's output (`Evaluation Output`) is the single most expensive component overall.
- Average full interaction: ~980 tokens @ $0.00344

---

### Current Usage Patterns

**Projected Monthly Usage (Initial Launch):**

| Metric                         | Value                            |
| ------------------------------ | -------------------------------- |
| Total interactions/month       | 10,000                           |
| Average interactions/day       | ~333                             |
| Total tokens used/month        | 9,800,000 tokens                 |
| **Total projected cost/month** | **$34.40**                       |
| Models used                    | Gemini 1.5 Flash, Gemini 1.5 Pro |

**Cost Breakdown by Component (Monthly):**

| Component                   | Cost per Month |
| --------------------------- | -------------- |
| Scenario Generation (Flash) | $3.90          |
| Scenario Evaluation (Pro)   | $30.50         |
| **Total**                   | **$34.40**     |

---

## 2. Cost Model (Current vs. Projected)

### Production Phase (10,000 interactions/month)

| Phase      | Interactions | Cost (Current Model) | Cost (Optimized) | Savings |
| ---------- | ------------ | -------------------- | ---------------- | ------- |
| Monthly    | 10,000       | $34.40               | $1.73            | **95%** |
| **Annual** | **120,000**  | **$412.80**          | **$20.76**       | **95%** |

**Budget Allocation (Optimized Monthly):**

- AI API costs: $1.73
- Infrastructure (Server, DB): $10
- Buffer/contingency: $8.27
- **Total Budget: $20/month** (highly sustainable)

---

## 3. Optimization Strategies

### Strategy 1: Decouple Evaluation from Context ⭐ High Impact

**Current:** The entire 350-token scenario is sent back to the model for evaluation.

**Optimized:** Store the scenario in a database. Send only a short summary and the user's choice to the evaluation prompt.

**Implementation:**

- **Step 1:** Store the full scenario, challenge summary, and options in a DB with a `scenario_id`.
- **Step 2:** Use a compact evaluation prompt that references the stored data.

**Optimized Evaluation Prompt (~95 tokens):**

```text
You are an expert {career_title}. A user faced a critical challenge and had to choose from three options.

Challenge: "{challenge_summary}"
Options:
A: "{option_a}"
B: "{option_b}"
C: "{option_c}"

User's Choice: "{user_choice}"

Evaluate the choice. Provide concise feedback and a score (0-10). Return ONLY raw JSON:
{"feedback": "...", "score": ...}
```

**Token Savings:** 350 input tokens per evaluation.
**Cost Savings:** **~$12.30/month (36% reduction)** from this change alone.

---

### Strategy 2: Hybrid Model Selection ⭐ High Impact

**Strategy:** Use the cheaper Gemini Flash for the evaluation step instead of Gemini Pro. The task of evaluating a choice against 3 options may not require the power of Pro.

**Current Model:** Gemini Pro for evaluation.
**Optimized:** Gemini Flash for evaluation (after quality validation).

**Model Pricing (Evaluation Step):**

- Gemini Pro: $3.50/1M input, $10.50/1M output
- Gemini Flash: $0.35/1M input, $1.05/1M output (**90% cheaper!**)

**Cost Calculation (Per Evaluation - Optimized Prompt):**

- **Pro:** `(95in * $3.50) + (100out * $10.50)` = $0.00138
- **Flash:** `(95in * $0.35) + (100out * $1.05)` = $0.00014

**Implementation:**
Create a "Golden Set" of 20+ test cases. Run them through both models and compare feedback quality using semantic similarity and human review.

```python
# A simple routing function
def get_evaluation_model(quality_requirement="default"):
    if quality_requirement == "high_nuance":
        return "gemini-1.5-pro-latest"
    # Default to the cheaper, faster model
    return "gemini-1.5-flash-latest"
```

**Cost Savings:** **~$12.40/month (36% reduction)** by switching models.

---

### Strategy 3: Implement Scenario Caching ⭐ High Impact

**Strategy:** Cache generated scenarios for each career title to avoid redundant, expensive generation calls for popular roles.

**Expected Cache Hit Rate:** 90% (for popular roles like "Product Manager").

**Implementation (Python/Redis):**

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_or_create_scenario(career_title: str):
    cache_key = f"scenario:{career_title.lower().replace(' ', '_')}"

    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)  # Cache hit!

    # Cache miss - call API
    result = generate_scenario_with_llm(career_title)

    # Cache for 24 hours
    redis_client.setex(cache_key, 86400, json.dumps(result))
    return result
```

**Cost Savings (90% hit rate):**

- Reduces the $3.90/month generation cost by 90%.
- **Saves ~$3.51/month (10% total reduction)**.

---

### Strategy 4: Condense Prompts & Output ⭐ Medium Impact

**Strategy:** Reduce token count by making prompts more direct and adding output length constraints.

**Optimized Generation Prompt (~45 tokens - 30% reduction):**

```
You are a job simulation designer. Generate a realistic scenario (~150 words) for {career_title} with 1 challenge and 3 options (A/B/C). Output ONLY raw JSON: {"scenario": "string", "options": ["string", "string", "string"]}
```

**Optimized Evaluation Prompt (included in Strategy 1):** Add constraint `Provide concise feedback (~75 words)`.

**Why This Works:**

- Removes fluff ("for realistic job experiences").
- Removes redundancy ("Avoid hallucinations").
- Enforces shorter, more focused outputs, which also improves user experience.

**Token Savings:**

- **Generation:** -20 (in), -140 (out)
- **Evaluation:** -50 (out)
- **Total:** 210 tokens per interaction.
  **Cost Savings:** **~$6.80/month (20% reduction)**.

---

## 4. Combined Optimization Impact

### Cumulative Savings

| Optimization          | Token Reduction            | Cost Savings/Month | Implementation Effort |
| --------------------- | -------------------------- | ------------------ | --------------------- |
| #1: Decouple Context  | 350 input                  | $12.30 (36%)       | 8 hours               |
| #2: Hybrid Model      | N/A                        | $12.40 (36%)       | 4 hours               |
| #3: Caching (90% hit) | All tokens (90% gen calls) | $3.51 (10%)        | 2-4 hours             |
| #4: Condense Prompts  | 210 total                  | $6.80 (20%)        | 1 hour                |

**Original Projected Cost:** **$34.40/month**
**After ALL Optimizations:** **$1.73/month (95% reduction!)**

---

## 5. Implementation Roadmap

### Week 1 (Immediate - Do Now)

- [ ] **Condense all prompts** (1 hour)
  - Deploy new, shorter prompts for generation and evaluation.
  - Test quality with a golden set.
- [ ] **Implement Scenario Caching** (2-4 hours)
  - Set up Redis (Upstash free tier is perfect).
  - Implement the cache-aside logic.

**Expected Savings:** Immediate ~30% cost reduction.

---

### Week 2 (High Priority)

- [ ] **Implement Hybrid Model Selection** (4 hours)
  - Create the "Golden Set" for evaluation.
  - Build the quality assessment script.
  - Make a data-driven decision to switch evaluation to Gemini Flash.

**Expected Savings:** Additional ~36% cost reduction.

---

### Week 3 (High Priority)

- [ ] **Decouple Evaluation Context** (8 hours)
  - Add `challenge_summary`, etc., to your database schema.
  - Update application logic to store scenarios and retrieve summaries for evaluation.
  - Deploy the final compact evaluation prompt.

**Expected Savings:** Final ~36% cost reduction, reaching the ~95% total goal.

---

## 6. Cost Tracking Dashboard

### Metrics to Monitor

**Daily:**

- [ ] Cost per interaction (running average)
- [ ] Total daily spend
- [ ] Token usage trend (in vs. out)
- [ ] Model distribution (Pro vs. Flash calls)

**Weekly:**

- [ ] Weekly cost total
- [ ] Cache hit rate
- [ ] Budget burn rate

### Dashboard Implementation

**Simple Spreadsheet:**

```
Date | Interactions | Total Tokens | Cost   | Avg Cost/Int | Cache Hit % | Notes
-----|--------------|--------------|--------|--------------|-------------|---------
10/25 | 350          | 343,000      | $1.20  | $0.00344     | N/A         | Baseline
10/26 | 320          | 198,400      | $0.78  | $0.00244     | 55%         | Caching+Condensing
10/27 | 400          | 64,000       | $0.068 | $0.00017     | 91%         | All Opts Active
```

---

## 7. Budget Allocation (Optimized, Full Semester)

| Category                       | Budgeted |
| ------------------------------ | -------- |
| **AI API (Optimized)**         | $15      |
| **Infrastructure (DB, Cache)** | $15      |
| **Buffer/Contingency**         | $20      |
| **TOTAL**                      | **$50**  |

**Budget Health:** ✅ Healthy (well within a typical project budget).

---

## 8. Cost Alerts & Thresholds

### Alert Levels

**Warning (Yellow):**

- Daily spend > $1.00
- Weekly spend > $5.00

**Critical (Red):**

- Daily spend > $2.50
- 90% of monthly budget consumed

### Response Plan

**If Yellow Alert:** Review logs for anomalies, check cache hit rate.
**If Red Alert:** Pause new user signups, investigate potential bugs or abuse, team meeting to re-evaluate architecture.

---

## 9. Alternative Models Consideration

### Model Comparison (For Evaluation Task)

| Model                | Input Cost/1M | Output Cost/1M | Quality   | Notes                                     |
| -------------------- | ------------- | -------------- | --------- | ----------------------------------------- |
| **Gemini 1.5 Pro**   | $3.50         | $10.50         | Excellent | Overkill, too expensive.                  |
| **Gemini 1.5 Flash** | $0.35         | $1.05          | Very Good | **Chosen Model.** Best cost/quality.      |
| **GPT-4o-mini**      | $0.15         | $0.60          | Very Good | Cheaper, but requires OpenAI integration. |
| **Claude 3 Haiku**   | $0.25         | $1.25          | Very Good | Another strong alternative.               |

**Decision:** Stick with Gemini Flash for evaluation. It offers an excellent balance of quality and extremely low cost, and avoids adding another API provider.

---

## 10. Long-Term Cost Sustainability

### Post-Launch Considerations

**Expected Scale:**

- 5,000 users
- 4 interactions per user per month
- 20,000 interactions/month

**Costs (Fully Optimized Model):**

- 20,000 interactions × $0.00017/interaction = **$3.40/month**
- Infrastructure: $15/month (upgraded tiers)
- **Total: ~$18.40/month**

**Conclusion:** The optimized architecture is highly scalable and economically viable for a real product launch.

---

## ✅ Cost Optimization Checklist

**Week 1 (This Week):**

- [ ] Condense all prompts.
- [ ] Deploy Redis caching logic.
- [ ] Set up cost tracking spreadsheet.

**Week 2:**

- [ ] Build and run quality assessment for Gemini Flash vs. Pro.
- [ ] Switch evaluation model to Gemini Flash.
- [ ] Update cost projections.

**Week 3:**

- [ ] Refactor backend to decouple evaluation.
- [ ] Deploy final architecture.
- [ ] Validate final cost model and celebrate savings.

**Ongoing:**

- [ ] Monitor daily costs.
- [ ] Review weekly spend and cache hit rate.

---

**Document Version:** 1.0
**Last Updated:** [Current Date]
**Next Review:** End of Week 1 (after initial optimizations)
