from pathlib import Path 

import matplotlib.pyplot as plt 
from qiskit import QuantumCircuit, transpile # imports circuit class and circuit compiler
from qiskit.visualization import plot_histogram #imports measurement histogram function
from qiskit_aer import AerSimulator #imports the local simulator
from qiskit_aer.noise import NoiseModel, depolarizing_error #imports tools for contructing a noise model

#create the output folder
figure_folder = Path(__file__).parent / "figures" 
figure_folder.mkdir(exist_ok=True)

#define the simulation settings
shots = 4096
seed = 2026
p1 = 0.02 #sets the depolarizing strength for single qubit gate operations
p2 = 0.10 #sets the depolarizing strength for two qubit gate operations

#construct bell state circuit
bell_circuit = QuantumCircuit(2)
bell_circuit.h(0)
bell_circuit.cx(0,1)
bell_circuit.measure_all()

#Run ideal simulation
ideal_simulator = AerSimulator()
ideal_compiled = transpile(bell_circuit, ideal_simulator) #compiles the circuit for ideal simulator
ideal_job = ideal_simulator.run(ideal_compiled, shots = shots, seed_simulator = seed) #runs the ideal circuit
ideal_result = ideal_job.result() #retrives the compled simulation results
ideal_counts = ideal_result.get_counts() #retrives the measurement counts

#contstruct the depolarizing errors
one_qubit_error = depolarizing_error(p1, 1) #creates a depolarizing channel for one-qubit gates
two_qubit_error = depolarizing_error(p2, 2) #creates a depolarizing channel for two-qubit gates


#construct the noise model
noise_model = NoiseModel() #Creates an initially empty Aer noise model
noise_model.add_all_qubit_quantum_error(one_qubit_error, ["h", "x", "rz", "sx"]) #adds the one qubit error to common one qubit instructions
noise_model.add_all_qubit_quantum_error(two_qubit_error, ["cx"]) #adds the two qubit error to every controlled x instruction

# run the noisy simulation 
noisy_simulator = AerSimulator(noise_model = noise_model) #creates an aer simulator containing the noise model
noisy_compiled = transpile(bell_circuit, noisy_simulator, optimization_level = 0) #compiles the circuit without gate optimization 
noisy_job = noisy_simulator.run(noisy_compiled, shots = shots, seed_simulator = seed) #runs the circuit with the simulated noise
noisy_result = noisy_job.result() #retrieves the simulation results
noisy_counts = noisy_result.get_counts() #retrives the measurement counts

#calculate the bell state success probabilities
ideal_successes = ideal_counts.get("00", 0) + ideal_counts.get("11", 0) # counts ideal shots with the expected correlated outcomes 
ideal_successs_probability = ideal_successes / shots #converts the succesful shots into a probability

noisy_successes = noisy_counts.get("00", 0) + noisy_counts.get("11", 0) #counts noisy shots with the expected correlated outcomes
noisy_success_probability = noisy_successes / shots #converts the successful shots into a probability. 

#print the numerical results
print("Ideal counts:", ideal_counts) #prints the count dictionary from the ideal simulation
print("Noisy counts:", noisy_counts) #prints the count dictionary from the noisy simulation
print(f"Ideal Bell success probability: {ideal_successs_probability:.4f}") # prints the ideal success probability
print(f"Noisy Bell success probability: {noisy_success_probability:.4f}") #prints the noisy success probability 

#create comparison histogram
histogram_figure = plot_histogram([ideal_counts, noisy_counts], legend=["Ideal", "Depolarizing noise"], color=["navy","darkorange"], figsize=(8,5)) #creates a grouped histogram comparing ideal and noisy counts
histogram_axis = histogram_figure.axes[0] # retrives the plotting axes from histogram figure
histogram_axis.set_title("Ideal and Noisy Bell-State Measurements") #upper title
histogram_axis.set_ylabel("Number of measurements") #label vertical axis
histogram_axis.grid(axis="y", alpha=0.25) # add horizontal grid
histogram_figure.tight_layout() #adjust spacing so labels are not clipped

#save the comparison histogram
histogram_file = figure_folder / "ideal_vs_noisy_bell.png" 
histogram_figure.savefig(
    histogram_file,
    dpi = 300,
    bbox_inches = "tight"
)
print(f"\nHistogram saved to: {histogram_file}")

#draw and save bell-state circuit
circuit_figure = bell_circuit.draw(output="mpl", fold= -1)
circuit_figure.suptitle("Bell-State circuit used in both simulations", fontsize=14)

circuit_file = figure_folder / "noisy_bell_circuit.png"
circuit_figure.savefig(
    circuit_file,
    dpi= 300,
    bbox_inches = "tight"
)

#display the results
plt.show() 
