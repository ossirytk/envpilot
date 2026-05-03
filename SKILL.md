---
name: envpilot
description: Safe .env file inspector — keys only, never values. Use this skill when the user wants to inspect, compare, or validate environment variable files without exposing secrets. Invoke for prompts like "what keys are in .env?", "compare .env and .env.example", "am I missing any env vars?", or "find all .env files in this project".
---

## Overview

envpilot reads, diffs, and validates `.env` files, returning only key names — secret values are never exposed, logged, or transmitted. Use it to safely reason about environment configuration without leaking credentials.

## Available Tools

| Tool | When to use |
|------|-------------|
| `read_env` | List all keys defined in a `.env` file. Required: `path`. Returns key names only. |
| `diff_env` | Compare keys between two `.env` files. Required: `base_path`, `compare_path`. Returns `only_in_base`, `only_in_compare`, `in_both`. |
| `validate_env` | Check that all keys in a reference file exist in a target file. Required: `reference_path`, `target_path`. Returns missing keys. |
| `list_env_files` | Discover `.env` files in a directory tree. Optional: `root` (default `.`), `max_depth` (default `4`). |

## Guidance

- **Never ask for or display values** — envpilot intentionally omits them. If the user needs to check a value, they should do so manually.
- **Onboarding check**: use `validate_env` with `.env.example` as `reference_path` and `.env` as `target_path` to find missing required vars.
- **Compare environments**: use `diff_env` with `base_path` set to `.env.staging` and `compare_path` set to `.env.production` to spot differences (keys only).
- **Discovery first**: use `list_env_files` before `read_env` when you don't know the exact path.
