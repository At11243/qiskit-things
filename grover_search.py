from pathlib import Path 

import matplotlib.pyplot as plt  
from qiskit import QuantumCircuit, transpile  
from qiskit.circuit.library import grover_operator  # Imports Qiskit's Grover-operator constructor.
from qiskit.visualization import plot_histogram  # Imports Qiskit's measurement-histogram function.
from qiskit_aer import AerSimulator  

#create the output folder 
figure_folder = Path(__file__).parent / "figures"
figure_folder.mkdir(exist_ok=True)

#define the simulation settings
shots = 1024
seed = 2026

#construct the phase oracle
oracle = QuantumCircuit(2, name="Oracle") #creates the two qubit circuit that will act as the oracle
oracle.cz(0,1) # changes the sign of the |11> amplitude while leaving the other basis states alone

#construct the grover operator
grover_iteration = grover_operator(oracle) #combines the phase oracle with Grovers diffusion operation 

#construct the complete grover circuit
grover_circuit = QuantumCircuit(2)
grover_circuit.h(range(2)) #places both qubits into an equal superposition of 00,01,10 and 11
grover_circuit.compose(grover_iteration, inplace=True) #applies one complete grover interation to the superposition
grover_circuit.measure_all() #measures both qubits and creates classical bits

#create the ideal simulator
simulator = AerSimulator()

#compile and run the grover circuit
compiled_circuit = transpile(grover_circuit, simulator) 
job = simulator.run(compiled_circuit, shots= shots, seed_simulator = seed)
result = job.result()
counts = result.get_counts()

#calculate the search success probability
marked_counts = counts.get("11", 0) # retrieves the number of times the marked state 11 was measured
success_probability = marked_counts / shots 

#print the results
print("Grover measurement counts:", counts)
print(f"Probability of measuring the marked state 11: {success_probability:.4f}")

#prepare all four possible outcomes for plotting
basis_state = ["00","01","10","11"] #lists all measurement outcomes
state_counts = [counts.get(state, 0) for state in basis_state] #retrieves each count and usese zero for unobserved states


#create the grover histogram
histogram_figure, histogram_axis = plt.subplots(figsize=(8,5)) #creates the histogram figure and plotting axis
bars = histogram_axis.bar(basis_state, state_counts, color = "seagreen") #draws one bar for each possible state
histogram_axis.bar_label(bars, padding = 3) #places the numerical count above each bar
histogram_axis.set_title("Grover search result for marked state |11>")
histogram_axis.set_xlabel("Measured computation-basis state")
histogram_axis.set_ylabel("Number of measurements")
histogram_axis.set_ylim(0, shots * 1.08) #leaves sapce above the tallest bar for numerical label
histogram_axis.grid(axis="y", alpha=0.25)
histogram_figure.tight_layout()

#save the grover histogram
histogram_file = figure_folder / "grover_counts.png"
histogram_figure.savefig(
    histogram_file,
    dpi = 300,
    bbox_inches = "tight"
)
print(f"\nHistogram saved to: {histogram_file}")

#draw the high-level grover circuit
high_level_figure = grover_circuit.draw(output="mpl", fold = -1) #draws the circuit with the grover iteration shown as one block
high_level_figure.suptitle("High-level two qubit grover circuit", fontsize=14)

#save the high-level circuit
high_level_file = figure_folder / "grover_high_level_circuit.png"
high_level_figure.savefig(
    high_level_file,
    dpi = 300,
    bbox_inches = "tight"
)

#decompose the grover operator
decomposed_circuit = grover_circuit.decompose(reps = 2)

#draw and save the decomposed circuit
decomposed_figure = decomposed_circuit.draw(output="mpl", fold=-1)
decomposed_figure.suptitle("Decomposed two qubit grover circuit", fontsize=14)

decomposed_file = figure_folder / "grover_decomposed_circuit.png" 
decomposed_figure.savefig(
    decomposed_file, 
    dpi = 300,
    bbox_inches = "tight"
)
print(f"Decomposed circuit saved to: {decomposed_file}")

#display the results
plt.show()