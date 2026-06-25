# .devin - AI-IDE Skill Library

## Purpose

This directory contains the comprehensive skill library for the Network Swiss Tool Pro project. It integrates skills from multiple sources:

- **Local master prompts** from `docs/13-master-prompts/`
- **Antigravity Awesome Skills** from https://github.com/sickn33/antigravity-awesome-skills.git
- **Claude Skills** from https://github.com/alirezarezvani/claude-skills.git
- **Claude Code Prompts** from https://github.com/repowise-dev/claude-code-prompts.git
- **Awesome Cursor Skills** from https://github.com/spencerpauly/awesome-cursor-skills.git

## Structure

```
.devin/
├── skills/                    # Skill definitions
│   ├── global-master-prompt-rules/    # G-18: Absolute governance rules
│   ├── index-prompt/                  # G-00: Mandatory entry point
│   ├── prompt-activation-policy/      # G-13: Role activation policy
│   ├── prompt-command-center/         # G-CC: Command orchestration
│   ├── elon-musk/                     # Innovation and first principles thinking
│   ├── product-manager/               # Product management skills
│   ├── product-inventor/              # Product thinking and design systems
│   ├── backend-architect/            # Backend architecture skills
│   ├── senior-architect/              # Senior architecture skills
│   ├── cloud-architect/              # Cloud architecture skills
│   ├── python-pro/                   # Python development expertise
│   ├── network-engineer/             # Network engineering skills
│   ├── database-admin/               # Database administration
│   ├── database-architect/           # Database architecture
│   ├── postgresql/                   # PostgreSQL expertise
│   ├── security-auditor/             # Security auditing
│   ├── code-reviewer/                # Code review expertise
│   └── api-design-principles/        # API design best practices
├── agents/                    # Agent definitions
│   └── antigravity-agents/           # Agents from antigravity-awesome-skills
├── plugins/                   # Plugin definitions
│   └── antigravity-plugins/          # Plugins from antigravity-awesome-skills
├── workflows/                 # Workflow definitions
├── scripts/                   # Helper scripts
│   ├── antigravity-scripts/           # Scripts from antigravity-awesome-skills
│   └── antigravity-tools/             # Tools from antigravity-awesome-skills
├── SKILL_ACTIVATION_SYSTEM.md  # Automatic skill activation system
└── README.md                  # This file
```

## Automatic Skill Activation

All skills are automatically activated based on task scope and system context, as defined in `SKILL_ACTIVATION_SYSTEM.md`. The system ensures:

1. **Mandatory skills** are always active (global-master-prompt-rules, index-prompt, prompt-activation-policy, prompt-command-center)
2. **Professional role skills** are activated based on task domain signals
3. **Special skills** (like elon-musk) are activated when relevant
4. **Dependency chain** is enforced for proper coordination
5. **Escalation rules** handle conflicts and uncertainties

## Professional Roles

The skill library includes comprehensive skills for all professional roles involved in the project:

### Product & Strategy
- `product-manager` - Product management and strategy
- `product-inventor` - Product thinking, design systems, UI engineering
- `business-analyst` - Business analysis and requirements
- `competitive-landscape` - Competitive analysis and market research
- `market-sizing-analysis` - Market sizing and opportunity assessment

### Architecture & Design
- `backend-architect` - Backend architecture and API design
- `senior-architect` - Senior architecture and system design
- `cloud-architect` - Cloud infrastructure and multi-cloud architecture
- `api-design-principles` - REST and GraphQL API design principles
- `architecture` - General architecture patterns
- `architecture-patterns` - Architecture design patterns
- `architecture-decision-records` - ADR management
- `c4-architecture-c4-architecture` - C4 model architecture
- `c4-code` - C4 code level diagrams
- `c4-component` - C4 component diagrams
- `c4-container` - C4 container diagrams
- `c4-context` - C4 context diagrams

