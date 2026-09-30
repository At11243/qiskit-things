# Bell and GHZ states under depolarizing noise

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error #imports tools for constructing noise models

# create the output folder
figure_folder = Path(__file__).parent / "figures"
figure_folder.mkdir(exist_ok = True)

#define a function that creates an entangled state
def make_entangled_state(number_of_qubits): #defines a function that creates either a bell or GHZ state
    circuit = QuantumCircuit(number_of_qubits) #creates a circuit with the requested number of qubits

    circuit.h(0) #places qubvit zero into an equal superposition of zero and one
    for target_qubit in range(1 , number_of_qubits): #repeats once for every remaining qubit
        circuit.cx(0 ,target_qubit) #correlates the target qubit wth qubit zero

    circuit.measure_all() #measures every qubit and creates the classical measurement bit

    return circuit # returns the completed circuit to the part of the program that requested it

#define a function that creates the depolarizing noise model

def make_noise_model(one_qubit_probability): #defines a function that constructs a noise model
    noise_model = NoiseModel() #creates an initially empty noise model

    if one_qubit_probability == 0.0: #checkes whether an ideal simulation was requested
        return noise_model #reutrns the empty noise model so no errors are applied

    two_qubit_probability = min(5 * one_qubit_probability, 0.40) #makes CX gates noisier than H gates

    one_qubit_error = depolarizing_error( #begins constructing the one-qubit error channel
        one_qubit_probability, #sets the probability that the H gate experiences an error
        1 #speciifes that this error acts on one qubit
    )

    two_qubit_error = depolarizing_error( #begins constructing the two-qubit error channel
        two_qubit_probability, #sets the probability that the CX gate experiences an error
        2, #specifies that this error acts on two qubits
    ) 

    noise_model.add_all_qubit_quantum_error( #adds the one-qubit error to every H gate
        one_qubit_error, #supplies the depolarizing error that should be applied
        ["h"], #identifies H as the gate affected by this error
    )

    noise_model.add_all_qubit_quantum_error( #adds the two-qubit error to every CX gate
        two_qubit_error, #Supplies the two-qubit depolarizing error
        ["cx"] # identifies H as the gate affected by this error
    )

    return noise_model #returns completed noise model

#define a function that runs a circuit
def run_circuit(circuit, noise_model, shots, simulator_seed): #defines a reusable circuit simulation function
    simulator = AerSimulator(noise_model= noise_model) #creates an aer simulator using the selected noise model

    compiled_circuit = transpile( #begins compiling the circuit into the selected basis gates
        circuit, #supplies the quantum circuit that should be compiled
        basis_gates = ["h", "cx"], #preserves H and CX so the noise model can identify them
        optimization_level = 0, # avoids optimizations that might remove or replcae the noisy gates
    )

    job = simulator.run( #submits the compiled circuit to the simulator
        compiled_circuit, #supplies the circuit that will be simulated
        shots = shots, #sets the number of simulated measurements
        seed_simulator = simulator_seed, #makes the random sampling reproducible
    )

    result = job.result() #retrieves the completed simulation results
    counts = result.get_counts() #retrieves the measurement counts for every observed bit string

    return counts # returns the measurement counts 

#define a function that calculates the success probability
def calculate_success_probability(counts, number_of_qubits, shots): #defines how sucess is measured
    all_zeros = "0" * number_of_qubits # construcst the all zero result, such as 00 or 000
    all_ones = "1" * number_of_qubits #  construcst the all one, such as 11 or 111

    successful_measurements = counts.get(all_zeros, 0) + counts.get(all_ones, 0) #counts correlated outcomes 
    success_probability = successful_measurements / shots #calculated probability

    return success_probability #returns the calculated probability 

#create the bell and GHZ circuits
bell_circuit = make_entangled_state(2) #creates the two qubit bell-state circuit
ghz_circuit = make_entangled_state(3) #creates the three qubit GHZ-state circuit

#define the simulation settings
noise_levels = np.array([0.0, 0.005, 0.01, 0.02, 0.04, 0.08]) #lists the H-gate error probabilities
shots = 4096 #sets the number of measurements at each noise level
base_seed = 2026 #definfes the starting reproducible random seed

bell_success_probabilities = [] #creates a list for bell-state success probabilities
ghz_success_probabilities = [] #creates a list for ghz-state success probabilities

