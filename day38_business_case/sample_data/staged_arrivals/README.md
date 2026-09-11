# Staged and Late-Arriving Partner Updates

These files must be processed in folder order. They simulate information arriving at different times rather than presenting a perfectly complete dataset.

## Timeline

| Stage | Available at | What arrives | Expected learning outcome |
|---|---|---|---|
| 01 | 2025-09-03 08:00 UTC | Sales containing two unknown partner product codes | Preserve raw rows and quarantine unresolved mappings |
| 02 | 2025-09-05 11:30 UTC | Partner-authorized mapping changes | Version mappings and reprocess eligible exceptions |
| 03 | 2025-09-07 09:15 UTC | Corrections to two previously submitted transactions | Update the intended business event without creating duplicates |

Do not load all three folders at once during the walkthrough. Students should inspect warehouse and control state after each stage.

The term "partner" is used because the source organizations are sales partners, although the late-update behavior is also representative of supplier feeds.