### Development (Languages)
- `python-pro` - Python 3.12+ with modern features and best practices
- `javascript-pro` - JavaScript mastery and best practices
- `golang-pro` - Go language expertise
- `java-pro` - Java development expertise
- `cpp-pro` - C++ programming expertise
- `csharp-pro` - C# development expertise
- `typescript-pro` - TypeScript advanced types
- `ruby-pro` - Ruby development expertise
- `rust-pro` - Rust programming expertise
- `elixir-pro` - Elixir development expertise
- `haskell-pro` - Haskell development expertise
- `julia-pro` - Julia development expertise
- `php-pro` - PHP development expertise
- `django-pro` - Django framework expertise
- `fastapi-pro` - FastAPI framework expertise
- `dotnet-architect` - .NET architecture
- `dotnet-backend-patterns` - .NET backend patterns

### Development (Frameworks & Tools)
- `react-best-practices` - React best practices
- `react-patterns` - React design patterns
- `react-state-management` - React state management
- `angular` - Angular framework
- `angular-best-practices` - Angular best practices
- `vue` - Vue.js framework
- `flutter-expert` - Flutter development
- `ios-developer` - iOS development
- `android-dev` - Android development
- `django-pro` - Django framework
- `fastapi-pro` - FastAPI framework

### Database & Data
- `database-admin` - Database administration and automation
- `database-architect` - Database architecture and schema design
- `postgresql` - PostgreSQL-specific schema and best practices
- `database-design` - Database design principles
- `database-migrations-sql-migrations` - SQL migrations
- `database-migrations-migration-observability` - Migration observability
- `database-optimizer` - Database optimization
- `database-cloud-optimization-cost-optimize` - Cloud database optimization
- `dbt-transformation-patterns` - DBT transformation patterns
- `nosql-expert` - NoSQL database expertise
- `data-engineer` - Data engineering
- `data-scientist` - Data science
- `data-engineering-data-driven-feature` - Data-driven features
- `data-engineering-data-pipeline` - Data pipelines
- `data-quality-frameworks` - Data quality
- `data-storytelling` - Data storytelling
- `ml-engineer` - Machine learning engineering
- `ml-pipeline-workflow` - ML pipelines
- `mlops-engineer` - MLOps engineering
- `machine-learning-ops-ml-pipeline` - ML operations

### Network & Infrastructure
- `network-engineer` - Network engineering and security architectures
- `hybrid-cloud-networking` - Hybrid cloud networking
- `multi-cloud-architecture` - Multi-cloud architecture
- `hybrid-cloud-architect` - Hybrid cloud architecture
- `cloud-architect` - Cloud architecture
- `aws-skills` - AWS expertise
- `aws-serverless` - AWS serverless
- `aws-cost-optimizer` - AWS cost optimization
- `cloudformation-best-practices` - CloudFormation best practices
- `cdk-patterns` - AWS CDK patterns
- `azure-ai-projects-py` - Azure AI Python
- `azure-ai-projects-java` - Azure AI Java
- `azure-ai-projects-dotnet` - Azure AI .NET
- `azure-ai-projects-ts` - Azure AI TypeScript
- `gcp-cloud-run` - GCP Cloud Run

### Security
- `security-auditor` - DevSecOps, comprehensive cybersecurity, compliance frameworks
- `security-and-hardening` - Security hardening
- `backend-security-coder` - Backend security
- `frontend-security-coder` - Frontend security
- `mobile-security-coder` - Mobile security
- `container-security-hardening` - Container security
- `api-security-best-practices` - API security
- `api-security-testing` - API security testing
- `gdpr-data-handling` - GDPR compliance
- `pci-compliance` - PCI compliance
- `threat-modeling-expert` - Threat modeling
- `threat-mitigation-mapping` - Threat mitigation
- `attack-tree-construction` - Attack trees
- `stride-analysis-patterns` - STRIDE analysis

