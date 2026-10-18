# NX-OS Configurator Program Decision Flow

## Overview

This document maps the complete decision flow, progress paths, and possibilities of the NX-OS Configuration Authority software. It visualizes how users navigate through the system, what decisions they make, and what outcomes are possible.

## System Architecture Flow

```mermaid
graph TB
    Start[Start Application] --> ModeSelection{Select Mode}
    
    ModeSelection -->|Quick Mode| QuickFlow[Guided Wizard Flow]
    ModeSelection -->|Architect Mode| ArchitectFlow[Expert Scenario Flow]
    ModeSelection -->|Multi-Switch Mode| MultiSwitchFlow[Multi-Switch Deployment]
    ModeSelection -->|Training Mode| TrainingFlow[Training Mode]
    
    QuickFlow --> WizardStep1[Step 1: Mode Selection]
    ArchitectFlow --> ScenarioSelect[Select Scenario Template]
    MultiSwitchFlow --> TemplateSelect[Select Deployment Template]
    TrainingFlow --> TrainingExercises[Training Exercises]
    
    WizardStep1 --> Step2[Step 2: vPC Decision]
    ScenarioSelect --> ConfigBuilder[Config Builder / Manual]
    TemplateSelect --> SwitchManagement[Switch Management]
    
    Step2 -->|vPC Yes| Step3_vPC[Step 3: Platform with vPC]
    Step2 -->|vPC No| Step3_Standalone[Step 3: Platform Standalone]
    
    Step3_vPC --> Step4[Step 4: Features]
    Step3_Standalone --> Step4
    
    Step4 --> Step5[Step 5: VLANs]
    Step5 --> Step6[Step 6: Interfaces]
    Step6 --> Step7[Step 7: Links]
    Step7 --> Step8[Step 8: Review]
    
    Step8 --> Validate{Validate Configuration}
    Validate -->|Errors| ErrorFix[Fix Errors]
    ErrorFix --> Step8
    Validate -->|Success| Generate[Generate Configuration]
    
    Generate --> Output[Output: Config Files]
    Output --> End[End]
    
    ConfigBuilder --> Generate
    SwitchManagement --> GenerateDeployment[Generate All Configs]
    GenerateDeployment --> Output
```

## Detailed Wizard Decision Tree

```mermaid
graph TD
    A[Start Wizard] --> B{Select Role}
    
    B -->|Core| C1[Core Switch Path]
    B -->|Leaf| C2[Leaf Switch Path]
    B -->|Access| C3[Access Switch Path]
    B -->|Spine| C4[Spine Switch Path]
    B -->|OOB| C5[OOB Management Path]
    
    C1 --> D1{vPC Pair?}
    C2 --> D2{vPC Pair?}
    C3 --> D3{vPC Pair?}
    C4 --> D4[No vPC - Spine]
    C5 --> D5[No vPC - OOB]
    
    D1 -->|Yes| E1[vPC Core Configuration]
    D1 -->|No| F1[Standalone Core]
    D2 -->|Yes| E2[vPC Leaf Configuration]
    D2 -->|No| F2[Standalone Leaf]
    D3 -->|Yes| E3[vPC Access Configuration]
    D3 -->|No| F3[Standalone Access]
    
    E1 --> G[Platform & Identity]
    E2 --> G
    E3 --> G
    F1 --> G
    F2 --> G
    F3 --> G
    D4 --> G
    D5 --> G
    
    G --> H[Features Selection]
    H --> I[VLAN Configuration]
    I --> J[Interface Configuration]
    J --> K[Links Configuration]
    K --> L[Review & Generate]
```

## vPC Configuration Flow

```mermaid
graph TD
    A[vPC Decision: Yes] --> B[Configure vPC Domain]
    B --> C{Domain ID Valid?}
    C -->|No| C1[Enter Valid Domain 1-4096]
    C1 --> B
    C -->|Yes| D[Configure Peer-Link Ports]
    
    D --> E{Ports Valid?}
    E -->|No| E1[Enter Valid Port Range]
    E1 --> D
    E -->|Yes| F[Configure Keepalive Ports]
    
    F --> G{Ports Valid?}
    G -->|No| G1[Enter Valid Port Range]
    G1 --> F
    G -->|Yes| H[Configure Keepalive IPs]
    
    H --> I{Use Default IPs?}
    I -->|Yes| J[Auto-generate from Domain]
    I -->|No| K[Manual IP Entry]
    
    J --> L{IPs Valid?}
    K --> L
    
    L -->|No| L1[Enter Valid IPv4 Addresses]
    L1 --> H
    L -->|Yes| M{Local != Remote?}
    
    M -->|No| M1[IPs Must Be Different]
    M1 --> H
    M -->|Yes| N[vPC Configuration Complete]
    
    N --> O[Generate Pair Configs]
    O --> P[Primary Config]
    O --> Q[Secondary Config]
```

