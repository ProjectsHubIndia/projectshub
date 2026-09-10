const roadmapData = {
  // NODE 1
  what_is_ai_eng: {
    title: "What is an AI Engineer?",
    desc: '<p>An AI Engineer is a software engineer who specializes in applying pre-trained models (like GPT, Claude, or Gemini) to solve product problems. They focus on prompt design, retrieval pipelines, agents, evaluation, cost, and latency — not on training models from scratch. Think "product builder who speaks fluent LLM."</p>',
    image: "/static/image/projectshub-ai-developer-workspace.webp",
    free: [
      {
        type: "article",
        label: "Article",
        title: "The Rise of the AI Engineer — Latent Space (Swyx)",
        url: "https://www.latent.space/p/ai-engineer"
      },
      {
        type: "video",
        label: "YouTube",
        title: "What is an AI Engineer? Career Roadmap & Core Skills",
        url: "https://www.youtube.com/watch?v=2S3Ykgw_a4A"
      },
      {
        type: "docs",
        label: "Docs",
        title: "OpenAI Developer Platform & Application Quickstart",
        url: "https://platform.openai.com/docs/quickstart"
      },
      {
        type: "article",
        label: "Guide",
        title: "Anthropic Build with Claude: Production Patterns",
        url: "https://docs.anthropic.com/en/docs/build-with-claude/overview"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Transitioning from Software Dev to AI Engineer",
        url: "https://chatgpt.com/?q=Act+as+a+Senior+AI+Engineering+Mentor.+Explain+how+a+traditional+software+developer+transitions+into+an+AI+Engineer.+Cover+core+skills%2C+mental+models%2C+and+first+3+projects+to+build."
      },
      {
        type: "course",
        label: "Practice",
        title: "Hands-on Architecture: Prompt vs Finetuning vs RAG Decision Tree",
        url: "https://github.com/anthropics/anthropic-cookbook"
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "AI Engineer Starter Pack: 5 Production Projects with Full Source Code",
        url: "/projects/?category=ml"
      },
      {
        type: "course",
        label: "Bootcamp",
        title: "Full-Stack AI Application Bootcamp with 1-on-1 Mentorship",
        url: "/workshops/"
      }
    ]
  },
  roles_resps: {
    title: "Roles and Responsibilities",
    desc: "<p>A typical AI Engineer designs prompts and context, builds RAG and agent pipelines, picks and benchmarks models, manages API cost and rate limits, adds guardrails and moderation, and writes evaluations to catch regressions. They also handle the unglamorous parts: caching, retries, logging, and monitoring quality in production.</p>",
    image: "/static/image/ai-machine-learning-project-code.webp",
    free: [
      {
        type: "article",
        label: "Article",
        title: "What an AI Engineer Actually Does Daily in Production",
        url: "https://github.com/brexhq/prompt-engineering"
      },
      {
        type: "video",
        label: "YouTube",
        title: "AI Engineering Responsibilities & Systems Architecture",
        url: "https://www.youtube.com/results?search_query=ai+engineer+responsibilities+production"
      },
      {
        type: "docs",
        label: "Docs",
        title: "LLM System Observability & Tracing Best Practices",
        url: "https://docs.smith.langchain.com/"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Real-world AI Engineer Case Study & Failure Debugging",
        url: "https://chatgpt.com/?q=Act+as+an+AI+Engineering+Lead.+Walk+me+through+a+real-world+case+study+where+an+AI+feature+fails+in+production+due+to+latency+and+hallucination%2C+and+help+me+debug+and+solve+it."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Production RAG Pipeline with Evaluation & Observability",
        url: "/projects/?category=ml"
      }
    ]
  },
  impact_product: {
    title: "Impact on Product Development",
    desc: '<p>AI shifts product work from "code every rule by hand" to "describe the goal and let the model handle the messy middle." Features that were impossible or expensive — summarization, natural-language search, drafting, classification — now take days instead of months. The trade-off is new concerns: non-determinism, hallucination, cost per request, and the need for evaluation.</p>',
    image: "/static/image/ai-development-hero.webp",
    free: [
      {
        type: "article",
        label: "Article",
        title: "Designing AI Products: UX Patterns & State Management",
        url: "https://www.nngroup.com/articles/ai-ux-patterns/"
      },
      {
        type: "docs",
        label: "Docs",
        title: "Production LLM Product Design Principles (OpenAI)",
        url: "https://platform.openai.com/docs/guides/production-best-practices"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Designing AI Product UX with Graceful Degradation",
        url: "https://chatgpt.com/?q=Teach+me+how+to+design+an+AI-powered+product+feature+with+graceful+fallbacks%2C+streaming+UX%2C+and+cost+controls."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Production AI SaaS with Token Metering & Auth",
        url: "/projects/?category=ml"
      }
    ]
  },
  ai_vs_ml: {
    title: "AI Engineer vs ML Engineer",
    desc: "<p>An ML Engineer trains, tunes, and deploys custom models, working with datasets, GPUs, and model architectures. An AI Engineer consumes already-trained models through APIs and SDKs and concentrates on the application layer around them. The fastest way to ship AI features today is the AI Engineer path; the ML Engineer path is heavier on data and modeling.</p>",
    image: "/static/image/business-ai-team.webp",
    free: [
      {
        type: "article",
        label: "Article",
        title: "AI Engineer vs ML Engineer: Comparing Roles & Compensation",
        url: "https://www.latent.space/p/ai-engineer"
      },
      {
        type: "video",
        label: "YouTube",
        title: "Machine Learning vs AI Engineering: Which Should You Learn?",
        url: "https://www.youtube.com/results?search_query=ai+engineer+vs+ml+engineer"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Diagnostic Quiz for AI vs ML Career Choice",
        url: "https://chatgpt.com/?q=Assess+my+programming+experience+and+guide+me+between+the+AI+Engineer+and+ML+Engineer+career+tracks."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Model Training vs API Application: 2 Guided Capstone Projects",
        url: "/projects/?category=ml"
      }
    ]
  },

  // NODE 2
  how_llm_work: {
    title: "How LLMs Work",
    desc: '<p>At inference time the model reads your prompt as a sequence of tokens and repeatedly predicts the most likely next token, appending each one and feeding it back in. There is no database lookup — the "knowledge" lives in the weights learned during training. This is why output is fluent but can be confidently wrong (hallucination).</p>',
    image: "/static/image/ai-machine-learning-project-code.webp",
    free: [
      {
        type: "video",
        label: "YouTube",
        title: "Intro to Large Language Models — Andrej Karpathy (1hr Deep Dive)",
        url: "https://www.youtube.com/watch?v=zjkBMFhNj_g"
      },
      {
        type: "article",
        label: "Visual Guide",
        title: "Illustrated Transformer & LLM Inference Architecture (Jay Alammar)",
        url: "https://jalammar.github.io/illustrated-transformer/"
      },
      {
        type: "docs",
        label: "Docs",
        title: "Transformers & Attention Mechanisms Explained (Hugging Face)",
        url: "https://huggingface.co/docs/transformers/index"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Autoregressive Next-Token Prediction Simulation",
        url: "https://chatgpt.com/?q=Explain+autoregressive+decoding+in+LLMs+step-by-step+with+an+ASCII+diagram+and+a+concrete+example."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Build a Custom LLM Inference & Streaming Server with FastAPI",
        url: "/projects/?category=ml"
      }
    ]
  },
  tokens: {
    title: "Tokens",
    desc: "<p>Models don't see words or characters — they see tokens, which are chunks of text (roughly ¾ of a word in English). Prompt length, context limits, and pricing are all measured in tokens, not words. Understanding tokenization helps you estimate cost and stay within model limits.</p>",
    image: "/static/image/tools-new.webp",
    free: [
      {
        type: "docs",
        label: "Tool",
        title: "OpenAI Interactive Tokenizer Web App (tiktoken)",
        url: "https://platform.openai.com/tokenizer"
      },
      {
        type: "article",
        label: "Article",
        title: "Byte-Pair Encoding (BPE) Tokenization in Modern LLMs",
        url: "https://huggingface.co/learn/nlp-course/chapter6/5"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Calculate Tokens, Context Budget, and API Costs",
        url: "https://chatgpt.com/?q=Teach+me+how+tokenization+works+in+BPE%2C+why+tokenization+affects+math+and+spelling%2C+and+how+to+calculate+token+budgets."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Smart Token Counter & Context Window Optimizer Tool",
        url: "/projects/?category=ml"
      }
    ]
  },
  context: {
    title: "Context Window",
    desc: "<p>The context window is the maximum number of tokens a model can consider at once, covering both your input and its output. Exceed it and earlier content is dropped or the request fails. Larger windows let you pass more documents and history, but they cost more and can dilute the model's attention.</p>",
    image: "/static/image/analytics_dashboard.webp",
    free: [
      {
        type: "article",
        label: "Article",
        title: "Lost in the Middle: How Language Models Use Long Contexts (Stanford)",
        url: "https://arxiv.org/abs/2307.03172"
      },
      {
        type: "docs",
        label: "Docs",
        title: "Anthropic & Google 1M+ Token Context Windows Guide",
        url: "https://docs.anthropic.com/en/docs/build-with-claude/context-window"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Long Context Window vs RAG Decision Framework",
        url: "https://chatgpt.com/?q=When+should+I+dump+an+entire+codebase+into+a+1M+token+context+window+vs+using+RAG%3F+Compare+cost%2C+speed%2C+and+accuracy."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Long-Document Analysis System with Sliding Context Windows",
        url: "/projects/?category=ml"
      }
    ]
  },
  sampling_params: {
    title: "Sampling Parameters",
    desc: "<p>Sampling parameters control how the model chooses each next token, trading off determinism against creativity. The main knobs are temperature, top-p, top-k, and penalties. Tuning them shapes whether output is focused and repeatable or varied and inventive.</p>",
    image: "/static/image/ai-automation-hero.webp",
    free: [
      {
        type: "docs",
        label: "Docs",
        title: "OpenAI API Reference: Temperature, Top-P, and Penalties",
        url: "https://platform.openai.com/docs/api-reference/chat/create"
      },
      {
        type: "article",
        label: "Deep Dive",
        title: "Demystifying Sampling: Temperature, Top-K, and Nucleus Sampling",
        url: "https://towardsdatascience.com/demystifying-sampling-parameters-in-llms-2e8484f9328a"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Tuning Temperature & Top-P for Classification vs Creative Tasks",
        url: "https://chatgpt.com/?q=Give+me+exact+recommended+sampling+parameter+settings+(temperature%2C+top_p%2C+frequency_penalty)+for+10+common+AI+tasks."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Dynamic Sampling & Prompt Experimentation Workbench",
        url: "/projects/?category=ml"
      }
    ]
  },
  temperature: {
    title: "Temperature",
    desc: "<p>Temperature scales randomness: low values (near 0) make output focused and deterministic, high values make it diverse and creative. Use low temperature for extraction, classification, and code; higher for brainstorming and creative writing. It's the single most useful sampling knob.</p>",
  },
  top_k: {
    title: "Top-k",
    desc: "<p>Top-k restricts sampling to the k most likely next tokens, cutting off the long tail of unlikely options. Smaller k means safer, more predictable text. It's a simpler alternative or complement to top-p.</p>",
  },
  top_p: {
    title: "Top-p (Nucleus Sampling)",
    desc: '<p>Top-p limits choices to the smallest set of tokens whose combined probability exceeds p (e.g. 0.9), sampling only from that "nucleus." It adapts the candidate pool to the model\'s confidence. Often used instead of, not alongside, aggressive temperature changes.</p>',
  },
  repetition_penalties: {
    title: "Repetition Penalties",
    desc: "<p>Repetition (or frequency/presence) penalties reduce the probability of tokens that have already appeared, discouraging loops and repeated phrases. They help keep longer generations fresh. Overusing them can make text feel forced or incoherent.</p>",
  },
  ai_vs_agi: {
    title: "AI vs AGI",
    desc: "<p>Today's AI is \"narrow\" — extremely capable within trained domains but with no general understanding or goals of its own. AGI (Artificial General Intelligence) refers to a hypothetical system that can learn and reason across any domain at human level. Everything you build as an AI Engineer uses narrow AI; AGI does not exist yet and you don't need it to ship value.</p>",
  },
  llm: {
    title: "Large Language Model (LLM)",
    desc: "<p>An LLM is a neural network trained on enormous amounts of text to predict the next token given everything before it. By learning these statistical patterns at scale, it can write, summarize, translate, reason, and answer questions. As an AI Engineer you treat it as a powerful, probabilistic text engine you steer with prompts.</p>",
  },
  embeddings_term: {
    title: "Embeddings",
    desc: "<p>An embedding is a list of numbers (a vector) that represents the meaning of text, so similar meanings sit close together in vector space. They turn language into math you can compare, search, and cluster. Embeddings are the foundation of semantic search and RAG.</p>",
  },
  training_term: {
    title: "Training",
    desc: "<p>Training is the expensive, one-time process of adjusting billions of weights by showing the model massive text corpora and correcting its next-token predictions. It usually includes pre-training (raw text) followed by fine-tuning and alignment (instruction tuning, RLHF) to make the model helpful and safe. You rarely train models yourself — you consume the result.</p>",
  },
  inference_term: {
    title: "Inference",
    desc: "<p>Inference is running a trained model to generate output for your input — the part you actually pay for and optimize. Key inference concerns are latency, throughput, cost per token, and the sampling settings that control randomness. Most of an AI Engineer's day-to-day tuning happens at inference time.</p>",
  },
  vector_db_term: {
    title: "Vector Databases",
    desc: "<p>A vector database stores embeddings and retrieves the most similar ones quickly, even across millions of vectors. It handles indexing, metadata filtering, and scaling so you don't have to. It's the storage backbone of semantic search and RAG.</p>",
    image: "/static/image/analytics_dashboard.webp",
    free: [
      {
        type: "article",
        label: "Article",
        title: "Vector Databases Explained: From Pinecone to Qdrant & pgvector",
        url: "https://www.pinecone.io/learn/vector-database/"
      },
      {
        type: "video",
        label: "YouTube",
        title: "Vector Databases in 100 Seconds + Architecture Deep Dive",
        url: "https://www.youtube.com/results?search_query=vector+databases+explained"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: HNSW vs IVF vs Flat Indexing Comparison",
        url: "https://chatgpt.com/?q=Explain+HNSW+vs+IVF+indexing+algorithms+in+vector+databases+with+trade-offs+in+recall%2C+latency%2C+and+memory."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Semantic Code Search Engine with Qdrant and FastAPI",
        url: "/projects/?category=ml"
      }
    ]
  },
  ai_agents_term: {
    title: "AI Agents",
    desc: "<p>An AI agent uses an LLM to plan and take actions toward a goal, calling tools, observing results, and looping until done. Unlike a single prompt, an agent can break a task into steps and act on the world. They power assistants that do things, not just answer.</p>",
    image: "/static/image/ai-automation-hero.webp",
    free: [
      {
        type: "article",
        label: "Article",
        title: "Building Effective Agents — Anthropic Research & Engineering",
        url: "https://www.anthropic.com/research/building-effective-agents"
      },
      {
        type: "docs",
        label: "Docs",
        title: "LangGraph Multi-Agent Architecture Guide",
        url: "https://langchain-ai.github.io/langgraph/"
      },
      {
        type: "video",
        label: "YouTube",
        title: "AI Agents Masterclass: Tool Calling, Memory & ReAct Pattern",
        url: "https://www.youtube.com/results?search_query=ai+agents+langgraph+tutorial"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Step-by-Step ReAct Agent Implementation Drill",
        url: "https://chatgpt.com/?q=Teach+me+how+to+build+a+ReAct+(Reasoning+%2B+Acting)+agent+from+scratch+in+pure+Python+without+any+frameworks."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Autonomous Multi-Agent Market Research Team with LangGraph",
        url: "/projects/?category=ml"
      }
    ]
  },
  rag_term: {
    title: "RAG",
    desc: "<p>Retrieval-Augmented Generation (RAG) retrieves relevant documents and feeds them into the prompt so the model answers from your data, not just its training. It's the standard way to give an LLM up-to-date, private, or domain-specific knowledge. RAG reduces hallucination and lets you cite sources.</p>",
    image: "/static/image/projectshub-ai-developer-workspace.webp",
    free: [
      {
        type: "article",
        label: "Article",
        title: "Advanced RAG Techniques: Hybrid Search, Reranking & Chunking",
        url: "https://towardsdatascience.com/advanced-rag-01-preprocessing-chunking-5670c743b857"
      },
      {
        type: "docs",
        label: "Docs",
        title: "LlamaIndex Production RAG Architecture Guide",
        url: "https://docs.llamaindex.ai/en/stable/"
      },
      {
        type: "video",
        label: "YouTube",
        title: "RAG from Scratch: Indexing, Retrieval & Generation (LangChain)",
        url: "https://www.youtube.com/watch?v=sVcwVQRHIc8"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Diagnosing and Fixing Retrieval Failures in RAG",
        url: "https://chatgpt.com/?q=My+RAG+pipeline+is+hallucinating+or+retrieving+irrelevant+chunks.+Walk+me+through+a+systematic+debugging+checklist."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Enterprise Multi-Document RAG with Cohere Reranking & Hybrid Search",
        url: "/projects/?category=ml"
      }
    ]
  },
  fine_tuning_term: {
    title: "Fine-tuning",
    desc: "<p>Fine-tuning further trains a base model on your own examples so it adopts a style, format, or narrow skill. It's worth it when prompting alone can't get consistent behavior and you have quality labeled data. It does not reliably add fresh knowledge — for that, use retrieval (RAG).</p>",
  },

  // NODE 3
  zero_shot: {
    title: "Zero-shot Prompting",
    desc: "<p>Zero-shot means asking the model to do a task with only an instruction and no examples. It works well for tasks the model already understands. It's the simplest approach — try it first before adding examples.</p>",
  },
  few_shot_adv: {
    title: "Few-shot Prompting",
    desc: "<p>Few-shot prompting includes a handful of input–output examples in the prompt to demonstrate the exact format and style you want. It sharply improves consistency on structured or unusual tasks. Choose examples that closely resemble real inputs.</p>",
  },
  chain_of_thought: {
    title: "Chain-of-Thought (CoT)",
    desc: '<p>Chain-of-thought prompting asks the model to reason step by step before answering, which improves accuracy on math, logic, and multi-step problems. You can prompt it explicitly ("think step by step") or use models that reason internally. The trade-off is more tokens and latency.</p>',
  },
  react_prompt: {
    title: "ReAct Prompting",
    desc: "<p>ReAct (Reason + Act) interleaves reasoning steps with tool actions: the model thinks, calls a tool, observes the result, and continues. It's a foundational pattern for agents that need to look things up or take actions. The visible reasoning trace also aids debugging.</p>",
  },
  cot_adv: {
    title: "Chain-of-Thought (CoT)",
    desc: '<p>Chain-of-thought prompting asks the model to reason step by step before answering, which improves accuracy on math, logic, and multi-step problems. You can prompt it explicitly ("think step by step") or use models that reason internally. The trade-off is more tokens and latency.</p>',
  },
  input_format: {
    title: "Input Format",
    desc: "<p>How you structure the input — message roles, delimiters, ordering of instructions and data — measurably affects output quality. Clear separation of system instructions, context, and the user request reduces ambiguity. Consistent formatting also makes prompts easier to cache and maintain.</p>",
  },
  func_calling_adv: {
    title: "Function Calling / Tools",
    desc: "<p>Function (tool) calling lets the model decide to invoke functions you define, returning the function name and arguments as structured data. You run the function and feed the result back, enabling the model to fetch data or take actions. This is the building block of agents and assistants.</p>",
  },
  prompt_caching: {
    title: "Prompt Caching",
    desc: "<p>Prompt caching stores the processed form of a repeated prompt prefix (like a long system prompt or document) so subsequent requests are faster and cheaper. It's ideal when many requests share the same large context. Big savings for RAG and agent loops that reuse instructions.</p>",
  },
  streaming: {
    title: "Streaming Responses",
    desc: "<p>Streaming sends tokens as they're generated instead of waiting for the full reply, so users see text appear immediately. It dramatically improves perceived speed for chat UIs and lets you process output incrementally. Almost all providers support server-sent-event streaming.</p>",
  },
  system_prompting: {
    title: "System Prompting",
    desc: "<p>The system prompt sets persistent rules, persona, and constraints that apply across the whole conversation. It's where you define tone, format, boundaries, and the assistant's job. A strong system prompt is the backbone of consistent behavior.</p>",
  },
  role_behavior: {
    title: "Role & Behavior",
    desc: '<p>Assigning the model a role ("You are an expert SQL reviewer") and describing desired behavior focuses its responses and raises quality. Defining what it should and shouldn\'t do reduces drift. Pair the role with concrete output expectations.</p>',
  },
  context_constraints: {
    title: "Constraining Outputs and Inputs",
    desc: "<p>Constraining means bounding what goes in and what comes out — enforcing schemas, allowed values, length limits, and rejecting out-of-scope requests. It improves reliability and safety. Combine schema-constrained output with input validation and guardrails.</p>",
  },
  struct_output_adv: {
    title: "Structured Output",
    desc: "<p>Structured output forces the model to return data in a fixed schema (usually JSON), so your code can parse it reliably. Modern APIs support JSON mode or schema-constrained decoding to guarantee valid output. Essential whenever an LLM feeds into downstream code rather than a human.</p>",
  },
  ext_memory: {
    title: "External Memory",
    desc: '<p>External memory stores facts, preferences, and past interactions outside the context window (in a database or vector store) and retrieves them when needed. It gives an otherwise stateless model long-term recall. This is how assistants "remember" users across sessions.</p>',
  },
  rag_filters: {
    title: "RAG and Dynamic Filters",
    desc: "<p>Dynamic filters combine semantic search with metadata constraints (user, date, permission, category) computed at query time. They ensure retrieval respects access control and relevance. Essential for multi-tenant and permissioned data.</p>",
  },
  context_compaction: {
    title: "Context Compaction",
    desc: "<p>Compaction shrinks long conversations or documents into compact summaries so they fit the window and stay relevant. You replace stale, verbose history with condensed notes while keeping key facts. It controls cost and prevents the model from drowning in irrelevant text.</p>",
  },
  context_isolation: {
    title: "Context Isolation",
    desc: "<p>Isolation keeps unrelated tasks, users, or tools in separate context scopes so information doesn't leak or interfere. In multi-agent or multi-tenant systems this prevents one task's data from polluting another's reasoning. It's both a quality and a security concern.</p>",
  },

  // NODE 4
  pre_trained: {
    title: "Pre-trained Models",
    desc: "<p>Pre-trained models have already learned language from huge datasets, so you can use them immediately through an API. This is the foundation of AI engineering: you get state-of-the-art capability without owning data, GPUs, or training pipelines. Your job is to apply, combine, and guide these models well.</p>",
  },
  closed_vs_open: {
    title: "Closed vs Open Source Models",
    desc: "<p>Closed models (GPT, Claude, Gemini) are accessed via API — best quality and zero ops, but you depend on the vendor and send them your data. Open-source models (Llama, Mistral, Qwen, Gemma) can be self-hosted for control, privacy, and predictable cost, at the price of running infrastructure. Many teams use closed models to prototype and open models where data sensitivity or scale justify hosting.</p>",
  },
  self_hosted: {
    title: "Self-hosted Models",
    desc: "<p>Self-hosting means running models on your own servers or cloud GPUs instead of calling a provider. It's the right call when data can't leave your environment or when scale makes per-token API pricing too expensive. Plan for GPU cost, autoscaling, and model-serving infrastructure.</p>",
  },
  closed_models: {
    title: "Closed Models",
    desc: "<p>Closed models (GPT, Claude, Gemini) are accessed via API — best quality and zero ops, but you depend on the vendor and send them your data. Open-source models (Llama, Mistral, Qwen, Gemma) can be self-hosted for control, privacy, and predictable cost, at the price of running infrastructure. Many teams use closed models to prototype and open models where data sensitivity or scale justify hosting.</p>",
  },
  open_models: {
    title: "Open Source Models",
    desc: "<p>Closed models (GPT, Claude, Gemini) are accessed via API — best quality and zero ops, but you depend on the vendor and send them your data. Open-source models (Llama, Mistral, Qwen, Gemma) can be self-hosted for control, privacy, and predictable cost, at the price of running infrastructure. Many teams use closed models to prototype and open models where data sensitivity or scale justify hosting.</p>",
  },
  hf_tasks: {
    title: "Hugging Face Tasks",
    desc: "<p>Tasks are categories like text generation, classification, summarization, translation, image, and audio that organize models by what they do. Browsing by task is the quickest way to find the right model for a problem. Each task page explains the inputs, outputs, and common models.</p>",
  },
  hf_hub: {
    title: "Hugging Face Hub",
    desc: "<p>The Hub is the platform that hosts hundreds of thousands of models and datasets with versioning, model cards, and access controls. You browse, download, and share artifacts here. Model cards document a model's training, license, and intended use.</p>",
  },
  transformers_js: {
    title: "Transformers.js",
    desc: "<p>Transformers.js runs Hugging Face models directly in the browser or Node using WebGPU/WASM, with no server round-trip. It enables private, offline, client-side AI features. Best for small models and privacy-sensitive in-browser tasks.</p>",
  },
  ollama: {
    title: "Ollama",
    desc: "<p>Ollama lets you download and run open models locally with a single command and an OpenAI-compatible API. It's the easiest way to experiment with local LLMs on a laptop or server. Great for prototyping, offline work, and privacy-sensitive development.</p>",
  },
  lm_studio: {
    title: "LM Studio",
    desc: "<p>LM Studio is a desktop app for discovering, downloading, and running open models with a friendly GUI and a local server endpoint. It's beginner-friendly for trying models without the command line. Useful for local testing and comparing models offline.</p>",
  },
  openrouter: {
    title: "OpenRouter",
    desc: "<p>OpenRouter is a single API that routes to hundreds of models across many providers, with unified billing and automatic fallback. It's great for comparing models, avoiding vendor lock-in, and adding redundancy. One key, many models.</p>",
  },
  openai_api: {
    title: "OpenAI Responses API",
    desc: "<p>OpenAI's Responses API is the modern interface for generating output, calling tools, and handling reasoning and multimodal input in one unified call. It replaces older completion-style endpoints with a more agent-friendly design. Learn its message and tool format since most examples now use it.</p>",
  },
  claude_api: {
    title: "Claude Messages API",
    desc: "<p>Anthropic's Messages API takes a list of role-tagged messages (system, user, assistant) and returns the model's reply, with support for tools, vision, and streaming. It's the primary way to call Claude programmatically. The structured message format maps cleanly to chat applications.</p>",
  },
  gemini_api: {
    title: "Google Gemini API",
    desc: "<p>The Gemini API exposes Google's models for text, multimodal, and tool-using requests, available both directly and through Vertex AI. It supports very large context and native image/audio/video input. Use it when you're in the Google ecosystem or need long context.</p>",
  },
  hf_sdk: {
    title: "Hugging Face Inference SDK",
    desc: "<p>The Inference SDK/API lets you call hosted models over HTTP without managing servers, or run them locally with the same interface. It's a fast way to test open models in code. Good bridge between prototyping and self-hosting.</p>",
  },

  // NODE 5
  semantic_search: {
    title: "Semantic Search",
    desc: "<p>Semantic search finds results by meaning rather than exact keywords, by embedding the query and documents and comparing vectors. It surfaces relevant content even when wording differs. It's the core retrieval technique behind modern search and RAG.</p>",
  },
  data_classification: {
    title: "Data Classification",
    desc: "<p>Embeddings let you classify text by comparing it to labeled examples or category vectors — no training required for simple cases. Useful for tagging, routing, and triage. A lightweight alternative to fine-tuning a classifier.</p>",
  },
  recommendation: {
    title: "Recommendation Systems",
    desc: '<p>By embedding items and users, you can recommend things that are "close" in vector space to what someone liked. Embeddings capture similarity that keyword matching misses. A practical, low-effort recommendation approach.</p>',
  },
  anomaly: {
    title: "Anomaly Detection",
    desc: "<p>Embeddings make outliers visible: items far from the normal cluster in vector space are likely anomalies. Useful for fraud, spam, and quality monitoring. You set a distance threshold to flag the unusual.</p>",
  },
  prop_embeddings: {
    title: "OpenAI Embeddings API",
    desc: "<p>OpenAI's embeddings endpoint turns text into high-quality vectors with a simple API call. It's a common default for semantic search and RAG when you're already using OpenAI. Watch dimension size and cost for large corpora.</p>",
  },
  open_embeddings: {
    title: "Sentence Transformers",
    desc: "<p>Sentence Transformers is an open-source library of embedding models you can run locally for free. It's popular when you want to avoid API costs or keep data in-house. A go-to for self-hosted retrieval pipelines.</p>",
  },

  // NODE 6
  chroma: {
    title: "Chroma",
    desc: "<p>Chroma is a lightweight, developer-friendly open-source vector database that's easy to run locally or embed in an app. It's ideal for prototyping and small-to-medium projects. Minimal setup, Python-first.</p>",
  },
  pinecone: {
    title: "Pinecone",
    desc: "<p>Pinecone is a fully managed, scalable vector database that removes ops entirely. It's a popular choice for production RAG when you'd rather not run infrastructure. Pay-as-you-go with strong performance at scale.</p>",
  },
  weaviate: {
    title: "Weaviate",
    desc: "<p>Weaviate is an open-source vector database with built-in hybrid (keyword + vector) search and optional managed hosting. It's feature-rich for production search. Good when you need both semantic and keyword relevance.</p>",
  },
  faiss: {
    title: "FAISS",
    desc: "<p>FAISS is Meta's open-source library for fast similarity search over vectors, running in-process rather than as a server. It's extremely fast and free but lower-level — you manage storage and metadata yourself. Great for embedded or research use.</p>",
  },
  qdrant: {
    title: "Qdrant",
    desc: "<p>Qdrant is an open-source vector database with strong filtering, payload support, and both self-hosted and cloud options. It's performance-focused and production-ready. Popular for filtered semantic search.</p>",
  },
  supabase_pgvector: {
    title: "Supabase (pgvector)",
    desc: "<p>Supabase adds vector search to Postgres via the pgvector extension, so you keep vectors next to your relational data. It's convenient when you already use Postgres and want one database. Good for teams avoiding a separate vector store.</p>",
  },
  indexing: {
    title: "Indexing Embeddings",
    desc: "<p>Indexing organizes vectors so similarity search stays fast as the dataset grows, using structures like HNSW or IVF. Without an index, search scans every vector and slows down. Vector databases handle indexing for you.</p>",
  },
  perf_sim_search: {
    title: "Performing Similarity Search",
    desc: "<p>Similarity search compares a query vector to stored vectors using a distance metric (cosine, dot product, Euclidean) and returns the nearest matches. It's the retrieval step in RAG and semantic search. Choosing the right metric should match how the embeddings were trained.</p>",
  },

  // NODE 7
  rag_usecases: {
    title: "RAG Use Cases",
    desc: "<p>RAG powers document Q&A, customer-support bots, internal knowledge search, and any feature that must answer from a specific corpus. Anywhere the answer lives in your documents rather than the model's memory, RAG fits. It's the most common real-world LLM pattern.</p>",
  },
  rag_vs_fine: {
    title: "RAG vs Fine-tuning",
    desc: "<p>RAG injects external knowledge at query time by retrieving relevant documents into the prompt — ideal for facts that change or are too large to memorize. Fine-tuning bakes behavior and format into the weights — ideal for consistent tone or task structure. They're complementary: RAG for knowledge, fine-tuning for behavior, and often both together.</p>",
  },
  chunking: {
    title: "Chunking",
    desc: "<p>Chunking splits documents into smaller passages so each can be embedded and retrieved independently. Chunk size and overlap strongly affect retrieval quality — too big buries the answer, too small loses context. Tuning chunking is one of the highest-impact RAG decisions.</p>",
  },
  embedding_rag: {
    title: "Embedding (in RAG)",
    desc: "<p>In RAG, you embed each chunk once at ingestion and embed the query at request time, then compare them. Consistent use of one embedding model is essential. The quality of embeddings sets the ceiling on retrieval quality.</p>",
  },
  vector_db_rag: {
    title: "Vector Databases",
    desc: "<p>A vector database stores embeddings and retrieves the most similar ones quickly, even across millions of vectors. It handles indexing, metadata filtering, and scaling so you don't have to. It's the storage backbone of semantic search and RAG.</p>",
  },
  retrieval_process: {
    title: "Retrieval Process",
    desc: "<p>Retrieval embeds the query, searches the vector store for the most similar chunks, optionally re-ranks and filters them, and assembles the top results into context. Good retrieval is the difference between accurate and hallucinated answers. This is where most RAG tuning effort goes.</p>",
  },
  generation: {
    title: "Generation",
    desc: "<p>Generation is the final step: the model reads the retrieved context plus the question and produces a grounded answer, ideally with citations. Prompt the model to use only the provided context and to say when it doesn't know. This keeps answers faithful to your data.</p>",
  },
  sdks_direct: {
    title: "Using SDKs Directly",
    desc: "<p>Official SDKs (Python, JS/TS, etc.) wrap the raw HTTP API with typed helpers, retries, and streaming support. They're the fastest way to integrate, though plain HTTP requests work anywhere and avoid heavy dependencies. Pick SDKs for convenience, raw requests for constrained or minimal environments.</p>",
  },
  langchain: {
    title: "LangChain",
    desc: "<p>LangChain is a framework that provides building blocks for chains, retrieval, memory, agents, and tool use across many model providers. It speeds up prototyping of RAG and agent apps. Powerful but can add abstraction overhead — use the parts you need.</p>",
  },
  llama_index: {
    title: "LlamaIndex",
    desc: "<p>LlamaIndex specializes in connecting LLMs to your data: loading, indexing, retrieving, and querying documents. It's focused and convenient for RAG pipelines. A strong choice when retrieval is the core of your app.</p>",
  },
  haystack: {
    title: "Haystack",
    desc: "<p>Haystack is an open-source framework for building production search and RAG pipelines with modular, composable components. It's geared toward robust, deployable systems. Good when you need a structured, production-minded pipeline.</p>",
  },

  // NODE 8
  agents_usecases: {
    title: "Agents Use Cases",
    desc: "<p>Agents handle research, data gathering, code writing and execution, customer workflows, and multi-step automation. They shine when a task needs several tool calls and decisions. Start narrow — scoped agents are far more reliable than open-ended ones.</p>",
  },
  react_agents: {
    title: "ReAct (Agent Reasoning)",
    desc: "<p>ReAct is the reason-act-observe loop that lets an agent think, take an action, see the outcome, and adjust. It's the canonical pattern behind tool-using agents. The interleaved trace makes agent behavior easier to follow and debug.</p>",
  },
  tools_func: {
    title: "Tools / Function Calling (Agents)",
    desc: "<p>Tools are functions the agent can call — search, calculators, database queries, APIs. You describe each tool's signature and the model decides when to use it. The breadth and reliability of your tools determine what the agent can accomplish.</p>",
  },
  multi_agents: {
    title: "Multi-Agents",
    desc: "<p>Multi-agent systems split work across specialized agents (e.g. planner, researcher, writer) that coordinate or hand off tasks. They can tackle complex jobs but add cost, latency, and orchestration complexity. Use them only when a single agent genuinely can't cope.</p>",
  },
  custom_agents: {
    title: "Manual Implementation",
    desc: "<p>You can build an agent yourself with a loop: send the prompt, let the model request a tool, run the tool, feed results back, repeat until it produces a final answer. Doing it manually teaches you exactly how agents work and keeps you in control. Many production agents are just a well-managed loop, not a heavy framework.</p>",
  },
  crewai: {
    title: "CrewAI",
    desc: "<p>CrewAI is a framework for building multi-agent systems where agents take on specific roles (researcher, writer) and collaborate. It's popular for orchestrating complex, multi-step tasks that need diverse skills.</p>",
  },
  langgraph: {
    title: "LangGraph",
    desc: "<p>LangGraph extends LangChain to build resilient, stateful multi-agent systems as graphs. It's powerful for creating complex loops with checkpoints and human-in-the-loop workflows.</p>",
  },
  autogen: {
    title: "AutoGen",
    desc: "<p>AutoGen is Microsoft's framework for multi-agent conversations, where agents can be backed by LLMs, tools, or humans. It's very flexible for simulating teams of agents working together.</p>",
  },
  openai_swarm: {
    title: "OpenAI Swarm",
    desc: "<p>Swarm is OpenAI's lightweight, experimental framework showcasing how to build multi-agent systems with simple handoffs between agents. It's great for learning agent coordination patterns.</p>",
  },
  openai_agentkit: {
    title: "OpenAI AgentKit / Agents SDK",
    desc: "<p>OpenAI's Agents SDK / AgentKit provides primitives for building agents: tool calling, handoffs between agents, guardrails, and tracing. It standardizes common agent plumbing. A solid starting point if you're on OpenAI.</p>",
  },
  claude_agent_sdk: {
    title: "Claude Agent SDK",
    desc: "<p>Anthropic's Agent SDK gives a framework for building Claude-powered agents with tools, memory, and multi-step workflows. It encodes patterns proven in Anthropic's own agentic products. Good for production agents on Claude.</p>",
  },
  vertex_agent: {
    title: "Vertex AI Agent Builder",
    desc: "<p>Vertex AI Agent Builder is Google Cloud's managed environment for creating, grounding, and deploying agents with enterprise controls. It bundles retrieval, tools, and governance. Aimed at enterprise teams on Google Cloud.</p>",
  },

  // NODE 9
  mcp_host: {
    title: "MCP Host",
    desc: "<p>The host is the AI application (like a chat app or IDE) that the user interacts with and that wants to use external capabilities. It runs one or more MCP clients to reach servers. The host decides which servers to connect and how their tools are offered to the model.</p>",
  },
  mcp_server: {
    title: "MCP Server",
    desc: "<p>An MCP server exposes tools, resources, and prompts — like file access, a database, or an API — to any MCP client. You write a server once and reuse it across hosts. Servers are how you give models new capabilities in a standard way.</p>",
  },
  mcp_data: {
    title: "Transport Layer",
    desc: "<p>MCP communicates over transports — typically stdio for local servers and HTTP/SSE for remote ones. The transport carries the JSON-RPC messages between client and server. You pick the transport based on whether the server runs locally or over a network.</p>",
  },
  build_mcp_server: {
    title: "Building an MCP Server",
    desc: "<p>Building a server means defining the tools and resources you want to expose, implementing their handlers, and declaring their schemas so clients can discover them. SDKs exist for several languages to handle the protocol. Start by wrapping one useful API or data source.</p>",
  },
  build_mcp_client: {
    title: "Building an MCP Client",
    desc: "<p>Building a client means connecting to a server, discovering its tools, and forwarding the model's tool calls and their results. Most developers use an existing host's client, but writing one teaches the protocol. It's mainly relevant if you're building your own AI application.</p>",
  },
  connect_mcp: {
    title: "Connect to Local Server",
    desc: "<p>Local servers run on the same machine and connect via stdio, ideal for accessing local files, scripts, or developer tools. Setup is simple and data never leaves the machine. Common for IDE and desktop assistant integrations.</p>",
  },

  // NODE 10
  prompt_injection: {
    title: "Prompt Injection Attacks",
    desc: "<p>Prompt injection is when malicious text — in user input or retrieved content — tricks the model into ignoring its instructions or leaking data. It's the top security risk in LLM apps. Defenses include separating trusted instructions from untrusted data, output validation, and least-privilege tool access.</p>",
  },
  sec_privacy: {
    title: "Security and Privacy Concerns",
    desc: "<p>LLM apps can leak sensitive data through prompts, logs, or model outputs, and may send user data to third-party providers. Minimize what you send, redact PII, control logging, and understand each vendor's data-retention policy. Treat user data as a liability to protect, not just an input.</p>",
  },
  bias_fairness: {
    title: "Bias and Fairness",
    desc: "<p>Models inherit biases from their training data and can produce unfair or stereotyped output. Test across demographics and use cases, add mitigations, and be transparent about limitations. Fairness is an ongoing evaluation task, not a one-time checkbox.</p>",
  },
  content_mod: {
    title: "Content Moderation APIs",
    desc: "<p>Moderation APIs (such as OpenAI's moderation endpoint) classify text or images for unsafe categories like hate, self-harm, or sexual content. Run user input and model output through them to catch policy violations. They're a cheap first line of defense before and after generation.</p>",
  },
  adversarial: {
    title: "Conducting Adversarial Testing",
    desc: "<p>Adversarial testing (red-teaming) deliberately attacks your own system with jailbreaks, injections, and edge cases to find failures before users do. Build a suite of hostile prompts and run it regularly. Treat it as part of your evaluation and release process.</p>",
  },
  robust_prompting: {
    title: "Robust Prompt Engineering",
    desc: "<p>Robust prompts hold up across varied and adversarial inputs without breaking format or being hijacked. Techniques include explicit constraints, input delimiters, validation of output, and testing against edge cases. Treat prompts like code: version them and test them.</p>",
  },
  constraining: {
    title: "Constraining Inputs and Outputs (Safety)",
    desc: "<p>Limiting allowed inputs and validating outputs is a core safety control: reject out-of-scope requests, strip unsafe content, and enforce schemas. It reduces both accidental and malicious failures. Combine with moderation APIs for layered defense.</p>",
  },

  // NODE 11
  tracing: {
    title: "Tracing & Logging",
    desc: "<p>Tracing captures the full lifecycle of an LLM request — prompt, context, tool calls, and output. It's essential for debugging complex RAG or agent workflows where a failure could happen at any step.</p>",
  },
  cost_monitor: {
    title: "Cost / Latency Monitoring",
    desc: "<p>Monitoring cost per token and latency per request is critical when scaling. LLM APIs can get expensive fast, and tracking these metrics helps you decide when to switch to smaller models or implement caching.</p>",
  },
  prod_monitor: {
    title: "Production Monitoring",
    desc: "<p>Production monitoring involves tracking live traffic for errors, timeouts, and guardrail violations. You need dashboards to alert you when the LLM provider goes down or when your application starts failing.</p>",
  },
  llm_as_judge: {
    title: "LLM-as-a-judge",
    desc: "<p>Using an LLM to evaluate the output of another LLM. It's a scalable way to grade responses for relevance, tone, or accuracy without human intervention, forming the backbone of automated evaluation pipelines.</p>",
  },
  eval_metrics: {
    title: "Evaluation Metrics",
    desc: "<p>Metrics like RAGAS (context precision, answer relevancy) or custom heuristics help you quantify how well your AI feature is performing. Without metrics, you can't confidently deploy prompt or model changes.</p>",
  },
  prompt_versioning: {
    title: "Prompt Versioning",
    desc: "<p>Treating prompts as code by versioning them in Git or a dedicated prompt management system. It allows you to roll back bad prompts and A/B test different instructions systematically.</p>",
  },

  // NODE 12
  multi_ai: {
    title: "Multimodal AI",
    desc: "<p>Multimodal AI works with more than text — images, audio, and video — in a single model or pipeline. It enables features like describing photos, transcribing speech, or generating images from prompts. Modern frontier models are increasingly multimodal by default.</p>",
  },
  multi_usecases: {
    title: "Multimodal AI Use Cases",
    desc: "<p>Use cases include image captioning and Q&A, document and chart understanding, voice assistants, audio transcription, and image/video generation. Multimodality unlocks products that text-only models can't build. Match the modality to the user's real input.</p>",
  },
  image_understanding: {
    title: "Image Understanding",
    desc: "<p>Image understanding lets a model interpret pictures — describing scenes, reading text (OCR), answering questions, or extracting structured data from documents and charts. It powers visual search, accessibility, and document processing. Send an image plus a question and get a grounded answer.</p>",
  },
  image_generation: {
    title: "Image Generation",
    desc: "<p>Image generation creates pictures from text prompts using diffusion or similar models. It's used for design, marketing, prototyping, and content. Quality depends heavily on prompt detail and the chosen model.</p>",
  },
  video_understanding: {
    title: "Video Understanding",
    desc: "<p>Video understanding analyzes footage to summarize, search, caption, or answer questions about its content over time. It extends image understanding with temporal reasoning. Useful for media, surveillance, and education.</p>",
  },
  audio_processing: {
    title: "Audio Processing",
    desc: "<p>Audio processing covers transcription, translation, classification, and analysis of sound and speech. It's the foundation of voice features and call analytics. Often the first step before feeding content to a text model.</p>",
  },
  speech_to_text: {
    title: "Speech-to-Text",
    desc: "<p>Speech-to-text (ASR) converts spoken audio into written text, enabling voice input, captions, and transcription. Accuracy varies with accent, noise, and domain vocabulary. It's the entry point for most voice applications.</p>",
  },
  text_to_speech: {
    title: "Text-to-Speech",
    desc: "<p>Text-to-speech (TTS) generates natural-sounding spoken audio from text, powering voice assistants, narration, and accessibility. Modern TTS supports multiple voices, languages, and emotional tone. It pairs with STT to build full voice interfaces.</p>",
  },
  vision_api: {
    title: "OpenAI Vision API",
    desc: "<p>OpenAI's vision capability lets GPT models accept images alongside text and reason about them. Use it for OCR, document Q&A, and visual understanding. You pass images as URLs or base64 in the message.</p>",
  },
  dalle_api: {
    title: "DALL·E API",
    desc: "<p>DALL·E is OpenAI's image-generation API that creates and edits images from text prompts. It's a quick way to add image generation to an app. Control output with detailed prompts and size/quality settings.</p>",
  },
  nano_banana: {
    title: "Nano Banana API (Gemini Image)",
    desc: "<p>Nano Banana is Google's Gemini-based image generation and editing model, known for strong prompt adherence and consistent edits. It's used for high-quality generation and targeted image edits. Accessed through the Gemini API.</p>",
  },
  whisper_api: {
    title: "Whisper API",
    desc: "<p>Whisper is OpenAI's speech-to-text model offering robust, multilingual transcription. It's a popular default for converting audio to text. Available as an API and as open weights you can self-host.</p>",
  },
  langchain_multi: {
    title: "LangChain for Multimodal Apps",
    desc: "<p>LangChain provides abstractions for chaining multimodal steps — combining vision, audio, and text models with retrieval and tools. It speeds up building pipelines that span modalities. Use it to orchestrate multi-step multimodal workflows.</p>",
  },
  llamaindex_multi: {
    title: "LlamaIndex for Multimodal Apps",
    desc: "<p>LlamaIndex supports indexing and querying across text and images, enabling multimodal RAG. It lets you retrieve from documents that mix modalities. Useful when your knowledge base includes images and diagrams.</p>",
  },

  // NODE 13
  dev_tools_intro: {
    title: "Development Tools",
    desc: "<p>AI coding tools embed models into your editor to autocomplete, refactor, explain, and even write whole features. They speed up development and are themselves great examples of well-built AI products. Learning them makes you both a faster engineer and a better AI builder.</p>",
    free: [
      {
        type: "article",
        label: "Guide",
        title: "AI-Assisted Coding Tools Landscape: Architecture & Workflows",
        url: "https://github.blog/news-insights/research/research-how-ai-is-impacting-software-development/"
      },
      {
        type: "video",
        label: "YouTube",
        title: "Best AI Code Editors Ranked: Cursor vs Windsurf vs Claude Code",
        url: "https://www.youtube.com/results?search_query=best+ai+code+editors+cursor+vs+windsurf"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Choosing and Mastering AI Development Tools",
        url: "https://chatgpt.com/?q=Compare+Cursor%2C+Windsurf%2C+and+Claude+Code+for+production+full-stack+development.+What+are+the+best+practices+for+AI-assisted+coding%3F"
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "AI Developer Workspace & Modern Full-Stack Boilerplate",
        url: "/projects/?category=ml"
      }
    ]
  },
  cursor: {
    title: "Cursor",
    desc: "<p>Cursor is an AI-first code editor (a VS Code fork) with deep codebase awareness, inline edits, chat, and agentic multi-file changes. It's popular for fast, context-aware coding. Strong at understanding and modifying whole projects.</p>",
    free: [
      {
        type: "docs",
        label: "Documentation",
        title: "Cursor Official Documentation & Getting Started",
        url: "https://docs.cursor.com/"
      },
      {
        type: "video",
        label: "YouTube",
        title: "Cursor AI Tutorial for Developers: Full Guide & Rules",
        url: "https://www.youtube.com/results?search_query=cursor+ai+tutorial+for+developers+full+guide"
      },
      {
        type: "article",
        label: "Rules",
        title: "Cursor Directory: Best System Prompts, .cursorrules & Workflows",
        url: "https://cursor.directory/"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Mastering Cursor Rules (.cursorrules) and Agent Mode",
        url: "https://chatgpt.com/?q=Teach+me+how+to+configure+Cursor+with+.cursorrules%2C+system+prompts%2C+and+multi-file+edits+for+a+production+full-stack+project."
      },
      {
        type: "course",
        label: "Challenge",
        title: "Hands-on Exercise: Debugging a Complex Repository Using Cursor Composer",
        url: "https://chatgpt.com/?q=Give+me+a+practice+challenge+for+using+Cursor+Composer+and+AI-assisted+refactoring+in+TypeScript+or+Python."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Full-Stack AI Project Starter Kit Built with Cursor",
        url: "/projects/?category=ml"
      },
      {
        type: "course",
        label: "Mentorship",
        title: "ProjectsHub 1-on-1 AI Coding & Pair-Programming Mastery",
        url: "/workshops/"
      }
    ]
  },
  windsurf: {
    title: "Windsurf",
    desc: "<p>Windsurf is an AI-powered IDE with an agentic flow that can plan and execute multi-step coding tasks across files. It emphasizes a smooth human-in-the-loop coding experience with its Cascade agent. A direct alternative to Cursor.</p>",
    free: [
      {
        type: "docs",
        label: "Documentation",
        title: "Windsurf IDE by Codeium Documentation",
        url: "https://codeium.com/windsurf"
      },
      {
        type: "video",
        label: "YouTube",
        title: "Windsurf AI IDE vs Cursor: Complete Developer Comparison",
        url: "https://www.youtube.com/results?search_query=windsurf+ide+vs+cursor+review"
      },
      {
        type: "article",
        label: "Guide",
        title: "Cascade Flows: Multi-file Agentic Workflows in Windsurf",
        url: "https://codeium.com/blog"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Setting Up Cascade Workflows & Rules in Windsurf",
        url: "https://chatgpt.com/?q=Explain+Windsurf+IDE+Cascade+agentic+flows+and+how+to+leverage+them+for+rapid+feature+development."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Production Microservices Built with Agentic IDEs",
        url: "/projects/?category=ml"
      }
    ]
  },
  claude_code: {
    title: "Claude Code",
    desc: "<p>Claude Code is Anthropic's agentic coding tool that works from the terminal and editors, capable of reading, writing, and running code across a project. It's strong at large, multi-step engineering tasks. Good for delegating substantial coding work to an agent.</p>",
    free: [
      {
        type: "docs",
        label: "Documentation",
        title: "Anthropic Claude Code CLI Documentation",
        url: "https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview"
      },
      {
        type: "video",
        label: "YouTube",
        title: "Claude Code CLI: Autonomous Terminal Agent in Action",
        url: "https://www.youtube.com/results?search_query=claude+code+anthropic+terminal+agent"
      },
      {
        type: "article",
        label: "Patterns",
        title: "Agentic Engineering Patterns with Claude 3.7 Sonnet",
        url: "https://github.com/anthropics/anthropic-cookbook"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Building and Testing via Claude Code Terminal Agent",
        url: "https://chatgpt.com/?q=How+do+I+use+Claude+Code+agent+in+my+terminal+to+refactor+a+codebase+and+run+tests+autonomously%3F"
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Autonomous Agentic Systems with Anthropic Claude",
        url: "/projects/?category=ml"
      }
    ]
  },
  codex: {
    title: "Codex",
    desc: "<p>Codex is OpenAI's agentic coding tool/agent that can implement features, fix bugs, and run tasks in a sandboxed environment. It automates larger chunks of development. Useful for offloading well-scoped coding jobs.</p>",
    free: [
      {
        type: "docs",
        label: "Documentation",
        title: "OpenAI Codex & API Code Generation Guide",
        url: "https://platform.openai.com/docs/guides/code"
      },
      {
        type: "video",
        label: "YouTube",
        title: "OpenAI Codex & Developer Agents Explained",
        url: "https://www.youtube.com/results?search_query=openai+codex+agent+developer+guide"
      },
      {
        type: "article",
        label: "Cookbook",
        title: "OpenAI Cookbook: Code Generation & Transpilation",
        url: "https://github.com/openai/openai-cookbook"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: Evaluating Sandboxed AI Code Execution",
        url: "https://chatgpt.com/?q=Explain+how+sandboxed+code+execution+environments+like+OpenAI+Codex+work+safely."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "AI Code Generation & Execution Sandbox Platform",
        url: "/projects/?category=ml"
      }
    ]
  },
  replit: {
    title: "Replit",
    desc: "<p>Replit is a browser-based development platform with an AI agent that can build and deploy full apps from natural-language prompts. It removes local setup entirely. Great for beginners, prototyping, and learning by building.</p>",
    free: [
      {
        type: "docs",
        label: "Documentation",
        title: "Replit Documentation & Agent Quickstart",
        url: "https://docs.replit.com/"
      },
      {
        type: "video",
        label: "YouTube",
        title: "Replit Agent: Build and Deploy Full Stack Apps in Minutes",
        url: "https://www.youtube.com/results?search_query=replit+agent+full+stack+app+tutorial"
      },
      {
        type: "article",
        label: "Deployment",
        title: "Deploying Python & Node.js Production Apps on Replit",
        url: "https://docs.replit.com/deployments/about-deployments"
      }
    ],
    tutor: [
      {
        type: "tutor",
        label: "AI Tutor",
        title: "Interactive Prompt: From Natural Language Prompt to Live Deployed App on Replit",
        url: "https://chatgpt.com/?q=Teach+me+how+to+prompt+the+Replit+Agent+to+build+a+full-stack+SaaS+app+with+database+and+authentication."
      }
    ],
    premium: [
      {
        type: "project",
        label: "ProjectsHub",
        title: "Production Cloud Deployments & Serverless Architecture",
        url: "/projects/?category=ml"
      }
    ]
  },
};

