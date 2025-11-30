# Capstone Link

**Team Name:** AscendAI  
**Project Title:** CareerSim Platform  
**Team Members:** Sopo Mrelashvili, Toma Danelia, Davit Ioramashvili, Temo Machavariani  
**Date:** 2025-11-30  
**Repository:** https://github.com/dioramashvili/Ascend.AI  

---

## Capstone Integration Summary

This document explains how our Lab 6 functions integrate into the full Capstone project.

### Function Reused from Lab 6
**generate_career_scenario(career_title)**  
**Purpose:** Generates realistic career simulation scenarios used across the CareerSim platform.

---

## Integration Plan

- Function moved to: `src/functions/scenarios.py`  
- Integrated with refined prompt templates (Week 7)  
- Called through the main LLM pipeline using structured function calling  
- Used in chatbot flow:  
  - **User:** “Generate a scenario for a data analyst.”  
  - **System:** LLM triggers function → returns scenario → displayed to the user  

---

## Next Step

Next week we will add a new function:  
**evaluate_user_response(career_title, user_answer)**  
Purpose: Automatically evaluate the user’s written answer with scoring and feedback based on rubric templates.

This function will integrate into the scenario evaluation workflow and store results via `save_evaluation()`.

