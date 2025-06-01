from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister
import numpy as np

# generate swap gate using CX gates
quantum_register = QuantumRegister(size=2, name="x")
swap_circuit = QuantumCircuit(quantum_register, name="swap")
swap_circuit.cx(quantum_register[0],quantum_register[1])
swap_circuit.cx(quantum_register[1],quantum_register[0])
swap_circuit.cx(quantum_register[0],quantum_register[1])
Swap = swap_circuit.to_gate()

# generate controlled Z-rotation gates using single-qubit Z-rotations and CX gates
def crz(angle):
    quantum_register = QuantumRegister(size=2, name="x")
    crz_circuit = QuantumCircuit(quantum_register,name="crz")
    crz_circuit.p(angle/2, quantum_register[1])
    crz_circuit.cx(quantum_register[0],quantum_register[1])
    crz_circuit.p(-angle/2, quantum_register[1])
    crz_circuit.cx(quantum_register[0],quantum_register[1])

    return crz_circuit

# generate double-controlled Z-rotation gates using single-qubit Z_rotations and Toffoli gates
def ccrz(angle):
    quantum_register = QuantumRegister(size=3, name="x")
    ccrz_circuit = QuantumCircuit(quantum_register,name="crz")
    ccrz_circuit.p(angle/2, quantum_register[2])
    ccrz_circuit.ccx(quantum_register[0],quantum_register[1],quantum_register[2])
    ccrz_circuit.p(-angle/2, quantum_register[2])
    ccrz_circuit.ccx(quantum_register[0],quantum_register[1],quantum_register[2])

    return ccrz_circuit

# implement QFT and inverse QFT
# code adapted from Ákos Nagy
def quantum_fourier_transform(n):
    quantum_register = QuantumRegister(size=n, name="x")
    QFT_circuit = QuantumCircuit(quantum_register, name=f"QFT")

    for q, p in zip(quantum_register[:n >> 1], reversed(quantum_register[n >> 1:])):
        #QFT_circuit.swap(q, p)
        QFT_circuit.compose(Swap,qubits=[q,p],inplace=True)


    for i, q in enumerate(quantum_register, start=1):
        QFT_circuit.h(q)
        for j, p in enumerate(quantum_register[i:], start=1):
            #QFT_circuit.cp(np.pi / (1 << j), q, p)
            QFT_circuit.compose(crz(np.pi / (1 << j)), qubits=[q,p], inplace=True)

    return QFT_circuit

def inverse_quantum_fourier_transform(n):
    quantum_register = QuantumRegister(size=n, name="x")
    inverse_QFT_circuit = QuantumCircuit(quantum_register, name=f"IQFT")

    for i, q in enumerate(reversed(quantum_register), start=1):
        for j, p in enumerate(reversed(quantum_register[n + 1 - i:]), start=1):
            #inverse_QFT_circuit.cp(- np.pi / (1 << (i - j)), q, p)
            inverse_QFT_circuit.compose(crz( -np.pi / (1 << (i-j))), qubits=[q,p], inplace=True)
            
        inverse_QFT_circuit.h(q)

    for q, p in zip(quantum_register[:n >> 1], reversed(quantum_register[n >> 1:])):
        #inverse_QFT_circuit.swap(q, p)
        inverse_QFT_circuit.compose(Swap,qubits=[q,p],inplace=True)


    return inverse_QFT_circuit

# creates a quantum circuit on 2d+1 qubits 
# given |a> |b> |c>, returns |a+b mod 2^d> |b> |c> if c=1, or |a> |b> |c> if c=0
def c_quantum_adder(d):
    a_register = QuantumRegister(size=d, name="a")
    b_register = QuantumRegister(size=d, name="b")
    c_register = QuantumRegister(size=1, name="c")
    
    quantum_adder_circuit = QuantumCircuit(a_register, b_register, c_register, name=f"{d}-qubit adder")
    
    quantum_adder_circuit.compose(quantum_fourier_transform(d), inplace=True)
    quantum_adder_circuit.barrier()

    # phaser part
    for ida, q in enumerate(reversed(a_register)):
        for idb, r in enumerate(b_register):
            quantum_adder_circuit.compose(ccrz((1 << idb) * np.pi / (1 << ida)), qubits=[2*d,r,q], inplace=True)

    quantum_adder_circuit.barrier()
    quantum_adder_circuit.compose(inverse_quantum_fourier_transform(d), inplace=True)
    
    return quantum_adder_circuit

