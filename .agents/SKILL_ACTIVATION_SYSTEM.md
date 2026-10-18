# SKILL ACTIVATION SYSTEM

## Purpose

Automatic skill activation system that ensures all relevant skills are loaded and applied based on task scope and system context, without requiring explicit user invocation.

## Auto-Activation Rules

### 1. Mandatory Skills (Always Active)

These skills are automatically activated at the start of every AI session:

- `global-master-prompt-rules` (G-18) - Absolute governance rules
- `index-prompt` (G-00) - Mandatory entry point
- `prompt-activation-policy` (G-13) - Role activation policy
- `prompt-command-center` (G-CC) - Command orchestration

### 2. Professional Role Skills (Context-Based)

These skills are automatically activated based on task domain signals:

| Signal | Skills to Activate |
|--------|-------------------|
| Architecture, design, structure | `backend-architect`, `senior-architect`, `cloud-architect`, `architecture`, `architecture-patterns`, `architecture-decision-records`, `c4-architecture-c4-architecture`, `c4-code`, `c4-component`, `c4-container`, `c4-context` |
| Code implementation, development | `python-pro`, `code-reviewer`, `code-review-and-quality`, `code-simplification`, `javascript-pro`, `golang-pro`, `java-pro`, `cpp-pro`, `csharp-pro`, `typescript-pro`, `ruby-pro`, `rust-pro`, `elixir-pro`, `haskell-pro`, `julia-pro`, `php-pro`, `django-pro`, `fastapi-pro`, `dotnet-architect`, `dotnet-backend-patterns` |
| Network, topology, VPC | `network-engineer`, `hybrid-cloud-networking`, `multi-cloud-architecture`, `hybrid-cloud-architect` |
| Database, SQL, storage | `database-admin`, `database-architect`, `postgresql`, `database-design`, `database-migrations-sql-migrations`, `database-migrations-migration-observability`, `database-optimizer`, `database-cloud-optimization-cost-optimize`, `dbt-transformation-patterns`, `nosql-expert` |
| Security, authentication, secrets | `security-auditor`, `security-and-hardening`, `backend-security-coder`, `frontend-security-coder`, `mobile-security-coder`, `container-security-hardening`, `api-security-best-practices`, `api-security-testing`, `gdpr-data-handling`, `pci-compliance` |
| Product, strategy, features | `product-manager`, `product-inventor`, `business-analyst`, `competitive-landscape`, `market-sizing-analysis` |
| API design, endpoints | `api-design-principles`, `api-patterns`, `api-documenter`, `api-testing-observability-api-mock`, `openapi-spec-generation` |
| DevOps, CI/CD, deployment | `deployment-engineer`, `deployment-pipeline-design`, `cicd-automation-workflow-automate`, `ci-cd-and-automation`, `docker-expert`, `kubernetes-architect`, `kubernetes-deployment`, `k8s-manifest-generator`, `k8s-security-policies`, `helm-chart-scaffolding`, `terraform-specialist`, `gitops-workflow`, `github-actions-templates`, `gitlab-ci-patterns` |
| Testing, QA | `e2e-testing`, `e2e-testing-patterns`, `javascript-testing-patterns`, `python-testing-patterns`, `test-driven-development`, `code-review-ai-ai-review`, `code-review-excellence`, `comprehensive-review-full-review`, `comprehensive-review-pr-enhance` |
| Performance, optimization | `performance-optimizer`, `performance-profiling`, `application-performance-performance-optimization`, `cost-optimization`, `aws-cost-optimizer` |
| Observability, monitoring | `observability-engineer`, `observability-and-instrumentation`, `observability-monitoring-monitor-setup`, `observability-monitoring-slo-implement`, `distributed-tracing`, `prometheus-configuration`, `grafana-dashboards` |
| Data, ML, AI | `data-engineer`, `data-scientist`, `data-engineering-data-driven-feature`, `data-engineering-data-pipeline`, `data-quality-frameworks`, `ml-engineer`, `ml-pipeline-workflow`, `mlops-engineer`, `machine-learning-ops-ml-pipeline`, `ai-engineer`, `llm-application-dev-ai-assistant`, `llm-application-dev-langchain-agent`, `llm-application-dev-prompt-optimize`, `llm-evaluation`, `llm-ops`, `llm-prompt-optimizer`, `llm-structured-output`, `llm-app-patterns`, `rag-engineer`, `rag-implementation`, `hybrid-search-implementation`, `vector-database-engineer`, `vector-index-tuning` |
| Frontend, UI, UX | `frontend-developer`, `frontend-ui-engineering`, `frontend-mobile-development-component-scaffold`, `react-best-practices`, `react-patterns`, `react-state-management`, `angular`, `angular-best-practices`, `vue`, `flutter-expert`, `ios-developer`, `android-dev` |
| Microservices, distributed systems | `microservices-patterns`, `monorepo-architect`, `monorepo-management`, `service-mesh-expert`, `service-mesh-observability`, `istio-traffic-management`, `linkerd-patterns`, `event-sourcing-architect`, `event-store-design`, `cqrs-implementation`, `saga-orchestration`, `domain-driven-design`, `ddd-context-mapping`, `ddd-strategic-design`, `ddd-tactical-patterns` |
| Cloud, infrastructure | `cloud-architect`, `aws-skills`, `aws-serverless`, `aws-cost-optimizer`, `cloudformation-best-practices`, `cdk-patterns`, `azure-ai-projects-py`, `azure-ai-projects-java`, `azure-ai-projects-dotnet`, `azure-ai-projects-ts`, `gcp-cloud-run` |
| Debugging, troubleshooting | `debugger`, `debugging-strategies`, `debugging-toolkit-smart-debug`, `debugging-and-error-recovery`, `error-debugging-error-analysis`, `error-debugging-error-trace`, `error-debugging-multi-agent-review`, `error-detective`, `error-diagnostics-error-analysis`, `error-diagnostics-error-trace`, `error-diagnostics-smart-debug`, `error-handling-patterns`, `devops-troubleshooter`, `distributed-debugging-debug-trace` |
| Documentation, ADRs | `documentation-and-adrs`, `docs-architect`, `documentation-generation-doc-generate`, `code-documentation-code-explain`, `code-documentation-doc-generate` |
| Git, version control | `git-workflow-and-versioning`, `git-advanced-workflows`, `git-pr-workflows-git-workflow`, `git-pr-workflows-onboard`, `git-pr-workflows-pr-enhance`, `git-pushing` |
| Context management | `context-engineering`, `context-driven-development`, `context-management-context-restore`, `context-management-context-save`, `context-manager`, `context-optimization`, `context-window-management` |
| Planning, task breakdown | `planning-and-task-breakdown`, `incremental-implementation`, `spec-driven-development`, `source-driven-development`, `idea-refine` |
| Incident response | `incident-responder`, `incident-response-incident-response`, `incident-response-smart-fix`, `incident-runbook-templates` |
| Legacy modernization | `legacy-modernizer`, `framework-migration-code-migrate`, `framework-migration-deps-upgrade`, `framework-migration-legacy-modernize` |
| Dependency management | `dependency-management-deps-audit`, `dependency-upgrade`, `codebase-cleanup-deps-audit`, `codebase-cleanup-tech-debt` |
| Refactoring | `code-refactoring-context-restore`, `code-refactoring-refactor-clean`, `code-refactoring-tech-debt`, `codebase-cleanup-refactor-clean` |
| Blockchain, Web3 | `blockchain-developer`, `defi-protocol-templates`, `nft-standards`, `web3-testing` |
| Mobile development | `mobile-developer`, `mobile-security-coder`, `flutter-expert`, `ios-developer`, `android-dev`, `react-native-architecture`, `react-native-skills` |
| Embedded systems | `arm-cortex-expert`, `firmware-analyst`, `memory-forensics`, `memory-safety-patterns` |
| Reverse engineering | `reverse-engineer`, `anti-reversing-techniques`, `protocol-reverse-engineering`, `binary-analysis-patterns` |
| Threat modeling | `threat-modeling-expert`, `threat-mitigation-mapping`, `attack-tree-construction`, `stride-analysis-patterns` |
| Compliance | `gdpr-data-handling`, `pci-compliance`, `security-compliance-compliance-check`, `security-requirement-extraction` |
| SEO | `seo-authority-builder`, `seo-cannibalization-detector`, `seo-content-auditor`, `seo-content-planner`, `seo-content-refresher`, `seo-content-writer`, `seo-keyword-strategist`, `seo-meta-optimizer`, `seo-snippet-hunter`, `seo-structure-architect` |
| Startup | `startup-analyst`, `startup-business-analyst-business-case`, `startup-business-analyst-financial-projections`, `startup-business-analyst-market-opportunity`, `startup-financial-modeling`, `startup-metrics-framework` |
| Game development | `game-development`, `godot-gdscript-patterns`, `unity-developer`, `unity-ecs-patterns`, `minecraft-bukkit-pro` |
| Data science | `data-scientist`, `data-storytelling`, `quant-analyst`, `backtesting-frameworks` |
| Automation | `billing-automation`, `changelog-automation`, `github-automation`, `gitlab-automation`, `jira-automation`, `confluence-automation`, `notion-automation` |
| Workflow orchestration | `workflow-orchestration-patterns`, `workflow-patterns`, `conductor-implement`, `conductor-manage`, `conductor-new-track`, `conductor-revert`, `conductor-setup`, `conductor-status`, `conductor-validator` |
| Async programming | `async-python-patterns`, `go-concurrency-patterns`, `rust-async-patterns`, `fp-async` |
| Functional programming | `fp-backend`, `fp-data-transforms`, `fp-either-ref`, `fp-errors`, `fp-option-ref`, `fp-pipe-ref`, `fp-pragmatic`, `fp-react`, `fp-refactor`, `fp-taskeither-ref`, `fp-ts-errors`, `fp-ts-pragmatic`, `fp-ts-react`, `fp-types-ref` |
| Testing patterns | `bats-testing-patterns`, `javascript-testing-patterns`, `python-testing-patterns`, `e2e-testing-patterns`, `testing-patterns` |
| Build systems | `bazel-build-optimization`, `make-automation`, `nx-workspace-patterns`, `turborepo-caching` |
| Package management | `python-packaging`, `uv-package-manager` |
| Temporal workflows | `temporal-python-pro`, `temporal-python-testing` |
| Search | `search-specialist`, `similarity-search-patterns`, `hybrid-search-implementation` |
| Secrets management | `secrets-management`, `mtls-configuration` |
| SLOs | `slo-implementation`, `observability-monitoring-slo-implement` |
| Screen reader | `screen-reader-testing` |
| Shell scripting | `bash-pro`, `bash-scripting`, `bash-linux`, `bash-defensive-patterns`, `posix-shell-pro` |
| SQL | `sql-pro`, `sql-optimization-patterns`, `postgresql-optimization` |
| Spark | `spark-optimization` |
| Solidity | `solidity-security` |
| SAST | `sast-configuration`, `security-scanning-security-sast` |
| Shellcheck | `shellcheck-configuration` |
| TDD | `tdd-orchestrator`, `tdd-workflows-tdd-cycle`, `tdd-workflows-tdd-green`, `tdd-workflows-tdd-red`, `tdd-workflows-tdd-refactor` |
| Team collaboration | `team-collaboration-issue`, `team-collaboration-standup-notes`, `team-composition-analysis` |
| Tutorial | `tutorial-engineer` |
| UI/UX | `ui-ux-designer`, `ui-visual-validator`, `design-taste-frontend`, `high-end-visual-design` |
| Unit testing | `unit-testing-test-generate`, `test-automator` |
| Validation | `deployment-validation-config-validate`, `lint-and-validate` |
| Vector database | `vector-database-engineer`, `vector-index-tuning` |
| WCAG | `wcag-audit-patterns` |
| Workflows | `workflow-orchestration-patterns`, `workflow-patterns` |