// Dynamic Resource Provider: Handcrafted + Contextual Fallback
function getTopicResources(tagId, data) {
  const title = data.title || "AI Engineering Concept";
  const cleanSlug = tagId.replace(/_/g, "-");

  // Free Resources
  const free = (data.free && data.free.length > 0) ? data.free : [
    {
      type: "docs",
      label: "Documentation",
      title: `${title} — Specifications & Reference Guide`,
      url: `https://www.google.com/search?q=${encodeURIComponent(title + " developer documentation API guide")}`
    },
    {
      type: "video",
      label: "YouTube",
      title: `${title} Architecture & Hands-on Masterclass`,
      url: `https://www.youtube.com/results?search_query=${encodeURIComponent(title + " tutorial AI engineering full guide")}`
    },
    {
      type: "article",
      label: "Guide",
      title: `Production System Patterns for ${title}`,
      url: `https://github.com/topics/${cleanSlug}`
    }
  ];

  // AI Tutor Practice & Prompts
  const tutor = (data.tutor && data.tutor.length > 0) ? data.tutor : [
    {
      type: "tutor",
      label: "AI Tutor",
      title: `Interactive Prompt: Explain "${title}" with code examples & mental models`,
      url: `https://chatgpt.com/?q=${encodeURIComponent('Act as an expert AI Engineer and teacher. Teach me ' + title + ' step-by-step. Provide: 1) Intuitive explanation, 2) Production code snippet, 3) Common pitfalls and how to debug them.')}`
    },
    {
      type: "course",
      label: "Architecture",
      title: `System Design Drill: Evaluating ${title} in Production Pipelines`,
      url: `https://chatgpt.com/?q=${encodeURIComponent('Give me a challenging real-world engineering problem involving ' + title + ' and guide me through solving it interactively.')}`
    }
  ];

  // Premium ProjectsHub Resources
  const premium = (data.premium && data.premium.length > 0) ? data.premium : [
    {
      type: "project",
      label: "ProjectsHub",
      title: `Production Project with Source Code: ${title} System`,
      url: `/projects/?category=ml`
    },
    {
      type: "course",
      label: "Bootcamp",
      title: `ProjectsHub 1-on-1 AI Mentorship & Engineering Workshop`,
      url: `/workshops/`
    }
  ];

  // Only assign image if explicitly provided in data
  const image = data.image || null;

  return { free, tutor, premium, image };
}

