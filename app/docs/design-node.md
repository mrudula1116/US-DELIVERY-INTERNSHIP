# Design Note — US Delivery AI Support System

## 1. Production Failure Modes

### Failure Mode 1: Incorrect ticket classification

The triage system can incorrectly classify a ticket when the subject or body contains ambiguous language. For example, a ticket may mention billing while the actual problem is an integration failure. Keyword-based classification can therefore select the wrong category or product.

I would detect this by monitoring classification distributions and testing representative tickets through the evaluation harness. Low-confidence or ambiguous classifications should be flagged for human review rather than being automatically routed. The mitigation would be to improve the classification rules, add precedence between conflicting categories, and eventually use a trained or LLM-based classifier with structured output and confidence scoring.

### Failure Mode 2: Incorrect or irrelevant knowledge-base retrieval

The retrieval layer may return a technically related document that is not the best match for the ticket. This can happen when several products or troubleshooting documents contain overlapping terminology.

I would detect this through retrieval evaluation cases that check whether the expected knowledge-base document appears in the top results. Retrieval scores and failed evaluation cases should be monitored. The mitigation is to improve chunking, ranking, product-aware weighting, and query normalization. For higher scale, a vector or hybrid retrieval system could replace the current lightweight lexical retrieval approach.

### Failure Mode 3: Missing or inconsistent source data

The application depends on the provided synthetic accounts, tickets, and knowledge-base documents. Missing account fields, malformed JSON, unexpected ticket structures, or missing Markdown files could cause incorrect outputs or runtime failures.

I would detect this using input validation, startup checks, exception logging, and adversarial evaluation cases containing incomplete data. The mitigation is to validate schemas before processing, provide safe defaults for optional fields, and return explicit errors when required information such as an account ID cannot be found.

---

## 2. Latency vs. Quality

A deliberate design trade-off was made in favour of predictable response time and simplicity. The current retrieval implementation loads and searches the local Markdown knowledge base instead of making an external retrieval request for every ticket. This reduces network latency and makes the system deterministic and easy to run locally.

The trade-off is that lightweight lexical retrieval is less semantically powerful than a production embedding-based or hybrid retrieval system. A semantically similar ticket may use different terminology from the knowledge-base document and therefore receive a weaker match.

If latency were the hard constraint, I would keep the knowledge base indexed in memory rather than reading and processing every Markdown file for each request. I would also cache frequently used retrieval results and use a lightweight local index. If quality were more important than latency, I would introduce embeddings and a vector or hybrid search layer.

---

## 3. Data Sensitivity

Support tickets and customer account summaries can contain personally identifiable information and commercially sensitive information. The design therefore keeps the provided mock dataset local and does not require sending customer data to external APIs.

The system should avoid logging complete ticket bodies, customer contacts, account information, or other sensitive fields unnecessarily. Application logs should contain identifiers and operational metadata rather than raw customer content. Secrets such as API keys must be stored in environment variables and never committed to the repository.

If an external LLM or API were introduced in production, sensitive fields should first be minimized or redacted. Only the information required to perform the specific task should be sent to the external service. Access should also be controlled using authentication, authorization, encryption, and audit logging.

The assignment specifically requires use of the provided mock dataset only, so the current implementation does not depend on live customer data or external datasets.

---

## 4. Scaling to 10× Ticket Volume

The current implementation is suitable for the provided synthetic dataset but would require changes at significantly larger scale. With ten times the ticket volume, the first bottleneck would likely be repeated data loading and retrieval rather than the ticket classification rules themselves.

The knowledge base is currently small enough for local processing, but repeatedly scanning Markdown documents for every request becomes inefficient as the knowledge base grows. Similarly, loading large ticket datasets repeatedly from JSON files would increase latency and memory usage.

At 10× scale, I would introduce persistent storage for tickets and accounts, database indexes on account IDs and ticket timestamps, and an in-memory or persistent retrieval index for the knowledge base. Ticket processing could also be made asynchronous using a queue for high-volume workloads.

For the RAG layer, I would use a hybrid retrieval system combining lexical search with embeddings. Frequently requested account summaries and retrieval results could be cached.

The API layer could then be horizontally scaled behind a load balancer, while the database and retrieval index would be shared across application instances. Monitoring would track latency, error rate, retrieval quality, classification accuracy, and resource utilization.

## Conclusion

The current architecture prioritizes simplicity, deterministic behaviour, local data handling, and clear separation between ticket processing, account services, and knowledge-base retrieval. For production deployment, the most important improvements would be stronger validation, better retrieval quality, observability, persistent indexed storage, privacy controls, and scalable infrastructure.