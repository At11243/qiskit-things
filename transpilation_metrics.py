#This program compares the four optimization levels present in qiskit

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import grover_operator #imports qiskits grover operator constructor

#create output folder
figure_folder = Path(__file__).parent / "figures" 
figure_folder.mkdir(exist_ok = True)

#construct the grover oracle
oracle = QuantumCircuit(2, name = "Oracle") #creates a two qubit phase-oracle circuit
oracle.cz(0,1) # marks the state |11> by changing the sign of its amplitude

#construct the grover circuit
grover_iteration = grover_operator(oracle) #combines the oracle and diffusion operaton into one Grover iteration

grover_circuit = QuantumCircuit(2) #creates the main two qubit circuit
grover_circuit.h(range(2)) #places both qubits into an equal superposition
grover_circuit.compose(grover_iteration, inplace=True) #adds one grover iteration to the circuit
grover_circuit.measure_all() #measures both qubits and creates classical measurement bits for them

#define the transpilation settings
basis_gates = ["rz", "sx", "x", "cx"] #defines the get set allowed in every compiled circuit
optimization_levels = [0,1,2,3] #lists the four available optimization levels
transpiler_seed = 2026 # makes any stochastic transpiler choices reproducible

#create storage for the results

compiled_circuits = {} #creates a dictionary to store compiled circuits
circuit_depths = [] #creates a list that will store each circuit depth
total_operations = [] #creates a list that will store each total operation count
cx_operations = [] #creates a list that will store each controlled x count

#compile the circuit at each optimization level
for level in optimization_levels: #repeats the report for each optimization level
    compiled = transpile(grover_circuit, basis_gates = basis_gates, optimization_level=level, seed_transpiler=transpiler_seed)
    compiled_circuits[level] = compiled

    depth = compiled.depth() #calculates the circuits longest dependency path
    operation_total = compiled.size() #calculates the total number of non-directive operations
    cx_total = compiled.count_ops().get("cx",0) #calculates the number of controlled x gates
    circuit_depths.append(depth) #adds the total circuit depth to the results list
    total_operations.append(operation_total) #adds the total operation count to the results list
    cx_operations.append(cx_total) #adds the contolled x count to the results list
    print(f"\nOptimization level {level}") #prints the current optimization level 
    print("Operation counts:", compiled.count_ops()) #prints a count for each operation type
    print("Total operations:", compiled.size()) #prints the total number of circuit operations
    print("Circuit depth:", compiled.depth()) #prints the circuits longest dependency path
    print("CX gates:", compiled.count_ops().get("cx", 0)) #prints the number of two qubit controlled x gates

#create the resource-comparison graph 
x_positions = np.arange(len(optimization_levels)) #creates one horizontal position for each optimization level
bar_width = 0.25 #set the width of each group of bars

metrics_figure, metrics_axis = plt.subplots(figsize=(9,5)) #creates the comparison figure and plotting axis
metrics_axis.bar(x_positions - bar_width, circuit_depths, width = bar_width, label="Circuit depth",color="navy")
metrics_axis.bar(x_positions, total_operations, width=bar_width, label="Total operations", color = "steelblue")
metrics_axis.bar(x_positions + bar_width, cx_operations, width = bar_width, label = "CX operations", color = "darkorange")
metrics_axis.set_title("Effect of Transpiler Optimiation level")
metrics_axis.set_xlabel("Optimization level")
metrics_axis.set_ylabel("Resource count")
metrics_axis.set_xticks(x_positions)
metrics_axis.set_xticklabels(optimization_levels)
metrics_axis.grid(axis="y", alpha = 0.25)
metrics_axis.legend()
metrics_figure.tight_layout()

#save the resource-comparison graph
metrics_file = figure_folder / "transpilation_metrics.png" 
metrics_figure.savefig(
    metrics_file,
    dpi = 300,
    bbox_inches = "tight"
)
print(f"\nResource graph saved to: {metrics_file}")

#draw and save the original circuit
original_figure = grover_circuit.draw(output="mpl", fold = -1)
original_figure.suptitle("Original high-level Grover circuit", fontsize=14)

original_file = figure_folder / "transpilation_original_circuit.png"
original_figure.savefig(
    original_file,
    dpi = 300,
    bbox_inches = "tight"
)

#select a representative compiled circuit
selected_level = 2 #selects moderate optimization for the circuit diagram
selected_circuit = compiled_circuits[selected_level] #retrieves the circuit compiled at optimization level two

#draw and save the compiled circuit
compiled_figure = selected_circuit.draw(output = "mpl", fold = -1)
compiled_figure.suptitle("Grover circuit after level-2 transpilation", fontsize = 14)

compiled_file = figure_folder / "transpilation_compiled_circuit.png"
compiled_figure.savefig(
    compiled_file,
    dpi = 300,
    bbox_inches = "tight"
)
print(f"Compiled circuit saved to: {compiled_file}")

#display the results
plt.show() 