// ==========================================================================
// PURE VANILLA CENTERED POP-UP MODAL (Zero Bootstrap Dependency)
// ==========================================================================
function openRoadmapModal(tagId) {
  const rawData = roadmapData[tagId] || { title: tagId.replace(/_/g, " ") };
  const enriched = getTopicResources(tagId, rawData);
  const data = { ...rawData, ...enriched };

  // Track and highlight the active tag
  document.querySelectorAll(".tag").forEach((t) => t.classList.remove("active"));
  const ev = window.event;
  let clickedTag = ev && ev.target ? ev.target.closest(".tag") : null;
  if (!clickedTag) {
    clickedTag = document.querySelector(`.tag[onclick*="'${tagId}'"]`) || document.querySelector(`.tag[onclick*="${tagId}"]`);
  }
  if (clickedTag) {
    clickedTag.classList.add("active");
  }

  // Populate dynamic category badge
  const modalBadge = document.getElementById("modalBadge");
  if (modalBadge) {
    const chapterHeading = clickedTag ? clickedTag.closest(".timeline-item")?.querySelector("h2, h3")?.innerText : "";
    modalBadge.innerHTML = `<i class="fa-solid fa-compass"></i> ${chapterHeading || 'AI Engineering Deep Dive'}`;
  }

  // Populate Title & Desc
  const titleEl = document.getElementById("modalTitle");
  const descEl = document.getElementById("modalDesc");
  if (titleEl) titleEl.innerText = data.title;
  if (descEl) descEl.innerHTML = data.desc || `<p>Practical architecture guidelines and production implementations for <strong>${data.title}</strong>.</p>`;

  // Helper to generate HTML for links
  const generateLinks = (items) => {
    if (!items || items.length === 0)
      return '<p class="text-muted small mb-0">No resources available currently.</p>';
    return items
      .map(
        (item) => `
          <a href="${item.url || '#'}" ${item.url && item.url !== '#' ? 'target="_blank" rel="noopener noreferrer"' : ''} class="resource-link">
            <span class="resource-type ${item.type || 'article'}">${item.label || 'Resource'}</span>
            <span class="resource-title">${item.title}</span>
            <i class="fa-solid fa-arrow-up-right-from-square ms-auto opacity-50" style="font-size:0.75rem;"></i>
          </a>
        `,
      )
      .join("");
  };

  // Populate Sections
  const freeList = document.getElementById("freeList");
  const tutorList = document.getElementById("tutorList");
  const premiumList = document.getElementById("premiumList");

  if (freeList) freeList.innerHTML = generateLinks(data.free);
  if (tutorList) tutorList.innerHTML = generateLinks(data.tutor);
  if (premiumList) premiumList.innerHTML = generateLinks(data.premium);

  // Populate topic image (only if explicitly defined for this topic)
  const modalImgWrap = document.getElementById("modalImageWrap");
  const modalImg = document.getElementById("modalImage");
  const modalLabel = document.getElementById("modalImageLabel");

  if (data.image) {
    if (modalImg) {
      modalImg.src = data.image;
      modalImg.alt = data.title;
    }
    if (modalLabel) modalLabel.textContent = "📖  " + data.title;
    if (modalImgWrap) modalImgWrap.style.display = "block";
  } else {
    if (modalImgWrap) modalImgWrap.style.display = "none";
  }

  // Open Pop-up Modal Overlay
  const overlay = document.getElementById("roadmapModalOverlay");
  if (overlay) {
    overlay.classList.add("open");
    overlay.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
  }
}

