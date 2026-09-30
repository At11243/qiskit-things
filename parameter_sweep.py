from pathlib import Path #tools for constructing files and file paths

import matplotlib.pyplot as plt #tools for creating and displaying graphs
import numpy as np #mathematical arrays and functions
from qiskit import QuantumCircuit, transpile #imports the circuit class and circuit compiler
from qiskit.circuit import Parameter #imports qiskits symbolic circuit parameter class
from qiskit_aer import AerSimulator #imports the local aer simulator

# make the folder for the figures
figure_folder = Path(__file__).parent / "figures" #definesa  figures folder beside the python file.
figure_folder.mkdir(exist_ok=True) #creates the folder if it doesn't exist


theta = Parameter("theta") #defines a symbolic parameter named Theta

#Create the parameterized circuit 

template = QuantumCircuit(1,1) #Creates a circuit containing one qubit and one classical bit
template.h(0) #places qubit 0 into an equal superposition
template.rz(theta, 0) #applies a symbolic rotation of theta around the z axis
template.h(0) # Converts the accumulated relative phase into a population difference. This circuit effectively acts as a ramsey interferometer
template.measure(0,0)  # measures qubit zero and stores the result in classical bit zero. 

#define the simulation settings
angles = np.linspace(0, 2 * np.pi, 25) #creates 25 equally spaced angles from 0 to 2pi
shots = 4096 #sets the number of simulated measurements at each angle
simulator = AerSimulator() # chooses the local aer simulator
p0_values = [] #Creates an empty list that will store the measured probabilities of zero 

#run the parameter sweep
for index,angle in enumerate(angles): #repeats the calculation for every angle in the sweep
    bound_circuit = template.assign_parameters({theta: float(angle)}) # replaces theta with the current numerical angle
    compiled_circuit = transpile(bound_circuit, simulator) #converst the circuit into instructions supported by Aer
    job = simulator.run(compiled_circuit, shots = shots, seed_simulator = 2026 + index) #executes the circuit with a reproducable seed
    result = job.result() #retrives the simulation result
    counts = result.get_counts() #retrives the measurements for each state
    zero_counts = counts.get("0", 0) #retrives the number of zero outcomes or returns zero if none occured
    p0 = zero_counts / shots #converts the number of zero outcomes into an estimated probability
    p0_values.append(p0) #adds the estimated probability to the results list
    print(f"theta = {angle:.3f} rad, counts = {counts}, P(0) = {p0:.4f}") #prints the result for this angle. 


#calculate the theoretical result
theory_values = np.cos(angles / 2) ** 2 #calculates the theoretical predication P(0) = cos^2 (theta/2)

#create the parameter sweep graph
figure, axis = plt.subplots(figsize = (8,5)) #creates a figure and a set of plotting axes.
axis.plot(angles, theory_values, color="navy", linewidth=2, label="Ideal Theory") #draws the continuous theoretical curve
axis.plot(angles, p0_values, color="darkorange", label="Aer Simulation") 
axis.set_title("Parameterized H-Rz(theta)-H Circuit") # adds the title
axis.set_xlabel("Rotation angle theta (radians)") #adds the x-axis label
axis.set_ylabel("Probability of measuring zero") #adds the y-axis label
axis.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])  # Places ticks at multiples of pi
axis.set_xticklabels(["0", "pi/2", "pi", "3pi/2", "2pi"])  # Gives the selected tick locations labels
axis.set_ylim(-0.03, 1.03)  # Sets the vertical range slightly beyond zero and one
axis.grid(alpha=0.25)  # Adds a faint grid to make values easier to read
axis.legend()  # Displays labels identifying the theoretical curve and simulation points
figure.tight_layout()  # Adjusts spacing so the labels are not clipped

#save the parameter sweet graph
graph_file = figure_folder / "parameter_sweep.png" #defines the filename for the parameter sweep graph
figure.savefig(
    graph_file,
    dpi = 300, 
    bbox_inches = "tight"
)
print(f"\nGraph saved to: {graph_file}")

#draw and save circuit diagram
circuit_figure = template.draw(output="mpl", fold = -1) #Draws the circuit while preserving theta 
circuit_figure.suptitle("Parameterized H-Rz(theta)-H Circuit", fontsize = 14) #adds title
circuit_file = figure_folder / "parameterized_circuit.png" #defines filename for circuit diagram
circuit_figure.savefig(
    circuit_file,
    dpi = 300,
    bbox_inches = "tight"
)
print(f"Circuit diagram saved to: {circuit_file}")

#show results
plt.show()