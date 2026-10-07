// Generated compatibility snapshot of the canonical Python MCP contracts.
// Source: D1traverser-debug/financial-writing-agent@v0.2.1-runtime-rule-hardening
// Generated at build time from the previous gzip payload. Runtime loading is static and performs no I/O.
export const PYTHON_CONTRACT_SNAPSHOT: any = {
  "oracle": "D1traverser-debug/financial-writing-agent@v0.2.1-runtime-rule-hardening",
  "schemas": {
    "start_writing_taskInput": {
      "additionalProperties": false,
      "properties": {
        "prompt": {
          "description": "The user's concrete publishable financial-writing request.",
          "minLength": 1,
          "title": "Prompt",
          "type": "string"
        },
        "source_refs": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Explicit source URLs or references supplied for this task.",
          "title": "Source Refs"
        },
        "target_platforms": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Explicit destination platforms; omit to use the formal default routing.",
          "title": "Target Platforms"
        },
        "visuals_enabled": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Explicit visual override; omit to use runtime defaults.",
          "title": "Visuals Enabled"
        },
        "visual_profile_ref": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Reference to an already-approved visual/avatar profile when available.",
          "title": "Visual Profile Ref"
        },
        "content_mode": {
          "anyOf": [
            {
              "enum": [
                "FORMAL_ARTICLE",
                "WECHAT_STICKER_POST"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Explicit content mode override only when the request clearly requires it.",
          "title": "Content Mode"
        }
      },
      "required": [
        "prompt"
      ],
      "title": "StartWritingTaskInput",
      "type": "object"
    },
    "WritingTaskSummary": {
      "$defs": {
        "ArtifactSummary": {
          "properties": {
            "file_name": {
              "title": "File Name",
              "type": "string"
            },
            "exists": {
              "title": "Exists",
              "type": "boolean"
            },
            "sha256": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Sha256"
            },
            "resource_uri": {
              "title": "Resource Uri",
              "type": "string"
            },
            "mime_type": {
              "title": "Mime Type",
              "type": "string"
            }
          },
          "required": [
            "file_name",
            "exists",
            "resource_uri",
            "mime_type"
          ],
          "title": "ArtifactSummary",
          "type": "object"
        },
        "CompletionChecklist": {
          "properties": {
            "runtime_gates": {
              "enum": [
                "PASS",
                "INCOMPLETE"
              ],
              "title": "Runtime Gates",
              "type": "string"
            },
            "research_evidence": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Research Evidence",
              "type": "string"
            },
            "structure_style_continuity": {
              "$ref": "#/$defs/StyleChecklist"
            },
            "word_render": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Word Render",
              "type": "string"
            },
            "compliance_risk": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Compliance Risk",
              "type": "string"
            },
            "visuals": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Visuals",
              "type": "string"
            },
            "knowledge": {
              "$ref": "#/$defs/KnowledgeChecklist"
            }
          },
          "required": [
            "runtime_gates",
            "research_evidence",
            "structure_style_continuity",
            "word_render",
            "compliance_risk",
            "visuals",
            "knowledge"
          ],
          "title": "CompletionChecklist",
          "type": "object"
        },
        "GateSummary": {
          "properties": {
            "status": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Status",
              "type": "string"
            },
            "evidence": {
              "items": {
                "type": "string"
              },
              "title": "Evidence",
              "type": "array"
            },
            "notes": {
              "default": "",
              "title": "Notes",
              "type": "string"
            }
          },
          "required": [
            "status"
          ],
          "title": "GateSummary",
          "type": "object"
        },
        "KnowledgeChecklist": {
          "properties": {
            "context_gate": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Context Gate",
              "type": "string"
            },
            "sync_gate": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Sync Gate",
              "type": "string"
            },
            "reused_refs": {
              "minimum": 0,
              "title": "Reused Refs",
              "type": "integer"
            },
            "writeback_candidates": {
              "minimum": 0,
              "title": "Writeback Candidates",
              "type": "integer"
            },
            "writeback_receipts": {
              "minimum": 0,
              "title": "Writeback Receipts",
              "type": "integer"
            }
          },
          "required": [
            "context_gate",
            "sync_gate",
            "reused_refs",
            "writeback_candidates",
            "writeback_receipts"
          ],
          "title": "KnowledgeChecklist",
          "type": "object"
        },
        "StyleChecklist": {
          "properties": {
            "editorial": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Editorial",
              "type": "string"
            },
            "anti_ai_style": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Anti Ai Style",
              "type": "string"
            }
          },
          "required": [
            "editorial",
            "anti_ai_style"
          ],
          "title": "StyleChecklist",
          "type": "object"
        }
      },
      "properties": {
        "task_id": {
          "title": "Task Id",
          "type": "string"
        },
        "status": {
          "enum": [
            "IN_PROGRESS",
            "BLOCKED",
            "COMPLETE"
          ],
          "title": "Status",
          "type": "string"
        },
        "current_stage": {
          "enum": [
            "INTAKE",
            "RESEARCH",
            "RESEARCH_AUDIT",
            "EDITORIAL",
            "TITLE",
            "DRAFT",
            "EDITORIAL_AUDIT",
            "DELIVERY",
            "MECHANICAL_AUDIT",
            "FINAL_AUDIT",
            "COMPLETE",
            "BLOCKED"
          ],
          "title": "Current Stage",
          "type": "string"
        },
        "topic": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Topic"
        },
        "prompt_preview": {
          "title": "Prompt Preview",
          "type": "string"
        },
        "content_mode": {
          "enum": [
            "FORMAL_ARTICLE",
            "WECHAT_STICKER_POST"
          ],
          "title": "Content Mode",
          "type": "string"
        },
        "distribution_mode": {
          "enum": [
            "FINANCE_DEEP",
            "FINANCE_BROAD",
            "DUAL"
          ],
          "title": "Distribution Mode",
          "type": "string"
        },
        "delivery_channel": {
          "enum": [
            "WORD_FILE_ONLY",
            "CHAT_TEXT"
          ],
          "title": "Delivery Channel",
          "type": "string"
        },
        "visuals_enabled": {
          "title": "Visuals Enabled",
          "type": "boolean"
        },
        "required_outputs": {
          "items": {
            "type": "string"
          },
          "title": "Required Outputs",
          "type": "array"
        },
        "gate_status": {
          "additionalProperties": {
            "enum": [
              "NOT_RUN",
              "PASS",
              "REVISE",
              "FAIL",
              "N_A"
            ],
            "type": "string"
          },
          "title": "Gate Status",
          "type": "object"
        },
        "blocked_reason": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Blocked Reason"
        },
        "updated_at": {
          "format": "date-time",
          "title": "Updated At",
          "type": "string"
        },
        "next_action": {
          "title": "Next Action",
          "type": "string"
        },
        "source_refs": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Source Refs"
        },
        "visual_profile_ref": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Visual Profile Ref"
        },
        "gates": {
          "anyOf": [
            {
              "additionalProperties": {
                "$ref": "#/$defs/GateSummary"
              },
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Gates"
        },
        "artifacts": {
          "anyOf": [
            {
              "additionalProperties": {
                "$ref": "#/$defs/ArtifactSummary"
              },
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Artifacts"
        },
        "render_pages": {
          "anyOf": [
            {
              "additionalProperties": {
                "items": {
                  "type": "string"
                },
                "type": "array"
              },
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Render Pages"
        },
        "completion_checklist": {
          "anyOf": [
            {
              "$ref": "#/$defs/CompletionChecklist"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "task_id",
        "status",
        "current_stage",
        "prompt_preview",
        "content_mode",
        "distribution_mode",
        "delivery_channel",
        "visuals_enabled",
        "required_outputs",
        "updated_at",
        "next_action"
      ],
      "title": "WritingTaskSummary",
      "type": "object"
    },
    "get_writing_taskInput": {
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "description": "Exact persisted task ID returned by this runtime.",
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "detail": {
          "default": true,
          "description": "Return gates, publication artifact resources and rendered-page evidence when true.",
          "title": "Detail",
          "type": "boolean"
        }
      },
      "required": [
        "task_id"
      ],
      "title": "GetWritingTaskInput",
      "type": "object"
    },
    "resume_writing_taskInput": {
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "description": "Exact BLOCKED task ID to resume at its recorded original stage.",
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        }
      },
      "required": [
        "task_id"
      ],
      "title": "ResumeWritingTaskInput",
      "type": "object"
    },
    "list_recent_writing_tasksInput": {
      "additionalProperties": false,
      "properties": {
        "limit": {
          "default": 10,
          "description": "Maximum number of recent tasks to return.",
          "maximum": 50,
          "minimum": 1,
          "title": "Limit",
          "type": "integer"
        },
        "include_complete": {
          "default": false,
          "description": "Include already completed tasks when true.",
          "title": "Include Complete",
          "type": "boolean"
        }
      },
      "title": "ListRecentWritingTasksInput",
      "type": "object"
    },
    "WritingTaskList": {
      "$defs": {
        "ArtifactSummary": {
          "properties": {
            "file_name": {
              "title": "File Name",
              "type": "string"
            },
            "exists": {
              "title": "Exists",
              "type": "boolean"
            },
            "sha256": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Sha256"
            },
            "resource_uri": {
              "title": "Resource Uri",
              "type": "string"
            },
            "mime_type": {
              "title": "Mime Type",
              "type": "string"
            }
          },
          "required": [
            "file_name",
            "exists",
            "resource_uri",
            "mime_type"
          ],
          "title": "ArtifactSummary",
          "type": "object"
        },
        "CompletionChecklist": {
          "properties": {
            "runtime_gates": {
              "enum": [
                "PASS",
                "INCOMPLETE"
              ],
              "title": "Runtime Gates",
              "type": "string"
            },
            "research_evidence": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Research Evidence",
              "type": "string"
            },
            "structure_style_continuity": {
              "$ref": "#/$defs/StyleChecklist"
            },
            "word_render": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Word Render",
              "type": "string"
            },
            "compliance_risk": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Compliance Risk",
              "type": "string"
            },
            "visuals": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Visuals",
              "type": "string"
            },
            "knowledge": {
              "$ref": "#/$defs/KnowledgeChecklist"
            }
          },
          "required": [
            "runtime_gates",
            "research_evidence",
            "structure_style_continuity",
            "word_render",
            "compliance_risk",
            "visuals",
            "knowledge"
          ],
          "title": "CompletionChecklist",
          "type": "object"
        },
        "GateSummary": {
          "properties": {
            "status": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Status",
              "type": "string"
            },
            "evidence": {
              "items": {
                "type": "string"
              },
              "title": "Evidence",
              "type": "array"
            },
            "notes": {
              "default": "",
              "title": "Notes",
              "type": "string"
            }
          },
          "required": [
            "status"
          ],
          "title": "GateSummary",
          "type": "object"
        },
        "KnowledgeChecklist": {
          "properties": {
            "context_gate": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Context Gate",
              "type": "string"
            },
            "sync_gate": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Sync Gate",
              "type": "string"
            },
            "reused_refs": {
              "minimum": 0,
              "title": "Reused Refs",
              "type": "integer"
            },
            "writeback_candidates": {
              "minimum": 0,
              "title": "Writeback Candidates",
              "type": "integer"
            },
            "writeback_receipts": {
              "minimum": 0,
              "title": "Writeback Receipts",
              "type": "integer"
            }
          },
          "required": [
            "context_gate",
            "sync_gate",
            "reused_refs",
            "writeback_candidates",
            "writeback_receipts"
          ],
          "title": "KnowledgeChecklist",
          "type": "object"
        },
        "StyleChecklist": {
          "properties": {
            "editorial": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Editorial",
              "type": "string"
            },
            "anti_ai_style": {
              "enum": [
                "NOT_RUN",
                "PASS",
                "REVISE",
                "FAIL",
                "N_A"
              ],
              "title": "Anti Ai Style",
              "type": "string"
            }
          },
          "required": [
            "editorial",
            "anti_ai_style"
          ],
          "title": "StyleChecklist",
          "type": "object"
        },
        "WritingTaskSummary": {
          "properties": {
            "task_id": {
              "title": "Task Id",
              "type": "string"
            },
            "status": {
              "enum": [
                "IN_PROGRESS",
                "BLOCKED",
                "COMPLETE"
              ],
              "title": "Status",
              "type": "string"
            },
            "current_stage": {
              "enum": [
                "INTAKE",
                "RESEARCH",
                "RESEARCH_AUDIT",
                "EDITORIAL",
                "TITLE",
                "DRAFT",
                "EDITORIAL_AUDIT",
                "DELIVERY",
                "MECHANICAL_AUDIT",
                "FINAL_AUDIT",
                "COMPLETE",
                "BLOCKED"
              ],
              "title": "Current Stage",
              "type": "string"
            },
            "topic": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Topic"
            },
            "prompt_preview": {
              "title": "Prompt Preview",
              "type": "string"
            },
            "content_mode": {
              "enum": [
                "FORMAL_ARTICLE",
                "WECHAT_STICKER_POST"
              ],
              "title": "Content Mode",
              "type": "string"
            },
            "distribution_mode": {
              "enum": [
                "FINANCE_DEEP",
                "FINANCE_BROAD",
                "DUAL"
              ],
              "title": "Distribution Mode",
              "type": "string"
            },
            "delivery_channel": {
              "enum": [
                "WORD_FILE_ONLY",
                "CHAT_TEXT"
              ],
              "title": "Delivery Channel",
              "type": "string"
            },
            "visuals_enabled": {
              "title": "Visuals Enabled",
              "type": "boolean"
            },
            "required_outputs": {
              "items": {
                "type": "string"
              },
              "title": "Required Outputs",
              "type": "array"
            },
            "gate_status": {
              "additionalProperties": {
                "enum": [
                  "NOT_RUN",
                  "PASS",
                  "REVISE",
                  "FAIL",
                  "N_A"
                ],
                "type": "string"
              },
              "title": "Gate Status",
              "type": "object"
            },
            "blocked_reason": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Blocked Reason"
            },
            "updated_at": {
              "format": "date-time",
              "title": "Updated At",
              "type": "string"
            },
            "next_action": {
              "title": "Next Action",
              "type": "string"
            },
            "source_refs": {
              "anyOf": [
                {
                  "items": {
                    "type": "string"
                  },
                  "type": "array"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Source Refs"
            },
            "visual_profile_ref": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Visual Profile Ref"
            },
            "gates": {
              "anyOf": [
                {
                  "additionalProperties": {
                    "$ref": "#/$defs/GateSummary"
                  },
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Gates"
            },
            "artifacts": {
              "anyOf": [
                {
                  "additionalProperties": {
                    "$ref": "#/$defs/ArtifactSummary"
                  },
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Artifacts"
            },
            "render_pages": {
              "anyOf": [
                {
                  "additionalProperties": {
                    "items": {
                      "type": "string"
                    },
                    "type": "array"
                  },
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Render Pages"
            },
            "completion_checklist": {
              "anyOf": [
                {
                  "$ref": "#/$defs/CompletionChecklist"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            }
          },
          "required": [
            "task_id",
            "status",
            "current_stage",
            "prompt_preview",
            "content_mode",
            "distribution_mode",
            "delivery_channel",
            "visuals_enabled",
            "required_outputs",
            "updated_at",
            "next_action"
          ],
          "title": "WritingTaskSummary",
          "type": "object"
        }
      },
      "properties": {
        "tasks": {
          "items": {
            "$ref": "#/$defs/WritingTaskSummary"
          },
          "title": "Tasks",
          "type": "array"
        }
      },
      "required": [
        "tasks"
      ],
      "title": "WritingTaskList",
      "type": "object"
    },
    "record_knowledge_contextInput": {
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "status": {
          "enum": [
            "PASS",
            "N_A"
          ],
          "title": "Status",
          "type": "string"
        },
        "refs": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Real references actually retrieved from durable prior knowledge when status=PASS.",
          "title": "Refs"
        },
        "notes": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Reuse/conflict notes, or the explicit reason durable knowledge is unavailable/not applicable when status=N_A.",
          "title": "Notes"
        }
      },
      "required": [
        "task_id",
        "status"
      ],
      "title": "RecordKnowledgeContextInput",
      "type": "object"
    },
    "submit_researchInput": {
      "$defs": {
        "CompanyFinding": {
          "additionalProperties": false,
          "properties": {
            "name": {
              "minLength": 1,
              "title": "Name",
              "type": "string"
            },
            "ticker": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Ticker"
            },
            "relevance": {
              "minLength": 1,
              "title": "Relevance",
              "type": "string"
            },
            "business_stage": {
              "default": "",
              "title": "Business Stage",
              "type": "string"
            },
            "positive_evidence": {
              "items": {
                "type": "string"
              },
              "title": "Positive Evidence",
              "type": "array"
            },
            "negative_evidence": {
              "items": {
                "type": "string"
              },
              "title": "Negative Evidence",
              "type": "array"
            },
            "why_this": {
              "default": "",
              "title": "Why This",
              "type": "string"
            },
            "why_not": {
              "items": {
                "type": "string"
              },
              "title": "Why Not",
              "type": "array"
            },
            "market_role": {
              "default": "",
              "title": "Market Role",
              "type": "string"
            },
            "short_term_role": {
              "default": "",
              "title": "Short Term Role",
              "type": "string"
            },
            "positioning_signals": {
              "items": {
                "type": "string"
              },
              "title": "Positioning Signals",
              "type": "array"
            },
            "fund_flow_signals": {
              "items": {
                "type": "string"
              },
              "title": "Fund Flow Signals",
              "type": "array"
            }
          },
          "required": [
            "name",
            "relevance"
          ],
          "title": "CompanyFinding",
          "type": "object"
        },
        "EvidenceItem": {
          "additionalProperties": false,
          "properties": {
            "claim": {
              "minLength": 1,
              "title": "Claim",
              "type": "string"
            },
            "source": {
              "minLength": 1,
              "title": "Source",
              "type": "string"
            },
            "date": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Date"
            },
            "evidence_type": {
              "default": "web",
              "title": "Evidence Type",
              "type": "string"
            },
            "confidence": {
              "default": "medium",
              "enum": [
                "high",
                "medium",
                "low"
              ],
              "title": "Confidence",
              "type": "string"
            },
            "core_safe": {
              "default": false,
              "title": "Core Safe",
              "type": "boolean"
            },
            "verification_status": {
              "default": "UNRESOLVED",
              "enum": [
                "UNRESOLVED",
                "SINGLE_SOURCE_ATTRIBUTED",
                "INDEPENDENTLY_CROSS_CHECKED"
              ],
              "title": "Verification Status",
              "type": "string"
            },
            "source_group": {
              "default": "",
              "title": "Source Group",
              "type": "string"
            },
            "second_check_source": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Second Check Source"
            },
            "second_check_source_group": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Second Check Source Group"
            },
            "allowed_wording": {
              "default": "",
              "title": "Allowed Wording",
              "type": "string"
            },
            "conflict": {
              "default": "",
              "title": "Conflict",
              "type": "string"
            },
            "notes": {
              "default": "",
              "title": "Notes",
              "type": "string"
            }
          },
          "required": [
            "claim",
            "source"
          ],
          "title": "EvidenceItem",
          "type": "object"
        },
        "MarketCognition": {
          "additionalProperties": false,
          "properties": {
            "prior_knowledge_refs": {
              "items": {
                "type": "string"
              },
              "title": "Prior Knowledge Refs",
              "type": "array"
            },
            "concept_map": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Concept Map",
              "type": "array"
            },
            "adjacent_or_competing_concepts": {
              "items": {
                "type": "string"
              },
              "title": "Adjacent Or Competing Concepts",
              "type": "array"
            },
            "industry_logic": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Industry Logic",
              "type": "array"
            },
            "short_term_market_structure": {
              "items": {
                "type": "string"
              },
              "title": "Short Term Market Structure",
              "type": "array"
            },
            "knowledge_conflicts": {
              "items": {
                "type": "string"
              },
              "title": "Knowledge Conflicts",
              "type": "array"
            }
          },
          "required": [
            "concept_map",
            "industry_logic"
          ],
          "title": "MarketCognition",
          "type": "object"
        },
        "ResearchCoverage": {
          "additionalProperties": false,
          "properties": {
            "sweeps_completed": {
              "maximum": 10,
              "minimum": 2,
              "title": "Sweeps Completed",
              "type": "integer"
            },
            "coverage_status": {
              "enum": [
                "SATURATED",
                "BOUNDED_WITH_GAPS"
              ],
              "title": "Coverage Status",
              "type": "string"
            },
            "material_new_items_last_sweep": {
              "minimum": 0,
              "title": "Material New Items Last Sweep",
              "type": "integer"
            },
            "concept_coverage": {
              "minLength": 1,
              "title": "Concept Coverage",
              "type": "string"
            },
            "company_coverage": {
              "minLength": 1,
              "title": "Company Coverage",
              "type": "string"
            },
            "source_diversity": {
              "minLength": 1,
              "title": "Source Diversity",
              "type": "string"
            },
            "excluded_scope": {
              "items": {
                "type": "string"
              },
              "title": "Excluded Scope",
              "type": "array"
            },
            "stop_reason": {
              "minLength": 1,
              "title": "Stop Reason",
              "type": "string"
            }
          },
          "required": [
            "sweeps_completed",
            "coverage_status",
            "material_new_items_last_sweep",
            "concept_coverage",
            "company_coverage",
            "source_diversity",
            "stop_reason"
          ],
          "title": "ResearchCoverage",
          "type": "object"
        },
        "ResearchFailure": {
          "additionalProperties": false,
          "properties": {
            "failed_action": {
              "minLength": 1,
              "title": "Failed Action",
              "type": "string"
            },
            "failure_reason": {
              "minLength": 1,
              "title": "Failure Reason",
              "type": "string"
            },
            "retry_attempted": {
              "default": false,
              "title": "Retry Attempted",
              "type": "boolean"
            },
            "alternative_source_or_tool": {
              "default": "",
              "title": "Alternative Source Or Tool",
              "type": "string"
            },
            "impact_on_result": {
              "minLength": 1,
              "title": "Impact On Result",
              "type": "string"
            },
            "resolved": {
              "default": false,
              "title": "Resolved",
              "type": "boolean"
            }
          },
          "required": [
            "failed_action",
            "failure_reason",
            "impact_on_result"
          ],
          "title": "ResearchFailure",
          "type": "object"
        },
        "ResearchPackage": {
          "additionalProperties": false,
          "properties": {
            "topic": {
              "minLength": 1,
              "title": "Topic",
              "type": "string"
            },
            "chronology": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Chronology",
              "type": "array"
            },
            "what_changed": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "What Changed",
              "type": "array"
            },
            "industry_chain": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Industry Chain",
              "type": "array"
            },
            "transmission_chain": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Transmission Chain",
              "type": "array"
            },
            "universe": {
              "items": {
                "$ref": "#/$defs/CompanyFinding"
              },
              "title": "Universe",
              "type": "array"
            },
            "evidence_ledger": {
              "items": {
                "$ref": "#/$defs/EvidenceItem"
              },
              "minItems": 1,
              "title": "Evidence Ledger",
              "type": "array"
            },
            "counterevidence": {
              "items": {
                "type": "string"
              },
              "title": "Counterevidence",
              "type": "array"
            },
            "unresolved_gaps": {
              "items": {
                "type": "string"
              },
              "title": "Unresolved Gaps",
              "type": "array"
            },
            "provisional_theses": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Provisional Theses",
              "type": "array"
            },
            "source_boundary": {
              "minLength": 1,
              "title": "Source Boundary",
              "type": "string"
            },
            "cognition": {
              "$ref": "#/$defs/MarketCognition"
            },
            "coverage": {
              "$ref": "#/$defs/ResearchCoverage"
            },
            "review_queue": {
              "items": {
                "$ref": "#/$defs/StockBasePendingUpdate"
              },
              "title": "Review Queue",
              "type": "array"
            },
            "failed_tools_or_sources": {
              "items": {
                "$ref": "#/$defs/ResearchFailure"
              },
              "title": "Failed Tools Or Sources",
              "type": "array"
            },
            "knowledge_writeback_candidates": {
              "items": {
                "type": "string"
              },
              "title": "Knowledge Writeback Candidates",
              "type": "array"
            }
          },
          "required": [
            "topic",
            "chronology",
            "what_changed",
            "industry_chain",
            "transmission_chain",
            "evidence_ledger",
            "provisional_theses",
            "source_boundary",
            "cognition",
            "coverage"
          ],
          "title": "ResearchPackage",
          "type": "object"
        },
        "StockBasePendingUpdate": {
          "additionalProperties": false,
          "properties": {
            "stock_code": {
              "minLength": 1,
              "title": "Stock Code",
              "type": "string"
            },
            "field_or_relation": {
              "minLength": 1,
              "title": "Field Or Relation",
              "type": "string"
            },
            "old_value_if_known": {
              "default": "",
              "title": "Old Value If Known",
              "type": "string"
            },
            "proposed_value": {
              "minLength": 1,
              "title": "Proposed Value",
              "type": "string"
            },
            "source": {
              "minLength": 1,
              "title": "Source",
              "type": "string"
            },
            "reason": {
              "minLength": 1,
              "title": "Reason",
              "type": "string"
            },
            "verified_at": {
              "minLength": 1,
              "title": "Verified At",
              "type": "string"
            },
            "status": {
              "const": "PENDING_REVIEW",
              "default": "PENDING_REVIEW",
              "title": "Status",
              "type": "string"
            }
          },
          "required": [
            "stock_code",
            "field_or_relation",
            "proposed_value",
            "source",
            "reason",
            "verified_at"
          ],
          "title": "StockBasePendingUpdate",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "research": {
          "$ref": "#/$defs/ResearchPackage"
        }
      },
      "required": [
        "task_id",
        "research"
      ],
      "title": "SubmitResearchInput",
      "type": "object"
    },
    "submit_research_auditInput": {
      "$defs": {
        "GateDecision": {
          "additionalProperties": false,
          "properties": {
            "status": {
              "enum": [
                "PASS",
                "REVISE",
                "FAIL"
              ],
              "title": "Status",
              "type": "string"
            },
            "evidence": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Evidence",
              "type": "array"
            },
            "defects": {
              "items": {
                "type": "string"
              },
              "title": "Defects",
              "type": "array"
            },
            "revision_target": {
              "anyOf": [
                {
                  "enum": [
                    "RESEARCH",
                    "EDITORIAL",
                    "TITLE",
                    "DRAFT",
                    "DELIVERY"
                  ],
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Revision Target"
            },
            "remaining_boundaries": {
              "items": {
                "type": "string"
              },
              "title": "Remaining Boundaries",
              "type": "array"
            }
          },
          "required": [
            "status",
            "evidence"
          ],
          "title": "GateDecision",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "decision": {
          "$ref": "#/$defs/GateDecision"
        }
      },
      "required": [
        "task_id",
        "decision"
      ],
      "title": "SubmitResearchAuditInput",
      "type": "object"
    },
    "submit_editorial_planInput": {
      "$defs": {
        "EditorialPlan": {
          "additionalProperties": false,
          "properties": {
            "topic_dna": {
              "$ref": "#/$defs/TopicDNA"
            },
            "finance_deep": {
              "anyOf": [
                {
                  "$ref": "#/$defs/ModeEditorialPlan"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            },
            "finance_broad": {
              "anyOf": [
                {
                  "$ref": "#/$defs/ModeEditorialPlan"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            },
            "wechat_sticker": {
              "anyOf": [
                {
                  "$ref": "#/$defs/ModeEditorialPlan"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            }
          },
          "required": [
            "topic_dna"
          ],
          "title": "EditorialPlan",
          "type": "object"
        },
        "ModeEditorialPlan": {
          "additionalProperties": false,
          "properties": {
            "candidates": {
              "items": {
                "$ref": "#/$defs/StructureCandidate"
              },
              "maxItems": 3,
              "minItems": 2,
              "title": "Candidates",
              "type": "array"
            },
            "selected_structure": {
              "$ref": "#/$defs/StructureCandidate"
            },
            "emphasis": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Emphasis",
              "type": "array"
            },
            "side_focus_statement": {
              "minLength": 1,
              "title": "Side Focus Statement",
              "type": "string"
            },
            "company_selection_basis": {
              "items": {
                "type": "string"
              },
              "maxItems": 2,
              "minItems": 1,
              "title": "Company Selection Basis",
              "type": "array"
            },
            "outline_fingerprint_refs": {
              "items": {
                "type": "string"
              },
              "title": "Outline Fingerprint Refs",
              "type": "array"
            },
            "outline_collision_notes": {
              "items": {
                "type": "string"
              },
              "title": "Outline Collision Notes",
              "type": "array"
            }
          },
          "required": [
            "candidates",
            "selected_structure",
            "emphasis",
            "side_focus_statement",
            "company_selection_basis"
          ],
          "title": "ModeEditorialPlan",
          "type": "object"
        },
        "StructureCandidate": {
          "additionalProperties": false,
          "properties": {
            "name": {
              "minLength": 1,
              "title": "Name",
              "type": "string"
            },
            "rationale": {
              "minLength": 1,
              "title": "Rationale",
              "type": "string"
            },
            "sections": {
              "items": {
                "type": "string"
              },
              "minItems": 2,
              "title": "Sections",
              "type": "array"
            }
          },
          "required": [
            "name",
            "rationale",
            "sections"
          ],
          "title": "StructureCandidate",
          "type": "object"
        },
        "TopicDNA": {
          "additionalProperties": false,
          "properties": {
            "new_fact": {
              "minLength": 1,
              "title": "New Fact",
              "type": "string"
            },
            "main_transmission": {
              "minLength": 1,
              "title": "Main Transmission",
              "type": "string"
            },
            "likely_reader_misjudgment": {
              "minLength": 1,
              "title": "Likely Reader Misjudgment",
              "type": "string"
            },
            "core_contradictions": {
              "items": {
                "type": "string"
              },
              "maxItems": 3,
              "minItems": 1,
              "title": "Core Contradictions",
              "type": "array"
            },
            "comparison_dimensions": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Comparison Dimensions",
              "type": "array"
            },
            "compression_candidates": {
              "items": {
                "type": "string"
              },
              "title": "Compression Candidates",
              "type": "array"
            },
            "finance_wide_question": {
              "minLength": 1,
              "title": "Finance Wide Question",
              "type": "string"
            }
          },
          "required": [
            "new_fact",
            "main_transmission",
            "likely_reader_misjudgment",
            "core_contradictions",
            "comparison_dimensions",
            "finance_wide_question"
          ],
          "title": "TopicDNA",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "editorial_plan": {
          "$ref": "#/$defs/EditorialPlan"
        }
      },
      "required": [
        "task_id",
        "editorial_plan"
      ],
      "title": "SubmitEditorialPlanInput",
      "type": "object"
    },
    "submit_headlinesInput": {
      "$defs": {
        "HeadlineCandidate": {
          "additionalProperties": false,
          "properties": {
            "title": {
              "minLength": 1,
              "title": "Title",
              "type": "string"
            },
            "angle": {
              "minLength": 1,
              "title": "Angle",
              "type": "string"
            },
            "finance_relevance": {
              "minLength": 1,
              "title": "Finance Relevance",
              "type": "string"
            },
            "factual_anchor": {
              "minLength": 1,
              "title": "Factual Anchor",
              "type": "string"
            },
            "primary_gap": {
              "minLength": 1,
              "title": "Primary Gap",
              "type": "string"
            },
            "opening_payoff": {
              "minLength": 1,
              "title": "Opening Payoff",
              "type": "string"
            },
            "cognitive_load": {
              "enum": [
                "low",
                "medium",
                "high"
              ],
              "title": "Cognitive Load",
              "type": "string"
            }
          },
          "required": [
            "title",
            "angle",
            "finance_relevance",
            "factual_anchor",
            "primary_gap",
            "opening_payoff",
            "cognitive_load"
          ],
          "title": "HeadlineCandidate",
          "type": "object"
        },
        "HeadlinePackage": {
          "additionalProperties": false,
          "properties": {
            "finance_deep_candidates": {
              "items": {
                "$ref": "#/$defs/HeadlineCandidate"
              },
              "title": "Finance Deep Candidates",
              "type": "array"
            },
            "finance_broad_candidates": {
              "items": {
                "$ref": "#/$defs/HeadlineCandidate"
              },
              "title": "Finance Broad Candidates",
              "type": "array"
            },
            "finance_deep_selected": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Finance Deep Selected"
            },
            "finance_broad_selected": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Finance Broad Selected"
            },
            "wechat_sticker_candidates": {
              "items": {
                "$ref": "#/$defs/HeadlineCandidate"
              },
              "title": "Wechat Sticker Candidates",
              "type": "array"
            },
            "wechat_sticker_selected": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Wechat Sticker Selected"
            }
          },
          "title": "HeadlinePackage",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "headlines": {
          "$ref": "#/$defs/HeadlinePackage"
        }
      },
      "required": [
        "task_id",
        "headlines"
      ],
      "title": "SubmitHeadlinesInput",
      "type": "object"
    },
    "submit_draftInput": {
      "$defs": {
        "ArticleBlock": {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "enum": [
                "lead",
                "h1",
                "h2",
                "h3",
                "body"
              ],
              "title": "Kind",
              "type": "string"
            },
            "text": {
              "minLength": 1,
              "title": "Text",
              "type": "string"
            }
          },
          "required": [
            "kind",
            "text"
          ],
          "title": "ArticleBlock",
          "type": "object"
        },
        "ArticlePayload": {
          "additionalProperties": false,
          "properties": {
            "title": {
              "minLength": 1,
              "title": "Title",
              "type": "string"
            },
            "blocks": {
              "items": {
                "$ref": "#/$defs/ArticleBlock"
              },
              "minItems": 3,
              "title": "Blocks",
              "type": "array"
            },
            "risk_disclaimer": {
              "minLength": 60,
              "title": "Risk Disclaimer",
              "type": "string"
            },
            "stock_names": {
              "items": {
                "type": "string"
              },
              "title": "Stock Names",
              "type": "array"
            }
          },
          "required": [
            "title",
            "blocks",
            "risk_disclaimer"
          ],
          "title": "ArticlePayload",
          "type": "object"
        },
        "DraftPackage": {
          "additionalProperties": false,
          "properties": {
            "finance_deep": {
              "anyOf": [
                {
                  "$ref": "#/$defs/ArticlePayload"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            },
            "finance_broad": {
              "anyOf": [
                {
                  "$ref": "#/$defs/ArticlePayload"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            },
            "wechat_sticker_post": {
              "anyOf": [
                {
                  "$ref": "#/$defs/StickerPostPayload"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            }
          },
          "title": "DraftPackage",
          "type": "object"
        },
        "PlatformConstraintSnapshot": {
          "additionalProperties": false,
          "properties": {
            "platform": {
              "default": "微信贴图",
              "title": "Platform",
              "type": "string"
            },
            "verified_at": {
              "format": "date-time",
              "title": "Verified At",
              "type": "string"
            },
            "source_refs": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Source Refs",
              "type": "array"
            },
            "title_max_chars": {
              "anyOf": [
                {
                  "minimum": 1,
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Title Max Chars"
            },
            "body_max_chars": {
              "anyOf": [
                {
                  "minimum": 1,
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Body Max Chars"
            },
            "image_max_count": {
              "anyOf": [
                {
                  "minimum": 1,
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Image Max Count"
            },
            "notes": {
              "items": {
                "type": "string"
              },
              "title": "Notes",
              "type": "array"
            }
          },
          "required": [
            "verified_at",
            "source_refs"
          ],
          "title": "PlatformConstraintSnapshot",
          "type": "object"
        },
        "StickerPostPayload": {
          "additionalProperties": false,
          "properties": {
            "title": {
              "minLength": 1,
              "title": "Title",
              "type": "string"
            },
            "body": {
              "minLength": 1,
              "title": "Body",
              "type": "string"
            },
            "interaction_prompt": {
              "default": "",
              "title": "Interaction Prompt",
              "type": "string"
            },
            "risk_disclaimer": {
              "minLength": 60,
              "title": "Risk Disclaimer",
              "type": "string"
            },
            "constraints": {
              "$ref": "#/$defs/PlatformConstraintSnapshot"
            },
            "stock_names": {
              "items": {
                "type": "string"
              },
              "title": "Stock Names",
              "type": "array"
            }
          },
          "required": [
            "title",
            "body",
            "risk_disclaimer",
            "constraints"
          ],
          "title": "StickerPostPayload",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "draft": {
          "$ref": "#/$defs/DraftPackage"
        }
      },
      "required": [
        "task_id",
        "draft"
      ],
      "title": "SubmitDraftInput",
      "type": "object"
    },
    "submit_style_auditInput": {
      "$defs": {
        "StyleAuditDecision": {
          "additionalProperties": false,
          "properties": {
            "status": {
              "enum": [
                "PASS",
                "REVISE"
              ],
              "title": "Status",
              "type": "string"
            },
            "evidence": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Evidence",
              "type": "array"
            },
            "rubric": {
              "$ref": "#/$defs/StyleAuditRubric"
            },
            "detected_patterns": {
              "items": {
                "type": "string"
              },
              "title": "Detected Patterns",
              "type": "array"
            },
            "transition_findings": {
              "items": {
                "type": "string"
              },
              "title": "Transition Findings",
              "type": "array"
            },
            "extreme_language_findings": {
              "items": {
                "type": "string"
              },
              "title": "Extreme Language Findings",
              "type": "array"
            },
            "revision_notes": {
              "items": {
                "type": "string"
              },
              "title": "Revision Notes",
              "type": "array"
            }
          },
          "required": [
            "status",
            "evidence",
            "rubric"
          ],
          "title": "StyleAuditDecision",
          "type": "object"
        },
        "StyleAuditRubric": {
          "additionalProperties": false,
          "properties": {
            "template_fingerprint": {
              "enum": [
                "PASS",
                "REVISE"
              ],
              "title": "Template Fingerprint",
              "type": "string"
            },
            "transition_continuity": {
              "enum": [
                "PASS",
                "REVISE"
              ],
              "title": "Transition Continuity",
              "type": "string"
            },
            "repetition_control": {
              "enum": [
                "PASS",
                "REVISE"
              ],
              "title": "Repetition Control",
              "type": "string"
            },
            "rhythm_naturalness": {
              "enum": [
                "PASS",
                "REVISE"
              ],
              "title": "Rhythm Naturalness",
              "type": "string"
            },
            "extreme_language_control": {
              "enum": [
                "PASS",
                "REVISE"
              ],
              "title": "Extreme Language Control",
              "type": "string"
            }
          },
          "required": [
            "template_fingerprint",
            "transition_continuity",
            "repetition_control",
            "rhythm_naturalness",
            "extreme_language_control"
          ],
          "title": "StyleAuditRubric",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "report": {
          "$ref": "#/$defs/StyleAuditDecision"
        }
      },
      "required": [
        "task_id",
        "report"
      ],
      "title": "SubmitStyleAuditInput",
      "type": "object"
    },
    "submit_editorial_auditInput": {
      "$defs": {
        "GateDecision": {
          "additionalProperties": false,
          "properties": {
            "status": {
              "enum": [
                "PASS",
                "REVISE",
                "FAIL"
              ],
              "title": "Status",
              "type": "string"
            },
            "evidence": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Evidence",
              "type": "array"
            },
            "defects": {
              "items": {
                "type": "string"
              },
              "title": "Defects",
              "type": "array"
            },
            "revision_target": {
              "anyOf": [
                {
                  "enum": [
                    "RESEARCH",
                    "EDITORIAL",
                    "TITLE",
                    "DRAFT",
                    "DELIVERY"
                  ],
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Revision Target"
            },
            "remaining_boundaries": {
              "items": {
                "type": "string"
              },
              "title": "Remaining Boundaries",
              "type": "array"
            }
          },
          "required": [
            "status",
            "evidence"
          ],
          "title": "GateDecision",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "decision": {
          "$ref": "#/$defs/GateDecision"
        }
      },
      "required": [
        "task_id",
        "decision"
      ],
      "title": "SubmitEditorialAuditInput",
      "type": "object"
    },
    "submit_visual_packageInput": {
      "$defs": {
        "OpenAIFileRef": {
          "additionalProperties": false,
          "properties": {
            "download_url": {
              "minLength": 1,
              "title": "Download Url",
              "type": "string"
            },
            "file_id": {
              "minLength": 1,
              "title": "File Id",
              "type": "string"
            },
            "mime_type": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Mime Type"
            },
            "file_name": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "File Name"
            }
          },
          "required": [
            "download_url",
            "file_id"
          ],
          "title": "OpenAIFileRef",
          "type": "object"
        },
        "VisualAsset": {
          "additionalProperties": false,
          "properties": {
            "article_mode": {
              "enum": [
                "FINANCE_DEEP",
                "FINANCE_BROAD",
                "WECHAT_STICKER_POST"
              ],
              "title": "Article Mode",
              "type": "string"
            },
            "role": {
              "enum": [
                "hero",
                "section",
                "sticker"
              ],
              "title": "Role",
              "type": "string"
            },
            "semantic_focus": {
              "minLength": 1,
              "title": "Semantic Focus",
              "type": "string"
            },
            "file_id": {
              "minLength": 1,
              "title": "File Id",
              "type": "string"
            },
            "anchor_after_block": {
              "anyOf": [
                {
                  "minimum": 0,
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Anchor After Block"
            },
            "hook_text": {
              "default": "",
              "title": "Hook Text",
              "type": "string"
            },
            "aspect_ratio": {
              "minLength": 3,
              "title": "Aspect Ratio",
              "type": "string"
            },
            "avatar_included": {
              "default": true,
              "title": "Avatar Included",
              "type": "boolean"
            }
          },
          "required": [
            "article_mode",
            "role",
            "semantic_focus",
            "file_id",
            "aspect_ratio"
          ],
          "title": "VisualAsset",
          "type": "object"
        },
        "VisualPackage": {
          "additionalProperties": false,
          "properties": {
            "assets": {
              "items": {
                "$ref": "#/$defs/VisualAsset"
              },
              "minItems": 1,
              "title": "Assets",
              "type": "array"
            },
            "avatar_required": {
              "default": true,
              "title": "Avatar Required",
              "type": "boolean"
            },
            "target_chars_per_section_image": {
              "default": 700,
              "maximum": 2000,
              "minimum": 200,
              "title": "Target Chars Per Section Image",
              "type": "integer"
            },
            "planning_notes": {
              "items": {
                "type": "string"
              },
              "title": "Planning Notes",
              "type": "array"
            }
          },
          "required": [
            "assets"
          ],
          "title": "VisualPackage",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "visual_package": {
          "$ref": "#/$defs/VisualPackage"
        },
        "files": {
          "description": "ChatGPT-authorized generated/uploaded image file parameters referenced by file_id.",
          "items": {
            "$ref": "#/$defs/OpenAIFileRef"
          },
          "minItems": 1,
          "title": "Files",
          "type": "array"
        }
      },
      "required": [
        "task_id",
        "visual_package",
        "files"
      ],
      "title": "SubmitVisualPackageInput",
      "type": "object"
    },
    "build_and_mechanically_audit_deliveryInput": {
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        }
      },
      "required": [
        "task_id"
      ],
      "title": "BuildAndMechanicallyAuditDeliveryInput",
      "type": "object"
    },
    "record_knowledge_writebackInput": {
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "status": {
          "enum": [
            "PASS",
            "N_A"
          ],
          "title": "Status",
          "type": "string"
        },
        "refs": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Actual durable-store receipt references when writeback succeeded.",
          "title": "Refs"
        },
        "notes": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Reason/boundary notes; required by the runtime for N_A.",
          "title": "Notes"
        }
      },
      "required": [
        "task_id",
        "status"
      ],
      "title": "RecordKnowledgeWritebackInput",
      "type": "object"
    },
    "submit_final_auditInput": {
      "$defs": {
        "FinalAuditDecision": {
          "additionalProperties": false,
          "properties": {
            "status": {
              "enum": [
                "PASS",
                "REVISE",
                "FAIL"
              ],
              "title": "Status",
              "type": "string"
            },
            "evidence": {
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "title": "Evidence",
              "type": "array"
            },
            "defects": {
              "items": {
                "type": "string"
              },
              "title": "Defects",
              "type": "array"
            },
            "revision_target": {
              "anyOf": [
                {
                  "enum": [
                    "RESEARCH",
                    "EDITORIAL",
                    "TITLE",
                    "DRAFT",
                    "DELIVERY"
                  ],
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Revision Target"
            },
            "remaining_boundaries": {
              "items": {
                "type": "string"
              },
              "title": "Remaining Boundaries",
              "type": "array"
            },
            "acceptance_evidence": {
              "items": {
                "type": "string"
              },
              "title": "Acceptance Evidence",
              "type": "array"
            },
            "reviewed_render_pages": {
              "items": {
                "type": "string"
              },
              "title": "Reviewed Render Pages",
              "type": "array"
            }
          },
          "required": [
            "status",
            "evidence"
          ],
          "title": "FinalAuditDecision",
          "type": "object"
        }
      },
      "additionalProperties": false,
      "properties": {
        "task_id": {
          "minLength": 1,
          "title": "Task Id",
          "type": "string"
        },
        "decision": {
          "$ref": "#/$defs/FinalAuditDecision"
        }
      },
      "required": [
        "task_id",
        "decision"
      ],
      "title": "SubmitFinalAuditInput",
      "type": "object"
    }
  },
  "tools": [
    {
      "name": "start_writing_task",
      "title": "Start financial writing task",
      "description": "Create a new persisted writing workflow. Use only for a genuinely new publishable finance-writing task after ruling out a relevant unfinished task.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "start_writing_taskInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "get_writing_task",
      "title": "Get writing task",
      "description": "Read one persisted writing task without changing it. Use after task listing or when an exact task ID is already known.",
      "annotations": {
        "readOnlyHint": true,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": true
      },
      "meta": {},
      "inputSchemaRef": "get_writing_taskInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "resume_writing_task",
      "title": "Resume blocked writing task",
      "description": "Resume only a BLOCKED task after its external dependency or contract defect has been repaired. The runtime chooses the recorded original stage; callers cannot skip to an arbitrary stage.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "resume_writing_taskInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "list_recent_writing_tasks",
      "title": "List recent writing tasks",
      "description": "List recent persisted writing tasks for reliable continuation. Read-only and intended to prevent starting duplicate workflows or asking the user to repeat context.",
      "annotations": {
        "readOnlyHint": true,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": true
      },
      "meta": {},
      "inputSchemaRef": "list_recent_writing_tasksInput",
      "outputSchemaRef": "WritingTaskList"
    },
    {
      "name": "record_knowledge_context",
      "title": "Record durable knowledge recall outcome",
      "description": "Close the pre-research durable-knowledge recall gate. PASS requires real retrieved references; N_A requires an explicit reason. This prevents silently skipping connected prior knowledge.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "record_knowledge_contextInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_research",
      "title": "Submit research package",
      "description": "Validate and freeze the complete ResearchPackage at RESEARCH after the knowledge-context PASS/N_A decision, including auditable evidence verification, broad/deep cognition, review-queue receipts and bounded coverage.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "submit_researchInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_research_audit",
      "title": "Submit research audit",
      "description": "Record the independent research-audit verdict. PASS advances, REVISE must target RESEARCH, and FAIL blocks the persisted workflow.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "submit_research_auditInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_editorial_plan",
      "title": "Submit editorial plan",
      "description": "Validate TopicDNA and independent mode-specific candidate structures at EDITORIAL, including focus, company-selection basis and outline-collision evidence.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "submit_editorial_planInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_headlines",
      "title": "Submit headline package",
      "description": "Validate unique candidate headline sets, factual anchors, opening-payoff design and selected-title membership, then freeze the article acceptance contract.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "submit_headlinesInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_draft",
      "title": "Submit draft package",
      "description": "Validate every required draft against the frozen acceptance contract, including independent lead placement, selected title and frozen H1 structure.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "submit_draftInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_style_audit",
      "title": "Submit style audit",
      "description": "Record the independent anti-AI/style rubric at EDITORIAL_AUDIT. This gate must pass before the general editorial audit may pass.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "submit_style_auditInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_editorial_audit",
      "title": "Submit editorial audit",
      "description": "Record the independent semantic editorial verdict. PASS requires a passed style gate; REVISE may target TITLE or DRAFT and invalidates stale downstream checks.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "submit_editorial_auditInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_visual_package",
      "title": "Submit publication visuals",
      "description": "Accept authorized image file parameters at DELIVERY, validate mode/count/ratio/avatar requirements, safely copy bytes into task storage and record the visual gate.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {
        "openai/fileParams": [
          "files"
        ]
      },
      "inputSchemaRef": "submit_visual_packageInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "build_and_mechanically_audit_delivery",
      "title": "Build and mechanically audit delivery",
      "description": "Build required publication artifacts, run deterministic Word/render checks, and return both final-artifact links and page-render resources for visual inspection.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "build_and_mechanically_audit_deliveryInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "record_knowledge_writeback",
      "title": "Record knowledge writeback outcome",
      "description": "Record the explicit durable-knowledge writeback decision at FINAL_AUDIT. PASS needs real receipts; N_A needs an explicit reason; core writing can continue without an external store.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "record_knowledge_writebackInput",
      "outputSchemaRef": "WritingTaskSummary"
    },
    {
      "name": "submit_final_audit",
      "title": "Submit final audit",
      "description": "Record the final red-team verdict. PASS requires criterion-keyed acceptance evidence, explicit knowledge-sync status and an exact list of every rendered page actually inspected.",
      "annotations": {
        "readOnlyHint": false,
        "destructiveHint": false,
        "openWorldHint": false,
        "idempotentHint": false
      },
      "meta": {},
      "inputSchemaRef": "submit_final_auditInput",
      "outputSchemaRef": "WritingTaskSummary"
    }
  ],
  "resources": [
    {
      "uriTemplate": "writing-docx://{task_id}/{kind}",
      "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    },
    {
      "uriTemplate": "writing-json://{task_id}/{kind}",
      "mimeType": "application/json"
    },
    {
      "uriTemplate": "writing-text://{task_id}/{kind}",
      "mimeType": "text/plain; charset=utf-8"
    },
    {
      "uriTemplate": "writing-render://{task_id}/{kind}/{page}",
      "mimeType": "image/png"
    }
  ]
} as const;