function closeRoadmapModal() {
  const overlay = document.getElementById("roadmapModalOverlay");
  if (overlay) {
    overlay.classList.remove("open");
    overlay.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    document.documentElement.style.overflow = "";
  }
  document.querySelectorAll(".tag").forEach((t) => t.classList.remove("active"));
}

// Alias openDrawer to openRoadmapModal for compatibility with all existing tags
window.openDrawer = openRoadmapModal;
window.openRoadmapModal = openRoadmapModal;
window.closeRoadmapModal = closeRoadmapModal;

// Dynamic Stepper Logic
document.addEventListener("DOMContentLoaded", () => {
  const timelineItems = document.querySelectorAll(".timeline-item");
  const stepperContainer = document.getElementById("stepperContainer");

  let stepsHTML = '';

  timelineItems.forEach((item, index) => {
    const nodeId = "timeline-node-" + index;
    item.id = nodeId;

    const heading = item.querySelector("h2, h3").innerText;
    const cleanTitle = heading.replace(/^[0-9]+\.\s*/, "");

    stepsHTML += `
            <div class="stepper-step" onclick="scrollToNode('${nodeId}')">
              <div class="step-number">${index + 1}</div>
              <div class="step-title">${cleanTitle}</div>
            </div>
        `;
  });

  stepperContainer.innerHTML = `
    <div class="stepper-nav-outer">
      <button class="stepper-arrow stepper-arrow-left" id="stepperArrowLeft" aria-label="Scroll left">&#8249;</button>
      <div class="stepper-wrapper" id="stepperScrollArea">
        ${stepsHTML}
      </div>
      <button class="stepper-arrow stepper-arrow-right" id="stepperArrowRight" aria-label="Scroll right">&#8250;</button>
    </div>
  `;

  const scrollArea = document.getElementById("stepperScrollArea");
  const arrowLeft = document.getElementById("stepperArrowLeft");
  const arrowRight = document.getElementById("stepperArrowRight");
  const SCROLL_AMOUNT = 200;

  function updateArrows() {
    arrowLeft.style.opacity = scrollArea.scrollLeft > 0 ? "1" : "0.3";
    arrowRight.style.opacity = scrollArea.scrollLeft < scrollArea.scrollWidth - scrollArea.clientWidth - 1 ? "1" : "0.3";
  }

  arrowLeft.addEventListener("click", () => {
    scrollArea.scrollBy({ left: -SCROLL_AMOUNT, behavior: "smooth" });
  });

  arrowRight.addEventListener("click", () => {
    scrollArea.scrollBy({ left: SCROLL_AMOUNT, behavior: "smooth" });
  });

  scrollArea.addEventListener("scroll", updateArrows);
  updateArrows();
});

