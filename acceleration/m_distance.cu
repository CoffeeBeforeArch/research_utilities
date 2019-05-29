// This program is for accelerating the manhattan distance calculation
// between pairs of basic block vectors
// Only works for single kernel files (#TODO later)
// Maybe try GNU plot? (#TODO but Python is good for pretty pictures)
// By: Nick from CoffeeBeforeArch

#include <string>
#include <iostream>
#include <fstream>
#include <assert.h>

using namespace std;

// GPU kernel for calculating the Manhattan distance between basic block
// vectors. (#TODO easy candidate for cache tiling)
// Takes:
//  basic_blocks:   Pointer to basic block vectors
//  distances:      Pointer to Manhattan distance results
//  n_bbs    :      Number of basic blocks per basic block vector
//  n_threads:      Total number of basic block vectors
__global__ void m_distance(unsigned *basic_blocks, unsigned *distances, unsigned n_bbs, unsigned n_threads){
    // Calculate global thread position
    int tid = blockIdx.x * blockDim.x + threadIdx.x;

    // Boundary check
    if(tid < n_threads){
        // Temp variable for each distance calculation
        unsigned temp;

        // Compare this thread's BBV with all others
        for(int i = 0; i < n_threads; i++){
            // Reset temp between BBVs
            temp = 0;
            // Find distance between the two basic block counts
            for(int j = 0; j < n_bbs; j++){
                // Use sum of absolute difference intrinsic
                temp = __usad(basic_blocks[tid * n_bbs + j],
                        basic_blocks[i * n_bbs + j], temp);
            }
            
            // Write back the distance
            distances[tid * n_threads + i] = temp;
        }
    }
}

// Function for reading basic blocks from files into the program
// Takes:
//  data_file:      file pointer passed by reference
//  n:              number of integers to read
//  basic_blocks:   array storing the read in basic basic block counts
void read_file(ifstream &data_file, unsigned n_bbs, unsigned n_threads,
        unsigned *basic_blocks){
    for(int i = 0; i < (n_bbs * n_threads); i++){
        data_file >> basic_blocks[i];
    }
}

// Function for writing the Manhattan distances to a new file
// Takes:
//  output_file:    file pointer passed by reference
//  n_threads:      number of threads that had distances compared
//  distances:      array storing the Manhattan distances
void write_file(ofstream &output_file, unsigned n_threads, unsigned *distances){
    for(int i = 0; i < (n_threads * n_threads); i++){
        output_file << distances[i] << " ";
    }
    output_file << endl;
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

    // Variables to read in for each kernel of an app
    string kernel_name;
    unsigned n_bbs = 0;
    unsigned n_warps = 0;

    // Unified memory pointer
    unsigned *basic_blocks;

    // While we can still read in a kernel name
    while(getline(data_file, kernel_name)){
        // Dumb error check to break on empty kernel name (EOF?)
        if(kernel_name == "")
            break;

        // We should then get #BBs and #warps
        data_file >> n_warps;
        data_file >> n_bbs;

        // Allocate space for all the basic blocks
        cudaMallocManaged(&basic_blocks, n_bbs * n_warps * sizeof(unsigned));

        // Read out the basic block distributions
        read_file(data_file, n_bbs, n_warps, basic_blocks);

        // Allocate space for the basic block differences
        unsigned *distances;
        cudaMallocManaged(&distances, n_warps * n_warps * sizeof(unsigned));

        // Calculate grid dimensions using 512 thread TBs
        int TB_SIZE = 512;
        int GRID_SIZE = (n_warps + TB_SIZE - 1) / TB_SIZE;

        // Launch the kernel
        m_distance<<<GRID_SIZE, TB_SIZE>>>(basic_blocks, distances, n_bbs, n_warps);
    
        // Wait for the kernel to complete
        cudaDeviceSynchronize();

        // Open a file based on the kernel's name (truncate if exists)
        string output_name = kernel_name;
        output_name.append("1.txt");
        ofstream output_file;
        output_file.open(output_name.c_str(), ios::out | ios::app);
    
        // Add header to the output file
        output_file << kernel_name << endl;
        output_file << n_bbs << endl;
        output_file << n_warps << endl;

        // Write the output to a similarly formatted separate file
        write_file(output_file, n_warps, distances);

        // Close the output file
        output_file.close();

        // De-allocate unified memory
        cudaFree(basic_blocks);
    }

    // Close the data file
    data_file.close();

    return 0;
}
