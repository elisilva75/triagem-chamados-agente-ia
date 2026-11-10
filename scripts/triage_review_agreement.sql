WITH ranked_reviews AS (
    SELECT
        attempt_id,
        ticket_id,
        content_revision,
        category,
        priority,
        ROW_NUMBER() OVER (
            PARTITION BY attempt_id
            ORDER BY created_at DESC, id DESC
        ) AS review_rank
    FROM human_reviews
),
comparisons AS (
    SELECT
        attempt.mode,
        CASE WHEN attempt.suggestion ->> 'category' = review.category THEN 1 ELSE 0 END
            AS category_agrees,
        CASE WHEN attempt.suggestion ->> 'priority' = review.priority THEN 1 ELSE 0 END
            AS priority_agrees
    FROM ranked_reviews AS review
    JOIN triage_attempts AS attempt
        ON attempt.id = review.attempt_id
        AND attempt.ticket_id = review.ticket_id
        AND attempt.content_revision = review.content_revision
    WHERE review.review_rank = 1
        AND attempt.status = 'sucesso'
        AND attempt.suggestion ->> 'category' IS NOT NULL
        AND attempt.suggestion ->> 'priority' IS NOT NULL
)
SELECT
    mode,
    COUNT(*) AS reviewed_attempts,
    SUM(category_agrees) AS category_agreements,
    ROUND(100.0 * SUM(category_agrees) / COUNT(*), 2) AS category_agreement_pct,
    SUM(priority_agrees) AS priority_agreements,
    ROUND(100.0 * SUM(priority_agrees) / COUNT(*), 2) AS priority_agreement_pct,
    SUM(category_agrees * priority_agrees) AS both_agreements
FROM comparisons
GROUP BY mode
ORDER BY mode;