## Multi-Switch Deployment Flow

```mermaid
graph TD
    A[Multi-Switch Mode] --> B{Select Template}
    
    B -->|vPC Core + Leaf| C1[Core-Leaf Template]
    B -->|Spine-Leaf| C2[Spine-Leaf Template]
    B -->|6-Switch Fabric| C3[6-Switch Template]
    B -->|Dual Core| C4[Dual Core Template]
    B -->|Custom| C5[Custom Deployment]
    
    C1 --> D[Add Switches]
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    
    D --> E{Configure Switch}
    E -->|Add| F[Add New Switch]
    E -->|Edit| G[Edit Existing Switch]
    E -->|Delete| H[Delete Switch]
    
    F --> I[Select Role & Model]
    I --> J[Enter Identity]
    J --> K[Configure vPC if Applicable]
    K --> E
    
    G --> L[Modify Configuration]
    L --> E
    
    H --> M{Confirm Delete}
    M -->|Yes| E
    M -->|No| E
    
    E --> N{Create vPC Pairs}
    N -->|Yes| O[Select Primary Switch]
    O --> P[Select Secondary Switch]
    P --> Q[Configure Domain & Ports]
    Q --> N
    
    N -->|No| R{Configure Uplinks}
    R -->|Yes| S[Select Source Switch]
    S --> T[Select Destination Switch]
    T --> U[Configure Ports & PO ID]
    U --> R
    
    R -->|No| V[Generate All Configurations]
    V --> W[Validate Deployment]
    W --> X{Deployment Valid?}
    
    X -->|No| Y[Fix Configuration Errors]
    Y --> E
    X -->|Yes| Z[Output Config Files]
```

## Configuration Generation Flow

```mermaid
graph TD
    A[Generate Configuration] --> B[Collect User Input]
    B --> C[Load Hardware Profile]
    C --> D[Load Scenario Template]
    D --> E[Apply Feature Selection]
    E --> F[Generate VLAN Configuration]
    F --> G[Generate Interface Configuration]
    G --> H[Generate vPC Configuration]
    H --> I[Generate Port Configuration]
    I --> J[Apply Baseline Options]
    J --> K[Render Jinja2 Template]
    K --> L[Validate Output]
    
    L --> M{Validation Pass?}
    M -->|No| N[Return Error Details]
    N --> O[User Fixes Input]
    O --> A
    
    M -->|Yes| P[Generate CLI Config]
    P --> Q[Generate Device JSON]
    Q --> R[Generate Manifest]
    R --> S[Create Change Package]
    S --> T[Write to Vault]
    T --> U[Return Success]
```

## Error Handling Flow

```mermaid
graph TD
    A[User Action] --> B{Input Valid?}
    
    B -->|Yes| C[Proceed to Next Step]
    B -->|No| D[Identify Error Type]
    
    D --> E{Error Category}
    
    E -->|Format Error| F1[Invalid Format - e.g., IP CIDR]
    E -->|Range Error| F2[Out of Range - e.g., Domain ID]
    E -->|Required Field| F3[Missing Required Field]
    E -->|Conflict Error| F4[Configuration Conflict]
    E -->|Network Error| F5[API/Network Issue]
    
    F1 --> G[Show Inline Error Message]
    F2 --> G
    F3 --> G
    F4 --> H[Show Conflict Details]
    F5 --> I[Show Network Error]
    
    G --> J[Highlight Problem Field]
    H --> J
    I --> K[Retry Option]
    
    J --> L{User Fixes?}
    L -->|Yes| A
    L -->|No| M[Keep Error State]
    
    K --> N{Retry Success?}
    N -->|Yes| C
    N -->|No| I
```

## Feature Selection Flow

