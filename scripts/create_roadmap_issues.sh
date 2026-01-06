#!/bin/bash
# Script to create initial GitHub issues for the roadmap

set -e

# Phase 1: Stabilization
gh issue create --title "Phase 1.3: Expand Automated Tests & CI/CD" --body "Implement comprehensive end-to-end tests and set up GitHub Actions CI/CD pipeline. Aim for >80% coverage." --label "enhancement"
gh issue create --title "Phase 1.4: Implement User Authentication" --body "Add JWT-based authentication for API and React dashboard. Implement RBAC (Admin/Operator)." --label "enhancement"

# Phase 2: Deployment & Integration
gh issue create --title "Phase 2.1: Develop Kubernetes Manifests" --body "Create K8s Deployment, Service, and Ingress manifests. Add Helm charts for easier deployment." --label "enhancement"
gh issue create --title "Phase 2.2: Real UAV Hardware Support" --body "Integrate DJI SDK or MAVLink for real drone control. Add abstraction layer for hardware." --label "enhancement"
gh issue create --title "Phase 2.3: Add Alerting & Notifications" --body "Implement email/Slack notifications for critical events. Add toast notifications to dashboard." --label "enhancement"
gh issue create --title "Phase 2.4: Expand AI Capabilities" --body "Fine-tune YOLOv8 models. Implement model versioning and edge optimization." --label "enhancement"

# Phase 3: Usability & Expansion
gh issue create --title "Phase 3.1: Promote the Repo" --body "Add badges, write blog posts, and improve documentation for community engagement." --label "documentation"
gh issue create --title "Phase 3.2: Implement Load Testing" --body "Use Locust to simulate high traffic. optimize database and API performance." --label "enhancement"
gh issue create --title "Phase 3.3: Build Mobile Companion App" --body "Develop React Native mobile app for field operators." --label "enhancement"
gh issue create --title "Phase 3.4: Add Analytics Module" --body "Add charts and graphs for mission statistics and detection metrics." --label "enhancement"
gh issue create --title "Phase 3.5: Support Multi-UAV Swarms" --body "Implement swarm coordination algorithms and collision avoidance." --label "enhancement"

echo "✅ Created all roadmap issues."