#run the noise sweep
print("Bell and GHZ states under depolarizing noise") #prints a heading for numerical results
print()

for noise_index, one_qubit_probability in enumerate(noise_levels): #repeats the experiement at every noise level
    two_qubit_probability = min(5 * one_qubit_probability, 0.40) #Calculates the corresponding CX error rate
    noise_model = make_noise_model(one_qubit_probability) #creates the noise model for this experiment

    bell_counts = run_circuit( #begins running the bell-state circuit
        bell_circuit, #supplies the two-qubit bell circuit,
        noise_model, #supplies the current depolarizing noise model
        shots, #supplies the number of measurements 
        base_seed + noise_index, #supplies a reproducible seed for this simulation
    )

    ghz_counts = run_circuit( #begins running the ghz-state circuit
        ghz_circuit, #supplies the three-qubit ghz circuit
        noise_model, #supplies the current depolarizing noise model
        shots, #supplies the number of measurements
        base_seed + 100 + noise_index #uses a separate reproducible seed for the GHZ simulation
    )

    bell_success = calculate_success_probability( #begins calculating bell-state success
        bell_counts, #supplies the bell-state measurement counts
        2, #states that the bell circuit contains two qubits
        shots, #supplies the total number of measurements
    )

    ghz_success = calculate_success_probability( #begins calculating ghz-state success
        ghz_counts, #supplies the ghz state measurement counts
        3, #states the the ghz circuit contains three qubits
        shots, #supplies the total number of measurements
    )

    bell_success_probabilities.append(bell_success) #stores the bell-state result
    ghz_success_probabilities.append(ghz_success) #stores the GHZ-state result

    print(
        f"H error = {one_qubit_probability:.3f}, "
        f"CX error= {two_qubit_probability:.3f}, "
        f"Bell success = {bell_success:.4f}, "
        f"GHZ success = {ghz_success:.4f}"
    )

#create the noise comparison graph

noise_figure, noise_axis = plt.subplots(figsize=(9,5.5)) #creates the graph and plotting axis

noise_axis.plot( #begins plotting the bell-state results
    noise_levels, #supplies the H-gate error probabilites for the horizontal axis
    bell_success_probabilities, #supplies the bell-state success probabilities
    marker = "o", #places a circular marker at every simulated point
    markersize=7, #sets the size of the markers
    linewidth= 2, #sets the thickness of the connecting line
    color="navy",
    label="Bell state: correct outcomes 00 or 11",
)

noise_axis.plot( #begins plotting the GHZ-state results
    noise_levels,
    ghz_success_probabilities,
    marker = "s",
    markersize=7,
    linewidth=2,
    color="darkorange",
    label="GHZ state: correct outcomes 000 or 111"
)

noise_axis.set_title("Bell and GHZ correlations Under Depolarizing Noise")
noise_axis.set_xlabel("One-qubit depolarizing error probability")
noise_axis.set_ylabel("Probability of a correlated measurement")
noise_axis.set_xticks(noise_levels)
noise_axis.set_ylim(0.45, 1.03)
noise_axis.grid(alpha=0.25)
noise_axis.legend()
noise_figure.tight_layout()

#save the noise-comparison graph
noise_graph_file = figure_folder / "bell_ghz_noise_comparison.png"

noise_figure.savefig(
    noise_graph_file,
    dpi = 300,
    bbox_inches = "tight",
)
print(f"\nNoise-comparison graphg saved to: {noise_graph_file}")

#draw and save the bell-state circuit
bell_figure = bell_circuit.draw(output= "mpl", fold = -1)
bell_figure.suptitle("Two-Qubit Bell-State Circuit", fontsize=14)

bell_circuit_file = figure_folder / "bell_project_circuit.png"

bell_figure.savefig(
    bell_circuit_file,
    dpi = 300,
    bbox_inches = "tight"
)

print(f"Bell-state circuit saved to: {bell_circuit_file}")

#draw and save the ghz-state circuit
ghz_figure = ghz_circuit.draw(output="mpl", fold = -1)
ghz_figure.suptitle("Three-Qubit GHZ-State Circuit")

ghz_circuit_file = figure_folder / "ghz_project_circuit.png"

ghz_figure.savefig(
    ghz_circuit_file,
    dpi = 300,
    bbox_inches = "tight"
)
print(f"GHZ-state circuit saved to: {ghz_circuit_file}")

#display the results
plt.show()