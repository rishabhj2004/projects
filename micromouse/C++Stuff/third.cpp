#include <iostream>
using namespace std;

int main(){
    double sale=95000;
    cout<<"sale:"<<sale<<endl;
    double state_tax=4.0/100;
    double county_tax=2.0/100;
    double state_sum=sale*state_tax;
    double county_sum=sale*county_tax;
    cout<<"state tax: "<<state_sum << endl << "county tax: "<<county_sum<<endl;
    cout<<"total tax: "<<state_sum+county_sum<<endl<< "total sale profit: "<< sale-(state_sum+county_sum)<<endl;
    return 0;
}