### DevOps & CI/CD
- `deployment-engineer` - Deployment engineering
- `deployment-pipeline-design` - Pipeline design
- `cicd-automation-workflow-automate` - CI/CD automation
- `ci-cd-and-automation` - CI/CD and automation
- `docker-expert` - Docker expertise
- `kubernetes-architect` - Kubernetes architecture
- `kubernetes-deployment` - Kubernetes deployment
- `k8s-manifest-generator` - K8s manifest generation
- `k8s-security-policies` - K8s security
- `helm-chart-scaffolding` - Helm charts
- `terraform-specialist` - Terraform expertise
- `gitops-workflow` - GitOps workflows
- `github-actions-templates` - GitHub Actions
- `gitlab-ci-patterns` - GitLab CI

### Testing & QA
- `e2e-testing` - End-to-end testing
- `e2e-testing-patterns` - E2E testing patterns
- `javascript-testing-patterns` - JavaScript testing
- `python-testing-patterns` - Python testing
- `test-driven-development` - TDD
- `code-review-ai-ai-review` - AI code review
- `code-review-excellence` - Code review excellence
- `comprehensive-review-full-review` - Full review
- `comprehensive-review-pr-enhance` - PR enhancement
- `code-reviewer` - Code review expertise
- `code-review-and-quality` - Code review and quality

### Performance & Optimization
- `performance-optimizer` - Performance optimization
- `performance-profiling` - Performance profiling
- `application-performance-performance-optimization` - App performance
- `cost-optimization` - Cost optimization
- `aws-cost-optimizer` - AWS cost optimization

### Observability & Monitoring
- `observability-engineer` - Observability engineering
- `observability-and-instrumentation` - Instrumentation
- `observability-monitoring-monitor-setup` - Monitor setup
- `observability-monitoring-slo-implement` - SLO implementation
- `distributed-tracing` - Distributed tracing
- `prometheus-configuration` - Prometheus config
- `grafana-dashboards` - Grafana dashboards

### AI & Machine Learning
- `ai-engineer` - AI engineering
- `llm-application-dev-ai-assistant` - LLM AI assistant
- `llm-application-dev-langchain-agent` - LangChain agents
- `llm-application-dev-prompt-optimize` - Prompt optimization
- `llm-evaluation` - LLM evaluation
- `llm-ops` - LLM operations
- `llm-prompt-optimizer` - Prompt optimizer
- `llm-structured-output` - Structured output
- `llm-app-patterns` - LLM app patterns
- `rag-engineer` - RAG engineering
- `rag-implementation` - RAG implementation
- `hybrid-search-implementation` - Hybrid search
- `vector-database-engineer` - Vector databases
- `vector-index-tuning` - Vector index tuning

### Frontend & UI/UX
- `frontend-developer` - Frontend development
- `frontend-ui-engineering` - Frontend UI engineering
- `frontend-mobile-development-component-scaffold` - Mobile component scaffold
- `ui-ux-designer` - UI/UX design
- `ui-visual-validator` - Visual validation
- `design-taste-frontend` - Design taste
- `high-end-visual-design` - Visual design

### Microservices & Distributed Systems
- `microservices-patterns` - Microservices patterns
- `monorepo-architect` - Monorepo architecture
- `monorepo-management` - Monorepo management
- `service-mesh-expert` - Service mesh
- `service-mesh-observability` - Service mesh observability
- `istio-traffic-management` - Istio traffic
- `linkerd-patterns` - Linkerd patterns
- `event-sourcing-architect` - Event sourcing
- `event-store-design` - Event store design
- `cqrs-implementation` - CQRS
- `saga-orchestration` - Saga orchestration
- `domain-driven-design` - DDD
- `ddd-context-mapping` - DDD context mapping
- `ddd-strategic-design` - DDD strategic design
- `ddd-tactical-patterns` - DDD tactical patterns

### Debugging & Troubleshooting
- `debugger` - Debugging
- `debugging-strategies` - Debugging strategies
- `debugging-toolkit-smart-debug` - Smart debug
- `debugging-and-error-recovery` - Error recovery
- `error-debugging-error-analysis` - Error analysis
- `error-debugging-error-trace` - Error tracing
- `error-debugging-multi-agent-review` - Multi-agent review
- `error-detective` - Error detection
- `error-diagnostics-error-analysis` - Diagnostics analysis
- `error-diagnostics-error-trace` - Diagnostics trace
- `error-diagnostics-smart-debug` - Smart diagnostics
- `error-handling-patterns` - Error handling
- `devops-troubleshooter` - DevOps troubleshooting
- `distributed-debugging-debug-trace` - Distributed debugging