function scrollToNode(nodeId) {
  const node = document.getElementById(nodeId);
  if (node) {
    // Smooth scroll to the node, leaving some padding at the top
    const yOffset = -80;
    const y = node.getBoundingClientRect().top + window.scrollY + yOffset;
    window.scrollTo({ top: y, behavior: "smooth" });
  }
}

// Theme Logic & Initial Screen State
document.addEventListener("DOMContentLoaded", () => {
  // Enforce ProjectsHub pure white / light theme matching other pages
  document.documentElement.classList.remove("dark");
  document.documentElement.classList.add("light");
  document.body.classList.remove("dark", "ai-roadmap-dark");
  document.body.classList.add("light", "light-mode");

  // Move Modal overlay directly to document.body to avoid parent stacking-context clipping
  const overlay = document.getElementById("roadmapModalOverlay");
  if (overlay && overlay.parentElement !== document.body) {
    document.body.appendChild(overlay);
  }

  // Bind Pop-up Modal close events
  const backdrop = document.getElementById("roadmapModalBackdrop");
  const dialog = document.getElementById("roadmapModalDialog");
  const closeBtn = document.getElementById("modalCloseBtn");
  const footerCloseBtn = document.getElementById("modalFooterClose");

  if (backdrop) backdrop.addEventListener("click", closeRoadmapModal);
  if (closeBtn) closeBtn.addEventListener("click", closeRoadmapModal);
  if (footerCloseBtn) footerCloseBtn.addEventListener("click", closeRoadmapModal);

  // Prevent clicks inside the modal card from closing the modal
  if (dialog) {
    dialog.addEventListener("click", (e) => {
      e.stopPropagation();
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeRoadmapModal();
  });

  // Open modal if explicitly specified in hash (e.g. #what_is_ai_eng)
  const hashTopic = window.location.hash.replace("#", "");
  if (hashTopic && (roadmapData[hashTopic] || document.querySelector(`.tag[onclick*="${hashTopic}"]`))) {
    setTimeout(() => {
      openRoadmapModal(hashTopic);
    }, 250);
  }
});

// Timeline Scroll Fill Animation
document.addEventListener("DOMContentLoaded", () => {
  const timeline = document.querySelector(".timeline");
  const timelineIcons = document.querySelectorAll(".timeline-icon");
  const progressBadge = document.getElementById("timelineProgressBadge");
  const progressText = document.getElementById("timelineProgressText");

  if (timeline) {
    function updateTimeline() {
      const scrollPosition = window.scrollY;
      const maxScroll = Math.max(
        1,
        document.documentElement.scrollHeight - window.innerHeight,
      );

      let progress = (scrollPosition / maxScroll) * 100;
      progress = Math.max(0, Math.min(progress, 100));

      const roundedProgress = Math.round(progress);

      // Update fill line height via CSS variable
      timeline.style.setProperty("--scroll-progress", `${progress}%`);

      // Update badge text and position along the fill line
      if (progressBadge && progressText) {
        progressText.textContent = `${roundedProgress}%`;

        // Position badge at the bottom of the fill line using timeline's actual position
        const timelineRectForBadge = timeline.getBoundingClientRect();
        const fillHeight = (progress / 100) * timeline.offsetHeight;
        // top = timeline top (relative to viewport) + fillHeight + scrollY = absolute position
        const badgeAbsTop =
          timelineRectForBadge.top + window.scrollY + fillHeight;
        // left = center of the timeline
        const badgeAbsLeft =
          timelineRectForBadge.left + timeline.offsetWidth / 2;

        progressBadge.style.position = "absolute";
        progressBadge.style.top = `${badgeAbsTop}px`;
        progressBadge.style.left = `${badgeAbsLeft}px`;
        progressBadge.style.transform = "translate(-50%, -50%)";

        // Hide badge at 0% or 100% for cleanliness
        progressBadge.style.opacity =
          roundedProgress <= 0 || roundedProgress >= 100 ? "0" : "1";
      }

      const timelineRect = timeline.getBoundingClientRect();
      const timelineAbsoluteTop = timelineRect.top + window.scrollY;
      const fillLineBottom =
        timelineAbsoluteTop + (progress / 100) * timeline.offsetHeight;

      timelineIcons.forEach((icon) => {
        const iconRect = icon.getBoundingClientRect();
        const iconAbsoluteTop = iconRect.top + window.scrollY;
        const iconCenter = iconAbsoluteTop + iconRect.height / 2;

        if (fillLineBottom >= iconCenter) {
          icon.classList.add("filled");
        } else {
          icon.classList.remove("filled");
        }
      });
    }

    window.addEventListener("scroll", updateTimeline);
    window.addEventListener("resize", updateTimeline);
    // Initial call to set state on load
    updateTimeline();
  }
});

// =============================================
// Mobile Screen Border Trace Animation
// Scroll 0–25%  → TOP    line fills (left→right)
// Scroll 25–50% → RIGHT  line fills (top→bottom)
// Scroll 50–75% → BOTTOM line fills (right→left)
// Scroll 75–100%→ LEFT   line fills (bottom→top)
// =============================================
document.addEventListener("DOMContentLoaded", () => {
  const borderTop = document.getElementById("borderTop");
  const borderRight = document.getElementById("borderRight");
  const borderBottom = document.getElementById("borderBottom");
  const borderLeft = document.getElementById("borderLeft");

  if (!borderTop) return;

  // Helper: calculate 0–100 fill within a scroll segment
  function segmentFill(progress, segStart, segEnd) {
    if (progress <= segStart) return 0;
    if (progress >= segEnd) return 100;
    return ((progress - segStart) / (segEnd - segStart)) * 100;
  }

  function updateBorderTrace() {
    // Only run on mobile
    if (window.innerWidth > 768) {
      // Reset all lines on desktop/tablet resize
      borderTop.style.width = "0";
      borderRight.style.height = "0";
      borderBottom.style.width = "0";
      borderLeft.style.height = "0";
      return;
    }

    const scrollPos = window.scrollY;
    const maxScroll = Math.max(
      1,
      document.documentElement.scrollHeight - window.innerHeight,
    );
    const progress = Math.min(100, Math.max(0, (scrollPos / maxScroll) * 100));

    // Segment 1: 0–25% → TOP grows left → right
    borderTop.style.width = segmentFill(progress, 0, 25) + "vw";

    // Segment 2: 25–50% → RIGHT grows top → bottom
    borderRight.style.height = segmentFill(progress, 25, 50) + "vh";

    // Segment 3: 50–75% → BOTTOM grows right → left
    borderBottom.style.width = segmentFill(progress, 50, 75) + "vw";

    // Segment 4: 75–100% → LEFT grows bottom → top
    borderLeft.style.height = segmentFill(progress, 75, 100) + "vh";
  }

  window.addEventListener("scroll", updateBorderTrace, { passive: true });
  window.addEventListener("resize", updateBorderTrace);
  updateBorderTrace(); // initial state on load
});
