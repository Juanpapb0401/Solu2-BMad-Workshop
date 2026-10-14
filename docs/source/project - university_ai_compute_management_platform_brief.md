# **University AI Compute Management Platform Initial Couse Project statement** 

## **Student Project Brief** 

## **Context** 

The university is increasing the use of local AI infrastructure for teaching, experimentation, and model training. At present, access to local GPU machines and LLM services is fragmented, manually coordinated, and difficult to govern fairly across courses, teachers, student groups, and lab staff. The institution owns a heterogeneous local GPU fleet, including many machines with 24 GB GPUs and one stronger machine with two 48 GB GPUs, which means that different workloads may require different execution conditions and placement decisions. In realistic infrastructure environments, Kubernetes can expose GPUs as schedulable resources through device plugins, allowing workloads to be assigned according to available hardware capacity. 

## **Problem Statement** 

The university needs a system that governs how local AI resources are used across academic activities. The current situation creates uncertainty about who is allowed to use which models, when training jobs may be launched, whether resources will be available for scheduled classes, and how shared GPU capacity can be allocated fairly. The institution therefore requires a platform that can control access to local models and GPU-backed services, support reservations and operational restrictions, monitor resource consumption, and provide visibility into the status and usage of the infrastructure. 

## **Project Intention** 

The purpose of this project is to specify and later design a system that manages access to local LLM inference and training resources over a shared GPU infrastructure. The system should support academic priorities, transparent resource usage, operational control, and institutional governance. At this initial stage, students must approach the problem as a whole-system specification challenge rather than as a set of pre-defined modules. The first objective is to understand the stakeholders, goals, tensions, constraints, and required capabilities of the overall system before deciding how it may later be decomposed. 

## **Stakeholders** 

The project involves multiple stakeholders with different goals and constraints: 

- **Academic administration** needs fair, policy-aligned use of institutional infrastructure, traceability of usage, and support for academic priorities. 

- **Teachers** need to ensure that students access only appropriate resources and that machines required for scheduled classes remain available. 

- **Students** need transparent access to approved models and services, clear usage limits, and understandable reasons when requests are restricted. 

- **Lab operators and infrastructure staff** need visibility into machine health, occupancy, restrictions, failures, and operational workload distribution. 

- **Privileged users or advanced researchers** may require permission to run long jobs, distributed training, or high-demand workloads under controlled conditions. 

## **High-Level Goals** 

The system is expected to support the following goals: 

- Govern which users can access which models or services. 

- Associate permissions and quotas with academic contexts such as subjects, groups, or privilege levels. 

- Support the controlled use of local models across multiple machines. 

- Allow reservation of resources or services when workloads require exclusive use of GPUs or high VRAM consumption. 

- Prevent conflicts between academic classes and general infrastructure usage. 

- Restrict some workloads, such as training jobs, to specific time windows or authorized users. 

- Provide visibility into whether machines are available, reserved, busy, idle, or failing. 

- Track and report usage in meaningful terms, including token consumption and infrastructure utilization. 

## **Operational Context** 

The project should be understood as operating over a local GPU fleet with heterogeneous hardware capacity. Some inference services or training jobs may fit on a single machine, while others may require more memory or multiple workers. Kubernetes supports the scheduling of GPUs as explicit resources through vendor device plugins, and this makes it realistic to think of local machines as part of a managed compute environment rather than as isolated desktops. Likewise, LLM-serving systems can expose metrics 

such as prompt-token and generation-token counters, which makes usage monitoring and quota enforcement plausible design concerns from the beginning.[cite:10] Distributed training can also be represented realistically because Kubeflow Training Operator supports multi-node PyTorch and TensorFlow jobs across multiple workers.[cite:24] 

## **Constraints and Tensions** 

The specification should take into account that this is a shared institutional system with competing demands. Not all users should have the same privileges. Not all models should be available to all subjects. Not all workloads should run at all times. Resource scarcity, fairness, operational control, and academic scheduling are central tensions in the problem. Some jobs may consume most or all available GPU memory, some classes may need exclusive access during specific hours, and some institutional actors may require stronger oversight than others. 

## **Scope of the First Specification** 

For the first SDD iteration, the focus is on producing a system-level specification of the whole problem. This includes identifying actors, goals, constraints, core capabilities, business rules, assumptions, and open questions. At this stage, the work should not prematurely lock the architecture, infrastructure implementation, or final modular decomposition of the solution. The emphasis is on clarifying what the institution needs the system to do and under what conditions before deciding exactly how the solution will be organized internally. 

## **Out of Scope for the First Iteration** 

The following should **not** be treated as fixed in the initial specification: 

- The final internal module split of the platform. 

- The exact database schema. 

- The exact user interface design. 

- The final deployment architecture. 

- The exact technology stack beyond the realistic context already described. 

These elements may emerge later during planning and design, but they should not replace the initial work of clarifying the institutional problem and the stakeholder expectations. 

## **Expected First Deliverable** 

The first deliverable should be a clear, structured specification of the system from the stakeholder perspective. It should describe: 

- The institutional problem. 

- The relevant stakeholders and their goals. 

- The main capabilities the system must provide. 

- The principal constraints, rules, and tensions. 

- The assumptions the team is making. 

- The open questions that still require clarification. 

- The boundaries of what the system is and is not responsible for. 

A strong first specification should reduce ambiguity about the problem space without prematurely freezing implementation details. This aligns with Spec-Driven Development, where the early artifact should define the intended behavior and constraints before planning and construction become dominant concerns. 

Starting question for the team is: 

**How should a university govern access to local LLM inference and training resources across a shared GPU fleet so that academic priorities, fairness, operational control, and observability are all preserved?** 

