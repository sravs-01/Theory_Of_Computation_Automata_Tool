# Theory_Of_Computation_Automata_Tool

## Problem Statement

The project is aimed at solving computational problems related to the conversion between different automata representations. This includes converting regular expressions (regex) to deterministic finite automata (DFA), non-deterministic finite automata (NFA), and epsilon-NFA (eNFA), as well as converting NFAs to DFAs. These conversions play a crucial role in understanding formal languages, automata theory, and their applications in computer science.

## Introduction

Finite automata are a fundamental concept in the Theory of Computation and Automata Theory. They are used to represent and recognize regular languages. A finite automaton consists of states and transitions between those states based on inputs, making it a powerful model for pattern matching and language recognition.

This project provides Python-based utilities for converting different types of automata representations, allowing students and researchers to simulate and analyze automata and regular languages. It is designed to help in understanding the theoretical aspects of automata as well as their practical applications in fields like lexical analysis and formal language processing.

## Goal of the Project

The primary goal of this project is to create a tool that allows easy conversion between different forms of automata, particularly:

1. Converting regular expressions to DFA (Deterministic Finite Automaton)
2. Converting regular expressions to eNFA (epsilon-Nondeterministic Finite Automaton)
3. Converting NFAs to DFAs

This tool will allow users to visualize and simulate how regular expressions and non-deterministic finite automata can be transformed into deterministic automata, enabling a better understanding of the automata and language theory.

## DFA / NDFA / NDFA - DFA

- **Deterministic Finite Automaton (DFA):** A state machine where for every state and input, there is exactly one transition to another state. DFAs are used to accept or reject strings in regular languages.
  
- **Nondeterministic Finite Automaton (NDFA or NFA):** A state machine where for each state and input, there may be multiple possible transitions or no transition. NFAs are easier to define but less efficient than DFAs in terms of computational power.

- **eNFA (Epsilon-NFA):** A special type of NFA that includes epsilon (empty string) transitions, allowing it to move between states without consuming any input symbols.

- **NFA to DFA Conversion:** It is known from the theory of computation that every NFA can be converted into an equivalent DFA, which has the same language recognition capability but may require more states. This project includes this conversion as part of its utility.

## Contributors

- Nadimpalli Venkata Sai Kiran Varma (CB.EN.U4CSE22424)
- Soma Siva Pravallika (CB.EN.U4CSE22440)
- Suman Panigrahi (CB.EN.U4CSE22444)
- Oruganti Sravani (CB.EN.U4CSE22457)
- Balavida Hemanth Sai Vardhan (CB.EN.U4CSE22464)

## Usage

To use the project, follow these steps:

1. Clone the repository to your local machine.
2. Install the required dependencies and tools for running the simulations.
3. Run the respective Python scripts (`nfa_to_dfa.py`, `regex_to_dfa.py`, `regex_to_enfa.py`) with appropriate inputs for automata conversion.
4. The project will output the results, displaying the corresponding DFA or eNFA based on the input.

For detailed instructions on running the project, refer to the provided User Manual.

## License

This project is licensed under the MIT License.
