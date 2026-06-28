#include <iostream>
#include <vector>
int main(){
    std::vector <int> numbers={10,20,30};
    numbers.push_back(40);
    numbers.push_back(50);
    std::cout<<numbers[2]<<"\n";
    numbers[0]=99;
    numbers.pop_back();
    std::cout<<"The whole array:"<<"\n";
    for(int num:numbers){
        std::cout<<num<<" ";
    }
}