### Documentation
- `documentation-and-adrs` - Documentation and ADRs
- `docs-architect` - Documentation architecture
- `documentation-generation-doc-generate` - Doc generation
- `code-documentation-code-explain` - Code explanation
- `code-documentation-doc-generate` - Code documentation

### Git & Version Control
- `git-workflow-and-versioning` - Git workflows
- `git-advanced-workflows` - Advanced Git
- `git-pr-workflows-git-workflow` - PR workflows
- `git-pr-workflows-onboard` - PR onboarding
- `git-pr-workflows-pr-enhance` - PR enhancement
- `git-pushing` - Git pushing

### Context Management
- `context-engineering` - Context engineering
- `context-driven-development` - Context-driven dev
- `context-management-context-restore` - Context restore
- `context-management-context-save` - Context save
- `context-manager` - Context management
- `context-optimization` - Context optimization
- `context-window-management` - Window management

### Planning & Task Breakdown
- `planning-and-task-breakdown` - Planning
- `incremental-implementation` - Incremental implementation
- `spec-driven-development` - Spec-driven dev
- `source-driven-development` - Source-driven dev
- `idea-refine` - Idea refinement

### Incident Response
- `incident-responder` - Incident response
- `incident-response-incident-response` - Incident handling
- `incident-response-smart-fix` - Smart fixes
- `incident-runbook-templates` - Runbook templates

### Legacy Modernization
- `legacy-modernizer` - Legacy modernization
- `framework-migration-code-migrate` - Code migration
- `framework-migration-deps-upgrade` - Dependency upgrade
- `framework-migration-legacy-modernize` - Legacy modernize

### Dependency Management
- `dependency-management-deps-audit` - Dependency audit
- `dependency-upgrade` - Dependency upgrade
- `codebase-cleanup-deps-audit` - Codebase audit
- `codebase-cleanup-tech-debt` - Tech debt cleanup

### Refactoring
- `code-refactoring-context-restore` - Context restore
- `code-refactoring-refactor-clean` - Clean refactor
- `code-refactoring-tech-debt` - Tech debt refactor
- `codebase-cleanup-refactor-clean` - Cleanup refactor

### Blockchain & Web3
- `blockchain-developer` - Blockchain development
- `defi-protocol-templates` - DeFi protocols
- `nft-standards` - NFT standards
- `web3-testing` - Web3 testing

### Mobile Development
- `mobile-developer` - Mobile development
- `mobile-security-coder` - Mobile security
- `flutter-expert` - Flutter
- `ios-developer` - iOS
- `android-dev` - Android
- `react-native-architecture` - React Native
- `react-native-skills` - React Native skills

### Embedded Systems
- `arm-cortex-expert` - ARM Cortex
- `firmware-analyst` - Firmware
- `memory-forensics` - Memory forensics
- `memory-safety-patterns` - Memory safety

### Reverse Engineering
- `reverse-engineer` - Reverse engineering
- `anti-reversing-techniques` - Anti-reversing
- `protocol-reverse-engineering` - Protocol reverse engineering
- `binary-analysis-patterns` - Binary analysis

### Compliance
- `gdpr-data-handling` - GDPR
- `pci-compliance` - PCI
- `security-compliance-compliance-check` - Compliance check
- `security-requirement-extraction` - Requirement extraction

### SEO
- `seo-authority-builder` - Authority building
- `seo-cannibalization-detector` - Cannibalization detection
- `seo-content-auditor` - Content audit
- `seo-content-planner` - Content planning
- `seo-content-refresher` - Content refresh
- `seo-content-writer` - Content writing
- `seo-keyword-strategist` - Keyword strategy
- `seo-meta-optimizer` - Meta optimization
- `seo-snippet-hunter` - Snippet hunting
- `seo-structure-architect` - Structure architecture