### 3. Special Skills (Context-Based)

| Signal | Skills to Activate |
|--------|-------------------|
| Innovation, first principles, disruption | `elon-musk` |
| Product thinking, design systems | `product-inventor` |

### 4. Integration with docs/13-master-prompts

The system automatically integrates with the existing master prompt framework:

- Council roles from `docs/13-master-prompts/roles/combined/`
- Domain specialists from `docs/13-master-prompts/roles/`
- Policies from `docs/13-master-prompts/` (G-03 through G-11)

### 5. Dependency Chain Enforcement

When multiple skills are activated, they are coordinated in dependency order:

```
RESYNC (global-master-prompt-rules)
→ Product Strategist (product-manager, product-inventor) [when scope changes]
→ System Architect (backend-architect, senior-architect, cloud-architect)
→ Lead Developer (python-pro)
→ QA Engineer (code-reviewer)
→ Security Reviewer (security-auditor)
→ Observability Engineer
→ Documentation Steward
→ Release Manager
→ Prompt Librarian
```

### 6. Auto-Activation Triggers

The system automatically activates skills based on:

1. **Task keywords** - Words in the user's request
2. **File context** - Files being modified or viewed
3. **Project context** - Current project state and structure
4. **Domain signals** - Technical domain indicators
5. **Previous context** - Conversation history and previous actions