```mermaid
graph TD
    A[Features Step] --> B[Baseline Options]
    A --> C[Optional Features]
    
    B --> D{Select Baseline}
    D -->|Institutional| E1[Apply Institutional Baseline]
    D -->|Minimal| E2[Apply Minimal Baseline]
    D -->|Custom| E3[Apply Custom Baseline]
    
    E1 --> F[Apply: Aliases, SNMP, CoPP]
    E2 --> G[Apply: Basic Settings]
    E3 --> H[Apply: Selected Options]
    
    C --> I{Select Features}
    
    I -->|vPC| J1[Enable vPC Feature]
    I -->|HSRP| J2[Enable HSRP Feature]
    I -->|LLDP| J3[Enable LLDP Feature]
    I -->|LACP| J4[Enable LACP Feature]
    I -->|BFD| J5[Enable BFD Feature]
    I -->|VXLAN| J6[Enable VXLAN Feature]
    I -->|NXAPI| J7[Enable NXAPI Feature]
    
    J1 --> K[Configure vPC Settings]
    J2 --> L[Configure HSRP Settings]
    J3 --> M[Configure LLDP Settings]
    J4 --> N[Configure LACP Settings]
    J5 --> O[Configure BFD Settings]
    J6 --> P[Configure VXLAN Settings]
    J7 --> Q[Configure NXAPI Settings]
    
    K --> R[Feature Configuration Complete]
    L --> R
    M --> R
    N --> R
    O --> R
    P --> R
    Q --> R
```

## VLAN Configuration Flow

```mermaid
graph TD
    A[VLANs Step] --> B{Configuration Mode}
    
    B -->|Manual| C[Manual VLAN Entry]
    B -->|Template| D[Select VLAN Template]
    
    C --> E[Add VLAN Row]
    E --> F[Enter VLAN ID]
    F --> G{VLAN Valid?}
    G -->|No| G1[Enter Valid VLAN 1-4094]
    G1 --> F
    G -->|Yes| H[Enter VLAN Name]
    
    H --> I{SVI Required?}
    I -->|Yes| J[Enter SVI IP]
    J --> K[Enter SVI Description]
    K --> L[Add Another VLAN?]
    I -->|No| L
    
    D --> M{Select Template}
    M -->|Data Center| N1[VLANs 10-50]
    M -->|Campus| N2[VLANs 100-199]
    M -->|DMZ| N3[VLANs 200-299]
    M -->|Custom| C
    
    N1 --> O[Auto-populate VLANs]
    N2 --> O
    N3 --> O
    O --> P[Customize as Needed]
    P --> L
    
    L -->|Yes| E
    L -->|No| Q[VLAN Configuration Complete]
```

## Interface Configuration Flow

```mermaid
graph TD
    A[Interfaces Step] --> B{Configuration Mode}
    
    B -->|Manual| C[Manual Interface Entry]
    B -->|Auto| D[Auto from Hardware Profile]
    
    C --> E[Add Interface Row]
    E --> F[Select Interface]
    F --> G[Set Mode]
    G --> H{Mode Type}
    
    H -->|Access| I1[Set Access VLAN]
    H -->|Trunk| I2[Set Trunk VLANs]
    H -->|Routed| I3[No VLAN]
    H -->|Bare| I4[No Configuration]
    
    I1 --> J[Add Description]
    I2 --> J
    I3 --> J
    I4 --> J
    
    J --> K{vPC Member?}
    K -->|Yes| L[Set vPC ID]
    K -->|No| M[No vPC]
    
    L --> N[Add Another Interface?]
    M --> N
    N -->|Yes| E
    N -->|No| O[Interface Configuration Complete]
    
    D --> P[Load Hardware Profile]
    P --> Q[Auto-populate Interfaces]
    Q --> R[Customize as Needed]
    R --> O
```

## Links Configuration Flow

```mermaid
graph TD
    A[Links Step] --> B{Switch Type}
    
    B -->|Core| C[Configure Downlinks]
    B -->|Leaf/Access| D[Configure Uplinks]
    B -->|Standalone| E[No Links Required]
    
    C --> F{Downlink Type}
    F -->|10G Leaf| G1[Ports 1-10]
    F -->|1G Leaf| G2[Ports 11-20]
    F -->|Mixed| G3[Both Ranges]
    
    G1 --> H[Configure Port Descriptions]
    G2 --> H
    G3 --> H
    
    H --> I[Set Trunk Mode]
    I --> J[Set Allowed VLANs]
    J --> K[Downlink Configuration Complete]
    
    D --> L{Uplink Type}
    L -->|1GB Leaf| M1[Ports 51-52]
    L -->|10GB Leaf| M2[Ports 53-54]
    
    M1 --> N[Configure Port Descriptions]
    M2 --> N
    
    N --> O[Set Destination Core]
    O --> P[Set Trunk Mode]
    P --> Q[Uplink Configuration Complete]
    
    E --> R[Links Configuration Complete]
```

