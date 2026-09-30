# This program applies the fourier transofrm and its inverse to verify that the original input state is recovered

from pathlib import Path

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFTGate # impoorts qiskits quantum fourier transform gate 
from qiskit_aer import AerSimulator

#create output folder
figure_folder = Path(__file__).parent / "figures"
figure_folder.mkdir(exist_ok = True)

#define the simulation settings
number_of_qubits = 3 #sets the number of qubits used in the fourier transform
shots = 1024 #sets the number of simulated measurements
seed = 2026 # seeds the simulator seed

#construct the qft and the inverse-qft gates
qft_gate = QFTGate(number_of_qubits) #creates a three qubit QFT gate
inverse_qft_gate = qft_gate.inverse() #creates the inverse QFT gate

#construct the complete round trip circuit
qft_circuit = QuantumCircuit(number_of_qubits) #creates a quantum circuit containing three qubits
qft_circuit.x(0) #changes qubit zero from 0 to one and prepares the displayed state |001>
qft_circuit.append(qft_gate, range(number_of_qubits)) #applies the qft gate to all three qubits
qft_circuit.append(inverse_qft_gate, range(number_of_qubits)) #applies the inverse qft to all three qubits
qft_circuit.measure_all() #measures every qubit and creates classical measurement bits

#create the simulator
simulator = AerSimulator()

#compile and run the circuit
compiled_circuit = transpile(qft_circuit, simulator) 
job = simulator.run(compiled_circuit, shots = shots, seed_simulator = seed)
result = job.result()
counts = result.get_counts()

#calculate the round trip success probability
recovered_counts = counts.get("001", 0) #retrieves the number of times the original state was recovered
success_probability = recovered_counts / shots

#print the results
print("QFT round trip counts:", counts)
print(f"Probability of recovering |001>: {success_probability:.4f}")

#prepare all eight basis states for plotting
basis_states = [format(number, "03b") for number in range(8)] #creates the labels 000 through 111
state_counts = [counts.get(state, 0) for state in basis_states] #retrieves each count and uses zero for absent states
bar_colors = ["darkorange" if state == "001" else "lightsteelblue" for state in basis_states] #highlights the expected state

#create the measurement histogram
histogram_figure, histogram_axis = plt.subplots(figsize=(9,5)) 
bars = histogram_axis.bar(basis_states, state_counts, color= bar_colors)
histogram_axis.bar_label(bars, padding = 3)
histogram_axis.set_title("QFT  Followed by inverse QFT")
histogram_axis.set_xlabel("Measured computational-basis state")
histogram_axis.set_ylabel("Number of measurements")
histogram_axis.set_ylim(0, shots * 1.08)
histogram_axis.grid(axis="y", alpha=0.25)
histogram_figure.tight_layout()

#save measurement histogram
histogram_file = figure_folder / "qft_round_trip_counts.png"
histogram_figure.savefig(
    histogram_file,
    dpi = 300,
    bbox_inches = "tight"
)
print(f"\nHistogram saved to: {histogram_file}")

#draw the high level qft circuit
high_level_figure = qft_circuit.draw(output="mpl", fold =-1)
high_level_figure.suptitle("QFT and Inverse-QFT round trip", fontsize=14)

#save the high level circuit
high_level_file = figure_folder / "qft_round_trip_circuit.png"
high_level_figure.savefig(
    high_level_file,
    dpi = 300,
    bbox_inches = "tight"
)

#decompose the qft circuit
decomposed_circuit = qft_circuit.decompose(reps =2) #expands the qft blocks into lower level gates

#draw and save the decomposed circuit
decomposed_figure = decomposed_circuit.draw(output="mpl", fold = -1)
decomposed_figure.suptitle("Decomposed QFT and Inverse-QFT circuit", fontsize = 14)

decomposed_file = figure_folder / "qft_round_trip_decomposed.png"
decomposed_figure.savefig(
    decomposed_file,
    dpi = 300,
    bbox_inches = "tight"
)

#display the results
plt.show() 