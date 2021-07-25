#include <iostream>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <algorithm>
#include <utility>
#include <random>
#include <iterator>
#include <fstream>
#include <sstream>
#include <string>

using namespace std;

bool sortbysec(const pair<int, int>& a,
	const pair<int, int>& b)
{
	return (a.second < b.second);
}
//função que peguei da internet - funcionando

//By default the sort function sorts the vector elements on basis of first element of pairs.

void remove_at(vector<pair<int, int>> &vect, int n) {
	swap(vect[n], vect[vect.size() - 1]);
	vect.pop_back();
	sort(vect.begin(), vect.end(), sortbysec);
	return;
}

int remove_random(vector<pair<int, int>> &v) {
	srand(time(NULL));
	int n = rand() % (v.size());
	int x = v[n].first;
	remove_at(v, n);
	return x;
	
} // retorna o valor que foi removido

void sinsert(vector< pair<int, int> > &v, pair<int, int> &xi) {
	v.push_back(xi);
	sort(v.begin(), v.end(), sortbysec);
	return;
}

void remove_weight(vector<pair<int, int>> &v, int x) {
	for (int i = 0; i < v.size(); i++){
		if(v[i].first == x)
		{
			remove_at(v, i);
			break;
		}
	}
	return;
} // checa se o id q vai ser apagado está no weight_vector e apaga o elemento se estiver

int vector_weight_sum(vector<pair<int, int>> &v) {
	int sum = 0;
	for (int i = 0; i < v.size(); i++)
		sum += v[i].second;
	return sum;
}

class WS {
public:
	double self_s;
	double self_tau;
	vector< pair<int, int> > H;
	vector< pair<int, int> > C;
	vector< pair<int, int> > weight_vector;

	WS(int s) { //construtor com parâmetros
		self_s = s;
		self_tau = 0;
	}

	int len() {
		return (H.size() + C.size());
	}

	//métodos de teste
	void H_check() {
		cout << "H = [";
		for (int i = 0; i < H.size(); i++) {
			cout << "(" << H[i].first << "," << H[i].second << ")";
			if (i < H.size()-1)
				cout << ", ";
		}
		cout << "]\n";
	}

	void C_check() {
		cout << "C = [";
		for (int i = 0; i < C.size(); i++) {
			cout << "(" << C[i].first << "," << C[i].second << ")";
			if (i < C.size()-1)
				cout << ", ";
		}
		cout << "]\n";
	}

	int check_weight () {
		return vector_weight_sum(weight_vector);
	}

	void update(pair<int, int> xi, bool filter_weight) {
		int x;
		int wx;
		double W;
		pair<int, int> aux;
		int i;

		x = xi.first;
		wx = xi.second;

		if (filter_weight == 1)
			weight_vector.push_back(xi);


		if (len() < self_s) {
			if (self_tau == 0) {
				sinsert(H, xi);
			}
			else {
				cout << "Error\n";
				exit(1);
			}
			return;
		}
		// chega aqui quando toda a amostra está preenchida
		W = self_tau * C.size(); 
		vector< pair<int, int> > N;
		if (wx < self_tau) {
			N.push_back(xi);
			W += wx;
		}
		else {
			sinsert(H, xi);
		}
		int H_size = H.size();
		while ((H.size() > 0) && (W >= ((self_s - H_size) * H[0].second))) {
			aux.first = H[0].first;
			aux.second = H[0].second;
			H.erase(H.begin());
			N.push_back(aux);
			W += wx;
			H_size = H.size(); //por algum motivo nao funcionou o s - H.size() direto
		}

		H_size = H.size();
		self_tau = W / (self_s - H_size);

		random_device rd;  //Will be used to obtain a seed for the random number engine
		mt19937 gen(rd()); //Standard mersenne_twister_engine seeded with rd()
		uniform_real_distribution<> dis(0.0, nextafter(1, numeric_limits<double>::max()));
		double p = dis(gen);

		i = 0;
		while (p >= 0 && i < N.size()) {
			p -= (1 - N[i].second / self_tau);
			i++;
		}
		if (p < 0) {
			remove_weight(weight_vector, N[i-1].first);
			remove_at(N, i - 1);
		}
		else {
			remove_weight(weight_vector, remove_random(C));
		}

		vector<pair<int, int>> V;
		set_union(N.begin(), N.end(), C.begin(), C.end(), back_inserter(V));
		while (C.size() != 0)
			C.pop_back();
		for (int i = 0; i < V.size(); i++)
			C.push_back(V[i]);
		//C.extend(N); UNIÃO DE C COM N
	}
	
};

// classe e função tiradas da internet
class CSVRow
{
public:
	string const& operator[](size_t index) const
	{
		return m_data[index];
	}
	size_t size() const
	{
		return m_data.size();
	}
	void readNextRow(istream& str)
	{
		string         line;
		getline(str, line);

		stringstream   lineStream(line);
		string         cell;

		m_data.clear();
		while (getline(lineStream, cell, ','))
		{
			m_data.push_back(cell);
		}
		// This checks for a trailing comma with no data after it.
		if (!lineStream && cell.empty())
		{
			// If there was a trailing comma then add an empty element.
			m_data.push_back("");
		}
	}
private:
	vector<string>    m_data;
};

istream& operator>>(istream& str, CSVRow& data)
{
	data.readNextRow(str);
	return str;
}

int main()
{
	int s;
	pair<int, int> xi;

	int id, weight, size, field;
	string input_file, field_value;

	string foo;
	int aux = 0;

	while(1) {
		cin >> foo;
		if (foo.compare("--id")!=0) {
			cout << "Invalid Input\n";
			break;
		}
		cin >> id;
		if (id != 0) {
			cout << "Invalid Input\n";
			break;
		}
		cin >> foo;
		if (foo.compare("--weight")!=0){
			cout << "Invalid Input\n";
			break;
		}
		cin >> weight;
		if (weight == 1 || weight == 2 || weight == 8 || weight > 8 || weight < 0) {
			cout << "Invalid Input\n";
			break;
		}
		cin >> foo;
		if (foo.compare("--filter")) {
			cout << "Invalid Input\n";
			break;
		}
		cin >> field;
		if (field > 8 || field < 0) {
			cout << "Invalid Input\n";
			break;
		}
		cin >> field_value;
		cin >> foo;
		if (foo.compare("--size")!=0) {
			cout << "Invalid Input\n";
			break;
		}
		cin >> size;
		cin >> input_file;
		aux = 1; // só serve pra dizer q a entrada foi colocada corretamente
		break;
	}

	//cout << id << weight << field << field_value << size << input_file;

	ifstream file(input_file);
	WS ws(size);
	CSVRow row;
	
	int i = 0;
	while (file >> row)
	{
		if (i != 0) {
			xi.first = stoi(row[id]);
			xi.second = stoi(row[weight]);
			if(row[field].compare(field_value) == 0)
				ws.update(xi,true);
			else
				ws.update(xi,false);
		}
		i = 1;
	}


	// //printando o vetor final
	// vector<pair<int, int>> result_sample;
	// set_union(ws.C.begin(), ws.C.end(), ws.H.begin(), ws.H.end(), back_inserter(result_sample));

	// cout << "result_sample = [";
	// for (int i = 0; i < result_sample.size(); i++) {
	// 	cout << "(" << result_sample[i].first << "," << result_sample[i].second << ")";
	// 	if (i < result_sample.size()-1)
	// 		cout << ", ";
	// }
	// cout << "]\n";
	if (aux)
		cout << ws.check_weight() << "\n";
	
	return 0;
}