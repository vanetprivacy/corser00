// filename    : gen_begin.cpp
// author      : george corser, 2015-02-10
// description : this program reads a sorted trace file (form: t, v, x, y)
//               then computes the begin and end times for each vehicle
//               and writes the output to a sorted trace file with the times
//               (form: t, v, x, y, begin, end)
// input       : sorted trace file, e.g. rural.srt, urban.srt, city.srt
// output      : same as input file but with times appended to each line

// overall design...
    // declare and open files
    // declare variables
    // read input file line-by-line to find max vehicle id
    // re-read input file and create arrays, begin_time and end_time
    // re-read input file and write output file with begin_time and end_time

// preprocessor directives
#include <fstream>    // for ifstream, ofstream
#include <string>     // for string data types
#include <iomanip>    // for formatting test setw, setprecision
#include <iostream>   // for endl, fixed
#include <cmath>      // for sqrt()
using namespace std;  // to make code more readable (no "std::" prefix)

// function: main ------------------------------------------------------------
int main()
{
    // declare and open files
    ifstream inData;		      // declare input file object
    ofstream outData;		      // declare output file object
    inData.open("city.srt"); 	  // open infile
    outData.open("city.srtt");   // open outfile
	if (!inData.is_open()) cout << "Input file is not open" << endl;
	if (!outData.is_open()) cout << "Output file is not open" << endl; 

    // declare variables
    int t, v;                     // time, vehicle number
    float x, y;                   // geographical coordinates
	int maxv = 0;
	
    // read input file line-by-line to find max vehicle id
    while (inData >> t >> v >> x >> y)   // loop through all vehicles 	
    {
		if (v>maxv) maxv=v;
    }
    cout << "maxv: " << maxv << endl;
    
    // re-read input file and create arrays, begin_time and end_time
    float begin_time[maxv+1], end_time[maxv+1];
    for (int i=0; i<maxv+1; i++)
    {
        begin_time[i] = -1.0;
        end_time[i]   = -1.0;
    }
    inData.clear();
    inData.seekg(0, inData.beg);  // reposition to beginning of input file
    while (inData >> t >> v >> x >> y)   // loop through all input data 	
    {
		if (begin_time[v]==-1) begin_time[v]=t;
		end_time[v] = t;
    }

    // re-read input file and write output file with begin_time and end_time
    inData.clear();
    inData.seekg(0, inData.beg);  // reposition to beginning of input file
    while (inData >> t >> v >> x >> y)   // loop through all input data 	
    {
		outData << t << " " << v << " " << x << " " << y << " " 
		    << begin_time[v] << " " << end_time[v] << endl;
    }

	// close files
	inData.close();
	outData.close();
}
