from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt 

#Build the Bell-state Circuit
qc = QuantumCircuit(2) #Creates two qubits, both in state |0>
qc.h(0) #maps qubit zero to the state (|0> + |1>)/\sqrt{2}
qc.cx(0,1) #uses qubit zero as a control, and qubit one as a target to produce the state (|00> + |11>) / \sqrt{2} 
qc.measure_all() # adds one classical measurement bit for each qubit in the quantum circuit. This bit stores the measurements


#Draw and save the circuit
circuit_figure = qc.draw(output="mpl") #use matplotlib to render image of quantum circuit
circuit_figure.savefig(
    "bell_circuit.png", #name of file
    dpi=300, #resolution 
    bbox_inches = "tight" #border space
)

#run the circuit
simulator = AerSimulator() #the local simulator that is installed with qiskit-aer
compiled_circuit = transpile(qc,simulator) #passes our circuit through the transpiler which encodes the circuit into readable code for the simulator

result = simulator.run(
    compiled_circuit, #backend compatible circuit
    shots=1024, #how many samples to take
    seed_simulator = 2026 #random number seed
).result()

counts = result.get_counts() # gets the number of measurements of a specific state when collapsed under observation
print(counts) 

#create and save the histogram
histogram_figure = plot_histogram(
    counts, 
    title = "Bell-State Measurement Results"
)

histogram_figure.savefig(
    "bell_histogram.png",
    dpi = 300,
    bbox_inches = "tight"
)

#Display both figures
plt.show() 