# creates a quantum circuit on 2d+1 qubits
# given |a> |b> |c>, returns |a-b mod 2^d> |b> |c> if c=1, or |a> |b> |c> if c=0
def c_quantum_subtractor(d):
    a_register = QuantumRegister(size=d, name="a")
    b_register = QuantumRegister(size=d, name="b")
    c_register = QuantumRegister(size=1, name="c")
    
    quantum_subtr_circuit = QuantumCircuit(a_register, b_register, c_register, name=f"{d}-qubit subtractor")
    
    quantum_subtr_circuit.compose(quantum_fourier_transform(d), inplace=True)
    quantum_subtr_circuit.barrier()

    # phaser part
    for ida, q in enumerate(reversed(a_register)):
        for idb, r in enumerate(b_register):
            quantum_subtr_circuit.compose(ccrz(-(1 << idb) * np.pi / (1 << ida)), qubits=[2*d,r,q], inplace=True)

    quantum_subtr_circuit.barrier()
    quantum_subtr_circuit.compose(inverse_quantum_fourier_transform(d), inplace=True)
    
    return quantum_subtr_circuit

# creates a quantum circuit on 3d qubits
# given |a> |b> |z>, returns |a> |b> |z+ab mod 2^d> 
def quantum_multiplier(d):
    a_register = QuantumRegister(size=d, name="a")
    b_register = QuantumRegister(size=d, name="b")
    result_register = QuantumRegister(size=d, name="z")
    
    quantum_multiplier_circuit = QuantumCircuit(a_register, b_register, result_register, name=f"{d}-qubit multiplier")

    quantum_multiplier_circuit.compose(quantum_fourier_transform(d), qubits=[x+2*d for x in range(d)], inplace=True)
    quantum_multiplier_circuit.barrier()

    for k in range(d): 
        for ida, q in enumerate(reversed(a_register)):
            for idb, r in enumerate(b_register):
                quantum_multiplier_circuit.compose(ccrz((1 << (idb+k)) * np.pi / (1 << ida)), qubits=[r,q,2*d+k], inplace=True)

    quantum_multiplier_circuit.barrier()
    quantum_multiplier_circuit.compose(inverse_quantum_fourier_transform(d), qubits=[x+2*d for x in range(d)], inplace=True)
    
    return quantum_multiplier_circuit

quantum_multiplier(2).draw(output="mpl", style="bw")

# creates a quantum circuit on $3d+1$ qubits (plus $d$ ancillas) 
# that takes |x>_d |y>_d |0> |z>_d to |x>_d |y>_d |0> |z+x+y>_d 
# and |x>_d |y>_d |1> |z>_d to |x>_d |y>_d |1> |z+xy>_d
# (all arithmetic mod 2^d)  
def QCalc(d):
    a_register = QuantumRegister(size=d, name="a")
    b_register = QuantumRegister(size=d, name="b")
    z_register = QuantumRegister(size=1, name="z")
    res_register = QuantumRegister(size=d, name="result")
    ancilla = AncillaRegister(size=d, name="p")

    calc_circuit = QuantumCircuit(a_register, b_register, z_register, res_register, ancilla, name="QCalc")

    # add ab to result register
    calc_circuit.compose(quantum_multiplier(d), qubits=[x for x in range(2*d)] + [x+2*d+1 for x in range(d)], inplace=True)
    
    # if z=0: add ab to ancilla register, then a+b to result register, then subtract ab from ancilla register
    calc_circuit.x(z_register)
    calc_circuit.compose(c_quantum_adder(d), qubits=[x+3*d+1 for x in range(d)] + [x+2*d+1 for x in range(d)]+[2*d], inplace=True)
    calc_circuit.compose(c_quantum_adder(d), qubits=[x+2*d+1 for x in range(d)] + [x for x in range(d)]+[2*d], inplace=True)
    calc_circuit.compose(c_quantum_adder(d), qubits=[x+2*d+1 for x in range(d)] + [x+d for x in range(d)]+[2*d], inplace=True)
    calc_circuit.compose(c_quantum_subtractor(d), qubits=[x+2*d+1 for x in range(d)] + [x+3*d+1 for x in range(d)]+[2*d], inplace=True)
    calc_circuit.x(z_register)
    
    return calc_circuit