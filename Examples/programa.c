int h,g,e;
int f(int a, int* b){
    int y = 2;
    if(a != 0){
	if(a != 1){
        a = 2;}
    }
    
    printf("Escriba un numero");
    scanf("%d",&a);
    printf("Ha escrito: %d",a);
    return a;
}


int main(){
    int b = 2;
    int x = f(1, &h);
    return 0;
}

