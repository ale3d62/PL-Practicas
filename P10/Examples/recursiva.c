int recursiva(int i){
    if (i==0){
        return 0;
    }
    else{
        i=i-1;
        return i;
    }
}

int main(){
    int a=10,b=recursiva(a);
    printf("%d",a);
    return 0;

}