### Startup
- `startup-analyst` - Startup analysis
- `startup-business-analyst-business-case` - Business case
- `startup-business-analyst-financial-projections` - Financial projections
- `startup-business-analyst-market-opportunity` - Market opportunity
- `startup-financial-modeling` - Financial modeling
- `startup-metrics-framework` - Metrics framework

### Game Development
- `game-development` - Game development
- `godot-gdscript-patterns` - Godot patterns
- `unity-developer` - Unity development
- `unity-ecs-patterns` - Unity ECS
- `minecraft-bukkit-pro` - Minecraft Bukkit

### Automation
- `billing-automation` - Billing automation
- `changelog-automation` - Changelog automation
- `github-automation` - GitHub automation
- `gitlab-automation` - GitLab automation
- `jira-automation` - Jira automation
- `confluence-automation` - Confluence automation
- `notion-automation` - Notion automation

### Workflow Orchestration
- `workflow-orchestration-patterns` - Workflow patterns
- `workflow-patterns` - Workflows
- `conductor-implement` - Conductor implement
- `conductor-manage` - Conductor manage
- `conductor-new-track` - Conductor new track
- `conductor-revert` - Conductor revert
- `conductor-setup` - Conductor setup
- `conductor-status` - Conductor status
- `conductor-validator` - Conductor validator

### Async Programming
- `async-python-patterns` - Async Python
- `go-concurrency-patterns` - Go concurrency
- `rust-async-patterns` - Rust async
- `fp-async` - FP async

### Functional Programming
- `fp-backend` - FP backend
- `fp-data-transforms` - FP data transforms
- `fp-either-ref` - FP either
- `fp-errors` - FP errors
- `fp-option-ref` - FP option
- `fp-pipe-ref` - FP pipe
- `fp-pragmatic` - FP pragmatic
- `fp-react` - FP React
- `fp-refactor` - FP refactor
- `fp-taskeither-ref` - FP task either
- `fp-ts-errors` - FP TS errors
- `fp-ts-pragmatic` - FP TS pragmatic
- `fp-ts-react` - FP TS React
- `fp-types-ref` - FP types

### Testing Patterns
- `bats-testing-patterns` - BATS testing
- `javascript-testing-patterns` - JavaScript testing
- `python-testing-patterns` - Python testing
- `e2e-testing-patterns` - E2E testing
- `testing-patterns` - Testing patterns

### Build Systems
- `bazel-build-optimization` - Bazel optimization
- `make-automation` - Make automation
- `nx-workspace-patterns` - Nx patterns
- `turborepo-caching` - Turborepo caching

### Package Management
- `python-packaging` - Python packaging
- `uv-package-manager` - UV package manager

### Temporal Workflows
- `temporal-python-pro` - Temporal Python
- `temporal-python-testing` - Temporal testing

### Search
- `search-specialist` - Search specialist
- `similarity-search-patterns` - Similarity search
- `hybrid-search-implementation` - Hybrid search

### Secrets Management
- `secrets-management` - Secrets management
- `mtls-configuration` - mTLS configuration

### SLOs
- `slo-implementation` - SLO implementation
- `observability-monitoring-slo-implement` - SLO monitoring

### Screen Reader
- `screen-reader-testing` - Screen reader testing

### Shell Scripting
- `bash-pro` - Bash pro
- `bash-scripting` - Bash scripting
- `bash-linux` - Bash Linux
- `bash-defensive-patterns` - Bash defensive
- `posix-shell-pro` - POSIX shell

### SQL
- `sql-pro` - SQL pro
- `sql-optimization-patterns` - SQL optimization
- `postgresql-optimization` - PostgreSQL optimization

### Spark
- `spark-optimization` - Spark optimization

### Solidity
- `solidity-security` - Solidity security

### SAST
- `sast-configuration` - SAST configuration
- `security-scanning-security-sast` - Security SAST

### Shellcheck
- `shellcheck-configuration` - Shellcheck configuration

