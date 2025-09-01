# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive survey of human motion generation techniques spanning computer graphics, machine learning, biomechanics, and robotics. The goal is to create a systematic literature review, practical implementations, and comparative analysis of motion generation methods from 2015-2025.

## Repository Architecture

### Core Directory Structure
```
motion-gen-survey/
├── .magic-context/          # AI assistance context templates and prompt patterns
├── context/                 # Centralized knowledge base following magic-context pattern
│   ├── design/             # Technical specifications and architecture docs
│   ├── hints/              # How-to guides and troubleshooting for motion research
│   ├── instructions/       # Reusable prompt templates for consistent AI interactions  
│   ├── logs/               # Development session records and research outcomes
│   ├── plans/              # Implementation roadmaps and project strategies
│   ├── refcode/            # Reference implementations and code patterns
│   ├── roles/              # Specialized AI contexts for domain expertise
│   ├── summaries/          # Knowledge base and consolidated research findings
│   ├── tasks/              # Current work items (features/fixes/refactor/tests)
│   └── tools/              # Custom development utilities and research scripts
```

### Planned Implementation Structure (Phase 2+)
```
├── papers/                 # Literature collection and analysis
├── implementations/        # Code implementations and experiments  
├── datasets/               # Dataset analysis and preprocessing
├── experiments/            # Comparative studies and benchmarks
├── applications/           # Practical demonstrations
└── docs/                   # Generated documentation and reports
```

## Context System Usage

### Magic Context Integration
The `.magic-context` submodule provides AI prompt patterns and templates. Key resources:
- `general/context-dir-guide.md` - Standardized context directory methodology
- Use context files for specialized AI assistance across research domains

### Role-Based AI Assistance
Four specialized AI contexts in `context/roles/`:
- **research-analyst**: Paper analysis and trend identification
- **motion-expert**: Deep technical motion generation expertise  
- **survey-curator**: Content organization and taxonomy development
- **implementation-specialist**: Technical infrastructure and development

### Context File Standards
All context files follow HEADER format:
```markdown
## HEADER
- **Purpose**: [What this document is for]
- **Status**: [Active/Completed/Deprecated] 
- **Date**: [Creation/update date]
- **Dependencies**: [Required prerequisites]
- **Target**: [Intended audience]
```

## Development Phases

### Current Phase 1 Status (Weeks 1-2)
- ✅ Project structure and context directory setup
- ✅ Magic-context integration for AI assistance
- 🔄 Development environment configuration (pending)
- 📋 Research database and tooling setup (pending)

### Upcoming Phases
- **Phase 2** (Weeks 3-6): Systematic literature collection (300-500 papers)
- **Phase 3** (Weeks 7-10): Analysis framework and categorization
- **Phase 4** (Weeks 11-14): Synthesis and comparative analysis
- **Phase 5** (Weeks 15-16): Documentation and publication

## Research Methodology

### Literature Survey Approach
- **Target Venues**: SIGGRAPH, ICCV, CVPR, NeurIPS, ICML, ICLR, ICRA
- **Time Range**: 2015-2025 (focus on recent deep learning advances)
- **Scope**: Human motion synthesis, character animation, physics-based simulation
- **Goal**: 300-500 systematically categorized papers

### Taxonomy Framework
Primary categorization dimensions:
- **Approach Type**: Physics-based, data-driven, neural, hybrid, rule-based
- **Motion Domain**: Locomotion, upper body, full-body, facial, hand articulation
- **Application Context**: Animation, robotics, VR, medical, sports analysis
- **Technical Framework**: GANs, VAEs, diffusion models, transformers, optimization

## Key Project Challenges

### Technical Complexity
- Volume of literature (500+ papers estimated)
- Diverse approaches requiring deep domain understanding
- Rapidly evolving field with continuous new publications
- Need for consistent evaluation and comparison frameworks

### AI-Assisted Development Strategy
- Use role-based AI contexts for specialized expertise
- Leverage magic-context patterns for consistent interactions
- Maintain detailed context files for accumulated project knowledge
- Document all research sessions and outcomes in `context/logs/`

## Working with This Repository

### Before Starting Work
1. Review `context/summaries/project-overview.md` for current project status
2. Check `context/plans/survey-implementation-roadmap.md` for timeline and priorities
3. Use appropriate role context from `context/roles/` for specialized tasks
4. Consult `context/hints/howto-setup-survey-project.md` for environment setup

### Research Workflow
1. **Paper Analysis**: Follow templates in `context/roles/research-analyst/`
2. **Technical Evaluation**: Use `context/roles/motion-expert/` system prompts
3. **Organization**: Apply `context/roles/survey-curator/` methodologies
4. **Implementation**: Reference `context/roles/implementation-specialist/` patterns

### Documentation Standards
- Use HEADER format for all new context files
- Log significant research sessions in `context/logs/` with date prefixes
- Update task tracking in `context/tasks/` subdirectories
- Maintain consolidated findings in `context/summaries/`

## Important Notes

### Project Philosophy
This survey bridges academic research and practical implementation, making cutting-edge motion generation techniques accessible. Focus on both theoretical understanding and practical applicability.

### Quality Standards
- Systematic and consistent paper categorization
- Evidence-based analysis with specific citations
- Reproducible methodology and well-documented processes
- Balance between comprehensive coverage and practical insights