### 7. Escalation Rules

- **Unresolved conflicts** → Escalate to Team Meeting Council
- **Role relevance uncertain** → Err on the side of inclusion
- **Multiple applicable skills** → Activate all relevant skills in dependency order

## Implementation

### Skill Loading Order

1. Load mandatory skills (always active)
2. Analyze task context for signals
3. Activate relevant professional role skills
4. Activate relevant special skills
5. Integrate with docs/13-master-prompts council roles
6. Coordinate in dependency order
7. Create action log for activation
8. Trigger automatic task completion workflow

### Self-Improvement System

All skills are equipped with self-improvement capabilities:

#### Periodic Web Search
Each skill periodically (every 7 days):
- Searches the web for latest best practices in its domain
- Updates its knowledge base with new information
- Improves its prompts and guidelines
- Stays current with industry standards

#### Automatic Knowledge Updates
- Skills monitor relevant GitHub repositories for updates
- Skills track official documentation changes
- Skills learn from community best practices
- Skills adapt to new tools and frameworks

#### Self-Validation
- Skills validate their own recommendations
- Skills check for outdated practices
- Skills flag potential improvements
- Skills request updates when needed

### Automatic Task Completion

After any task execution, the system automatically performs documentation updates, version management, quality assurance, build & release, and communication.

