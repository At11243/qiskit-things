from pathlib import Path
from math import pi

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit 
from qiskit.circuit.library import HGate


#Create a folder for saved figures
figure_folder = Path(__file__).parent / "figures"
figure_folder.mkdir(exist_ok=True)

#Construct a one-qubit subcircuit 
block = QuantumCircuit(1, name="A") #Creates a single cubit subcircuit named A
block.append(HGate(), [0]) #Applies a Hadamard gate to qubit 0
block.rz(pi / 3, 0) # applies a pi/3 rotation around the z axis to qubit 0

# convert the subcircuit into a reusable gate
A = block.to_gate(label="A") #Converts the subcircuit into a reusable gate named A
controlled_A = A.control(1) #Creates a version of A with one control qubit
inverse_A = A.inverse() #Creates the inverse operaton A-dagger

#construct a larger circuit using these gates
qc = QuantumCircuit(2) #Creates the larger circuit with two qubits 
qc.append(A, [0]) #Applies the original A gate to qubit 0
qc.append(controlled_A, [0,1]) #Uses qubit zero as the control and qubit one as the target
qc.append(inverse_A, [1]) #Applies the inverse of A to qubit one

print(qc.draw()) #Prints a texts representation of the circuit in the terminal. 

#create graphical circuit diagram
figure = qc.draw(output="mpl", fold = -1) # creates the matplotlib circuit diagram
figure.suptitle("Reusable Gate, Controlled Gate, and Inverse Gate", fontsize = 14) #Adds a title above the diagram

#save image
output_file = figure_folder / "reusable_blocks.png" #defines the filename for the saved diagram
figure.savefig(
    output_file,
    dpi = 300,
    bbox_inches = "tight"
)

print(f"\nFigure saved to: {output_file}")
plt.show() 

