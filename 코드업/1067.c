#include <stdio.h>
int main()
{
    int a;
    scanf("%d", &a);

    if(a > 0)
    {
        printf("%s\n","plus");
        
            if(a%2==0)
            
                printf("%s\n","even");
            
            else
            
                printf("%s\n","odd");
            
        
    }
    else
    {
        printf("%s\n","minus");
        
            if(a%2==0)
            
                printf("%s\n","even");
            
            else
            
                printf("%s\n","odd");
            
        
    }
    return 0;
}