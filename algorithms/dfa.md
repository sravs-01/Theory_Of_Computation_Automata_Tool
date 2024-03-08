### Subset Construction Algorithm for DFA:

1. **Input:**
   - NFA with states Q, alphabet Σ, transition function δ, start state q₀, and set of accepting states F.

2. **Initialize:**
   - Create an empty set of states for the DFA: DQ = ∅.
   - Compute the ε-closure of the NFA's start state: \(DQ_{\text{start}} = \text{ε-closure}(q₀)\).
   - Initialize the DFA transition table as an empty table.

3. **Main Loop:**
   - While there are unmarked states in DQ:
     - Choose an unmarked state \(DQ_i\) from DQ.
     - Mark \(DQ_i\).
     - For each input symbol \(a\) in the alphabet:
       - Compute the ε-closure of the set \(DQ_i\) on input \(a\): \(DQ_{\text{next}} = \text{ε-closure}(\delta(DQ_i, a))\).
       - If \(DQ_{\text{next}}\) is not in DQ, add it as a new state and mark it.
       - Add the transition \(DQ_i \xrightarrow{a} DQ_{\text{next}}\) to the DFA transition table.

4. **DFA Accepting States:**
   - Any state in DQ that contains at least one accepting state from the NFA is an accepting state in the DFA.

5. **Output:**
   - The DFA is represented by the set of states DQ, alphabet Σ, transition table, start state \(DQ_{\text{start}}\), and set of accepting states.

### ε-closure Function:

The ε-closure of a state in the NFA is the set of states reachable from that state through ε-transitions.

\[ \text{ε-closure}(q) = \{ q \} \cup \{ p \in Q \,|\, (q, \epsilon) \xrightarrow{*} p \} \]

### Notes:
- \(DQ_i\) represents a set of states in the DFA.
- The asterisk in \((q, \epsilon) \xrightarrow{*} p\) indicates zero or more ε-transitions.

This algorithm systematically explores the states of the DFA, computing transitions based on the ε-closures of NFA states. It's essential to keep track of marked and unmarked states to avoid redundancy in state exploration.