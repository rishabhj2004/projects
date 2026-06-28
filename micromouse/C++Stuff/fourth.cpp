#include <iostream>
#include <cmath>
using namespace std;
int main(){
    double radius;
    std::cout<<"Enter the radius:";
    std::cin>>radius;
    double result=3.14*pow(radius,2);
    cout<<"the area is :" << result<<endl;
    return 0;
}