## Review and Generation Flow

```mermaid
graph TD
    A[Review Step] --> B[Display Configuration Summary]
    B --> C[Show Switch Details]
    C --> D[Show vPC Configuration]
    D --> E[Show VLAN List]
    E --> F[Show Interface List]
    F --> G[Show Links Configuration]
    
    G --> H{User Review}
    H -->|Changes Needed| I[Return to Step]
    I --> J[Modify Configuration]
    J --> A
    
    H -->|Approve| K[Validate Configuration]
    K --> L{Validation Pass?}
    
    L -->|No| M[Show Validation Errors]
    M --> N[Fix Errors]
    N --> K
    
    L -->|Yes| O[Generate Configuration]
    O --> P[Render CLI Output]
    P --> Q[Generate Device JSON]
    Q --> R[Create Manifest]
    R --> S[Write Files to Vault]
    S --> T[Display Success Message]
    T --> U[Configuration Complete]
```

## Progress Tracking Flow

```mermaid
graph LR
    A[Step 1: Mode] --> B[Step 2: vPC]
    B --> C[Step 3: Platform]
    C --> D[Step 4: Features]
    D --> E[Step 5: VLANs]
    E --> F[Step 6: Interfaces]
    F --> G[Step 7: Links]
    G --> H[Step 8: Review]
    
    A -.->|Progress: 12.5%| Progress[Overall Progress]
    B -.->|Progress: 25%| Progress
    C -.->|Progress: 37.5%| Progress
    D -.->|Progress: 50%| Progress
    E -.->|Progress: 62.5%| Progress
    F -.->|Progress: 75%| Progress
    G -.->|Progress: 87.5%| Progress
    H -.->|Progress: 100%| Progress
    
    style Progress fill:#0A84FF,stroke:#007AFF,stroke-width:2px
```

## Decision Points Summary

| Step | Decision | Options | Impact |
|------|----------|---------|--------|
| Mode Selection | Operating Mode | Quick, Architect, Multi-Switch, Training | Determines entire workflow |
| Role Selection | Switch Role | Core, Leaf, Access, Spine, OOB | Sets available features |
| vPC Decision | vPC Enabled | Yes, No | Enables/disables vPC configuration |
| Platform | Hardware Model | 9336C-FX2, 93180YC-EX, 9348GC-FXP | Determines port availability |
| Features | Baseline Options | Institutional, Minimal, Custom | Sets default configuration |
| Features | Optional Features | vPC, HSRP, LLDP, LACP, BFD, VXLAN, NXAPI | Enables specific capabilities |
| VLANs | Configuration Mode | Manual, Template | Speed of configuration |
| Interfaces | Configuration Mode | Manual, Auto | Level of customization |
| Links | Link Type | Uplink, Downlink, None | Network topology |
| Review | Approval | Approve, Modify | Final generation decision |

## Complexity Analysis

### Current Complexity (8 Steps)
- **Decision Points**: 15+
- **Possible Paths**: 50+
- **Average Clicks to Complete**: 40-60
- **Cognitive Load**: High (multiple contexts)

### Proposed Complexity (5 Steps)
- **Decision Points**: 10
- **Possible Paths**: 25
- **Average Clicks to Complete**: 25-35
- **Cognitive Load**: Medium (consolidated contexts)

## Key Improvement Areas

1. **Reduce Decision Fatigue**: Consolidate related decisions
2. **Simplify Navigation**: Fewer steps, clearer progression
3. **Improve Context**: Keep related information together
4. **Enhance Feedback**: Better error messages and validation
5. **Visual Clarity**: Better representation of complex configurations

## Conclusion

This decision flow analysis reveals that while the NX-OS Configurator is comprehensive, the current 8-step wizard creates unnecessary complexity. By consolidating related decisions and improving the visual hierarchy, we can significantly reduce cognitive load while maintaining all functionality. The proposed improvements focus on simplifying the existing user journey without adding new features.
