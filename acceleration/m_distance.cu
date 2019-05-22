// This program is for accelerating the manhattan distance calculation
// between pairs of basic block vectors
// Only works for single kernel files (#TODO later)
// By: Nick from CoffeeBeforeArch

#include <string>
#include <iostream>
#include <fstream>
#include <assert.h>

using namespace std;

__global__ void m_distance(){

}

// Function for reading basic blocks from files into the program
// Takes:
//  data_file:      file pointer passed by reference
//  n:              number of integers to read
//  basic_blocks:   array storing the read in basic basic block counts
void read_file(ifstream &data_file, int n_bbs, int n_threads, int *basic_blocks){
    for(int i = 0; i < (n_bbs * n_threads); i++){
        data_file >> basic_blocks[i];
    }
}

int main(int argc, char *argv[]){
    // Check if a file was passed in as an argument
    if(argc != 2){
        cout << "ERROR: No data file passed as an argument" << endl;
        assert(false);
    }

    // Open the file passed in as an argument
    ifstream data_file;
    data_file.open(argv[1]);

    // Check if the file was opened successfully
    if(!data_file){
        cout << "ERROR: Can not open file with path: " << argv[1]
            << endl;
        assert(false);
    }

    // Read kernel name, # basic blocks, and # threads
    string kernel_name;
    int n_bbs = 0;
    int n_threads = 0;
    data_file >> kernel_name;
    data_file >> n_bbs;
    data_file >> n_threads;

    // Allocate space for all the basic blocks
    int *basic_blocks  = new int[n_bbs * n_threads];

    // Read out the basic block distributions
    read_file(data_file, n_bbs, n_threads, basic_blocks);

    return 0;
}