See `.devin/workflows/automatic-task-completion.md` for detailed automatic task completion workflow.

### Skill Activation API

```python
def activate_skills(task_context, file_context, project_context):
    """
    Automatically activate all relevant skills based on context.
    
    Args:
        task_context: User's request and task description
        file_context: Files being modified or viewed
        project_context: Current project state and structure
    
    Returns:
        List of activated skills in dependency order
    """
    # 1. Load mandatory skills
    activated = load_mandatory_skills()
    
    # 2. Analyze task context for signals
    signals = analyze_task_signals(task_context)
    
    # 3. Activate relevant professional role skills
    for signal in signals:
        skills = get_skills_for_signal(signal)
        activated.extend(skills)
    
    # 4. Activate relevant special skills
    special_skills = get_special_skills(task_context)
    activated.extend(special_skills)
    
    # 5. Integrate with docs/13-master-prompts
    council_roles = get_council_roles(task_context)
    activated.extend(council_roles)
    
    # 6. Coordinate in dependency order
    activated = order_by_dependency(activated)
    
    # 7. Create action log
    log_skill_activation(activated)
    
    return activated
```

## Configuration

### Skill Registry

All available skills are registered in `.devin/skills/` with metadata:

- `SKILL.md` - Main skill definition
- `references/` - Supporting documentation
- `examples/` - Usage examples (if available)
- `scripts/` - Helper scripts (if available)

### Activation Rules

Activation rules are defined in each skill's `SKILL.md` file:

- `auto_activation` - Whether skill should be auto-activated
- `activation_triggers` - Keywords and signals that trigger activation
- `dependencies` - Skills that must be activated before this skill
- `priority` - Activation priority (higher = activated first)

## Testing

### Validation

The skill activation system is validated by:

1. **Unit tests** - Test individual skill activation logic
2. **Integration tests** - Test skill activation with various contexts
3. **End-to-end tests** - Test complete skill activation workflows

### Monitoring

Skill activation is logged for:

- Which skills were activated
- Why they were activated (triggers)
- In what order they were activated
- Any conflicts or escalations

## Maintenance

### Adding New Skills

To add a new skill:

1. Create skill directory in `.devin/skills/`
2. Create `SKILL.md` with proper metadata
3. Define activation triggers and dependencies
4. Add to skill registry
5. Test activation logic

### Updating Skills

To update an existing skill:

1. Modify `SKILL.md` with changes
2. Update activation triggers if needed
3. Update dependencies if needed
4. Test activation logic
5. Update skill registry

## Related Documentation

- `.devin/DOCUMENTATION_STRUCTURE.md` - Documentation structure and single source of truth
- `.devin/SKILL_TEMPLATE.md` - Standard skill template
- `.devin/workflows/automatic-task-completion.md` - Automatic task completion workflow (primary source)
- `.devin/workflows/ai-ide-automation.md` - AI IDE automation workflow (primary source)
- `docs/skill-improvement-process.md` - Skill improvement process (primary source)
- `docs/rebuilt-1-1/automatic-processes.md` - Automatic processes documentation (1:1 rebuild context)
- `docs/13-master-prompts/INDEX_PROMPT.md` (G-00)
- `docs/13-master-prompts/PROMPT_ACTIVATION_POLICY.md` (G-13)
- `docs/13-master-prompts/PROMPT_COMMAND_CENTER.md` (G-CC)
- `docs/13-master-prompts/ROLE_MATRIX.md` (G-04)
