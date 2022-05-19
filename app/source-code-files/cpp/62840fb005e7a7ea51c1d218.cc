#include <iostream>
#include <string>
#include <thread>
#include <assert.h>
int add(int a,int b){
	return 1 ;
}

        int main (int argc, char *argv[]) { 
        
    cxxopts::Options options("AIV", "Kiem tra danh gia");
	options.add_options()
		("a", "", cxxopts::value<int>())
		("b", "", cxxopts::value<int>())	;
        
    auto result = options.parse(argc, argv); 
        
    int a = result["a"].as<int>();

	int b = result["b"].as<int>();
  
        
    auto r = add(a, b); 
        
    std::cout <<r;
        
    return 0;      
        
}