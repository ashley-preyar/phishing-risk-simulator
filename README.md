# Phishing Risk Simulator

Agent-based simulation modeling phishing susceptibility across a 100-person 
organization over 12 weeks, built on IO psychology and behavioral science principles.

## Overview
Models employee phishing susceptibility using Big Five personality traits 
(conscientiousness, risk tolerance), stress-urgency interaction effects, and 
separate knowledge vs. vigilance decay curves.

## Key Features
- 100 agent employees with unique personality profiles
- Three phishing email types: generic, urgent, authority-based
- Event-driven training triggered only by click behavior
- SOC detection layer with email-type sensitivity
- Four-panel results dashboard

## Simulation Output
![Simulation Results](phishing_simulation_results.png)

## Background
Built as a portfolio project bridging an MA in IO Psychology with a 
Security+ certification. Designed to demonstrate how behavioral science 
applies to human risk modeling in cybersecurity contexts.

## Requirements
- Python 3.x
- matplotlib
- numpy

## Usage
python3 simulation.py
