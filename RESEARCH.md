# Problem and selection brief

Observed 26 October 2026. Rank 2 of today's five by problem evidence, practical usefulness, differentiation, reproducible demonstration and maintenance burden. These are editorial priorities, not measured scores or a growth prediction.

**User.** API maintainers changing accepted wire keys while keeping Python field names stable.

**Painful task.** Reordering or removing AliasChoices can change which payloads validate or which value wins when clients send both keys.

**Evidence.** [Official documentation](https://pydantic.dev/docs/validation/latest/concepts/alias/); [upstream issue 10839](https://github.com/pydantic/pydantic/issues/10839). Verified open upstream report about shared aliases/error locations on Pydantic 2.9.2. Migration demand is inferred from those semantics, not a direct request for this tool.

**Smallest complete outcome.** Bounded generation of key combinations and deliberately conflicting alias values, evaluated against both real Pydantic models. Reports accepted/rejected transitions and value changes.

**Acceptance.** The example reversing id/asset_id precedence must yield exactly one VALUE_CHANGED case with both models accepting. Removing id yields a concrete REJECTED_AFTER payload. Shared keys feeding two fields are preserved.

**Failure criteria.** Reject unsupported types/reserved field names and more than 512 generated key combinations. Missing fields produce structured Pydantic errors.

**Maintenance burden.** Pydantic plus pydantic-core and its normal dependencies. Limited flat required int/str/bool schemas avoid executing arbitrary user validators.

## Alternatives found

The day's first searches were `duckdb in:name sort:stars`, `numpy in:name sort:stars`, `pydantic in:name sort:stars`, `pandas in:name sort:stars` and `matplotlib in:name sort:stars`. We chose active software ecosystems rather than global lists/tutorials or five variants of one product. Use-case query: `pydantic migration sort:stars; expanded: pydantic sort:stars; bump-pydantic sort:stars`. GitHub search results were limited to the top 3 or 5 and inspected for relevance. This is the highest-star relevant upstream baseline found within this search coverage, not an exhaustive global ranking.

| Repository | Stars observed | Last push observed UTC | License | Role and workflow |
| --- | ---: | --- | --- | --- |
| [pydantic/pydantic](https://github.com/pydantic/pydantic) | 29195 | 2026-10-23T14:58:28Z | MIT | Upstream baseline and pinned integration engine |
| [datamodel-code-generator/datamodel-code-generator](https://github.com/datamodel-code-generator/datamodel-code-generator) | 4043 | 2026-10-26T04:13:53Z | MIT | Generate model source from schemas; a different migration step |
| [pydantic/bump-pydantic](https://github.com/pydantic/bump-pydantic) | 351 | 2026-05-27T15:54:33Z | MIT | Archived V1-to-V2 source codemod; historical alternative, not an active anchor |

Metadata observation: upstream 2026-10-26T06:29:02.826Z; comparables 2026-10-26T07:40:21Z. Pinned integration release: `v2.14.1`. Comparator README/docs were read; competitor installations and performance were not benchmarked. A successful example here establishes our behavior only. We do not claim those alternatives lack an equivalent workflow. Licenses apply to upstream code, which is not vendored here.


## Portfolio differentiation

All 223 owned repository names and indexed purposes were screened against these five candidate tasks. The closest contracts were reviewed explicitly: schema-gen creates Python models from JSON samples; this tool generates no source and instead compares accepted payload behavior. argv alias tools concern command-line flags, not Pydantic wire-model semantics. This screen uses the portfolio index and repository inventory rather than claiming an exhaustive source-code similarity analysis. No project is a rename, fork or split of another candidate. Today's other candidates concern distinct inputs: Parquet values, array-storage coordinates, model wire keys, resampling row groups and rendered text rectangles.

## Discovery and honest limits

A useful discovery path is a searchable task-focused README, one reproducible example, accurate GitHub topics and a chronological portfolio entry after verified publication. There is no authorization for promotional comments or third-party pull requests. Stars identify an audience to investigate; no adoption, speed advantage or organic growth is promised. Installation and CI evidence belong in the final validation receipt, not in unsupported comparative claims.
