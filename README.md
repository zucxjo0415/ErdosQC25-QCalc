# ErdosQC25-QCalc
Basic Quantum Calculator

Implements a Qiskit function QCalc, using only Hadamard, X gates, (single-qubit) Z-rotations, CX gates and Toffoli gates, that takes as input a positive integer $d$ and outputs a quantum circuit QCalc on $3d+1$ qubits (plus $d$ ancillas) such that

$$\mathrm{QCalc} \left( |x\rangle_d \ |y\rangle_d \ |z\rangle_1 \ |0\rangle_d \right) = \begin{cases} 
x\rangle_d \ |y\rangle_d \ |z\rangle_1 \ |x+y\rangle_d & \mbox{if }z=0 \\
x\rangle_d \ |y\rangle_d \ |z\rangle_1 \ |x\cdot y\rangle_d & \mbox{if }z=1
\end{cases}$$

where all arithmetic is modulo $2^d$.

(A miniproject for the Summer 2025 Erdős Institute Quantum Computing bootcamp.)