### TDD
- `tdd-orchestrator` - TDD orchestrator
- `tdd-workflows-tdd-cycle` - TDD cycle
- `tdd-workflows-tdd-green` - TDD green
- `tdd-workflows-tdd-red` - TDD red
- `tdd-workflows-tdd-refactor` - TDD refactor

### Team Collaboration
- `team-collaboration-issue` - Issue collaboration
- `team-collaboration-standup-notes` - Standup notes
- `team-composition-analysis` - Team composition

### Tutorial
- `tutorial-engineer` - Tutorial engineering

### Unit Testing
- `unit-testing-test-generate` - Test generation
- `test-automator` - Test automation

### Validation
- `deployment-validation-config-validate` - Config validation
- `lint-and-validate` - Lint and validate

### Vector Database
- `vector-database-engineer` - Vector database
- `vector-index-tuning` - Vector index tuning

### WCAG
- `wcag-audit-patterns` - WCAG audit

### Workflows
- `workflow-orchestration-patterns` - Workflow orchestration
- `workflow-patterns` - Workflow patterns

### Special
- `elon-musk` - First principles thinking, innovation, disruption

## Integration with docs/13-master-prompts

The skill library integrates seamlessly with the existing master prompt framework:

- Council roles from `docs/13-master-prompts/roles/combined/`
- Domain specialists from `docs/13-master-prompts/roles/`
- Policies from `docs/13-master-prompts/` (G-03 through G-11)
- Workflows from `docs/13-master-prompts/`

## Usage

Skills are automatically activated based on task context. No manual invocation is required. The system:

1. Analyzes task scope and system context
2. Identifies relevant skills based on signals
3. Activates skills in dependency order
4. Coordinates skill interactions
5. Logs all skill activations
6. Triggers automatic task completion workflow

### Self-Improvement System

All skills are equipped with self-improvement capabilities including periodic web search, GitHub monitoring, documentation tracking, community learning, and self-validation.

See `.devin/SKILL_ACTIVATION_SYSTEM.md` for detailed self-improvement system information.

### Automatic Task Completion

After any task execution, the system automatically performs documentation updates, version management, quality assurance, build & release, and communication.

See `.devin/workflows/automatic-task-completion.md` for detailed automatic task completion workflow.

## Adding New Skills

To add a new skill:

1. Create skill directory in `.devin/skills/`
2. Create `SKILL.md` with proper metadata
3. Define activation triggers and dependencies
4. Add to skill registry
5. Test activation logic

See `SKILL_ACTIVATION_SYSTEM.md` for detailed guidelines.

## Maintenance

The skill library is maintained as part of the project's documentation governance:

- Every skill change must be logged in action logs
- Skills must be kept in sync with code changes
- Skills must follow the governance framework (G-18)
- Skills must have proper documentation and examples

## Related Documentation

- `.devin/DOCUMENTATION_STRUCTURE.md` - Documentation structure and single source of truth
- `.devin/SKILL_ACTIVATION_SYSTEM.md` - Automatic skill activation system (primary source)
- `.devin/SKILL_TEMPLATE.md` - Standard skill template (primary source)
- `.devin/workflows/automatic-task-completion.md` - Automatic task completion workflow (primary source)
- `.devin/workflows/ai-ide-automation.md` - AI IDE automation workflow (primary source)
- `.devin/workflows/skill-batch-update.md` - Skill batch update workflow (primary source)
- `docs/skill-improvement-process.md` - Skill improvement process (primary source)
- `docs/rebuilt-1-1/automatic-processes.md` - Automatic processes documentation (1:1 rebuild context)
- `docs/13-master-prompts/INDEX_PROMPT.md` (G-00) - Master prompt entry point
- `docs/13-master-prompts/GLOBAL_MASTER_PROMPT_RULES.md` (G-18) - Absolute governance rules
- `docs/13-master-prompts/PROMPT_ACTIVATION_POLICY.md` (G-13) - Role activation policy
- `docs/13-master-prompts/ROLE_MATRIX.md` (G-04) - Role ownership and coordination

## Version

Current version: 1.0.0
Last updated: 2026-06-16
