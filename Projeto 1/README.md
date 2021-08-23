# IF775
Algoritmos Para Stream de Dados

Foram escolhidos dois algoritmos para implementação.
 - HyperLogLog (Python)
 - Weighted Sampling (C++)


## Para execução do HLL Python:
* Instalação de libs
 - ### pip install -r requirements.txt
 - ### python hll.py --target x --eps y --file path_to_file

## Para execução do Weighted Sampling C++:

- g++ -o ws weighted_sample.cpp
- ./ws
- --id [id] --weight [weight] --filter [field.no]  [field_value] --size [size] [arquivo.csv]

OBS: É essencial que a ordem de inserção dos atributos no Weighted Sampling seja obedecida.
